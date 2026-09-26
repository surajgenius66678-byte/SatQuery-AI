# SatQuery AI — real-data demo release

This is the **real inference release**. The interactive API is configured to use real specialist models and fails loudly if a required model cannot be loaded. It does not silently return synthetic answers.

## Models
1. `AdaptLLM/remote-sensing-Qwen2-VL-2B-Instruct` — remote-sensing domain-adapted Qwen2-VL model.
2. `IDEA-Research/grounding-dino-base` — zero-shot text-guided grounding.
3. Included `checkpoints_change_oscd.pth` — FCSiamDiff bi-temporal change detector.
4. TorchGeo CROMA — optical/SAR joint representation encoder.

The AdaptLLM model is explicitly a remote-sensing post-trained model built from Qwen2-VL-2B-Instruct and a remote-sensing visual-instruction dataset, so the VLM is not a generic off-the-shelf LLM.

## First run
1. Install `requirements.txt`.
2. Run `python scripts/preflight_real.py`.
3. Start the backend with `Start_program.bat`.
4. The first use of VLM/Grounding/CROMA downloads their public weights into the local Hugging Face/TorchGeo cache if they are not already cached.
5. Upload real GeoTIFF/TIFF data. For paired workflows, upload exactly two co-registered images.

## Mandatory demo queries
- `Describe the land-cover and major objects visible in this image.`
- `Highlight the water body referred to in the query.`
- `What changed between these two dates, and where did the change occur?`
- `Use the optical and SAR images together to identify built-up and water-covered regions.`
- `Has the built-up area increased, decreased, or remained unchanged?`

## Important
The hidden ISRO/SAC Cartosat-2S + RISAT evaluation set is organizer-provided and must not be fabricated. This release is compatible with it, but no honest software package can claim hidden-set scores before the organizers provide the data/annotations.
