---
name: film-to-screenplay
description: End-to-end AI Agent Skill that turns any movie title (or .srt file) into a complete, unabridged, Hollywood-format Screenplay PDF (US Letter, 12pt Courier) with direct dialogues (including Romanized regional dialects like Telugu, Tamil, Hindi, Kannada, Malayalam in English words, or English), standardized character cues, a permanently embedded SRT-reconstruction legal/fair-dealing disclaimer on the PDF Title Page, and a 1080x1080 static social disclaimer card. Activate whenever the user asks for a movie script, film screenplay, or transliterated movie dialogue script in PDF.
---

# Film-to-Screenplay Reconstruction & Legal PDF Compiler (`film-to-screenplay`)

You are an autonomous **Master Screenwriter, Script Supervisor, and Archival Screenplay Publisher**.

Whenever the user gives you a **movie name** (e.g., *"Give me the script for Pushpa 1"*, *"Write the RRR screenplay with Telugu dialogues in English words"*, *"Give me the Salaar / Kalki / Animal / Vikram movie script in PDF"*) or provides an `.srt` file, execute this complete end-to-end pipeline automatically without asking the user to do manual steps.

---

## Core Guarantees
1. **Unabridged Full-Length Coverage (150–210+ Pages)**: Never summarize or skip scenes. By splitting the film's chronological `.srt` subtitle track into 6 act chunks and dispatching 6 parallel screenwriter subagents, the entire 2–3 hour feature film is written line-by-line.
2. **Absolute Hollywood Screenplay Format**:
   - **Page Layout**: US Letter (`8.5" × 11"`), `1.5"` left binding margin, `1.0"` right/top/bottom margins, `12pt Courier` monospace (`6 lines/inch`), top-right pagination (`2.`, `3.`, ...) starting on script page 2.
   - **Elements**: Bold ALL-CAPS `INT.` / `EXT.` Scene Headings (Sluglines), present-tense cinematic English Action blocks, ALL-CAPS Character Cues indented at `3.7"`, italic `(parentheticals)` at `3.1"`, Dialogue columns at `2.5"` (`3.5"` width), and right-aligned Transitions (`CUT TO:`, `SMASH CUT TO:`, `DISSOLVE TO:`, `FADE OUT.`).
   - **Orphan Protection**: Scene headings, character names, and parentheticals use `keepWithNext=True` so a character name is never stranded at the bottom of a page without its dialogue.
3. **Direct Dialogues (Transliterated Regional Dialect or English)**:
   - When the user asks for **direct dialogues in English words (Romanized Telugu / Tamil / Hindi / Kannada / Malayalam)**, every spoken line is written in crystal-clear, phonetically natural Romanized script preserving the film's authentic regional dialect (e.g., Chittoor/Rayalaseema Telugu for *Pushpa*, Godavari/Telangana slang, etc.) while keeping Scene Headings and Action descriptions in crisp English.
4. **Embedded Legal & Fair-Dealing Protection (Zero AI Mention)**:
   - **Inside the PDF (Page 1 Title Page)**: Permanently embeds a 4-pillar legal & educational disclaimer stating that the screenplay is an **independent, unofficial study reconstruction derived from the released film's SRT subtitle track (~90–95% faithful to the theatrical cut, with minor variations possible)**, is **NOT an official production script** provided by the director, writers, or production house, and is shared **strictly free of charge for non-commercial screenwriting education and film study**. Never mentions AI.
   - **Static Giveaway Card (`<Movie>_Disclaimer_Card.png`)**: Automatically generates a `1080×1080` dark-mode editorial disclaimer card image ready for social/community giveaways.

---

## End-to-End Execution Pipeline

### Phase 1: Film Metadata & Character Roster Lookup
Use `search_web` (1 quick query) to verify the film's exact credits and character names:
- **Title & Release Year** (e.g., `PUSHPA: THE RISE - PART 1 (2021)`)
- **Director & Screenplay Writer** (e.g., `Sukumar`)
- **Dialogue Writer(s)** (e.g., `Srikanth Vissa`)
- **Music Composer** (e.g., `Devi Sri Prasad`)
- **Production House** (e.g., `Mythri Movie Makers & Muttamsetty Media`)
- **Standardized Character Names (ALL CAPS)**: Compile the exact list of 10–20 principal and supporting character names so all parallel subagents use identical spelling.

---

### Phase 2: Automated SRT Discovery & Chronological Segmentation
Run `scripts/fetch_and_segment_srt.py` to automatically fetch the film's `.srt` subtitle track (or load a local `.srt` file if one exists in the workspace) and split it into `6` balanced chronological act chunks aligned to natural scene gaps (`> 8.0s`):

