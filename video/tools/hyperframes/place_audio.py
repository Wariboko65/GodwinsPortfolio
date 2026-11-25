"""Write the music bed and SFX <audio> clips into a HyperFrames index.html at the <!--AUDIO--> marker
(or between <!--AUDIO--> ... <!--/AUDIO--> on later runs).
Usage: python3 place_audio.py project_dir cues.json
cues.json: {"music": {"src": "assets/music/bed.wav", "volume": 0.9},
            "sfx": [["impact-bass-1", start_s, volume], ...]}   # files in assets/sfx/fx/<name>.wav"""
import json, re, sys
import soundfile as sf
proj, cues = sys.argv[1], json.load(open(sys.argv[2]))
lines = ["<!--AUDIO-->"]
m = cues["music"]
d = sf.info(f"{proj}/{m['src']}").duration
lines.append(f'<audio id="music-bed" class="clip" src="{m["src"]}" data-start="0" data-duration="{d:.3f}" data-track-index="3" data-volume="{m["volume"]}"></audio>')
lanes = []  # end time of the last clip on each SFX lane (Studio lanes 4, 5, ...: lowest free one)
for i, (name, t, vol) in enumerate(sorted(cues["sfx"], key=lambda c: c[1])):
    d = sf.info(f"{proj}/assets/sfx/fx/{name}.wav").duration
    t = max(0, t)
    k = next((j for j, e in enumerate(lanes) if e <= t), len(lanes))
    if k == len(lanes): lanes.append(0)
    lanes[k] = t + d
    lines.append(f'<audio id="sfx-{i:02d}-{name}" class="clip" src="assets/sfx/fx/{name}.wav" data-start="{t:.3f}" data-duration="{d:.3f}" data-track-index="{4 + k}" data-volume="{vol}"></audio>')
lines.append("<!--/AUDIO-->")
p = f"{proj}/index.html"; s = open(p).read()
block = "\n      ".join(lines)
s = re.sub(r"<!--AUDIO-->.*?<!--/AUDIO-->", block, s, flags=re.S) if "<!--/AUDIO-->" in s else s.replace("<!--AUDIO-->", block)
open(p, "w").write(s)
print(f"placed music + {len(cues['sfx'])} sfx")
