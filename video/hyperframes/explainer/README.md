# Portfolio explainer v2 (60 s)

One film, each tool doing what it is best at:

| Part | Tool | Where |
| --- | --- | --- |
| The film: hook, JOPAD flow with a cursor that causes it, 14-solution fly-through, transitions, claim, end card | HyperFrames | `index.html`, `compositions/` |
| The plinth as a self-drawing technical drawing (plan → elevation, 450 × 450 × 1000 mm) | Manim Community Edition | `sources/manim/plinth.py` → `assets/video/plinth.mp4` |
| The hostel waste chart: six days rise, 150.4 kg lands, bars regroup into composition | Remotion | `sources/remotion/src/WasteChart.tsx` → `assets/video/waste.mp4` |
| Craft rules: kinetic type landing with squash, cuts and holds, easing by role | motion-skills (kinetic-typography, beat-sync-editing, animation-principles) | throughout |
| Acceptance: rhythm, rests, bursts, audio silences | OneTake `verify_promo.py` | passes all legs |

Music: "Day of the Fast Food" by Andrey Avkhimovich, CC BY 3.0 (Jamendo, via Openverse); credited on the end card.
The bed is cut with `video/tools/hyperframes/edit_music.py music-edits.json`; effects are placed with `place_audio.py audio-cues.json`.

```sh
(cd sources/manim && manim -qh --fps 30 -r 1920,1080 plinth.py Plinth)            # → copy to assets/video/plinth.mp4
(cd sources/remotion && npm install && npx remotion render src/index.ts WasteChart out/waste.mp4)
DO_NOT_TRACK=1 hyperframes render --quality looks -o raw.mp4
MASTER_TP=-3.6 python3 ../../tools/hyperframes/master_audio.py raw.mp4 explainer.mp4
python3 ~/.claude/skills/onetake/scripts/verify_promo.py explainer.mp4 --shots 0,2.35,3,6,11.18,11.5,14.2,19,23,26.6,30,30.55,35.5,43.8,46,48.3,53
```
