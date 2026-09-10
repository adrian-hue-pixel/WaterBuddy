from __future__ import annotations

from datetime import datetime, timezone
import html
import streamlit as st


AQUA = {
    "primary": "#63e8ff",
    "secondary": "#42a5ff",
    "light": "#c9f8ff",
    "dark": "#061b2b",
    "glow": "rgba(77, 224, 255, 0.55)",
}


def _get_mascot_variant() -> str:
    # One consistent WaterBuddy identity across every theme.
    return "aqua"


def _get_state(
    *,
    last_logged: int = 0,
    celebrate: bool = False,
) -> str:
    intake = int(st.session_state.get("daily_intake_ml", 0))
    goal = max(int(st.session_state.get("goal_ml", 1)), 1)
    percent = int(round((intake / goal) * 100))

    # 100% always gets the celebration animation.
    if celebrate or percent >= 100:
        return "celebrate"

    last_water_at = st.session_state.get("last_water_at")

    # No water logged today.
    if percent <= 0 and not last_water_at:
        return "thirsty"

    # Sad state after a long gap without drinking.
    if last_water_at:
        try:
            last_time = datetime.fromisoformat(str(last_water_at))

            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=timezone.utc)

            elapsed_hours = (
                datetime.now(timezone.utc)
                - last_time.astimezone(timezone.utc)
            ).total_seconds() / 3600

            if elapsed_hours >= 3:
                return "sad"

        except (TypeError, ValueError, OverflowError):
            pass

    if percent >= 50:
        return "happy_50"

    if percent >= 25:
        return "happy_25"

    return "thirsty"


