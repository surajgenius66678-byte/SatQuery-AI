"""
VLM adapter — Section 3.4: single-image VQA + captioning.

Wraps a HF-style vision-language model (the specific base checkpoint is
one of Part 6's open decisions, Section 3.6 — this adapter only knows the
*shape* of that model's input/output, not which checkpoint is loaded).

Expected model interface (whatever `loader.get()` returns must provide):
    model.generate(image_path: str, prompt: str) -> {"text": str, "score": float}
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

from backend.model_registry.adapters.base import BaseAdapter, confidence_band
from backend.shared.schemas import Confidence, Evidence, Modality, ModelRegistryEntry, TaskType, Tile

_DEFAULT_CAPTION_PROMPT = "Describe this satellite image in one factual sentence."


class VLMAdapter(BaseAdapter):
    handles = (TaskType.SINGLE_IMAGE_VQA, TaskType.CAPTIONING)

    def __init__(self, query: str | None = None, image_modalities: dict[ str, Modality] | None = None):
        # query set -> SINGLE_IMAGE_VQA; query unset -> CAPTIONING.
        self.query = query
        self.image_modalities = image_modalities or {}

    def preprocess(self, tiles: list[Tile], entry: ModelRegistryEntry) -> Any:
        if not tiles:
            raise ValueError("VLMAdapter.preprocess requires at least one tile.")

        # For paired optical/SAR or bi-temporal queries, create a real
        # side-by-side visual evidence panel from the corresponding tiles.
        # The VLM therefore sees both observations, not a synthetic answer.
        image_ids = []
        for tile in tiles:
            if tile.image_id not in image_ids:
                image_ids.append(tile.image_id)

        prompt = self.query or _DEFAULT_CAPTION_PROMPT
        if len(image_ids) < 2:
            return {"image_path": tiles[0].array_path, "prompt": prompt}

        from PIL import Image, ImageDraw
        import numpy as np
        import rasterio

        paths = []
        for image_id in image_ids[:2]:
            tile = next(t for t in tiles if t.image_id == image_id)
            with rasterio.open(tile.array_path) as src:
                bands = src.read().astype(np.float32)
            if bands.shape[0] >= 3:
                rgb = bands[:3]
            else:
                rgb = np.repeat(bands[:1], 3, axis=0)
            rgb = np.transpose(rgb, (1, 2, 0))
            lo = np.percentile(rgb, 2, axis=(0,1), keepdims=True)
            hi = np.percentile(rgb, 98, axis=(0,1), keepdims=True)
            rgb = np.clip((rgb-lo)/np.maximum(hi-lo,1e-6),0,1)
            paths.append(Image.fromarray((rgb*255).astype(np.uint8),'RGB'))

        h=max(img.height for img in paths); w=sum(img.width for img in paths)
        canvas=Image.new('RGB',(w,h+32),'white')
        labels=[]
        for i,img in enumerate(paths):
            x=sum(p.width for p in paths[:i]); canvas.paste(img,(x,32))
            modality=self.image_modalities.get(image_ids[i])
            labels.append(f"{modality.value if modality else 'IMAGE'} {i+1}")
        draw=ImageDraw.Draw(canvas)
        for i,label in enumerate(labels):
            x=sum(p.width for p in paths[:i])+8; draw.text((x,8),label,fill='black')

        cache=Path('/tmp/satquery_pair_panels'); cache.mkdir(parents=True,exist_ok=True)
        key=hashlib.sha256('|'.join(str(next(t.array_path for t in tiles if t.image_id==iid)) for iid in image_ids[:2]).encode()).hexdigest()[:20]
        out=cache/f'{key}.png'; canvas.save(out)
        prompt=(
            'Analyze BOTH panels together. Do not assume facts that are not visible. '
            'Panel labels identify the input modalities/times. Answer the user query '
            'using only visual evidence from the paired observations. User query: '+prompt
        )
        return {"image_path": str(out), "prompt": prompt}

    def infer(self, model: Any, model_input: Any) -> Any:
        return model.generate(image_path=model_input["image_path"], prompt=model_input["prompt"])

    def postprocess(
        self, raw_output: Any, tiles: list[Tile], entry: ModelRegistryEntry, modality_used: list[Modality],
    ) -> Evidence:
        task = TaskType.SINGLE_IMAGE_VQA if self.query else TaskType.CAPTIONING
        text = raw_output.get("text", "") if isinstance(raw_output, dict) else str(raw_output)
        score = float(raw_output.get("score", 0.0)) if isinstance(raw_output, dict) else 0.0
        return Evidence(
            task=task,
            model_used=entry.name,
            modality_used=modality_used,
            vqa_answer_raw=text,
            stats={"generation_score": score} if score else {},
            confidence=Confidence(
                value=score or None,
                band=confidence_band(score),
                basis="VLM decoder confidence score",
            ),
            warnings=[] if text else ["Model returned an empty response."],
        )
