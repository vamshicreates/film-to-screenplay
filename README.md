# Film-to-Screenplay (`film-to-screenplay`)

**Automated SRT-to-Hollywood Screenplay Reconstruction & Legal PDF Compiler Skill for AI Coding Agents.**

Give the agent **any movie title** (and optional language/transliteration preference—such as **Telugu, Tamil, Hindi, Kannada, or Malayalam direct dialogues written in English words**, or pure English), and it automatically:
1. Locates and downloads the complete theatrical/OTT `.srt` subtitle track and segments it into chronological act chunks aligned to scene gaps.
2. Dispatches **6 parallel screenwriter subagents** to reconstruct the **entire unabridged 150–210+ page feature screenplay** in strict **Fountain / Final Draft Screenplay Format** (`INT.`/`EXT.` sluglines, present-tense English action staging, standardized ALL-CAPS character cues, parentheticals, and crystal-clear direct dialogues).
3. Compiles the finished script into a **US Letter, 12pt Courier Hollywood Screenplay PDF** (`1.5"` left binding margin, `1.0"` right/top/bottom margins, top-right pagination, automatic orphan protection).
4. **Permanently embeds the 4-Pillar Legal & Fair-Dealing Disclaimer on Page 1 (Title Page)** of the PDF and generates a **1080×1080 Static Disclaimer Image Card (`.png`)** for community giveaways—explaining that the script is an independent, SRT-based reconstruction (~90–95% faithful to the theatrical cut) shared free of charge for non-commercial screenwriting study, with zero official affiliation and zero mention of AI.

---

## Embedded 4-Pillar Legal Protection

Every compiled PDF Title Page and generated `Disclaimer_Card.png` automatically includes:
1. **No Official Affiliation / Passing-Off Protection**: Explicitly states the document is an *unofficial, independent reconstruction* and is **not** provided or endorsed by the director, writers, producers, or production house.
2. **Transparent SRT Provenance (~90–95% Match)**: Clarifies the script was transcribed and formatted from the released film's subtitle (SRT) track (~90–95% faithful to the theatrical cut; minor errors may exist), proving no studio NDA or confidential pre-production draft was leaked.
3. **Non-Commercial Educational Fair Dealing**: Frames the giveaway strictly as a free, non-commercial educational resource created to help aspiring writers and filmmakers read and study screenplay structure.
4. **Copyright & IP Attribution**: Acknowledges that all underlying characters, story, and intellectual property belong solely to the original creators and copyright holders.

---

## Quick Installation & Usage Prompts

### Prompt 1 — Install Skill
```text
Install the film-to-screenplay skill from https://github.com/vamshicreates/film-to-screenplay into my skills directory (~/.gemini/config/skills/film-to-screenplay and .agents/skills/film-to-screenplay).
```

### Prompt 2 — Generate Any Movie Screenplay PDF (with Transliterated Direct Dialogues)
```text
Use the film-to-screenplay skill.
Write the complete movie script for "<Movie Name>" with <Telugu/Tamil/Hindi/English> direct dialogues (written in English words) and character names in absolute Hollywood screenplay format, and give me the legally protected PDF and static disclaimer card.
```

---

## Repository Structure

```text
film-to-screenplay/
├── SKILL.md                             # Complete multi-agent workflow & screenplay formatting rules
├── README.md                            # Documentation, legal pillars & usage prompts
├── LICENSE                              # MIT License
└── scripts/
    ├── fetch_and_segment_srt.py         # Automated SRT search, download & scene-gap act chunker
    └── compile_screenplay_pdf.py        # 12pt Courier PDF compiler + Title Page legal disclaimer + 1080x1080 PNG card generator
```
