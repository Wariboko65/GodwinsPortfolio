# Video tools

Everything used to edit narrated stickman explainers (premium motion-graphics edits) and to upscale footage.
System tools come from the cloud environment's setup script: FFmpeg, faster-whisper, yt-dlp, pedalboard,
onnxruntime, the Noto Color Emoji font and HyperFrames. Playwright + Chromium are preinstalled.

## realesrgan/ — sharpen cartoon footage on the CPU
- `animevideov3-x4.onnx`: Real-ESRGAN realesr-animevideov3 (x4), converted from the official ncnn release.
- `upscale.py model.onnx W H frames... --out DIR`: upscales each frame and resizes to W×H.
  About 3.5 s per 540×960 frame on 4 cores; feed it 540×960 frames for a 1080×1920 result.
- `ncnn2onnx.py`: the converter, if another ncnn model is ever needed.

## premium/ — the premium edit engine (time-driven HTML rendered frame by frame)
1. `python3 join_scenes.py cuts.json work/`: join and trim scene clips → narration.wav, small/ and frames/.
2. Transcribe: faster-whisper `small.en` with `word_timestamps=True` (set `HF_HUB_DISABLE_XET=1`).
3. `captions.py`: build `chunks.json` (word-by-word captions, keywords, emoji). Fix mis-heard words in it.
4. `template.html`: copy next to `frames/`, `chunks.json`, `jbmono.woff2`; edit the graphics section
   (hook, counters, pills, chips, stamps, timeline), `CUTS`, `PUNCH`, `SHAKE`, `NSRC`, `DURATION`.
   Serve the folder: `python3 -m http.server 8791 --bind 127.0.0.1`.
5. `node stills.mjs 8791 outdir t1 t2 ...`: check frames.
6. `node cues.mjs 8791 > cues.json`, then `python3 premium_audio.py cues.json narration.wav soundtrack.wav [--hole a b]`.
7. Optional sharp pass: upscale `small/` with realesrgan into `frames/`.
8. `node render.mjs 8791 master.mp4 soundtrack.wav` (motion blur, −14 LUFS), then re-encode with
   `-crf 28 -tune animation` for a small upload file.
