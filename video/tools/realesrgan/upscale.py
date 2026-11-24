"""Upscale images with realesr-animevideov3 (ONNX, CPU).
Usage: python3 upscale.py model.onnx out_w out_h in1.png [in2 ...] --out DIR
Each image is upscaled x4 by the model, then resized to out_w x out_h with Lanczos."""
import sys, os, time
import numpy as np
import onnxruntime as ort
from PIL import Image
args = sys.argv[1:]
outdir = args[args.index('--out') + 1]; args = args[:args.index('--out')]
model, W, H, files = args[0], int(args[1]), int(args[2]), args[3:]
so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
sess = ort.InferenceSession(model, so, providers=['CPUExecutionProvider'])
os.makedirs(outdir, exist_ok=True)
for f in files:
    t = time.time()
    img = np.asarray(Image.open(f).convert('RGB'), dtype=np.float32) / 255.0
    y = sess.run(None, {'input': img.transpose(2, 0, 1)[None]})[0][0]
    y = (np.clip(y, 0, 1).transpose(1, 2, 0) * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(y).resize((W, H), Image.LANCZOS).save(os.path.join(outdir, os.path.basename(f).rsplit('.', 1)[0] + '.png'))
    print(f"{os.path.basename(f)}: {time.time() - t:.2f}s", flush=True)
