from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st


logger = logging.getLogger(__name__)


def render_embedded_html(html: str, height: int = 160) -> None:
    """Render embedded HTML using Streamlit's available iframe/component APIs."""

    html_with_ts = html

    try:
        import hashlib
        import time

        ts = str(int(time.time()))
        html_with_ts = html + f"\\n<!--WB_TS:{ts}-->"
    except Exception:
        pass

    file_path = None

    # Persist HTML for optional file-backed iframe rendering.
    try:
        assets_dir = Path(__file__).resolve().parents[2] / "assets" / "embedded"
        assets_dir.mkdir(parents=True, exist_ok=True)

        import hashlib

        name = hashlib.sha1(html_with_ts.encode("utf-8")).hexdigest()[:12]
        file_path = assets_dir / f"embedded_{name}.html"

        if not file_path.exists():
            file_path.write_text(html_with_ts, encoding="utf-8")
    except Exception:
        logger.exception("Failed to write embedded HTML to assets folder")

    try:
        prefer_file = (
            __import__("os").getenv("WB_EMBED_IFRAME_AS_FILE", "0").lower()
            in ("1", "true", "yes")
        )

        file_url = None
        if file_path is not None:
            file_url = f"/assets/embedded/{file_path.name}"

        if prefer_file and hasattr(st, "iframe") and file_url:
            try:
                st.iframe(file_url, height=height)
                return
            except Exception:
                logger.exception(
                    "File-backed iframe failed, falling back to srcdoc: %s",
                    file_url,
                )

        try:
            import streamlit.components.v1 as components

            components.html(
                html_with_ts,
                height=height,
                scrolling=False,
            )
            return
        except Exception:
            logger.exception(
                "components.html failed; falling back to st.iframe"
            )

        if hasattr(st, "iframe"):
            try:
                st.iframe(srcdoc=html_with_ts, height=height)
                return
            except TypeError:
                try:
                    st.iframe(html_with_ts, height=height)
                    return
                except Exception:
                    logger.exception("st.iframe fallback also failed")

    except Exception:
        logger.exception("Failed to render embedded HTML")

        try:
            import streamlit.components.v1 as components

            components.html(
                html_with_ts,
                height=height,
                scrolling=False,
            )
        except Exception:
            logger.exception("Final embedded HTML fallback failed")
