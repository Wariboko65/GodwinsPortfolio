# Portfolio films (HyperFrames)

Three takes on the 30-second portfolio film, built with [HyperFrames](https://github.com/heygen-com/hyperframes)
(HTML + GSAP rendered frame by frame). The storylines are in `STORYLINES.md`; the renders are in `renders/`.

| Project | Storyline | Music |
| --- | --- | --- |
| `film-a/` | Two paths, one shape: match cuts, the booking card becomes the plinth outline on the drop | MusicGen 120 BPM cinematic electronic, filter build into a drop at 12.5 s |
| `film-b/` | One continuous flight: a single 3D camera move, no cuts (`gen_flight.py` writes it) | MusicGen deep house + sub drone, one 22 s filter swell into the 150.4 kg payoff |
| `film-c/` | Verbs on the beat: kinetic type cut on the beat grid (`gen_scenes.py` writes it) | MusicGen 808 future bass, 123 BPM, drop at 14.6 s |

Every fact on screen comes from `src/data/*.ts`. Sound effects are the Pixabay-licensed set bundled with HyperFrames
(`assets/sfx/CREDITS.md`), given deeper takes by `video/tools/hyperframes/sfx_variants.py`.

```sh
cd video/hyperframes/film-a
DO_NOT_TRACK=1 hyperframes check            # lint, layout, contrast
DO_NOT_TRACK=1 hyperframes snapshot --at 1,5,12.6
DO_NOT_TRACK=1 hyperframes render --quality looks -o raw.mp4
python3 ../../tools/hyperframes/master_audio.py raw.mp4 film-a.mp4   # -14 LUFS, phone-audible bass
```

Sound tools in `video/tools/hyperframes/`: `shape_music.py` (trim onto the beat grid, filter sweeps, gain automation),
`place_audio.py` (writes the music and SFX `<audio>` clips into `index.html`), `sfx_variants.py`, `master_audio.py`.
