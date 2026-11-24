"""Convert Real-ESRGAN's realesr-animevideov3 ncnn model (.param/.bin) to ONNX, so it runs on
CPU with onnxruntime instead of needing a (here: emulated) Vulkan GPU.

Architecture (SRVGGNetCompact): conv3x3+PReLU, 16 x (conv3x3+PReLU), conv3x3 -> 3*s*s channels,
PixelShuffle(s), plus a nearest-neighbour s-times upscale of the input.
The ncnn .bin stores, per layer in .param order: convolution = 4-byte tag + fp16 weights + fp32 bias;
PReLU = fp32 slopes.

Usage: python3 ncnn2onnx.py models/realesr-animevideov3-x4.param models/realesr-animevideov3-x4.bin out.onnx
"""
import sys

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

param, binf, out = sys.argv[1:4]
lines = [l.split() for l in open(param).read().splitlines()[2:]]
raw = open(binf, "rb").read()
off = 0


def take(n_bytes):
    global off
    b = raw[off:off + n_bytes]
    off += n_bytes
    return b


nodes, inits = [], []
x = "input"
in_ch = 3
scale = None
last_conv_out = None
for l in lines:
    kind, name = l[0], l[1]
    kv = dict(p.split("=") for p in l[4 + int(l[2]) + int(l[3]):] if "=" in p)
    if kind == "Convolution":
        oc, k, wsize = int(kv["0"]), int(kv["1"]), int(kv["6"])
        tag = int.from_bytes(take(4), "little")
        if tag == 0x01306B47:
            w = np.frombuffer(take(wsize * 2), dtype=np.float16).astype(np.float32)
        elif tag == 0:
            w = np.frombuffer(take(wsize * 4), dtype=np.float32)
        else:
            raise ValueError(f"unknown weight tag {tag:#x} in {name}")
        b = np.frombuffer(take(oc * 4), dtype=np.float32)
        ic = wsize // (oc * k * k)
        inits += [numpy_helper.from_array(w.reshape(oc, ic, k, k), name + "_w"), numpy_helper.from_array(b.copy(), name + "_b")]
        nodes.append(helper.make_node("Conv", [x, name + "_w", name + "_b"], [name], kernel_shape=[k, k], pads=[k // 2] * 4))
        x = name
        last_conv_out = oc
    elif kind == "PReLU":
        n = int(kv["0"])
        a = np.frombuffer(take(n * 4), dtype=np.float32).copy()
        inits.append(numpy_helper.from_array(a.reshape(n, 1, 1), name + "_a"))
        nodes.append(helper.make_node("PRelu", [x, name + "_a"], [name]))
        x = name
    elif kind == "PixelShuffle":
        scale = int(kv["0"])
        nodes.append(helper.make_node("DepthToSpace", [x], [name], blocksize=scale, mode="CRD"))
        x = name
assert off == len(raw), f"read {off} of {len(raw)} bytes"
inits.append(numpy_helper.from_array(np.array([1, 1, scale, scale], dtype=np.float32), "scales"))
nodes.append(helper.make_node("Resize", ["input", "", "scales"], ["up"], mode="nearest"))
nodes.append(helper.make_node("Add", [x, "up"], ["output"]))
g = helper.make_graph(nodes, "realesr_animevideov3",
                      [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, "h", "w"])],
                      [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3, "H", "W"])], inits)
m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 17)], ir_version=9)
onnx.checker.check_model(m)
onnx.save(m, out)
print(f"saved {out}: x{scale}, {len(inits)} tensors, all {len(raw)} weight bytes used")