def _mascot_svg(state: str) -> str:
    # Premium glossy WaterBuddy.
    # State-specific classes are animated by the CSS below.
    eye_offset = "0"
    mouth = """
        <path
            d="M93 126 Q110 142 127 126"
            fill="none"
            stroke="#062235"
            stroke-width="5"
            stroke-linecap="round"
        />
    """

    if state in ("happy_25", "happy_50"):
        mouth = """
            <path
                d="M91 125 Q110 145 129 125"
                fill="none"
                stroke="#062235"
                stroke-width="5"
                stroke-linecap="round"
            />
        """
    elif state == "celebrate":
        mouth = """
            <path
                d="M88 123 Q110 153 132 123"
                fill="#ff8fcf"
                stroke="#062235"
                stroke-width="4"
            />
        """
    elif state == "sad":
        mouth = """
            <path
                d="M91 140 Q110 122 129 140"
                fill="none"
                stroke="#062235"
                stroke-width="5"
                stroke-linecap="round"
            />
        """
    elif state == "thirsty":
        mouth = """
            <path
                d="M99 134 Q110 128 121 134"
                fill="none"
                stroke="#062235"
                stroke-width="4"
                stroke-linecap="round"
            />
        """


    return f"""
    <svg
        class="wb-mascot-svg wb-mascot-{state}"
        viewBox="0 0 220 240"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="WaterBuddy mascot"
    >
        <defs>
            <linearGradient id="wbBody" x1="25%" y1="5%" x2="80%" y2="100%">
                <stop offset="0%" stop-color="#d9fbff"/>
                <stop offset="22%" stop-color="{AQUA['primary']}"/>
                <stop offset="68%" stop-color="#39bfff"/>
                <stop offset="100%" stop-color="{AQUA['secondary']}"/>
            </linearGradient>

            <linearGradient id="wbShine" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ffffff" stop-opacity=".92"/>
                <stop offset="55%" stop-color="#ffffff" stop-opacity=".18"/>
                <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
            </linearGradient>

            <radialGradient id="wbGlow">
                <stop offset="0%" stop-color="#8ff5ff" stop-opacity=".75"/>
                <stop offset="100%" stop-color="#3caeff" stop-opacity="0"/>
            </radialGradient>

            <filter id="wbShadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow
                    dx="0"
                    dy="12"
                    stdDeviation="9"
                    flood-color="#061827"
                    flood-opacity=".28"
                />
            </filter>

            <filter id="wbGlowFilter" x="-80%" y="-80%" width="260%" height="260%">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <!-- ambient glow -->
        <ellipse
            cx="110"
            cy="216"
            rx="76"
            ry="18"
            fill="url(#wbGlow)"
            class="wb-mascot-ground-glow"
        />

        <!-- floating droplets -->
        <g class="wb-mascot-particles">
            <circle cx="38" cy="82" r="5" fill="#9df7ff"/>
            <circle cx="182" cy="62" r="4" fill="#ffffff"/>
            <circle cx="194" cy="105" r="6" fill="#58dfff"/>
            <circle cx="29" cy="128" r="3" fill="#55caff"/>
        </g>

        <!-- left arm -->
        <g class="wb-mascot-arm wb-mascot-arm-left">
            <path
                d="M57 160 Q32 158 27 178 Q25 187 33 191 Q43 194 51 181 L68 168"
                fill="url(#wbBody)"
                stroke="#159ed4"
                stroke-width="3"
            />
        </g>

        <!-- right arm -->
        <g class="wb-mascot-arm wb-mascot-arm-right">
            <path
                d="M163 158 Q190 151 199 170 Q203 179 195 185 Q186 190 178 177 L157 169"
                fill="url(#wbBody)"
                stroke="#159ed4"
                stroke-width="3"
            />
        </g>

        <!-- main droplet body -->
        <g class="wb-mascot-body">
            <path
                d="
                    M110 18
                    C105 31 65 61 57 98
                    C48 139 68 176 110 187
                    C152 176 172 139 163 98
                    C155 61 115 31 110 18 Z
                "
                fill="url(#wbBody)"
                stroke="#75efff"
                stroke-width="3"
            />

            <!-- glossy highlight -->
            <path
                d="
                    M86 54
                    C70 75 66 101 70 119
                    C74 137 82 143 87 138
                    C91 134 83 117 87 94
                    C90 76 101 62 101 51
                    C100 43 92 44 86 54 Z
                "
                fill="url(#wbShine)"
                opacity=".92"
            />

            <!-- forehead shine -->
            <ellipse
                cx="122"
                cy="49"
                rx="17"
                ry="7"
                fill="#ffffff"
                opacity=".28"
                transform="rotate(25 122 49)"
            />

            <!-- eyes -->
            <g class="wb-mascot-eyes">
                <ellipse
                    cx="87"
                    cy="108"
                    rx="16"
                    ry="22"
                    fill="#ffffff"
                    stroke="#0b3150"
                    stroke-width="3"
                />
                <ellipse
                    cx="133"
                    cy="108"
                    rx="16"
                    ry="22"
                    fill="#ffffff"
                    stroke="#0b3150"
                    stroke-width="3"
                />

                <ellipse
                    cx="{87 + int(eye_offset)}"
                    cy="110"
                    rx="10"
                    ry="15"
                    fill="#062235"
                />
                <ellipse
                    cx="{133 + int(eye_offset)}"
                    cy="110"
                    rx="10"
                    ry="15"
                    fill="#062235"
                />

                <circle cx="90" cy="104" r="4.5" fill="#ffffff"/>
                <circle cx="136" cy="104" r="4.5" fill="#ffffff"/>
                <circle cx="84" cy="118" r="2" fill="#75eaff"/>
                <circle cx="130" cy="118" r="2" fill="#75eaff"/>
            </g>

            <!-- eyebrows -->
            <path
                d="M73 82 Q87 73 98 82"
                fill="none"
                stroke="#0b3150"
                stroke-width="5"
                stroke-linecap="round"
            />
            <path
                d="M122 82 Q135 73 147 82"
                fill="none"
                stroke="#0b3150"
                stroke-width="5"
                stroke-linecap="round"
            />

            {mouth}

            <!-- cheeks -->
            <ellipse cx="70" cy="128" rx="9" ry="5" fill="#ff9dcc" opacity=".52"/>
            <ellipse cx="150" cy="128" rx="9" ry="5" fill="#ff9dcc" opacity=".52"/>

            <!-- tiny chest droplet -->
            <path
                d="M110 150 C104 158 101 162 101 166 C101 171 105 175 110 175 C115 175 119 171 119 166 C119 162 116 158 110 150 Z"
                fill="#eaffff"
                opacity=".85"
            />
        </g>

        <!-- celebration sparkles -->
        <g class="wb-mascot-sparkles">
            <path d="M28 54 L31 63 L40 66 L31 69 L28 78 L25 69 L16 66 L25 63 Z"
                  fill="#fff5b0"/>
            <path d="M188 38 L191 47 L200 50 L191 53 L188 62 L185 53 L176 50 L185 47 Z"
                  fill="#ffffff"/>
            <path d="M201 133 L204 142 L213 145 L204 148 L201 157 L198 148 L189 145 L198 142 Z"
                  fill="#8ef8ff"/>
        </g>

        <!-- water ring -->
        <ellipse
            cx="110"
            cy="201"
            rx="55"
            ry="10"
            fill="none"
            stroke="#5de8ff"
            stroke-width="3"
            opacity=".75"
            class="wb-mascot-ring"
        />
    </svg>
    """


