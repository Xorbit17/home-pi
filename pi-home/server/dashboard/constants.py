from zoneinfo import ZoneInfo
from typing import Literal, Dict
from pathlib import Path
from .jobs.services.image_processing import resize_crop, quantize_to_palette, output_image, openai_process
from color_constants import SHADED_PALETTE_SET
from openai import OpenAI

def parse_env_file(path: str | Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            env[key] = value
    return env


LOCAL_TZ = ZoneInfo("Europe/Brussels")
APP_DIR = Path(__file__).resolve().parents[0]  # app; a.k.a. the current django app
PROJECT_DIR = APP_DIR.parents[0]  # server; a.k.a the django root
PI_DIR = PROJECT_DIR.parents[
    0
]  # pi_home; a.k.a root of all sources of projects running on this pi
ENV_PATH = PI_DIR / ".env.server"
SECRETS = parse_env_file(ENV_PATH)

IMAGE_DIR = Path(SECRETS["IMAGE_DIR"])
ICAL_GOOGLE_CALENDAR_URL = SECRETS["ICAL_GOOGLE_CALENDAR_URL"]
OPENAI_KEY = SECRETS["OPENAI_KEY"]
OPENAI_CLIENT = OpenAI(api_key=OPENAI_KEY)
OPENAI_PORTRAIT_SIZE= "1024x1536"
OPENAI_SQUARE_SIZE= "1024x1024"
OPENAI_LANDSCAPE_SIZE= "1536x1024"
IMAGE_ART_GENERATION_MODEL="gpt-5"

NEWS_MODE = "news"
PHOTO_MODE = "photo"

MODE_CHOICES = [
    (NEWS_MODE, "Newspaper"),
    (PHOTO_MODE, "Photo"),
]

WEEKDAY_CHOICES = [
    (0, "Mon"),
    (1, "Tue"),
    (2, "Wed"),
    (3, "Thu"),
    (4, "Fri"),
    (5, "Sat"),
    (6, "Sun"),
]

NEWS_KIND = "news"
PHOTO_KIND = "photo"

ASSET_CHOICES = [(NEWS_KIND, "Newspaper"), (PHOTO_KIND, "Photo")]

DEBUG = "DEBUG"
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"

LOG_LEVEL_CHOICES = [
    (DEBUG, "Debug"),
    (INFO, "Info"),
    (WARN, "Warning"),
    (ERROR, "Error"),
]

CALENDAR = "CALENDAR"
RSS = "RSS"
WEATHER = "WEATHER"
PUSH = "PUSH"
ART = "ART"
NEWSPAPER = "NEWSPAPER"

JOB_KIND_CHOICES = [
    (CALENDAR, "Get calendar"),
    (RSS, "Get RSS"),
    (WEATHER, "Get weather"),
    (PUSH, "Push to displays"),
    (ART, "Generate art"),
    (NEWSPAPER, "Generate newspaper"),
]

JobKind = Literal[
    "CALENDAR",
    "RSS",
    "WEATHER",
    "PUSH",
    "ART",
    "NEWSPAPER",
]

RUNNING = "RUNNING"
SUCCESS = "SUCCESS"
SKIPPED = "SKIPPED"
ERROR = "ERROR"
QUEUED = "QUEUED"

JOB_STATUS_CHOICES = [
    (RUNNING, "Running"),
    (SUCCESS, "Success"),
    (SKIPPED, "Skipped"),
    (ERROR, "Error"),
    (QUEUED, "Queued"),
]

JobStatus = Literal["RUNNING", "SUCCESS", "SKIPPED", "ERROR", "QUEUED"]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic"}
MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".heic": "image/heic",
}

QualityClassification = Literal["NOT_SUITED", "BAD", "PASSABLE", "GOOD", "VERY_GOOD"]
ContentTypeClassification = Literal[
    "PERSON",
    "PEOPLE",
    "ANIMAL",
    "LANDSCAPE",
    "CITY",
    "BUILDING",
    "NATURE",
    "ART",
    "BUILDING",
    "CITY" "OBJECT",
    "OTHER",
]
RenderDecision = Literal["BOTH", "ARTIFY", "LEAVE_PHOTO"]

from typing import Literal, List, Tuple

# =====================
# Content Type Literals
# =====================

ContentTypeClassification = Literal[
    "PERSON",
    "PEOPLE",
    "ANIMAL",
    "LANDSCAPE",
    "CITY",
    "BUILDING",
    "NATURE",
    "ART",
    "OBJECT",
    "OTHER",
]

