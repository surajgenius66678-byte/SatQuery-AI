from __future__ import annotations
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
required=[ROOT/'checkpoints_change_oscd.pth', ROOT/'backend/model_registry/config/models.yaml']
missing=[str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit('Missing required local release files: '+', '.join(missing))
print('Local release files: OK')
print('VLM:', os.getenv('SATQUERY_VLM_CHECKPOINT','AdaptLLM/remote-sensing-Qwen2-VL-2B-Instruct'))
print('Grounding:', os.getenv('SATQUERY_GROUNDING_MODEL','IDEA-Research/grounding-dino-base'))
print('Change detector: included OSCD FCSiamDiff checkpoint')
print('Fusion: TorchGeo CROMA pretrained weights')
print('MOCKS: disabled unless SATQUERY_ENABLE_MOCKS=1 is explicitly set for tests')
