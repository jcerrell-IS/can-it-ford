import os
os.environ.setdefault("TI_OFFLINE_CACHE", "1")
os.environ.setdefault("TI_OFFLINE_CACHE_FILE_PATH", os.path.expanduser("~/.cache/taichi-can-it-ford"))
import genesis as gs
gs.init(backend=gs.metal, logging_level="warning")
scene = gs.Scene(show_viewer=False)
scene.add_entity(gs.morphs.Plane())
scene.build()
for _ in range(3):
    scene.step()
print("GENESIS_METAL_SMOKE_OK")
