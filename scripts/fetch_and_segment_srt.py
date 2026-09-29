#!/usr/bin/env python3
"""
fetch_and_segment_srt.py
Searches for a film's SRT subtitle track (or accepts a local .srt file),
parses all timestamped dialogue blocks, marks scene transitions (>8s gaps),
and splits the film into N balanced chronological act chunks for parallel
screenplay reconstruction.
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request


def search_subtitlecat(query: str, prefer_keyword: str = ""):
    """Search SubtitleCat for matching SRT files and return the best download URL."""
    encoded = urllib.parse.quote_plus(query)
    search_url = f"https://www.subtitlecat.com/index.php?search={encoded}"
    req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    sub_pages = re.findall(r'href=["\'](subs/\d+/[^"\']+\.html)["\']', html)
    if not sub_pages:
        raise RuntimeError(f"No subtitle entries found on SubtitleCat for query: {query}")

    # Rank pages by prefer_keyword (e.g., TELUGU, TAMIL, HINDI, Original, AMZN, WEB-DL)
    ranked = sorted(
        sub_pages,
        key=lambda p: (
            prefer_keyword.lower() in p.lower() if prefer_keyword else False,
            "amzn" in p.lower() or "web-dl" in p.lower() or "bluray" in p.lower(),
        ),
        reverse=True,
    )

    for page_rel in ranked[:8]:
        page_url = "https://www.subtitlecat.com/" + page_rel.lstrip("/")
        req_p = urllib.request.Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
        p_html = urllib.request.urlopen(req_p, timeout=15).read().decode("utf-8", errors="ignore")
        en_links = re.findall(r'href=["\'](/subs/\d+/[^"\']+-en\.srt)["\']', p_html)
        orig_links = re.findall(r'href=["\'](/subs/\d+/[^"\']+-orig\.srt)["\']', p_html)
        all_srt = re.findall(r'href=["\'](/subs/\d+/[^"\']+\.srt)["\']', p_html)
        chosen = (en_links or orig_links or all_srt)
        if chosen:
            srt_url = "https://www.subtitlecat.com" + chosen[0]
            req_s = urllib.request.Request(srt_url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req_s, timeout=20).read().decode("utf-8", errors="ignore")
            if len(data.splitlines()) > 200:
                return srt_url, data

    raise RuntimeError(f"Could not download a valid SRT file for query: {query}")


def ts_to_sec(ts: str) -> float:
    h, m, s_ms = ts.strip().split(":")
    s, ms = re.split(r"[,.]", s_ms)
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(content: str):
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    blocks = [b.strip() for b in content.strip().split("\n\n") if b.strip()]
    items = []
    for b in blocks:
        lines = [ln.strip() for ln in b.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        # Find timestamp line
        ts_idx = -1
        for idx, ln in enumerate(lines):
            if "-->" in ln:
                ts_idx = idx
                break
        if ts_idx == -1 or ts_idx + 1 >= len(lines):
            continue
        m = re.match(
            r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)",
            lines[ts_idx],
        )
        if not m:
            continue
        s = ts_to_sec(m.group(1))
        e = ts_to_sec(m.group(2))
        txt = " ".join(lines[ts_idx + 1 :])
        txt = re.sub(r"<[^>]+>", "", txt).strip()
        if not txt:
            continue
        items.append(
            {
                "id": len(items) + 1,
                "start_ts": m.group(1)[:8],
                "end_ts": m.group(2)[:8],
                "s": s,
                "e": e,
                "text": txt,
            }
        )
    return items


def segment_items(items, num_chunks: int = 6, scene_gap_sec: float = 8.0):
    n = len(items)
    if n == 0:
        raise ValueError("Parsed 0 subtitle blocks from SRT.")
    if num_chunks <= 1 or n < num_chunks * 20:
        return [items]

    chunks = []
    target_size = n // num_chunks
    start_idx = 0
    for c in range(num_chunks - 1):
        approx_end = (c + 1) * target_size
        best_i = approx_end
        best_gap = -1.0
        lo = max(start_idx + 25, approx_end - 45)
        hi = min(n - 25, approx_end + 45)
        for i in range(lo, hi):
            gap = items[i]["s"] - items[i - 1]["e"]
            if gap > best_gap:
                best_gap = gap
                best_i = i
        chunks.append(items[start_idx:best_i])
        start_idx = best_i
    chunks.append(items[start_idx:])
    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Download or load a movie SRT file and segment it into chronological act chunks."
    )
    parser.add_argument("--query", help="Movie search query (e.g. 'Pushpa The Rise 2021')")
    parser.add_argument("--prefer", default="", help="Preferred release keyword (e.g. 'TELUGU', 'HINDI', 'TAMIL')")
    parser.add_argument("--srt-file", help="Path to an existing local .srt file (skips download if provided)")
    parser.add_argument("--output-dir", required=True, help="Directory to write raw.srt, chunks, and manifest.json")
    parser.add_argument("--chunks", type=int, default=6, help="Number of chronological act chunks (default: 6)")
    parser.add_argument("--gap-seconds", type=float, default=8.0, help="Timestamp gap in seconds to flag a new scene beat")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    raw_srt_path = os.path.join(args.output_dir, "source.srt")

    if args.srt_file and os.path.exists(args.srt_file):
        with open(args.srt_file, "r", encoding="utf-8", errors="ignore") as f:
            srt_data = f.read()
        source_info = os.path.abspath(args.srt_file)
    elif args.query:
        srt_url, srt_data = search_subtitlecat(args.query, args.prefer)
        source_info = srt_url
    else:
        print("Error: Provide either --query or --srt-file", file=sys.stderr)
        sys.exit(1)

    with open(raw_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_data)

    items = parse_srt(srt_data)
    chunks = segment_items(items, num_chunks=args.chunks, scene_gap_sec=args.gap_seconds)

    manifest = {
        "source": source_info,
        "raw_srt_path": os.path.abspath(raw_srt_path),
        "total_dialogue_blocks": len(items),
        "num_chunks": len(chunks),
        "chunks": [],
    }

    for idx, ch in enumerate(chunks, start=1):
        chunk_path = os.path.join(args.output_dir, f"chunk_{idx}.txt")
        with open(chunk_path, "w", encoding="utf-8") as out:
            prev_e = ch[0]["s"]
            for it in ch:
                gap = it["s"] - prev_e
                if gap >= args.gap_seconds:
                    out.write(f"\n--- [GAP {gap:.1f}s -> NEW BEAT / SCENE AT {it['start_ts']}] ---\n")
                out.write(f"[{it['id']:04d}] ({it['start_ts']}) {it['text']}\n")
                prev_e = it["e"]

        chunk_meta = {
            "chunk_index": idx,
            "path": os.path.abspath(chunk_path),
            "start_item": ch[0]["id"],
            "end_item": ch[-1]["id"],
            "line_count": len(ch),
            "start_time": ch[0]["start_ts"],
            "end_time": ch[-1]["end_ts"],
            "first_line": ch[0]["text"],
            "last_line": ch[-1]["text"],
        }
        manifest["chunks"].append(chunk_meta)

    manifest_path = os.path.join(args.output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
