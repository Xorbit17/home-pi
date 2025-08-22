from typing import Dict, Iterable, List, Sequence, Tuple, Optional, Union
from PIL import Image
from pathlib import Path
from django.template import Context, Template
from constants import OPENAI_CLIENT, IMAGE_ART_GENERATION_MODEL, OPENAI_PORTRAIT_SIZE
import base64
import io

RGB = Tuple[int, int, int]

ART_GENERATOR_PROMPT_TEMPLATE = Template((Path(__file__).resolve().parent[0] / "context-templates" / "image-artstyle-applicator.md").read_text())

def get_art_generator_prompt(context: dict) -> str:
    return ART_GENERATOR_PROMPT_TEMPLATE.render(Context(context))

def pil_to_base64(
    image: Image.Image,
    format: str = "PNG",
    **save_kwargs
) -> str:
    buf = io.BytesIO()
    # JPEG requires RGB (no alpha); strip alpha if needed
    if format.upper() == "JPEG" and image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")
    image.save(buf, format=format, **save_kwargs)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def base64_to_pil(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")

from pathlib import Path
from PIL import Image

def openai_process(image: Image.Image, markdown_filename: str, *, context: dict) -> Image.Image:
    base_dir = Path(__file__).resolve().parent
    md_path = base_dir / "context-templates" / "artstyles" / markdown_filename
    markdown_content = md_path.read_text(encoding="utf-8")
    prompt = get_art_generator_prompt(context={"artstyle_instructions": markdown_content})

    # 2) Choose encoding + MIME that actually match
    #    Prefer PNG if image has alpha; JPEG otherwise
    has_alpha = image.mode in ("RGBA", "LA", "P") and (
        "A" in image.getbands() or "transparency" in image.info
    )
    if has_alpha:
        fmt, mime, img_to_send = "PNG", "image/png", image
    else:
        fmt, mime, img_to_send = "JPEG", "image/jpeg", image.convert("RGB")

    b64 = pil_to_base64(img_to_send, format=fmt)

    # 3) Call Responses API with the image-generation tool
    resp = OPENAI_CLIENT.responses.create(
        model=IMAGE_ART_GENERATION_MODEL,  # e.g. a Responses-capable model with the image tool
        input=[
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": f"data:{mime};base64,{b64}"},
        ],
        tools=[{"type": "image_generation"}],
    )

    # 4) Extract first image payload defensively (SDKs may differ a bit)
    b64_out = None
    for out in getattr(resp, "output", []):
        t = getattr(out, "type", "")
        if t in ("image", "output_image"):
            # common shapes: out.image.b64_json or out.data[0].b64_json
            imgobj = getattr(out, "image", None) or getattr(out, "data", None)
            if isinstance(imgobj, list) and imgobj and hasattr(imgobj[0], "b64_json"):
                b64_out = imgobj[0].b64_json
                break
            if imgobj is not None and hasattr(imgobj, "b64_json"):
                b64_out = imgobj.b64_json
                break
        if t == "image_generation_call" and hasattr(out, "result"):
            res = out.result
            if isinstance(res, dict) and "b64_json" in res:
                b64_out = res["b64_json"]
                break

    if b64_out is None:
        raise RuntimeError("No image payload found in response")

    return base64_to_pil(b64_out)


def resize_crop(image: Image.Image, *, context: dict) -> Image.Image:
    target_w, target_h = context["resolution"]
    src_w, src_h = image.size

    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)

    resized = image.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    right = left + target_w
    bottom = top + target_h

    return resized.crop((left, top, right, bottom))

def output_image(image: Image.Image, output: Path, format: str, *, context: dict) -> None:
    output = Path(output)
    fmt = format.lstrip(".").upper() #TODO: validation
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format=fmt)

def noop(image:Image.Image) -> Image.Image:
    return image


def build_palette_list(
    palette: Dict[str, Iterable[Iterable[int]]],
    key_priority: Optional[Sequence[str]] = None,
    max_colors: Optional[int] = None,
) -> List[RGB]:
    """
    Flatten your palette dict into a unique, ordered list of (R,G,B).
    - key_priority: iterate these keys first (preserves your 'native' colors up front)
    - max_colors: optional cap (e.g., 256 for Pillow palettes)
    """
    seen = set()
    out: List[RGB] = []

    def emit(seq: Iterable[Iterable[int]]):
        for v in seq:
            if isinstance(v, (list, tuple)) and len(v) == 3:
                rgb = (int(v[0]), int(v[1]), int(v[2]))
                if rgb not in seen:
                    seen.add(rgb)
                    out.append(rgb)

    if key_priority:
        for k in key_priority:
            if k in palette:
                emit(palette[k])

    for k, seq in palette.items():
        if not key_priority or k not in key_priority:
            emit(seq)

    if max_colors is not None:
        return out[:max_colors]
    return out

def _build_P_mode_palette_image(colors: Sequence[RGB]) -> Image.Image:
    if len(colors) > 256:
        raise ValueError("Pillow palettes support max 256 colors.")
    flat = []
    for r, g, b in colors:
        flat.extend([int(r), int(g), int(b)])
    while len(flat) < 256 * 3:
        flat.extend([0, 0, 0])
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat)
    return pal

def quantize_to_palette(img: Image.Image, colors: Sequence[RGB]) -> Image.Image:
    """
    Remap `img` to `colors` using Pillow's fixed-palette quantizer (no dithering),
    then convert back to RGB. Keeps everything crisp and returns RGB.
    """
    if not isinstance(img, Image.Image):
        raise TypeError("img must be a PIL.Image.Image")

    base = img.convert("RGB")
    pal = _build_P_mode_palette_image(colors)
    q = base.quantize(palette=pal, dither=Image.Dither.NONE)  # P-mode
    return q.convert("RGB")


from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple
from PIL import Image

class PipelineError(RuntimeError):
    """Raised when a pipeline step fails or returns an invalid result."""
    pass

StepFn = Callable[..., Image.Image]
FinishFn = Callable[..., None]



def process_image(
    input: Union[Path, str],
    output: Union[Path, str],
    pipeline: List,                  # list[Step | FinalStep]
    pipeline_args: List[Tuple],      # per-step positional-args (tuples)
    context: dict,                   # strict schema; passed through untouched
) -> None:
    """
    Execute an image-processing pipeline.

    - Loads the input image first.
    - Runs all steps except the last sequentially, each returning a new Image.Image.
    - Calls the final step separately; it must save to `output` and return None.

    Conventions:
    - Every non-final step has signature: step(img: Image.Image, *args, context: dict) -> Image.Image
    - Final step has signature: final_step(img: Image.Image, output_path: Union[Path, str], *args, context: dict) -> None
    - `pipeline_args[i]` supplies the positional args tuple for `pipeline[i]` (excluding `img`, `context`, and for the
      final step also excluding `output_path`, which is injected here).
    """
    # Normalize paths
    in_path = Path(input)
    out_path = Path(output)

    # Load the source image
    img = Image.open(in_path)

    if not pipeline:
        raise ValueError("pipeline must contain at least one step (the final saving step).")

    # Run all intermediate steps
    for step, args in zip(pipeline[:-1], pipeline_args[:-1]):
        if args is None:
            args = ()
        elif not isinstance(args, (tuple, list)):
            args = (args,)
        img = step(img, *args, context=context)

    # Run the final (saving) step
    final_step = pipeline[-1]
    final_args = () if not pipeline_args else pipeline_args[-1]
    if final_args is None:
        final_args = ()
    elif not isinstance(final_args, (tuple, list)):
        final_args = (final_args,)

    final_step(img, out_path, *final_args, context=context)


