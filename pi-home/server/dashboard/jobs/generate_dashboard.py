from dashboard.jobs.job_registry import register
from dashboard.constants import (
    IMAGE_DIR,
)
from dashboard.color_constants import EXTENDED_PALETTE_SET
from pathlib import Path
from dashboard.jobs.job_registry import register
from dashboard.models.job import Job
from dashboard.models.application import PrerenderedDashboard
from dashboard.services.logger_job import RunLogger
from dashboard.services.generate_art import run_art_generation_pipeline, ImageProcessingContext
from playwright.sync_api import sync_playwright
from django.utils import timezone
from dashboard.services.generate_art import run_art_generation_pipeline, ImageProcessingContext

DEFAULT_W = 1200
DEFAULT_H = 1600

def render_png(url: str,*, width=DEFAULT_W, height=DEFAULT_H,
               wait_selector: str | None = None, extra_wait_ms: int = 0,
               no_sandbox: bool = False) -> bytes:
    launch_args = ["--disable-dev-shm-usage"]
    if no_sandbox:
        launch_args += ["--no-sandbox", "--disable-setuid-sandbox"]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=launch_args)
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
            color_scheme="light",
            bypass_csp=True,
            java_script_enabled=True,
            locale="en-US",
        )
        page = context.new_page()

        # Freeze animations
        page.add_style_tag(content="""
            * { animation: none !important; transition: none !important; }
            html, body { overflow: hidden !important; }
        """)

        page.goto(url, wait_until="networkidle", timeout=5_000)
        if wait_selector:
            page.wait_for_selector(wait_selector, state="visible", timeout=30_000)

        page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
        if extra_wait_ms:
            page.wait_for_timeout(extra_wait_ms)

        png_bytes = page.screenshot(full_page=False, omit_background=False, type="png")
        browser.close()
        return png_bytes

@register("DASHBOARD")
def generate_dashboard(job: Job, logger: RunLogger, params):
    now = timezone.now()

    newDashboard = PrerenderedDashboard.objects.create(
        path=None, # None means process started byt generation not funished
    )

    logger.info("Generating dashboard")
    out_path = Path(IMAGE_DIR).resolve() / "dashboards" / f"last_dashboard-{now.strftime('%Y%m%d')}.png"
    url = "http://localhost:8000/dashboard" # TODO wire in env vars for dynamic port allocation

    png_bytes: bytes | None = None
    try:
        png_bytes = render_png(url)
    except Exception as e:
        logger.error(f"Dashboard generation failed\n{str(e)}",)
        raise
    if png_bytes is None:
        raise RuntimeError("Impossible")
    
    logger.info("Running post processing")
    try:
        ctx: ImageProcessingContext = ImageProcessingContext(
            logger=logger,
            pipeline=["quantize_to_palette","output_image"],
            pipeline_args=[(EXTENDED_PALETTE_SET,), ("png",)],
        )
        run_art_generation_pipeline(png_bytes,out_path, ctx)
    except Exception as e:
        logger.error(f"Pineline after dashboard failed\n{str(e)}")
        raise
    
    newDashboard.path = str(out_path) # Generation successful
    newDashboard.save()


