from __future__ import annotations

import streamlit as st


def render_progress_visual(
    percent: int,
    intake_ml: int,
    goal_ml: int,
    celebrate: bool = False,
) -> None:
    percent = max(0, min(int(percent), 100))
    celebration_class = " celebrate" if celebrate else ""

    html = f"""
    <div class="wb-bottle-wrap{celebration_class}">
        <div class="wb-bottle">
            <div class="wb-bottle-neck"></div>

            <div class="wb-bottle-body">
                <div
                    class="wb-bottle-water"
                    id="wb-water"
                    style="height:{percent}%"
                >
                    <div class="wb-water-wave wb-wave-one"></div>
                    <div class="wb-water-wave wb-wave-two"></div>
                    <div class="wb-water-shimmer"></div>
                </div>

                <div class="wb-bottle-glass"></div>

                <div class="wb-bottle-highlight"></div>

                <div class="wb-bottle-label">
                    <strong>{intake_ml:,} ml</strong>
                    <span>/ {goal_ml:,} ml</span>
                </div>
            </div>
        </div>
    </div>

    <script>
    (() => {{
        const water = document.getElementById("wb-water");
        if (!water) return;

        const target = {percent};

        try {{
            const storageKey = "waterbuddy_previous_water_level";
            const previous = parseFloat(localStorage.getItem(storageKey));

            if (Number.isFinite(previous) && previous !== target) {{
                water.style.transition = "none";
                water.style.height = previous + "%";

                requestAnimationFrame(() => {{
                    requestAnimationFrame(() => {{
                        water.style.transition =
                            "height 1.15s cubic-bezier(.22,.75,.25,1)";
                        water.style.height = target + "%";
                    }});
                }});
            }}

            localStorage.setItem(storageKey, String(target));
        }} catch (e) {{
            water.style.height = target + "%";
        }}
    }})();
    </script>

    <style>
    .wb-bottle-wrap {{
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: flex-end;
        padding: 18px 0 8px;
    }}

    .wb-bottle {{
        position: relative;
        width: 190px;
        height: 330px;
        display: flex;
        flex-direction: column;
        align-items: center;
        filter: drop-shadow(0 22px 35px rgba(0,0,0,.22));
    }}

    .wb-bottle-neck {{
        width: 72px;
        height: 38px;
        margin-bottom: -2px;
        border: 2px solid rgba(255,255,255,.34);
        border-bottom: 0;
        border-radius: 18px 18px 5px 5px;
        background: linear-gradient(
            90deg,
            rgba(255,255,255,.16),
            rgba(255,255,255,.04),
            rgba(255,255,255,.16)
        );
        backdrop-filter: blur(8px);
        z-index: 3;
    }}

    .wb-bottle-body {{
        position: relative;
        width: 170px;
        height: 292px;
        overflow: hidden;
        border-radius: 34px 34px 30px 30px;
        border: 2px solid rgba(255,255,255,.30);
        background:
            linear-gradient(
                115deg,
                rgba(255,255,255,.20),
                rgba(255,255,255,.055) 42%,
                rgba(255,255,255,.12)
            );
        box-shadow:
            inset 8px 0 18px rgba(255,255,255,.07),
            inset -10px 0 22px rgba(0,0,0,.08),
            0 0 35px rgba(109,233,255,.10);
        backdrop-filter: blur(10px);
    }}

    .wb-bottle-water {{
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        min-height: 0;
        overflow: hidden;
        background:
            linear-gradient(
                180deg,
                rgba(94,225,255,.88),
                rgba(48,166,226,.94)
            );
        box-shadow:
            inset 0 10px 20px rgba(255,255,255,.10),
            0 -4px 18px rgba(70,215,255,.18);
        transition: height 1.15s cubic-bezier(.22,.75,.25,1);
        will-change: height;
    }}

    .wb-water-wave {{
        position: absolute;
        left: -20%;
        top: -13px;
        width: 140%;
        height: 26px;
        border-radius: 50%;
        background: rgba(170,245,255,.48);
        animation: wb-wave 3.2s linear infinite;
    }}

    .wb-wave-two {{
        top: -9px;
        opacity: .34;
        animation:
            wb-wave 4.4s linear infinite reverse,
            wb-wave-drift 2.6s ease-in-out infinite;
    }}

    .wb-water-shimmer {{
        position: absolute;
        top: 16px;
        left: -35%;
        width: 170%;
        height: 3px;
        background: rgba(255,255,255,.26);
        filter: blur(2px);
        animation: wb-shimmer 2.8s ease-in-out infinite;
    }}

    .wb-bottle-glass {{
        position: absolute;
        inset: 0;
        pointer-events: none;
        background:
            linear-gradient(
                105deg,
                rgba(255,255,255,.20) 0%,
                transparent 22%,
                transparent 68%,
                rgba(255,255,255,.08) 100%
            );
    }}

    .wb-bottle-highlight {{
        position: absolute;
        top: 25px;
        left: 23px;
        width: 13px;
        height: 180px;
        border-radius: 20px;
        background: linear-gradient(
            180deg,
            rgba(255,255,255,.62),
            rgba(255,255,255,.04)
        );
        opacity: .7;
        pointer-events: none;
    }}

    .wb-bottle-label {{
        position: absolute;
        left: 50%;
        bottom: 35px;
        transform: translateX(-50%);
        z-index: 4;
        min-width: 112px;
        padding: 10px 14px;
        text-align: center;
        border-radius: 14px;
        background: rgba(4,20,32,.42);
        border: 1px solid rgba(255,255,255,.18);
        box-shadow: 0 8px 20px rgba(0,0,0,.16);
        backdrop-filter: blur(8px);
        color: #fff;
        white-space: nowrap;
    }}

    .wb-bottle-label strong {{
        display: block;
        font-size: 17px;
        line-height: 1.15;
        color: #fff;
    }}

    .wb-bottle-label span {{
        display: block;
        margin-top: 3px;
        font-size: 11px;
        color: rgba(255,255,255,.72);
    }}

    @keyframes wb-wave {{
        from {{ transform: translateX(0) rotate(0deg); }}
        to {{ transform: translateX(-12%) rotate(360deg); }}
    }}

    @keyframes wb-wave-drift {{
        0%, 100% {{ transform: translateX(0) scaleY(1); }}
        50% {{ transform: translateX(5%) scaleY(1.25); }}
    }}

    @keyframes wb-shimmer {{
        0% {{ transform: translateX(-20%); opacity: .15; }}
        50% {{ transform: translateX(20%); opacity: .42; }}
        100% {{ transform: translateX(55%); opacity: .12; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .wb-bottle-water,
        .wb-water-wave,
        .wb-water-shimmer {{
            animation: none !important;
            transition: none !important;
        }}
    }}

    @media (max-width: 640px) {{
        .wb-bottle {{
            transform: scale(.88);
            transform-origin: bottom center;
            margin-top: -18px;
            margin-bottom: -18px;
        }}
    }}
    </style>
    """

    st.html(html)

    st.markdown(
        f"<div class='progress-caption'><span>Progress {percent}%</span></div>",
        unsafe_allow_html=True,
    )