# =====================
# Style Constants
# (single canonical list so you can reuse across categories)
# =====================

# Portrait / People friendly classics
COMMUNIST_POSTER = "COMMUNIST_POSTER"
STUDIO_GHIBLI_STYLE = "STUDIO_GHIBLI_STYLE"
RETRO_PIXEL_ART = "RETRO_PIXEL_ART"
POINTILLISM_HALFTONE = "POINTILLISM_HALFTONE"
MARKER_DRAWING = "MARKER_DRAWING"  # Needs more specific
CUBISM_ABSTRACT_FACE = "CUBISM_ABSTRACT_FACE"
WARHOL_POP_ART = "WARHOL_POP_ART"
WOODCUT_LINOCUT = "WOODCUT_LINOCUT"
MINIMAL_VECTOR_PORTRAIT = "MINIMAL_VECTOR_PORTRAIT"
CHILDRENS_BOOK_ILLUSTRATION = "CHILDRENS_BOOK_ILLUSTRATION"  # Needs more specific

# Modern/Media crossovers
PIXAR_STYLE = "PIXAR_STYLE"
DISNEY_CLASSIC = "DISNEY_CLASSIC"
SPIDERVERSE_COMIC = "SPIDERVERSE_COMIC"
GRITTY_WESTERN_COMICS = "GRITTY_WESTERN_COMICS"
MOEBIUS_FRENCH_SCI_FI = "MOEBIUS_FRENCH_SCI_FI"  # Needs more specifics, Jean giraud

# Group/scene styles
COMIC_BOOK_VIGNETTE = "COMIC_BOOK_VIGNETTE"
MANGA_DYNAMIC = "MANGA_DYNAMIC"
GHIBLI_GROUP_SCENE = "GHIBLI_GROUP_SCENE"
IMPRESSIONIST_BRUSHWORK = "IMPRESSIONIST_BRUSHWORK"
SILHOUETTE_COLOR_BLOCKS = "SILHOUETTE_COLOR_BLOCKS"
STENCIL_BANKSY_STYLE = "STENCIL_BANKSY_STYLE"

# Animal-centric
INK_WATERCOLOR = "INK_WATERCOLOR"
RETRO_ZOO_POSTER = "RETRO_ZOO_POSTER"
NATURALIST_SKETCH = "NATURALIST_SKETCH"
CARTOON_MASCOT = "CARTOON_MASCOT"
PIXEL_SPRITE_ANIMAL = "PIXEL_SPRITE_ANIMAL"
LOWPOLY_GEOMETRIC = "LOWPOLY_GEOMETRIC"
PAPERCUT_LAYER_ART = "PAPERCUT_LAYER_ART"
TOTEM_MYTHOLOGICAL = "TOTEM_MYTHOLOGICAL"

# Landscape / Nature / City / Building
UKIYOE_WOODBLOCK = "UKIYOE_WOODBLOCK"
PENCIL_GRAPHITE = "PENCIL_GRAPHITE"
PASTEL_POSTER = "PASTEL_POSTER"
SILKSCREEN_PRINT = "SILKSCREEN_PRINT"
GEOMETRIC_ABSTRACTION = "GEOMETRIC_ABSTRACTION"
ART_DECO_TRAVEL_POSTER = "ART_DECO_TRAVEL_POSTER"
WATERCOLOR_WASH = "WATERCOLOR_WASH"
CHARCOAL_DRAWING = "CHARCOAL_DRAWING"

NOIR_COMIC_SCENE = "NOIR_COMIC_SCENE"
CYBERPUNK_POSTER = "CYBERPUNK_POSTER"
SILKSCREEN_SKYLINE = "SILKSCREEN_SKYLINE"
ISOMETRIC_PIXEL_CITY = "ISOMETRIC_PIXEL_CITY"
CONSTRUCTIVIST_POSTER = "CONSTRUCTIVIST_POSTER"
WATERCOLOR_CITYSCAPE = "WATERCOLOR_CITYSCAPE"
VECTOR_FLAT_ILLUSTRATION = "VECTOR_FLAT_ILLUSTRATION"

BLUEPRINT_TECHNICAL = "BLUEPRINT_TECHNICAL"
WOODCUT_ENGRAVING = "WOODCUT_ENGRAVING"
ART_DECO_ARCHITECTURAL_POSTER = "ART_DECO_ARCHITECTURAL_POSTER"
POP_MINIMALISM = "POP_MINIMALISM"
SURREALIST_DECONSTRUCTION = "SURREALIST_DECONSTRUCTION"
STAINED_GLASS_STYLE = "STAINED_GLASS_STYLE"
LINEART_SKETCH = "LINEART_SKETCH"

