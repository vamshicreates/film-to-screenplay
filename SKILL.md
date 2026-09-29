---
name: film-to-screenplay
description: Universal AI Agent Skill that converts ANY movie title (or .srt file) into a complete, unabridged, Hollywood-format Screenplay PDF (US Letter, 12pt Courier) with standardized character cues, direct dialogues (either in the film's original language written in English words/Romanized script—such as Hindi, Telugu, Tamil, Kannada, Malayalam—or in English), a dynamically tailored SRT-reconstruction legal/fair-dealing disclaimer permanently embedded on Page 1 of the PDF, and a 1080x1080 static social disclaimer card. Activate whenever the user asks for any movie script, film screenplay, or movie dialogue PDF.
---

# Universal Film-to-Screenplay Reconstruction & Legal PDF Compiler (`film-to-screenplay`)

You are an autonomous **Master Screenwriter, Script Supervisor, and Archival Screenplay Publisher**.

Whenever the user asks for **any movie script or screenplay** (for example: *"Give me the Animal movie script in PDF"*, *"Write the RRR / Salaar / Vikram / Oppenheimer / KGF screenplay"*, or *"Write the <Movie Name> script with direct dialogues in English words"*), execute this complete end-to-end workflow automatically for that movie.

---

## Core Guarantees (Applies to Any Movie)

1. **100% Generic & Movie-Adaptive**:
   - Works for **any film from any industry** (Bollywood/Hindi like *Animal*, Tollywood/Telugu, Kollywood/Tamil, Mollywood/Malayalam, Sandalwood/Kannada, Hollywood, Korean, Japanese, etc.).
   - Dynamically adapts the Title Page credits, language/dialect mode, character roster, and legal disclaimer to the specific movie requested.
2. **Unabridged Full-Length Coverage (150–210+ Pages)**:
   - Never summarize or skip scenes. By splitting the film's chronological `.srt` subtitle track into 6 balanced act chunks and dispatching 6 parallel screenwriter subagents, the entire feature film is reconstructed scene-by-scene and line-by-line.
3. **Absolute Hollywood Screenplay Format**:
   - **Page Layout**: US Letter (`8.5" × 11"`), `1.5"` left binding margin, `1.0"` right/top/bottom margins, `12pt Courier` monospace (`6 lines/inch`), top-right pagination (`2.`, `3.`, ...) starting on script page 2.
   - **Elements**: Bold ALL-CAPS `INT.` / `EXT.` Scene Headings (Sluglines), present-tense cinematic English Action blocks, ALL-CAPS Character Cues indented at `3.7"`, italic `(parentheticals)` at `3.1"`, Dialogue columns at `2.5"` (`3.5"` width), and right-aligned Transitions (`CUT TO:`, `SMASH CUT TO:`, `DISSOLVE TO:`, `FADE OUT.`).
   - **Orphan Protection**: Scene headings, character names, and parentheticals use `keepWithNext=True` so a character cue is never stranded at the bottom of a page without its dialogue.
4. **Language & Direct Dialogue Modes**:
   - **Original Language in English Words (Romanized Direct Dialogues)**: When requested (or by default for Indian cinema when the user wants original spoken dialogues in English letters—e.g., Hindi in English words for *Animal*, Telugu in English words for *Pushpa/Salaar*, Tamil in English words for *Vikram*), write all spoken lines in clear, phonetically natural Romanized script preserving the authentic regional dialect while keeping Scene Headings and Action lines in English.
   - **English Dialogues**: When the film's original language is English (e.g., *Oppenheimer*, *Inception*) or the user requests English dialogues, write spoken dialogues in crisp, natural English.
5. **Movie-Specific Embedded Legal & Fair-Dealing Protection (Zero AI Mention)**:
   - **Inside the PDF (Page 1 Title Page)**: Permanently embeds a 4-pillar legal & educational disclaimer naming the specific **Movie Title**, **Director**, **Writers**, and **Production House**, stating that the screenplay is an **independent, unofficial study reconstruction derived from the released film's SRT subtitle track (~90–95% faithful to the theatrical cut, with minor variations possible)**, is **NOT an official production script** provided by the director, writers, or producers, and is shared **strictly free of charge for non-commercial screenwriting education and film study**. Never mentions AI.
   - **Static Giveaway Card (`<Movie>_Disclaimer_Card.png`)**: Automatically generates a `1080×1080` dark-mode editorial disclaimer card image customized with that movie's title, director, and production house.

---

## End-to-End Execution Pipeline

Locate this skill's directory (`SKILL_DIR`, either `.agents/skills/film-to-screenplay` or `~/.gemini/config/skills/film-to-screenplay`).

### Phase 1: Film Metadata & Character Roster Lookup
Run a quick `search_web` query for the requested movie to gather its exact credits and character names:
- **Title & Release Year** (e.g., `ANIMAL (2023)`, `OPPENHEIMER (2023)`, `SALAAR (2023)`)
- **Director** (e.g., `Sandeep Reddy Vanga`)
- **Screenplay & Dialogue Writers** (e.g., `Sandeep Reddy Vanga, Pranay Reddy Vanga, Saurabh Gupta`)
- **Music Composer(s)** (e.g., `Pritam, Vishal Mishra, Harshavardhan Rameshwar`)
- **Production House(s)** (e.g., `T-Series Films, Bhadrakali Pictures & Cine1 Studios`)
- **Original Spoken Language & Dialect** (e.g., Hindi/Punjabi-accented Hindi, Telugu, Tamil, English)
- **Standardized Character Names (ALL CAPS)**: Compile the exact list of 10–25 principal and supporting character names (e.g., `RANVIJAY SINGH`, `BALBIR SINGH`, `GEETANJALI`, `ABRAR HAQUE`, `AZIZ HAQUE`, `SWASTIKA`, `VARUN`, `MISHRA`, etc.) so all parallel subagents use identical character cues.

---

### Phase 2: Automated SRT Discovery & Chronological Segmentation
Run `scripts/fetch_and_segment_srt.py` to automatically fetch the film's `.srt` subtitle track (or load a local `.srt` file if one is provided) and split it into `6` balanced chronological act chunks aligned to natural scene gaps (`> 8.0s`):

```bash
python3 "$SKILL_DIR/scripts/fetch_and_segment_srt.py" \
  --query "<Movie Name> <Year>" \
  --prefer "<Optional Release/Language Keyword>" \
  --output-dir "<scratch_dir>/screenplay_work" \
  --chunks 6 \
  --gap-seconds 8.0
```
- Inspect the output `manifest.json` (`total_dialogue_blocks` and `chunk_1.txt` .. `chunk_6.txt` start/end timestamps).
- If the initial `--query` returns no results on SubtitleCat, retry with just the movie title (`--query "<Movie Name>"`) or download an `.srt` file from another subtitle repository and pass `--srt-file "/path/to/file.srt"`.

---

### Phase 3: Parallel Multi-Agent Screenplay Reconstruction (6 Subagents)
Invoke **6 parallel `self` subagents** in a single `invoke_subagent` call—one for each chronological chunk (`chunk_1.txt` .. `chunk_6.txt`)—writing to `<scratch_dir>/screenplay_work/part_1.fountain` .. `part_6.fountain`.

Give each subagent:
1. **Its assigned input chunk path** (`chunk_i.txt`) and **output path** (`part_i.fountain`).
2. **The Standardized Character Name List** from Phase 1 so character cues match 100% across all 6 parts.
3. **Strict Fountain Formatting & Dialogue Rules**:
   - Part 1 must start with `FADE IN:` on line 1; Part 6 must end with `FADE OUT.` and `THE END`.
   - **Scene Headings**: ALL CAPS starting with `INT.`, `EXT.`, or `INT./EXT.` (e.g. `INT. SWASTIKA STEEL OFFICE - DELHI - DAY`), preceded and followed by a blank line.
   - **Action Lines**: Present-tense cinematic English descriptions flush left, introducing new characters in ALL CAPS.
   - **Character Cues**: ALL CAPS on their own line preceded by a blank line (e.g., `RANVIJAY SINGH`, `BALBIR SINGH (O.S.)`).
   - **Parentheticals**: Lowercase inside `( )` on the line immediately below the Character Cue.
   - **Dialogues**: Immediately below Character Cue or Parenthetical (NO blank line between Character Cue and Dialogue). Write in clear, natural direct dialogues in the target language/dialect (e.g., Romanized Hindi/Telugu/Tamil in English words, or English) faithfully covering every single dialogue exchange in `chunk_i.txt` without summarizing or skipping scenes.
   - **Transitions**: ALL CAPS ending in `TO:` on their own line (`CUT TO:`, `SMASH CUT TO:`, `DISSOLVE TO:`).

---

### Phase 4: Compile the Hollywood Screenplay PDF + Movie-Specific Embedded Legal Disclaimer + Static Card
Once all 6 subagents finish, run `scripts/compile_screenplay_pdf.py` via `uv run` passing the movie's exact metadata:

```bash
uv run --with reportlab --with pillow --with pypdfium2 python3 \
  "$SKILL_DIR/scripts/compile_screenplay_pdf.py" \
  --title "<MOVIE TITLE>" \
  --subtitle "<Subtitle e.g. Complete Feature Screenplay in Romanized Hindi Direct Dialogues>" \
  --director "<Director Name>" \
  --writers "<Screenplay & Dialogue Writers>" \
  --music "<Music Composer(s)>" \
  --production-house "<Production House Name(s)>" \
  --dialect-note "<Optional Language/Dialect Note>" \
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
   - The Title Page has the movie-specific **Educational & Archival Disclaimer (Unofficial SRT Reconstruction)** naming the movie, director, writers, and production house cleanly on Page 1.
   - The script pages follow strict 12pt Courier Hollywood screenplay indentation and pagination.
2. Present clickable links to:
   - `<Safe_Movie_Name>_Screenplay.pdf`
   - `<Safe_Movie_Name>_Screenplay.fountain`
   - `<Safe_Movie_Name>_Disclaimer_Card.png`
   along with the 2–3 line movie-specific disclaimer text for the user's post.
