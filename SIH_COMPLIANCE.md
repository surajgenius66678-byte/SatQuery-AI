# SIH26167 compliance matrix — SatQuery AI

## Mandatory functional requirements

| SIH requirement | Release implementation |
|---|---|
| Single-image VQA | Remote-sensing Qwen2-VL specialist in `satquery-vlm-rs-qwen2vl` |
| One additional single-image task | Text-guided Grounding DINO specialist |
| Remote-sensing adaptation | AdaptLLM remote-sensing Qwen2-VL-2B-Instruct; model card identifies it as Qwen2-VL post-trained for remote sensing using a remote-sensing visual-instruction dataset |
| Bi-temporal change analysis | FCSiamDiff OSCD checkpoint included in release |
| Change-based VQA | FCSiamDiff change evidence + paired-image VLM semantic reasoner; the change detector never invents object labels |
| Optical-SAR joint analysis | TorchGeo CROMA + paired optical/SAR VLM reasoner |
| Agentic model/tool routing | Deterministic query/input planner creates an auditable multi-specialist execution plan |
| Input compatibility validation | GeoTIFF/TIFF validation, metadata checks, pixel/file caps, COG conversion |
| Co-registration | Cross-image gate before change/fusion tasks |
| Evidence grounding | Evidence schema, confidence, warnings and claim validation |
| Auditable trace | `/api/jobs/{id}/trace` and PDF report |
| Interactive GUI/web application | Static frontend + FastAPI backend |
| Downloadable report | `/api/jobs/{id}/report` generates a real PDF |

## Public benchmark compatibility

- VRSBench: captioning, visual grounding and VQA.
- RSVQA: single-image VQA.
- CDVQA: bi-temporal change VQA.
- ISRO/SAC: organizer-provided Cartosat-2S optical + RISAT SAR evaluation data.

The release contains evaluation scaffolding and does **not** manufacture benchmark samples or hidden labels. Official benchmark test splits must be used for final numbers.

## No synthetic application path

The application frontend has no mock mode. The API configures the real inference engine. If a required model cannot be loaded, the job fails and exposes the error instead of returning a fabricated answer.

Mock engines remain only in development unit-test files so architecture/queue tests can run without multi-gigabyte model downloads. They are not imported by the application.
