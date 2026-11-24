# Portfolio videos

Motion-graphics videos built from the site's own fonts, colours, photos and data.
Every fact on screen comes from `src/data/*.ts`.

## 30-second motion piece (current)

| File | What it is |
| --- | --- |
| `motion.html` | The animation: a small CSS 3D engine with a virtual camera (drone passes, push-ins, whip pans, zoom-throughs), depth of field and per-letter fly-ins. `window.seek(t)` draws the frame at `t` seconds. Open it with `?play` to watch, add `&v` for 9:16. |
| `render-motion.mjs` | Renders it to MP4 with motion blur (6 sub-frames per frame), film grain and the soundtrack. |
| `cues.mjs` | Reads the sound cues the page registers (time, kind, on-screen position). |
| `build_audio.py` | Synthesises the 120 BPM music and the sound effects from those cues and masters the mix. |
| `stills-motion.mjs` | Saves PNG stills at chosen times, for checking layout. |
| `portfolio-motion-16x9.mp4`, `portfolio-motion-9x16.mp4` | The rendered videos. |

```sh
npm install                                   # fonts come from node_modules
pip install numpy scipy soundfile pedalboard
python3 video/build_audio.py soundtrack.wav
node video/render-motion.mjs h video/portfolio-motion-16x9.mp4 soundtrack.wav
node video/render-motion.mjs v video/portfolio-motion-9x16.mp4 soundtrack.wav
```

Each format takes about 20 minutes to render. For a quick check of one part, add
`--from 6 --to 12`, or lower the motion blur with `--sub 2`.

## 60-second explainer (first version)

`explainer.html`, `timeline.js`, `render.mjs` and `stills.mjs` make the earlier flat
60-second version (`portfolio-explainer.mp4`). Run `node video/render.mjs` to re-render its
picture; its soundtrack was made by an earlier `build_audio.py` (see git history).
