# Batman Arkham Shadows — AI‑Assisted 2D Game

**A hands‑on experiment in building a full 2D game by driving development with natural‑language prompts to an AI assistant.**  
This repo contains the playable game, supporting assets, documentation, and teaching materials that show how AI can accelerate development and explain code changes as a learning tool.

---

### TL;DR
- **Code size:** ~2,346 lines of Python  
- **Highlights:** 7 boss territories, auto sprite splitting, procedural ambient music, performance caching, checkpoint + 3 lives system  
- **Pedagogy:** After each feature request the AI produced explanations of code changes, turning the project into a step‑by‑step Python learning experience.

---

## Demo / Visuals
**Include the Nano Banana infographic** (recommended filename: `infographic.png`) at the top of the repo or as the README banner to maximize visual impact. The infographic summarizes the pipeline, key metrics, and dashboard visuals.

---

## Key Features
- **Seven Villain Territories** in fixed progression: Two‑Face → Joker → Penguin → Scarface → Killer Croc → Bane → Deathstroke  
- **Auto Sprite Splitting**: converts multi‑pose images into animation frames and maps frames to actions (idle, run, jump, punch, kick, throw, special)  
- **Unique Boss AI**: state machines and villain‑specific behaviors (coin flip for Two‑Face, erratic Joker, multi‑phase Bane, adaptive Deathstroke)  
- **Gameplay Systems**: combos, batarang projectiles, henchmen spawns, checkpoints, respawn invincibility, HUD with golden bat lives  
- **Performance Optimizations**: sprite caching and preprocessing to target ~60 FPS  
- **Procedural Audio**: lightweight ambient and boss themes generated algorithmically  
- **Learning Layer**: AI explanations for each code change to teach dataclasses, enums, state machines, caching, image slicing, and more

---

## How to Run (Quick)
**Prerequisites**
- Python 3.10 recommended  
- `pip` available

**Install**
```bash
pip install pygame
```

**Run**
```bash
python batman_arkham_shadows.py
```

**Controls**
- **Move:** Arrow keys or WASD  
- **Jump:** Space  
- **Punch:** Z  
- **Kick:** X  
- **Batarang:** C  
- **Pause:** P  
- **Quit:** ESC

---

## Repository Structure (Representative)
```
batman_arkham_shadows/
├── batman_arkham_shadows.py    # main game loop
├── graphics.py                  # GraphicsManager, sprite caching
├── entities/                    # Player, Villain, Henchman classes
├── audio/                       # procedural music generator
├── sprites/                     # backgrounds, villains, henchmen
├── docs/                        # transcripts, design docs, prompts
├── assets/                      # demo video, infographic
└── README.md
```

> **Note:** Keep villain and background filenames consistent with villain names (e.g., `joker.png`, `backgrounds/joker.jpg`) to enable automatic loading.

---

## Architecture Overview
- **Game Loop:** central controller for states and level progression  
- **GraphicsManager:** sprite loading, background scaling, caching, background removal utilities  
- **SpriteSheetSplitter:** auto‑detects grid layouts and slices frames into named actions  
- **Entity Hierarchy:** `Entity` base class with `Player`, `Villain`, and `Henchman` subclasses  
- **Territory Manager:** loads villain‑named backgrounds and spawns level content  
- **Music Engine:** procedural audio generator for ambient and boss themes  
- **UI:** HUD, level intros, lives display

---

## Learning Outcomes (What this project teaches)
- **Object‑Oriented Design:** classes, inheritance, polymorphism  
- **State Machines:** enemy AI and animation control  
- **Image Processing:** sprite splitting, background removal, caching strategies  
- **Performance:** profiling and caching to maintain frame rate  
- **Audio Synthesis:** simple procedural sound generation  
- **Practical Python:** dataclasses, enums, file I/O, surface blitting, static utilities

---

## Example: How the AI Was Used
- Feature requests were expressed in plain English (e.g., “Add 3 lives and respawn at last safe position”).  
- The AI implemented the feature and returned the modified code plus a clear explanation of what changed and why.  
- This iterative loop turned each feature into a teachable unit.

---

## Demo Script (10 minutes) — For maintainers or reviewers
1. **Start the game**: `python batman_arkham_shadows.py`  
2. **Show HUD & controls**: demonstrate movement, punch, kick, batarang.  
3. **Demonstrate checkpoint & lives**: intentionally die, show respawn at last safe position and golden invincibility glow.  
4. **Advance to a boss**: defeat henchmen, trigger boss fight, show unique boss behavior (e.g., Joker’s erratic moves).  
5. **Open docs**: show `docs/` folder with transcripts and the “How to build 2D Python Game with the help of AI.docx” for learning context.  
6. **Show sprite assets**: open `sprites/villains/` and explain auto‑splitting logic in `graphics.py` or `spritesheet_splitter.py`.  
7. **Play a short boss theme**: demonstrate procedural audio via `audio/music_generator.py`.

---

## Contributing
- **Fork** the repo and create a feature branch.  
- **Mark new or modified code** with `# NEW` or `# MODIFIED` comments for easy review.  
- **Add assets** using the villain‑named convention to keep automatic loading working.  
- **Open a PR** with a clear description and a short demo video or GIF if possible.

---

## Documentation & Resources
- `docs/How to build 2D Python Game with the help of AI.docx` — step‑by‑step feature log and learning notes  
- `docs/meeting_transcript.txt` — recorded session transcript and commentary  
- `assets/` — demo video, infographic, and example sprites

---

## License
Add a license file (recommended: **MIT**) to make the project easy to reuse for educational purposes.

---

## Next Steps (Suggested)
- Add JSON animation config files for fine‑tuned frame mapping.  
- Provide a small web demo or GIFs for the README to increase discoverability.  
- Create a short tutorial series (3–5 lessons) that walks learners through one feature per lesson using the AI explanations.  
- Add unit tests for core systems (sprite splitting, territory loading, respawn logic).

---

## Contact & Credits
- **Author:** Arni (Arnold Nemeth)  
- **AI Assistant:** Claude Opus 4.5 (used as a development and teaching partner)  
- **Sprite generation:** Nano Banana Pro (pose generation)  
- **Infographic:** Nano Banana

---

If you want, I can now **generate the final `README.md` file content** in Markdown ready to paste into your repository, including a short banner section that references the infographic and a ready‑to‑copy demo script. Which filename should I use for the infographic in the README example (e.g., `infographic.png`)?
