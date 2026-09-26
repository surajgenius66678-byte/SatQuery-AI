# Benchmark execution plan

## VRSBench
Use the official test split for captioning, grounding and VQA. Do not train on the test split. The official repository provides evaluation code and benchmark annotations.

## RSVQA
Run the prescribed public test split through `SINGLE_IMAGE_VQA`. Store one JSON object per sample with `prediction` and `reference`.

## CDVQA
Run the prescribed public test split through `CHANGE_VQA`. Store one JSON object per sample with `prediction` and `reference`. The change detector output must remain available as evidence.

## ISRO/SAC
The organizer-provided Cartosat-2S optical + RISAT SAR pairs are private. Never create substitute labels. Place the supplied set under `evaluation/private/isro_sac/` and create predictions against the organizer manifest.

The final score must use the official metric definitions supplied with the competition/baseline packages. `evaluation/score.py` is only a smoke-test scorer and must not be presented as the official SIH score.