def render_mascot(
    snd_on: bool = True,
    last_logged: int = 0,
    celebrate: bool = False,
    show_animations: bool = True,
) -> None:
    state = _get_state(
        last_logged=last_logged,
        celebrate=celebrate,
    )

    animation_class = "" if show_animations else "wb-mascot-static"

    st.components.v1.html(
        f"""
        <div class="wb-mascot-stage {animation_class}">
            <div class="wb-mascot-aura"></div>

            <div class="wb-mascot-character">
                {_mascot_svg(state)}
            </div>

            <div class="wb-mascot-status">
                <span class="wb-mascot-dot"></span>
                <span>WaterBuddy</span>
            </div>
        </div>

        <style>
        .wb-mascot-stage {{
            position: relative;
            width: 100%;
            min-height: 310px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: visible;
            isolation: isolate;
        }}

        .wb-mascot-aura {{
            position: absolute;
            width: 190px;
            height: 190px;
            border-radius: 50%;
            background:
                radial-gradient(
                    circle,
                    rgba(85, 230, 255, .22) 0%,
                    rgba(66, 165, 255, .10) 38%,
                    transparent 72%
                );
            filter: blur(7px);
            z-index: -1;
            animation: wb-aura-breathe 4s ease-in-out infinite;
        }}

        .wb-mascot-character {{
            width: min(270px, 82%);
            transform-origin: center bottom;
            animation: wb-mascot-float 4s ease-in-out infinite;
            will-change: transform;
        }}

        .wb-mascot-svg {{
            width: 100%;
            height: auto;
            display: block;
            overflow: visible;
        }}

        .wb-mascot-body {{
            transform-origin: 110px 185px;
        }}

        .wb-mascot-eyes {{
            transform-origin: 110px 110px;
            animation: wb-eye-breathe 5s ease-in-out infinite;
        }}

        .wb-mascot-particles circle {{
            animation: wb-particle-float 3s ease-in-out infinite;
        }}

        .wb-mascot-particles circle:nth-child(2) {{
            animation-delay: .8s;
        }}

        .wb-mascot-particles circle:nth-child(3) {{
            animation-delay: 1.4s;
        }}

        .wb-mascot-particles circle:nth-child(4) {{
            animation-delay: 2s;
        }}

        .wb-mascot-ring {{
            transform-origin: 110px 201px;
            animation: wb-ring-pulse 2.8s ease-out infinite;
        }}

        .wb-mascot-sparkles {{
            opacity: 0;
        }}

        .wb-mascot-character:has(.wb-mascot-celebrate) {{
            animation:
                wb-mascot-celebrate 1.1s cubic-bezier(.2,.9,.3,1.25) infinite,
                wb-mascot-float 4s ease-in-out infinite;
        }}

        .wb-mascot-character:has(.wb-mascot-celebrate) .wb-mascot-sparkles {{
            opacity: 1;
            animation: wb-sparkle-pop 1.2s ease-out infinite;
        }}

        .wb-mascot-character:has(.wb-mascot-celebrate) .wb-mascot-ring {{
            animation:
                wb-ring-burst 1.1s ease-out infinite;
        }}

        .wb-mascot-happy .wb-mascot-body {{
            animation: wb-happy-bounce .65s ease-out;
        }}

        .wb-mascot-happy .wb-mascot-arm-right {{
            transform-origin: 165px 165px;
            animation: wb-wave 1s ease-in-out 2;
        }}

        /* Five hydration-based mascot states */
        .wb-mascot-thirsty .wb-mascot-body {{
            animation: wb-thirsty-pulse 2.2s ease-in-out infinite;
        }}

        .wb-mascot-thirsty .wb-mascot-arm-left,
        .wb-mascot-thirsty .wb-mascot-arm-right {{
            animation: wb-thirsty-arms 2.2s ease-in-out infinite;
        }}

        .wb-mascot-happy_25 .wb-mascot-body {{
            animation: wb-recover-bounce 1.8s ease-in-out infinite;
        }}

        .wb-mascot-happy_25 .wb-mascot-arm-right {{
            transform-origin: 165px 165px;
            animation: wb-gentle-wave 2.2s ease-in-out infinite;
        }}

        .wb-mascot-happy_50 .wb-mascot-body {{
            animation: wb-happy-bounce .9s ease-in-out infinite;
        }}

        .wb-mascot-happy_50 .wb-mascot-arm-left {{
            transform-origin: 60px 165px;
            animation: wb-happy-arm 1.4s ease-in-out infinite;
        }}

        .wb-mascot-happy_50 .wb-mascot-arm-right {{
            transform-origin: 165px 165px;
            animation: wb-happy-arm 1.4s ease-in-out .15s infinite;
        }}

        .wb-mascot-sad .wb-mascot-body {{
            animation: wb-sad-breathe 3.2s ease-in-out infinite;
        }}

        .wb-mascot-sad .wb-mascot-arm-left,
        .wb-mascot-sad .wb-mascot-arm-right {{
            animation: wb-sad-arms 3.2s ease-in-out infinite;
        }}

        .wb-mascot-sad .wb-mascot-particles {{
            opacity: .25;
        }}

        .wb-mascot-sad .wb-mascot-ring {{
            opacity: .18;
            animation: wb-sad-ring 3s ease-in-out infinite;
        }}

        @keyframes wb-thirsty-pulse {{
            0%, 100% {{ transform: scale(1) translateY(0); }}
            50% {{ transform: scale(.975) translateY(3px); }}
        }}

        @keyframes wb-thirsty-arms {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(5px); }}
        }}

        @keyframes wb-recover-bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}

        @keyframes wb-gentle-wave {{
            0%, 100% {{ transform: rotate(0deg); }}
            50% {{ transform: rotate(-8deg); }}
        }}

        @keyframes wb-happy-arm {{
            0%, 100% {{ transform: rotate(0deg); }}
            50% {{ transform: rotate(9deg); }}
        }}

        @keyframes wb-sad-breathe {{
            0%, 100% {{ transform: translateY(3px) scale(.985); }}
            50% {{ transform: translateY(7px) scale(.97); }}
        }}

        @keyframes wb-sad-arms {{
            0%, 100% {{ transform: rotate(0deg) translateY(2px); }}
            50% {{ transform: rotate(5deg) translateY(7px); }}
        }}

        @keyframes wb-sad-ring {{
            0%, 100% {{ transform: scaleX(.88); opacity: .12; }}
            50% {{ transform: scaleX(.96); opacity: .22; }}
        }}

        .wb-mascot-static *,
        .wb-mascot-static {{
            animation: none !important;
        }}

        .wb-mascot-status {{
            margin-top: -2px;
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            padding: .38rem .75rem;
            border-radius: 999px;
            background: rgba(7, 25, 42, .68);
            border: 1px solid rgba(104, 231, 255, .22);
            color: rgba(225, 249, 255, .88);
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .06em;
            text-transform: uppercase;
            backdrop-filter: blur(14px);
            box-shadow:
                0 8px 28px rgba(0,0,0,.18),
                inset 0 1px 0 rgba(255,255,255,.08);
        }}

        .wb-mascot-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #6ff4ff;
            box-shadow: 0 0 12px rgba(111,244,255,.9);
            animation: wb-status-pulse 2s ease-in-out infinite;
        }}

        @keyframes wb-mascot-float {{
            0%, 100% {{
                transform: translateY(0) rotate(-1deg);
            }}
            50% {{
                transform: translateY(-10px) rotate(1deg);
            }}
        }}

        @keyframes wb-aura-breathe {{
            0%, 100% {{
                transform: scale(.88);
                opacity: .55;
            }}
            50% {{
                transform: scale(1.08);
                opacity: .95;
            }}
        }}

        @keyframes wb-eye-breathe {{
            0%, 94%, 100% {{
                transform: scaleY(1);
            }}
            96% {{
                transform: scaleY(.08);
            }}
            98% {{
                transform: scaleY(1);
            }}
        }}

        @keyframes wb-particle-float {{
            0%, 100% {{
                transform: translateY(5px);
                opacity: .45;
            }}
            50% {{
                transform: translateY(-13px);
                opacity: 1;
            }}
        }}

        @keyframes wb-ring-pulse {{
            0%, 100% {{
                transform: scaleX(.9);
                opacity: .35;
            }}
            50% {{
                transform: scaleX(1.08);
                opacity: .85;
            }}
        }}

        @keyframes wb-happy-bounce {{
            0% {{ transform: scale(1); }}
            35% {{ transform: scale(1.045) translateY(-5px); }}
            70% {{ transform: scale(.985); }}
            100% {{ transform: scale(1); }}
        }}

        @keyframes wb-wave {{
            0%, 100% {{
                transform: rotate(0deg);
            }}
            25% {{
                transform: rotate(-13deg);
            }}
            50% {{
                transform: rotate(13deg);
            }}
            75% {{
                transform: rotate(-9deg);
            }}
        }}

        @keyframes wb-mascot-celebrate {{
            0%, 100% {{
                transform: translateY(0) rotate(-2deg) scale(1);
            }}
            30% {{
                transform: translateY(-24px) rotate(4deg) scale(1.04);
            }}
            55% {{
                transform: translateY(-8px) rotate(-3deg) scale(1.015);
            }}
            75% {{
                transform: translateY(-17px) rotate(2deg) scale(1.03);
            }}
        }}

        @keyframes wb-sparkle-pop {{
            0% {{
                transform: scale(.45) rotate(0deg);
                opacity: 0;
            }}
            35% {{
                transform: scale(1.15) rotate(12deg);
                opacity: 1;
            }}
            100% {{
                transform: scale(1) rotate(24deg);
                opacity: .55;
            }}
        }}

        @keyframes wb-ring-burst {{
            0% {{
                transform: scaleX(.75);
                opacity: .2;
            }}
            45% {{
                transform: scaleX(1.2);
                opacity: 1;
            }}
            100% {{
                transform: scaleX(1.45);
                opacity: 0;
            }}
        }}

        @keyframes wb-status-pulse {{
            0%, 100% {{ opacity: .5; transform: scale(.85); }}
            50% {{ opacity: 1; transform: scale(1.15); }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            .wb-mascot-stage *,
            .wb-mascot-stage {{
                animation: none !important;
            }}
        }}

        @media (max-width: 700px) {{
            .wb-mascot-stage {{
                min-height: 270px;
            }}

            .wb-mascot-character {{
                width: min(235px, 82%);
            }}
        }}
        </style>
        """,
        height=310,
        scrolling=False,
    )