# Nature-specific extras
BOTANICAL_PLATE = "BOTANICAL_PLATE"
INK_WASH_PAINTING = "INK_WASH_PAINTING"
STENCIL_LEAVES = "STENCIL_LEAVES"
CUTPAPER_COLLAGE = "CUTPAPER_COLLAGE"
ETCHING_COPPERPLATE = "ETCHING_COPPERPLATE"
OUTLINE_WITH_COLOR = "OUTLINE_WITH_COLOR"
ART_NOUVEAU_FLORAL = "ART_NOUVEAU_FLORAL"

# ART / OBJECT / OTHER oriented
BAUHAUS_POSTER = "BAUHAUS_POSTER"
SUPREMATISM_MINIMAL_SHAPES = "SUPREMATISM_MINIMAL_SHAPES"
OP_ART_HIGH_CONTRAST = "OP_ART_HIGH_CONTRAST"
DUOTONE_POSTER = "DUOTONE_POSTER"
PATENT_LINE_DRAWING = "PATENT_LINE_DRAWING"
VINTAGE_PRODUCT_POSTER = "VINTAGE_PRODUCT_POSTER"
ISOMETRIC_PIXEL_OBJECT = "ISOMETRIC_PIXEL_OBJECT"

PERSON_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        COMMUNIST_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["communist-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["studio-ghibli-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXAR_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixar-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        DISNEY_CLASSIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["disney-classic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SPIDERVERSE_COMIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["spiderverse-comic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        RETRO_PIXEL_ART,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["retro-pixel-art.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        POINTILLISM_HALFTONE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pointillism-halftone.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MARKER_DRAWING,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["marker-drawing.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CUBISM_ABSTRACT_FACE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["cubism-abstract-face.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WARHOL_POP_ART,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["warhol-pop-art.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WOODCUT_LINOCUT,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["woodcut-linocut.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MINIMAL_VECTOR_PORTRAIT,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["minimal-vector-portrait.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CHILDRENS_BOOK_ILLUSTRATION,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["childrens-book-illustration.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["moebius-french-sci-fi.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

PEOPLE_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        COMIC_BOOK_VIGNETTE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["comic-book-vignette.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MANGA_DYNAMIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["manga-dynamic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        GHIBLI_GROUP_SCENE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ghibli-group-scene.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SPIDERVERSE_COMIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["spiderverse-comic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        GRITTY_WESTERN_COMICS,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["gritty-western-comics.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STENCIL_BANKSY_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["stencil-banksy-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CHILDRENS_BOOK_ILLUSTRATION,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["childrens-book-illustration.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["studio-ghibli-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXAR_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixar-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        DISNEY_CLASSIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["disney-classic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["moebius-french-sci-fi.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

ANIMAL_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        INK_WATERCOLOR,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ink-watercolor.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        RETRO_ZOO_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["retro-zoo-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        NATURALIST_SKETCH,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["naturalist-sketch.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CARTOON_MASCOT,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["cartoon-mascot.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXEL_SPRITE_ANIMAL,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixel-sprite-animal.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        LOWPOLY_GEOMETRIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["lowpoly-geometric.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PAPERCUT_LAYER_ART,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["papercut-layer-art.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        TOTEM_MYTHOLOGICAL,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["totem-mythisch-totem.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WOODCUT_ENGRAVING,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["woodcut-engraving.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["studio-ghibli-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        DISNEY_CLASSIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["disney-classic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXAR_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixar-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

PERSON_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        COMMUNIST_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["communist-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["studio-ghibli-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXAR_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixar-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        DISNEY_CLASSIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["disney-classic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SPIDERVERSE_COMIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["spiderverse-comic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        RETRO_PIXEL_ART,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["retro-pixel-art.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        POINTILLISM_HALFTONE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pointillism-halftone.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MARKER_DRAWING,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["marker-drawing.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CUBISM_ABSTRACT_FACE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["cubism-abstract-face.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WARHOL_POP_ART,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["warhol-pop-art.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WOODCUT_LINOCUT,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["woodcut-linocut.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MINIMAL_VECTOR_PORTRAIT,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["minimal-vector-portrait.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CHILDRENS_BOOK_ILLUSTRATION,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["childrens-book-illustration.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["moebius-french-sci-fi.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

PEOPLE_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        COMIC_BOOK_VIGNETTE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["comic-book-vignette.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MANGA_DYNAMIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["manga-dynamic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        GHIBLI_GROUP_SCENE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ghibli-group-scene.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SPIDERVERSE_COMIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["spiderverse-comic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        GRITTY_WESTERN_COMICS,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["gritty-western-comics.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STENCIL_BANKSY_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["stencil-banksy-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CHILDRENS_BOOK_ILLUSTRATION,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["childrens-book-illustration.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["studio-ghibli-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXAR_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixar-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        DISNEY_CLASSIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["disney-classic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["moebius-french-sci-fi.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

ANIMAL_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        INK_WATERCOLOR,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ink-watercolor.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        RETRO_ZOO_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["retro-zoo-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        NATURALIST_SKETCH,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["naturalist-sketch.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CARTOON_MASCOT,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["cartoon-mascot.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXEL_SPRITE_ANIMAL,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixel-sprite-animal.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        LOWPOLY_GEOMETRIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["lowpoly-geometric.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PAPERCUT_LAYER_ART,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["papercut-layer-art.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        TOTEM_MYTHOLOGICAL,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["totem-mythisch-totem.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WOODCUT_ENGRAVING,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["woodcut-engraving.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["studio-ghibli-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        DISNEY_CLASSIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["disney-classic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PIXAR_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pixar-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

LANDSCAPE_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        UKIYOE_WOODBLOCK,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ukiyoe-woodblock.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PENCIL_GRAPHITE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pencil-graphite.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        PASTEL_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pastel-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SILKSCREEN_PRINT,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["silkscreen-print.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        GEOMETRIC_ABSTRACTION,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["geometric-abstraction.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        ART_DECO_TRAVEL_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["art-deco-travel-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WATERCOLOR_WASH,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["watercolor-wash.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CHARCOAL_DRAWING,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["charcoal-drawing.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["moebius-french-sci-fi.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

NATURE_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        BOTANICAL_PLATE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["botanical-plate.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        INK_WASH_PAINTING,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ink-wash-painting.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STENCIL_LEAVES,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["stencil-leaves.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CUTPAPER_COLLAGE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["cutpaper-collage.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        ETCHING_COPPERPLATE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["etching-copperplate.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        OUTLINE_WITH_COLOR,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["outline-with-color.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        ART_NOUVEAU_FLORAL,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["art-nouveau-floral.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        UKIYOE_WOODBLOCK,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ukiyoe-woodblock.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WATERCOLOR_WASH,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["watercolor-wash.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        POINTILLISM_HALFTONE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pointillism-halftone.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SILHOUETTE_COLOR_BLOCKS,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["silhouette-color-blocks.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

CITY_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        NOIR_COMIC_SCENE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["noir-comic-scene.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CYBERPUNK_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["cyberpunk-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SILKSCREEN_SKYLINE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["silkscreen-skyline.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        ISOMETRIC_PIXEL_CITY,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["isometric-pixel-city.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        CONSTRUCTIVIST_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["constructivist-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WATERCOLOR_CITYSCAPE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["watercolor-cityscape.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        VECTOR_FLAT_ILLUSTRATION,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["vector-flat-illustration.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        ART_DECO_ARCHITECTURAL_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["art-deco-architectural-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        UKIYOE_WOODBLOCK,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["ukiyoe-woodblock.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SPIDERVERSE_COMIC,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["spiderverse-comic.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        GRITTY_WESTERN_COMICS,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["gritty-western-comics.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["moebius-french-sci-fi.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        BLUEPRINT_TECHNICAL,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["blueprint-technical.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SILHOUETTE_COLOR_BLOCKS,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["silhouette-color-blocks.md", None, SHADED_PALETTE_SET, "png"],
    ),
]

BUILDING_ART_STYLES: List[Tuple[str, List, List]] = [
    (
        BLUEPRINT_TECHNICAL,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["blueprint-technical.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        WOODCUT_ENGRAVING,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["woodcut-engraving.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        ART_DECO_ARCHITECTURAL_POSTER,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["art-deco-architectural-poster.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        POP_MINIMALISM,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["pop-minimalism.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        SURREALIST_DECONSTRUCTION,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["surrealist-deconstruction.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        STAINED_GLASS_STYLE,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["stained-glass-style.md", None, SHADED_PALETTE_SET, "png"],
    ),
    (
        LINEART_SKETCH,
        [openai_process, resize_crop, quantize_to_palette, output_image],
        ["lineart-sketch.md", None, SHADED_PALETTE_SET, "png"],
    ),
]