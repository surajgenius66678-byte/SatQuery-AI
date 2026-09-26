# SatQuery AI — Real-data evaluation

This release contains **no synthetic inference path in the application**. Public benchmark evaluation is kept separate from the interactive GUI because VRSBench accepts public benchmark image formats in addition to GeoTIFF.

Supported evaluation sources:
- **VRSBench**: captioning, visual grounding, VQA. Official project reports 29,614 images, 52,472 referring expressions and 123,221 QA pairs.
- **RSVQA**: single-image VQA.
- **CDVQA**: bi-temporal change VQA.
- **ISRO/SAC**: private evaluation data supplied by the organizers; put it under `evaluation/private/isro_sac/` and run the same manifest/evaluation interface.

The evaluator writes JSONL predictions and a metrics summary. It never fabricates ground truth.
