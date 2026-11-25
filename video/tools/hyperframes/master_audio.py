"""Master a rendered film's soundtrack for social: deep but phone-audible bass, glue, -14 LUFS, -1 dBTP.
Usage: python3 master_audio.py in.mp4 out.mp4"""
import subprocess, sys, io
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
from pedalboard import Pedalboard, HighpassFilter, Compressor, Limiter, LowShelfFilter, HighShelfFilter, Distortion, Gain

src, out = sys.argv[1], sys.argv[2]
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-vn", "-f", "wav", "-ar", "48000", "-ac", "2", "-"], capture_output=True, check=True).stdout
a, sr = sf.read(io.BytesIO(raw), always_2d=True); a = a.T.astype(np.float32)
# harmonics of the sub (40-120 Hz) so small speakers still 'hear' the bass
sub = sosfiltfilt(butter(4, [40, 120], btype="band", fs=sr, output="sos"), a, axis=1).astype(np.float32)
harm = Pedalboard([Gain(14), Distortion(drive_db=12), HighpassFilter(160)])(sub, sr)
a = a + 0.12 * harm / max(1e-6, np.abs(harm).max()) * np.abs(sub).max()
chain = Pedalboard([HighpassFilter(24), LowShelfFilter(cutoff_frequency_hz=70, gain_db=1.5), HighShelfFilter(cutoff_frequency_hz=9000, gain_db=1.5),
                    Compressor(threshold_db=-16, ratio=2.0, attack_ms=12, release_ms=150), Limiter(threshold_db=-2.0, release_ms=60)])
a = chain(a, sr)
buf = io.BytesIO(); sf.write(buf, a.T, sr, format="WAV", subtype="PCM_24"); buf.seek(0)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-f", "wav", "-i", "-", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", f"loudnorm=I={__import__('os').environ.get('MASTER_I', '-14')}:TP={__import__('os').environ.get('MASTER_TP', '-1.0')}:LRA=11,alimiter=limit={__import__('os').environ.get('MASTER_LIMIT', '1.0')}:level=false", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out],
               input=buf.read(), check=True)
print("wrote", out)
