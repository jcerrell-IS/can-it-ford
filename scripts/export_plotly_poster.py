from pathlib import Path
from plot_phase_space import make_figure
OUT = Path("figures/poster_exports")
OUT.mkdir(parents=True, exist_ok=True)
fig = make_figure()
fig.update_layout(font=dict(family="Arial", size=22, color="#111111"), paper_bgcolor="white", plot_bgcolor="white")
fig.write_image(OUT / "phase_space.svg", width=1800, height=1200, scale=1)
fig.write_image(OUT / "phase_space.pdf", width=1800, height=1200, scale=1)
fig.write_image(OUT / "phase_space_preview.png", width=1800, height=1200, scale=2)
print("Wrote SVG/PDF/PNG to", OUT)
