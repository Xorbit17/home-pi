from __future__ import annotations

import os
import random
from typing import Iterable

from django.db import transaction
from job_registry import register
from dashboard.models.job import Job
from dashboard.models.application import SourceImage
from dashboard.jobs.logger_job import RunLogger
from dashboard.jobs.services.openai import openai_client
from constants import (
    IMAGE_DIR,
    IMAGE_EXTENSIONS,
    MIME_BY_EXT,
    ContentTypeClassification,
    QualityClassification,
    RenderDecision,
)
from openai import OpenAI
from pathlib import Path
import base64
from PIL import Image
from pydantic import BaseModel


CLASSIFY_PROMPT = (
    Path(__file__) / "context-templates" / "image-classifier.md"
).read_text()

class ImageClassification(BaseModel):
    quality: QualityClassification
    contentType: ContentTypeClassification
    renderDecision: RenderDecision
    portrait: bool
    multiplePersons: bool
    portraitSuitable: bool
    photoRealistic: bool 
    cartoony: bool
    art: bool
    descriptionOfImage: str
    qualityClassificationExplanation: str


def classify_image(path: str) -> ImageClassification | None:
    """
    Upload an image and ask OpenAI to classify its suitability for e-ink portrait generation.
    Returns the model's text response.
    """
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image extension: {ext}. Supported: {sorted(IMAGE_EXTENSIONS)}"
        )
    mime = MIME_BY_EXT.get(ext)
    image_bytes = Path(path).read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = openai_client.responses.parse(
        model="gpt-5.0",
        text_format=ImageClassification,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": CLASSIFY_PROMPT,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime};base64,{image_b64}",
                        "detail":"high", 
                    },
                ],
            }
        ],
    )
    return response.output_parsed

@register("CLASSIFY")
def classify_image_job(job: Job, logger: RunLogger, params: dict | None):
    pass