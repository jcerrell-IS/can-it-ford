import os
os.environ.setdefault("TI_OFFLINE_CACHE", "1")
os.environ.setdefault("TI_OFFLINE_CACHE_FILE_PATH", os.path.expanduser("~/.cache/taichi-can-it-ford"))
import taichi as ti
ti.init(arch=ti.metal, offline_cache=True, offline_cache_file_path=os.path.expanduser("~/.cache/taichi-can-it-ford"))
x = ti.field(dtype=ti.f32, shape=8)
@ti.kernel
def fill():
    for i in x:
        x[i] = i * 2.0
fill()
print("TAICHI_METAL_SMOKE_OK", x.to_numpy().tolist())
