"""Join scene clips into one timeline: trims, 24 fps, tiny audio fades at each cut.
Usage: python3 join_scenes.py cuts.json out_dir
cuts.json: [["clip1.mp4", in_s, out_s], ...]
Writes out_dir/assembled.mkv, narration.wav (48 kHz stereo), offsets.json, small/%05d.png (540x960, for
Real-ESRGAN) and frames/%05d.jpg (1080x1920 Lanczos, for previews)."""
import json, os, subprocess, sys
cuts, out = json.load(open(sys.argv[1])), sys.argv[2]
os.makedirs(f"{out}/small", exist_ok=True); os.makedirs(f"{out}/frames", exist_ok=True)
ins, fc, offs, t = [], [], [], 0.0
for k, (clip, a, b) in enumerate(cuts):
    ins += ["-i", clip]; d = b - a
    fc.append(f"[{k}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v{k}];"
              f"[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.04:.3f}:d=0.04[a{k}]")
    offs.append(round(t, 3)); t += d
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(cuts))) + f"concat=n={len(cuts)}:v=1:a=1[v][a]")
run = lambda *a: subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)
run(*ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-c:a", "pcm_s16le", f"{out}/assembled.mkv")
run("-i", f"{out}/assembled.mkv", "-vn", "-ar", "48000", "-ac", "2", f"{out}/narration.wav")
run("-i", f"{out}/assembled.mkv", "-vf", "scale=540:960:flags=area", "-start_number", "0", f"{out}/small/%05d.png")
run("-i", f"{out}/assembled.mkv", "-vf", "scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.1", "-q:v", "3", "-start_number", "0", f"{out}/frames/%05d.jpg")
json.dump({"offsets": offs, "duration": round(t, 3)}, open(f"{out}/offsets.json", "w"))
print("offsets", offs, "duration", round(t, 3))
