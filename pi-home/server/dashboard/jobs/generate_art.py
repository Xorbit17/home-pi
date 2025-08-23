from __future__ import annotations

import os
import random
from typing import Iterable

from job_registry import register
from dashboard.models.job import Job
from dashboard.models.application import SourceImage
from dashboard.jobs.logger_job import RunLogger
from constants import (
    IMAGE_DIR,
    IMAGE_EXTENSIONS,
)
from dashboard.jobs.services.openai import openai_client
from PIL import Image



def find_files() -> set[str]:
    """Return absolute paths of images in IMAGE_DIR (no subdirs)."""
    try:
        entries = os.listdir(IMAGE_DIR)
    except FileNotFoundError:
        return set()

    files = set()
    for f in entries:
        full = os.path.join(IMAGE_DIR, f)
        if os.path.isfile(full) and os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
            files.add(full)
    return files


def is_portrait(path: str) -> bool:
    with Image.open(path) as img:
        w, h = img.size
    return h >= w * 1.2  # e.g. portrait if height is at least 20% greater

def create_variant(source_image: SourceImage, params: dict | None):
    # TODO: call OpenAI, save Variant model, etc.
    # return Variant instance (or whatever you use)
    pass


def process_new_image(path: str, params: dict | None):
    """
    Create SourceImage if needed, then create a variant.
    If you enforce uniqueness, consider unique=True on SourceImage.path.
    """
    # If path is unique in DB, you can use get_or_create to be safe
    source_image, _ = SourceImage.objects.get_or_create(path=path)

    create_variant(source_image, params=params)


@register("ART")
def generate_art_job(job: Job, logger: RunLogger, params: dict | None):
    max_num_to_generate = int((params or {}).get("max_num_to_generate", 4))
    if max_num_to_generate <= 0:
        logger.warn("Nothing to do: max_num_to_generate <= 0")
        return
    fs_paths: set[str] = find_files()
    db_paths: set[str] = set(SourceImage.objects.values_list("path", flat=True))

    unprocessed_paths = list(fs_paths - db_paths)
    random.shuffle(unprocessed_paths)

    to_process = unprocessed_paths[:max_num_to_generate]

    processed = 0
    if to_process:
        logger.info(
            f"Found {len(unprocessed_paths)} new images. Will process {len(to_process)} in this run. Specifically: {', '.join(to_process)}"
        )
        for image_path in to_process:
            is_suitable = process_new_image(image_path, params=params)
            processed += 1 if is_suitable else 0

    remaining = max_num_to_generate - processed
    if remaining <= 0:
        return

    # Fall back: create variants for existing images
    logger.info(
        f"No (more) new images. Will create {remaining} variant(s) from existing images."
    )

    # Materialize to list, shuffle, then slice
    existing_images: list[SourceImage] = list(SourceImage.objects.all())
    if not existing_images:
        logger.info("No existing SourceImage records found. Nothing to do.")
        return

    random.shuffle(existing_images)
    chosen: Iterable[SourceImage] = existing_images[:remaining]

    for src in chosen:
        create_variant(src, params=params)