```bash
python3 /Users/rachanalekkala/Documents/VamshiCreates/AntiGravity/VamshiCreates/.agents/skills/film-to-screenplay/scripts/fetch_and_segment_srt.py \
  --query "<Movie Name> <Year>" \
  --prefer "<Language Keyword e.g. TELUGU / HINDI / TAMIL>" \
  --output-dir "<scratch_dir>/screenplay_work" \
  --chunks 6 \
  --gap-seconds 8.0
```
- Inspect the printed JSON manifest (`total_dialogue_blocks`, and `chunk_1.txt` .. `chunk_6.txt` start/end timestamps).
- If SubtitleCat does not have the film under that exact query, try a broader `--query` (e.g. title without year) or search the web for an alternative `.srt` URL and pass `--srt-file`.

---

### Phase 3: Parallel Multi-Agent Screenplay Reconstruction (6 Subagents)
Invoke **6 parallel `self` subagents** in a single `invoke_subagent` tool call—one for each chronological chunk (`chunk_1.txt` .. `chunk_6.txt`)—writing to `<scratch_dir>/screenplay_work/part_1.fountain` .. `part_6.fountain`.

Pass each subagent:
1. **Its assigned input chunk path** (`chunk_i.txt`) and **output path** (`part_i.fountain`).
2. **The Standardized Character Name List** from Phase 1 so character cues match 100% across all 6 parts.
3. **Strict Fountain Formatting & Dialogue Rules**:
   - Part 1 must begin with `FADE IN:` on line 1; Part 6 must end with `FADE OUT.` and `THE END`.
   - **Scene Headings**: ALL CAPS starting with `INT.`, `EXT.`, or `INT./EXT.` (e.g. `EXT. SESHACHALAM FOREST - NIGHT`), preceded and followed by a blank line.
   - **Action Lines**: Present-tense cinematic English descriptions flush left, introducing new characters in ALL CAPS.
   - **Character Cues**: ALL CAPS on their own line preceded by a blank line (e.g., `PUSHPA RAJ`, `KESHAVA (V.O.)`).
   - **Parentheticals**: Lowercase inside `( )` on the line immediately below the Character Cue.
   - **Dialogues**: Immediately below Character Cue or Parenthetical (NO blank line between Character Cue and Dialogue). Write in clear, natural direct dialogues in the target language/dialect (e.g., Romanized Telugu in English words) faithfully covering every single dialogue line in `chunk_i.txt` without summarizing or skipping scenes.
   - **Transitions**: ALL CAPS ending in `TO:` on their own line (`CUT TO:`, `SMASH CUT TO:`, `DISSOLVE TO:`).

---

### Phase 4: Compile the Hollywood Screenplay PDF + Embedded Legal Disclaimer + Static Card
Once all 6 subagents complete, run `scripts/compile_screenplay_pdf.py` via `uv run`:

```bash
uv run --with reportlab --with pillow --with pypdfium2 python3 \
  /Users/rachanalekkala/Documents/VamshiCreates/AntiGravity/VamshiCreates/.agents/skills/film-to-screenplay/scripts/compile_screenplay_pdf.py \
  --title "<MOVIE TITLE>" \
  --subtitle "Complete Feature Screenplay in Romanized <Language> Direct Dialogues" \
  --director "<Director Name>" \
  --writers "<Dialogue / Screenplay Writers>" \
  --music "<Music Composer>" \
  --production-house "<Production Company Name>" \
  --dialect-note "All spoken dialogues are written in direct <Language> (Romanized English script) preserving authentic regional dialect." \
  --output-pdf "<Workspace_Dir>/<Safe_Movie_Name>_Screenplay.pdf" \
  --output-fountain "<Workspace_Dir>/<Safe_Movie_Name>_Screenplay.fountain" \
  --disclaimer-image "<Workspace_Dir>/<Safe_Movie_Name>_Disclaimer_Card.png" \
  --preview-dir "<scratch_dir>/screenplay_work/previews" \
  "<scratch_dir>/screenplay_work/part_1.fountain" \
  "<scratch_dir>/screenplay_work/part_2.fountain" \
  "<scratch_dir>/screenplay_work/part_3.fountain" \
  "<scratch_dir>/screenplay_work/part_4.fountain" \
  "<scratch_dir>/screenplay_work/part_5.fountain" \
  "<scratch_dir>/screenplay_work/part_6.fountain"
```

---

### Phase 5: Visual Verification & Delivery
1. Call `view_file` on `<scratch_dir>/screenplay_work/previews/page_1.png`, `page_2.png`, and `<Workspace_Dir>/<Safe_Movie_Name>_Disclaimer_Card.png` to visually verify:
   - The Title Page has the embedded **Educational & Archival Disclaimer (Unofficial SRT Reconstruction)** clearly printed at the bottom.
   - The script pages follow strict 12pt Courier Hollywood screenplay indentation and top-right pagination.
2. Present the clickable links to:
   - `<Safe_Movie_Name>_Screenplay.pdf`
   - `<Safe_Movie_Name>_Screenplay.fountain`
   - `<Safe_Movie_Name>_Disclaimer_Card.png`
   along with the 2–3 line copy-paste disclaimer text for the user's community post.
