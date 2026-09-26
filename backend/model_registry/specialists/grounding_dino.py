from pathlib import Path
import os

import torch
import numpy as np
import rasterio
from PIL import Image
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor


class GroundingDINOModel:
    """
    Real text-guided grounding specialist backed by Grounding DINO.

    Contract expected by GroundingAdapter:
        ground(image_path, query) -> list[dict]
    """

    MODEL_ID = "IDEA-Research/grounding-dino-base"

    def __init__(self, device="cpu"):
        self.device = torch.device(device)

        model_id = os.environ.get(
            "SATQUERY_GROUNDING_MODEL",
            self.MODEL_ID,
        )

        cache_only = os.environ.get(
            "SATQUERY_OFFLINE",
            "0",
        ) == "1"

        self.processor = AutoProcessor.from_pretrained(
            model_id,
            local_files_only=cache_only,
        )

        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(
            model_id,
            local_files_only=cache_only,
        )

        self.model.to(self.device)
        self.model.eval()

        self.model_id = model_id

    def ground(self, image_path: str, query: str):
        """
        Run Grounding DINO on a GeoTIFF image.

        Returns:
            list[dict]
        """

        if not query or not query.strip():
            return []

        # ---------------------------------------------------------
        # Read GeoTIFF
        # ---------------------------------------------------------
        with rasterio.open(image_path) as src:
            raster = src.read().astype(np.float32)

        if raster.shape[0] >= 3:
            rgb = raster[:3]

        elif raster.shape[0] == 1:
            rgb = np.repeat(raster, 3, axis=0)

        else:
            raise ValueError(
                f"Grounding DINO cannot read {raster.shape[0]} bands"
            )

        # ---------------------------------------------------------
        # Convert satellite values to displayable RGB
        # ---------------------------------------------------------
        rgb = np.transpose(rgb, (1, 2, 0))

        rgb = np.nan_to_num(
            rgb,
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )

        # Robust percentile stretch for arbitrary
        # GeoTIFF reflectance / DN values.
        lo = np.percentile(
            rgb,
            2,
            axis=(0, 1),
            keepdims=True,
        )

        hi = np.percentile(
            rgb,
            98,
            axis=(0, 1),
            keepdims=True,
        )

        rgb = np.clip(
            (rgb - lo) / np.maximum(hi - lo, 1e-6),
            0.0,
            1.0,
        )

        rgb = (rgb * 255.0).astype(np.uint8)

        image = Image.fromarray(
            rgb,
            mode="RGB",
        )

        # ---------------------------------------------------------
        # Grounding DINO text prompt
        # ---------------------------------------------------------
        text = query.strip()

        if not text.endswith("."):
            text += "."

        # ---------------------------------------------------------
        # Processor
        # ---------------------------------------------------------
        inputs = self.processor(
            images=image,
            text=text,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            if hasattr(value, "to")
            else value
            for key, value in inputs.items()
        }

        # ---------------------------------------------------------
        # Model inference
        # ---------------------------------------------------------
        with torch.inference_mode():
            outputs = self.model(**inputs)

        # ---------------------------------------------------------
        # Target image size
        # ---------------------------------------------------------
        target_sizes = torch.tensor(
            [
                [
                    image.height,
                    image.width,
                ]
            ],
            device=self.device,
        )

        # ---------------------------------------------------------
        # Post-processing
        #
        # IMPORTANT:
        # Current Transformers Grounding DINO processor expects
        # `threshold`, not `box_threshold`.
        # ---------------------------------------------------------
        results = self.processor.post_process_grounded_object_detection(
            outputs,
            threshold=0.15,
            text_threshold=0.25,
            target_sizes=target_sizes,
        )[0]

        # ---------------------------------------------------------
        # Convert detections to SatQuery format
        # ---------------------------------------------------------
        detections = []

        boxes = results.get(
            "boxes",
            [],
        )

        scores = results.get(
            "scores",
            [],
        )

        labels = results.get(
            "text_labels",
            results.get(
                "labels",
                [],
            ),
        )

        for box, score, label in zip(
            boxes,
            scores,
            labels,
        ):
            box = box.detach().cpu().tolist()

            score = float(
                score.detach().cpu()
            )

            detections.append(
                {
                    "label": str(label),

                    "box_px": [
                        float(box[0]),
                        float(box[1]),
                        float(box[2]),
                        float(box[3]),
                    ],

                    "mask_rle": None,

                    "score": score,
                }
            )

        return detections