# Hailuo Prompt Recommendation, Panel 4 Flooded-Crossing Comparison

Purpose: this file documents the recommended prompt structure and generation
settings for the AI-generated flooded-crossing clip used in Panel 4 of the poster.

IMPORTANT SCOPE DISCLAIMER (put a version of this on the poster too):
The Hailuo clip is an AI-generated illustration for public communication only.
It is NOT simulation output, NOT observational data, and NOT scientific validation
of any ford / no-ford result. The depth label (approximately 30 cm) is a visual
proxy, not a measured or physics-verified quantity. Label the panel explicitly as
"AI-generated illustrative video" so no viewer mistakes it for the Genesis result.

Source: HailuoAI/MiniMax research notes, research date June 30, 2026. Hailuo/MiniMax
changes pricing, credits, model names, and UI often, so re-check credits and the model
menu live in the logged-in interface immediately before any regeneration.

---

## Recommended settings

- Model: Hailuo 2.3 (or 2.3-Fast for cheaper iteration). Do not assume a "2.5" video
  model exists unless it actually appears in the live HailuoAI/MiniMax UI.
- Workflow: Image-to-Video (I2V) from a composed first frame is the most reliable for
  a consistent, poster-quality result. Text-to-Video (T2V) is fine for fast ideation.
- Aspect ratio: 16:9 landscape.
- Clip length: 4 to 6 seconds (the documented sweet spot for water-physics consistency).
- Resolution: 1080p if available and credits allow, otherwise 768p (label as illustrative
  if you later upscale a 768p frame).
- Motion descriptors: keep to 2 or 3 concise terms. Budget 3 to 5 generations per shot
  because output varies run to run.
- Cost reference: 768p 6s costs about 25 credits, 1080p 6s about 50 credits. Free-tier
  downloads carry a watermark; only Standard-tier and above download watermark-free.
  Check the live in-app credit balance before committing.

## Prompt structure (the order that works)

camera + subject + action + water physics + environment/light + style + constraints

- Use explicit camera command syntax in brackets, for example [Tracking shot],
  [Push in], [Pan left], [Static shot].
- Describe water behavior on specific materials, not just "wet" or "shiny". Use concrete
  terms: ripples, foam streaks, bow wave, turbulent wake, water curling around tires,
  coarse asphalt texture visible through brownish floodwater.
- Use "slow, steady, controlled" language so the model does not turn it into a chase or
  crash. Give it fixed anchors (roadside posts, a continuous road edge).
- Prompt the visual proxy for depth ("water reaches the lower wheel hubs and lower door
  sills, below the headlights"), not just the number.

---

## Ready-to-paste Text-to-Video prompt

```text
Low-angle roadside three-quarter view, [Tracking shot], a mid-size silver sedan slowly enters a shallow flooded rural road crossing and steadily fords across from left to right without stopping. Water depth is approximately 30 cm, reaching the lower wheel hubs and lower door sills but staying below the headlights. A visibly flowing cross-current moves right-to-left across the road, with ripples, foam streaks, displaced rainwater curling around the tires, a small bow wave at the front bumper, and a turbulent wake behind the wheels. Wet asphalt texture remains visible through brownish floodwater; fixed roadside posts and a continuous road edge anchor the scene. Overcast daylight, diffuse gray sky, realistic reflections, documentary realism, 35mm lens, stable horizon, photorealistic. Successful ford only: no crash, no stalled engine, no floating vehicle, no submerged hood, no people, no text overlays.
```

## Ready-to-paste Image-to-Video prompt

Start from a first frame: 16:9, low roadside three-quarter view of the sedan at the near
dry edge of a shallow flooded crossing, visible road edge and fixed depth cues. Upload a
clear JPG/PNG/WEBP, then paste this motion prompt (it intentionally does not re-describe
static features, since the model can already see the image):

```text
The sedan begins from the dry near edge, rolls slowly into the flooded crossing, then continues across to the far bank without stopping. Cross-current flows right-to-left across the road; water reaches roughly the lower wheel hubs / about 30 cm and stays below the headlights. Ripples, foam streaks, displaced water, a small bow wave around the front tires, and a turbulent wake trail behind the wheels. Keep the car shape and road alignment stable. Low roadside three-quarter camera view, slow steady tracking shot, overcast diffuse light, photorealistic documentary footage. No crash, no stalling, no floating, no submerged hood, no people, no text.
```

---

## Frame extraction (if regenerating and pulling stills for the poster)

After downloading the MP4 (or a screen capture via Shift-Command-5 if the download is
flaky, try Chrome before capturing):

```bash
# Opening frame at 0.8 s
ffmpeg -ss 00:00:00.800 -i capture.mov -frames:v 1 opening_frame.png

# Peak-immersion frame at 3.0 s, forced to 1200x900 crop-to-fill
ffmpeg -ss 00:00:03.000 -i capture.mov -frames:v 1 \
  -vf "scale=1200:900:force_original_aspect_ratio=increase,crop=1200:900" \
  peak_immersion_1200x900.png

# Verify dimensions
sips -g pixelWidth -g pixelHeight peak_immersion_1200x900.png
```

---

## Status note (checked live 2026-07-17)

Hailuo output already exists in this directory. It was generated on July 3, 2026 using
the Text-to-Video prompt above (the source MP4 filenames contain that prompt text):

- Hailuo_Video_Low-angle roadside three-quart_528604257021341700.mp4
- Hailuo_Video_Low-angle roadside three-quarter view, _Tracking shot_, a mid-size silver sedan slowly enters a shal_528605825435185156.mp4
- Hailuo_Video_Without changing anything just_528534639070212104.mp4
- Extracted frames: hailuo_frame_2.5s.png, opening_frame_clean.png, peak_frame.png

So this document is a provenance / reproducibility record, not a request to generate.
Do not call any external generation API without separate explicit confirmation.
