# Film-to-Screenplay (`film-to-screenplay`)

**Universal SRT-to-Hollywood Screenplay Reconstruction & Legal PDF Compiler Skill for AI Coding Agents.**

Give the agent **any movie title**—from *Animal*, *Oppenheimer*, *Salaar*, *RRR*, *Vikram*, or *KGF* to any classic or modern film—and it automatically:
1. Looks up the film's exact **Director**, **Screenplay/Dialogue Writers**, **Music Composer**, **Production House**, and **Character Roster**.
2. Locates and downloads the complete theatrical/OTT `.srt` subtitle track and segments it into 6 balanced chronological act chunks aligned to scene gaps (`> 8.0s`).
3. Dispatches **6 parallel screenwriter subagents** to reconstruct the **entire unabridged 150–210+ page feature screenplay** in strict **Fountain / Final Draft Screenplay Format** (`INT.`/`EXT.` sluglines, present-tense English action staging, standardized ALL-CAPS character cues, parentheticals, and direct dialogues in either Romanized original language—such as Hindi, Telugu, Tamil, Kannada, Malayalam in English words—or English).
4. Compiles the finished script into a **US Letter, 12pt Courier Hollywood Screenplay PDF** (`1.5"` left binding margin, `1.0"` right/top/bottom margins, top-right pagination, automatic orphan protection).
5. **Dynamically embeds a Movie-Specific 4-Pillar Legal & Fair-Dealing Disclaimer on Page 1 (Title Page)** of the PDF and generates a **`1080×1080` Static Disclaimer Image Card (`.png`)** tailored with that exact film's title, director, writers, and production house—with zero mention of AI.

---

## Dynamic 4-Pillar Legal Protection (Tailored to Every Movie)

For whatever movie you request (e.g., *Animal*, *Pushpa*, *Oppenheimer*), `compile_screenplay_pdf.py` dynamically generates and embeds the disclaimer naming that specific film and its creators:
1. **No Official Affiliation / Passing-Off Protection**: Explicitly states the screenplay for `"<Movie Title>"` is an *unofficial, independent reconstruction* and is **not** provided or endorsed by the director (`<Director>`), writers (`<Writers>`), or producers (`<Production House>`).
2. **Transparent SRT Provenance (~90–95% Match)**: Clarifies the script was transcribed and formatted from the released film's subtitle (SRT) track (~90–95% faithful to the theatrical cut; minor variations may exist), proving no studio NDA or confidential pre-production draft was leaked.
3. **Non-Commercial Educational Fair Dealing**: Frames the giveaway strictly as a free, non-commercial educational resource created to help aspiring writers and filmmakers read and study screenplay structure.
4. **Copyright & IP Attribution**: Acknowledges that all underlying characters, story, and intellectual property belong solely to the original creators and copyright holders.

---

## Quick Installation & Usage Prompts

### Prompt 1 — Install Skill
```text
Install the film-to-screenplay skill from https://github.com/vamshicreates/film-to-screenplay into my skills directory (~/.gemini/config/skills/film-to-screenplay and .agents/skills/film-to-screenplay).
```

### Prompt 2 — Generate Any Movie Screenplay PDF (Examples)
```text
Write the Animal movie script with Hindi direct dialogues (written in English words) and character names in absolute screenplay format, and give me the PDF and disclaimer card.
```
```text
Give me the complete screenplay for Oppenheimer in PDF using the film-to-screenplay skill.
```
```text
Write the Salaar movie script with Telugu direct dialogues (written in English words) in PDF.
```

---

## Repository Structure

```text
film-to-screenplay/
├── SKILL.md                             # Universal multi-agent workflow & screenplay formatting rules
├── README.md                            # Documentation, legal pillars & usage prompts
├── LICENSE                              # MIT License
└── scripts/
    ├── fetch_and_segment_srt.py         # Automated SRT search, download & scene-gap act chunker
    └── compile_screenplay_pdf.py        # 12pt Courier PDF compiler + dynamic movie-specific legal disclaimer + 1080x1080 PNG card generator
```
