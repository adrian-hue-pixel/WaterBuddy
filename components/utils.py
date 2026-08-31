from __future__ import annotations

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def render_embedded_html(html: str, height: int = 160) -> None:
    """Render HTML in a forward-compatible way.

    This function now optionally injects a short-lived debug overlay into the
    embedded HTML (when WB_MASCOT_DEBUG=1) that briefly shows the mascot's
    data-state and whether a celebration banner is present. It also appends a
    small timestamp comment to the HTML so that successive renders are not
    treated as identical by the embedding path (cache-busting).
    """
    import hashlib
    from pathlib import Path

    try:
        import os
        # If enabled, inject a tiny client-side debug overlay which flashes the
        # mascot state and celebrate flag for ~1.8s. This helps confirm server
        # injected tokens reach the embedded frame in the browser.
        debug_enabled = os.getenv("WB_MASCOT_DEBUG", "0").lower() in ("1", "true", "yes")

        # Append a cache-busting timestamp comment so the HTML changes every
        # render and the browser/iframe won't reuse a previously cached blob.
        try:
            import time
            ts = str(int(time.time()))
        except Exception:
            ts = hashlib.sha1(os.urandom(8)).hexdigest()
        # Use a predictable, small comment suffix to change the sha1 when needed.
        html_with_ts = html + f"\n<!--WB_TS:{ts}-->"

        if debug_enabled:
            # Inject a small script that reads #mascot dataset.state and the
            # celebrate banner class and shows them briefly in an overlay.
            debug_script = r"""
<script>
(function(){
  try {
    const dbg = document.createElement('div');
    dbg.id = 'wb-embed-debug';
    dbg.style.cssText = 'position:fixed;left:8px;top:8px;z-index:99999;padding:6px 10px;border-radius:6px;background:rgba(0,0,0,0.65);color:#fff;font-size:12px;backdrop-filter:blur(4px);box-shadow:0 6px 18px rgba(0,0,0,0.35);';
    const mascot = document.getElementById('mascot');
    const banner = document.getElementById('celebrate-banner');
    const state = (mascot && mascot.dataset && mascot.dataset.state) || 'unknown';
    const celebrate = banner && banner.classList && banner.classList.contains('banner-show');
    dbg.textContent = 'DBG: state=' + state + '  CELEBRATE=' + (celebrate ? '1' : '0');
    document.body.appendChild(dbg);
    setTimeout(()=>{ try { dbg.remove(); } catch(e){} }, 1800);
  } catch(e) { /* no-op */ }
})();
</script>
"""
            html_with_ts = html_with_ts + debug_script
    except Exception:
        # If debug injection fails for any reason, fall back to original html.
        html_with_ts = html

    # Persist the HTML to the assets/embedded folder for inspection and optional
    # file-backed iframe serving.
    try:
        assets_dir = Path(__file__).resolve().parents[2] / "assets" / "embedded"
        assets_dir.mkdir(parents=True, exist_ok=True)
        name = hashlib.sha1(html_with_ts.encode('utf-8')).hexdigest()[:12]
        file_path = assets_dir / f"embedded_{name}.html"
        if not file_path.exists():
            file_path.write_text(html_with_ts, encoding="utf-8")
    except Exception:
        logger.exception("Failed to write embedded HTML to assets folder")

    try:
        # Allow toggling file-backed iframe behavior via environment variable.
        prefer_file = os.getenv("WB_EMBED_IFRAME_AS_FILE", "0").lower() in ("1", "true", "yes")

        file_url = None
        try:
            file_url = f"/assets/embedded/{file_path.name}"
        except Exception:
            file_url = None

        if prefer_file and hasattr(st, "iframe") and file_url:
            try:
                st.iframe(file_url, height=height)
                return
            except Exception:
                logger.exception("File-backed iframe failed, falling back to srcdoc: %s", file_url)

        # Use components.html which reliably executes inline scripts and styles
        # across many Streamlit versions.
        try:
            import streamlit.components.v1 as components

            components.html(html_with_ts, height=height, scrolling=False)
            return
        except Exception:
            logger.exception("components.html failed; falling back to st.iframe")

        # Prefer st.iframe with srcdoc as a final fallback.
        if hasattr(st, "iframe"):
            try:
                st.iframe(srcdoc=html_with_ts, height=height)
                return
            except TypeError:
                try:
                    st.iframe(html_with_ts, height=height)
                    return
                except Exception:
                    logger.exception("st.iframe(srcdoc) fallback also failed")
    except Exception as exc:
        logger.exception("Failed to render embedded HTML via st.iframe: %s", exc)
        try:
            import streamlit.components.v1 as components

            components.html(html_with_ts, height=height, scrolling=False)
        except Exception:
            logger.exception("Fallback to components.html also failed.")
