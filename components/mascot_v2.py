from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from services.mascot_service import get_mascot_service


VARIANT_PALETTES = {
    "aqua": {
        "primary": "#6de9ff",
        "secondary": "#5fb0ff",
        "accent": "#bff8ff",
        "highlight": "rgba(255,255,255,0.98)",
        "eye": "#052233",
        "shadow": "rgba(7, 24, 38, 0.16)",
    },
    "sunrise": {
        "primary": "#ff9a62",
        "secondary": "#f77f5b",
        "accent": "#ffe4c8",
        "highlight": "rgba(255,255,255,0.94)",
        "eye": "#4a2616",
        "shadow": "rgba(96, 51, 31, 0.15)",
    },
    "forest": {
        "primary": "#7adf9d",
        "secondary": "#5bcf8f",
        "accent": "#dff8e7",
        "highlight": "rgba(255,255,255,0.96)",
        "eye": "#113027",
        "shadow": "rgba(10, 32, 27, 0.16)",
    },
    "neon": {
        "primary": "#8b5cf6",
        "secondary": "#c084fc",
        "accent": "#f5d0fe",
        "highlight": "rgba(255,255,255,0.98)",
        "eye": "#220b33",
        "shadow": "rgba(69, 29, 112, 0.26)",
    },
    "yin_yang": {
        "primary": "#111827",
        "secondary": "#f8fafc",
        "accent": "#e5e7eb",
        "highlight": "rgba(255,255,255,0.96)",
        "eye": "#111827",
        "shadow": "rgba(17, 24, 39, 0.18)",
    },
}


def _get_mascot_variant() -> str:
    selected = str(st.session_state.get("mascot_variant", "aqua")).lower()
    if selected not in VARIANT_PALETTES:
        return "aqua"
    return selected


def _get_state_name(ms, last_logged: int, celebrate: bool) -> str:
    state_name = ms.get_state().value
    if celebrate:
        return "achievement"

    last_water_raw = st.session_state.get("last_water_at")
    if last_water_raw:
        try:
            last_water_at = datetime.fromisoformat(str(last_water_raw).replace("Z", "+00:00"))
        except ValueError:
            last_water_at = None
        if last_water_at is not None:
            elapsed_sec = (datetime.now(timezone.utc) - last_water_at.astimezone(timezone.utc)).total_seconds()
            if elapsed_sec >= 8 * 3600 and st.session_state.get("daily_intake_ml", 0) < max(250, int(st.session_state.get("goal_ml", 2500)) * 35 // 100):
                return "sad"

    if int(last_logged) > 0 and state_name not in {"warning", "sad"}:
        return "happy"
    return state_name


def render_mascot(snd_on: bool = True, last_logged: int = 0, celebrate: bool = False, show_animations: bool = True) -> None:
    """Render a premium 3D mascot with hydration-driven mood changes."""
    ms = get_mascot_service()
    state_name = _get_state_name(ms, last_logged, celebrate)

    variant = _get_mascot_variant()
    palette = VARIANT_PALETTES[variant]

    body_svg = {
        "aqua": """
            <path id="body" d="M60 8 C40 36 26 58 26 88 C26 120 44 134 60 134 C76 134 94 120 94 88 C94 58 80 36 60 8 Z" />
            <ellipse id="shine" cx="44" cy="34" rx="24" ry="16" fill="url(#shine)" opacity="0.96" />
            <g id="arms" transform="translate(0,12)">
              <path d="M18 92 C30 84 40 80 46 86" stroke="rgba(255,255,255,0.12)" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.95"/>
              <path d="M102 92 C90 84 80 80 74 86" stroke="rgba(255,255,255,0.12)" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.95"/>
            </g>
        """,
        "sunrise": """
            <g id="sun">
              <circle id="body" cx="60" cy="76" r="46" />
              <g id="sun-rays" stroke="rgba(255,255,255,0.32)" stroke-width="4" stroke-linecap="round">
                <line x1="60" y1="16" x2="60" y2="30" />
                <line x1="60" y1="122" x2="60" y2="136" />
                <line x1="15" y1="76" x2="29" y2="76" />
                <line x1="91" y1="76" x2="105" y2="76" />
                <line x1="24" y1="28" x2="34" y2="38" />
                <line x1="86" y1="28" x2="96" y2="38" />
                <line x1="24" y1="124" x2="34" y2="114" />
                <line x1="86" y1="124" x2="96" y2="114" />
              </g>
              <circle cx="60" cy="76" r="28" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.20)" stroke-width="1.4" />
              <ellipse cx="44" cy="66" rx="9" ry="7" fill="rgba(255,255,255,0.22)" />
              <ellipse cx="76" cy="66" rx="9" ry="7" fill="rgba(255,255,255,0.22)" />
            </g>
        """,
        "forest": """
            <g id="tree">
              <path id="body" d="M60 20 C46 20 36 31 36 44 C28 50 20 58 20 72 C27 66 36 63 45 63 C48 76 54 83 60 94 C66 83 72 76 75 63 C84 63 93 66 100 72 C100 58 92 50 84 44 C84 31 74 20 60 20 Z" />
              <path id="tree-trunk" d="M52 80 L68 80 L68 118 L52 118 Z" fill="rgba(116,74,42,0.82)" stroke="rgba(255,255,255,0.14)" stroke-width="1.2" />
              <path id="tree-base" d="M46 116 L74 116 L70 124 L50 124 Z" fill="rgba(21,79,48,0.28)"/>
              <circle cx="40" cy="49" r="10" fill="rgba(255,255,255,0.18)" />
              <circle cx="80" cy="49" r="10" fill="rgba(255,255,255,0.17)" />
              <circle cx="60" cy="35" r="11" fill="rgba(255,255,255,0.18)" />
            </g>
        """,
        "neon": """
            <g id="orb">
              <path id="body" d="M60 8 C82 8 98 25 98 48 C98 74 85 94 60 122 C35 94 22 74 22 48 C22 25 38 8 60 8 Z" />
              <path d="M60 28 C74 28 86 39 86 52 C86 72 76 84 60 100 C44 84 34 72 34 52 C34 39 46 28 60 28 Z" fill="rgba(255,255,255,0.18)" />
              <ellipse cx="45" cy="44" rx="16" ry="11" fill="rgba(255,255,255,0.22)" />
              <ellipse cx="76" cy="44" rx="16" ry="11" fill="rgba(255,255,255,0.20)" />
            </g>
        """,
        "yin_yang": """
            <g id="yin-yang-body">
              <circle id="body" cx="60" cy="76" r="46" />
              <path d="M60 30 A46 46 0 0 1 60 122 A36 36 0 0 0 60 30 Z" fill="rgba(255,255,255,0.08)"/>
              <path d="M60 30 A46 46 0 0 0 60 122 A36 36 0 0 1 60 30 Z" fill="rgba(15,15,15,0.18)"/>
              <circle cx="60" cy="54" r="15" fill="rgba(255,255,255,0.92)"/>
              <circle cx="60" cy="98" r="15" fill="rgba(11,11,11,0.88)"/>
              <circle cx="60" cy="54" r="6" fill="rgba(11,11,11,0.9)"/>
              <circle cx="60" cy="98" r="6" fill="rgba(255,255,255,0.92)"/>
            </g>
        """,
    }[variant]

    html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root {
  --mascot-primary: __PRIMARY__;
  --mascot-secondary: __SECONDARY__;
  --mascot-accent: __ACCENT__;
  --mascot-highlight: __HIGHLIGHT__;
  --mascot-eye: __EYE__;
  --mascot-shadow: __SHADOW__;
}
body { margin:0; background: transparent; }
.mascot-wrap { display:flex; align-items:center; justify-content:center; gap:12px; min-height:170px; }
.mascot-container { position:relative; width:132px; height:162px; transform-style:preserve-3d; }
.mascot { width:100%; height:100%; transform-style:preserve-3d; will-change: transform; transition: transform 220ms ease, filter 220ms ease, opacity 220ms ease; cursor:pointer; }
.mascot svg { width:100%; height:100%; display:block; pointer-events:none; filter: drop-shadow(0 14px 22px rgba(0,0,0,0.12)); }
.mascot-shadow { position:absolute; left:50%; bottom:6px; transform:translateX(-50%); width:76px; height:18px; border-radius:50%; background: var(--mascot-shadow); filter: blur(8px); transition: transform 220ms ease, opacity 220ms ease; }
.particles { position:absolute; inset:0; pointer-events:none; overflow:visible; }
.particle { position:absolute; width:8px; height:8px; border-radius:50%; opacity:0; transform-origin:center; }
.star { position:absolute; width:12px; height:12px; opacity:0; transform-origin:center; }

@keyframes bob { 0% { transform: translateY(0px) rotateX(0deg); } 50% { transform: translateY(-12px) rotateX(5deg); } 100% { transform: translateY(0px) rotateX(0deg); } }
@keyframes nudge { 0% { transform: rotate(0deg) translateY(0); } 25% { transform: rotate(-6deg) translateY(-3px); } 50% { transform: rotate(0deg) translateY(-6px); } 75% { transform: rotate(6deg) translateY(-3px); } 100% { transform: rotate(0deg) translateY(0); } }
@keyframes bounce { 0% { transform: scale(1) translateY(0); } 28% { transform: scale(1.12) translateY(-14px); } 58% { transform: scale(0.98) translateY(-4px); } 100% { transform: scale(1) translateY(0); } }
@keyframes pulse { 0% { transform: scale(1) translateY(0); } 35% { transform: scale(1.18) translateY(-10px); } 100% { transform: scale(1) translateY(0); } }
@keyframes confettiPop { 0% { transform: translateY(0) scale(0.6) rotate(0deg); opacity:1; } 60% { opacity:1; } 100% { transform: translateY(-140px) scale(1) rotate(360deg); opacity:0; } }
@keyframes starPop { 0% { transform: scale(0.3) rotate(0deg); opacity:0; } 30% { opacity:1; transform: scale(1.05) rotate(15deg); } 100% { transform: scale(0.9) rotate(180deg); opacity:0; } }
@keyframes stateShift { 0% { transform: scale(0.97); opacity: 0.8; } 100% { transform: scale(1); opacity: 1; } }
@keyframes blink { 0% { transform: scaleY(1); } 45% { transform: scaleY(0.12); } 55% { transform: scaleY(0.12); } 100% { transform: scaleY(1); } }

.mascot-idle { animation: bob 2400ms ease-in-out infinite; transform-origin:50% 50%; }
.mascot-nudge { animation: nudge 520ms ease-in-out; }
.mascot-bounce { animation: bounce 420ms cubic-bezier(.2,.9,.2,1); }
.mascot-celebrate { animation: pulse 820ms cubic-bezier(.2,.9,.2,1); }
.mascot-state-transition { animation: stateShift 260ms ease; }

.mascot[data-state="achievement"] #arms { transform: translateY(-14px); }
.mascot[data-state="achievement"] #body { transform-origin: 50% 60%; }


.mascot[data-state="idle"] #eyeL, .mascot[data-state="idle"] #eyeR { transform: scaleY(1); }
.mascot[data-state="happy"] #eyeL, .mascot[data-state="happy"] #eyeR { transform: translateY(-2px) scaleY(1.08); }
.mascot[data-state="drinking"] #body { filter: brightness(1.06) drop-shadow(0 0 18px rgba(255,255,255,0.2)); }
.mascot[data-state="excited"] #eyeL, .mascot[data-state="excited"] #eyeR { transform: scaleY(1.2) translateY(-3px); }
.mascot[data-state="warning"] #eyeL, .mascot[data-state="warning"] #eyeR { transform: translateX(-1px); }
.mascot[data-state="sad"] #eyeL, .mascot[data-state="sad"] #eyeR { transform: translateY(4px) scaleY(0.82); }
.mascot[data-state="thinking"] #eyeL, .mascot[data-state="thinking"] #eyeR { transform: scaleY(0.9); }
.mascot[data-state="listening"] #eyeL, .mascot[data-state="listening"] #eyeR { transform: translateY(-1px) scale(1.06); }
.mascot[data-state="achievement"] #body { filter: drop-shadow(0 0 12px rgba(255, 214, 94, 0.6)); }

#body { fill: url(#dropGradient); stroke: rgba(255,255,255,0.26); stroke-width:1.5; }
#tree-trunk { fill: rgba(116,74,42,0.82); stroke: rgba(255,255,255,0.18); stroke-width:1.3; }
#tree-base { fill: rgba(15, 70, 46, 0.22); }
#sun-rays { opacity: 0.9; }
#mouth { fill: none; stroke: rgba(25, 35, 52, 0.92); stroke-width:3; stroke-linecap:round; stroke-linejoin:round; transition: transform 200ms ease; }
#blush { opacity: 0.22; fill: var(--mascot-secondary); }
#eyeL, #eyeR { fill: var(--mascot-eye); transition: transform 180ms ease; transform-origin:center; animation: blink 6s ease-in-out infinite; }

    /* Celebration banner */
    #celebrate-banner { position:absolute; top:-34px; left:50%; transform:translateX(-50%) translateY(-8px) scale(0.96); background: linear-gradient(90deg, rgba(255,223,111,0.98), rgba(255,183,77,0.98)); padding:6px 12px; border-radius:12px; color:#061021; font-weight:800; font-size:0.88rem; box-shadow:0 8px 20px rgba(0,0,0,0.12); opacity:0; pointer-events:none; transition: transform 260ms cubic-bezier(.2,.9,.2,1), opacity 260ms ease; z-index:10; }
    .banner-show { opacity:1; transform:translateX(-50%) translateY(0) scale(1); }


@media (prefers-reduced-motion: reduce) {
  .mascot-idle, .mascot-bounce, .mascot-celebrate, .mascot-nudge, .mascot-state-transition { animation: none !important; }
}

/* ===== MASCOT EMOTIONAL STATE ANIMATIONS ===== */

.mascot-state-transition {
  animation: mascotStateEnter 260ms ease-out;
}

.mascot-happy {
  animation: mascotHappy 900ms ease-in-out infinite;
}

.mascot-drinking {
  animation: mascotDrinking 650ms ease-in-out;
}

.mascot-excited {
  animation: mascotExcited 520ms ease-in-out infinite;
}

.mascot-warning {
  animation: mascotWarning 700ms ease-in-out infinite;
}

.mascot-sad {
  animation: mascotSad 1200ms ease-in-out infinite;
}

.mascot-thinking {
  animation: mascotThinking 1000ms ease-in-out infinite;
}

.mascot-listening {
  animation: mascotListening 700ms ease-in-out infinite;
}

.mascot-speaking {
  animation: mascotSpeaking 500ms ease-in-out infinite;
}

@keyframes mascotStateEnter {
  0%   { opacity: .65; transform: scale(.94); }
  100% { opacity: 1; }
}

@keyframes mascotHappy {
  0%,100% { transform: translateY(0) rotate(0deg) scale(1); }
  25%     { transform: translateY(-7px) rotate(-3deg) scale(1.03); }
  50%     { transform: translateY(0) rotate(3deg) scale(1.02); }
  75%     { transform: translateY(-5px) rotate(-2deg) scale(1.03); }
}

@keyframes mascotDrinking {
  0%   { transform: translateY(0) rotate(0deg); }
  25%  { transform: translateY(4px) rotate(-5deg) scale(.97); }
  50%  { transform: translateY(7px) rotate(4deg) scale(.96); }
  75%  { transform: translateY(2px) rotate(-2deg) scale(.99); }
  100% { transform: translateY(0) rotate(0deg); }
}

@keyframes mascotExcited {
  0%,100% { transform: translateY(0) scale(1); }
  50%     { transform: translateY(-12px) scale(1.07); }
}

@keyframes mascotWarning {
  0%,100% { transform: translateX(0) rotate(-2deg); }
  20%     { transform: translateX(-7px) rotate(-5deg); }
  40%     { transform: translateX(7px) rotate(5deg); }
  60%     { transform: translateX(-5px) rotate(-4deg); }
  80%     { transform: translateX(5px) rotate(3deg); }
}

@keyframes mascotSad {
  0%,100% { transform: translateY(3px) rotate(-2deg); }
  50%     { transform: translateY(7px) rotate(2deg); }
}

@keyframes mascotThinking {
  0%,100% { transform: translateY(0) rotate(0deg); }
  50%     { transform: translateY(-3px) rotate(4deg); }
}

@keyframes mascotListening {
  0%,100% { transform: scale(1); }
  50%     { transform: scale(1.05) translateY(-3px); }
}

@keyframes mascotSpeaking {
  0%,100% { transform: translateY(0) scale(1); }
  50%     { transform: translateY(-4px) scale(1.04); }
}

</style>
</head>
<body>
<div class="mascot-wrap">
  <div id="celebrate-banner" role="status" aria-hidden="true">Goal reached!</div>
  <div class="mascot-container">
    <div id="mascot" class="mascot mascot-idle mascot-state-transition" data-state="__STATE__" title="WaterBuddy">
      <svg viewBox="0 0 120 150" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <linearGradient id="dropGradient" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stop-color="__ACCENT__" stop-opacity="1" />
            <stop offset="60%" stop-color="__PRIMARY__" stop-opacity="1" />
            <stop offset="100%" stop-color="__SECONDARY__" stop-opacity="1" />
          </linearGradient>
          <radialGradient id="shine" cx="30%" cy="25%">
            <stop offset="0%" stop-color="__HIGHLIGHT__" />
            <stop offset="45%" stop-color="rgba(255,255,255,0.45)" />
            <stop offset="100%" stop-color="rgba(255,255,255,0)" />
          </radialGradient>
        </defs>
        __BODY_SVG__
        <ellipse id="blush" cx="40" cy="92" rx="11" ry="6" />
        <ellipse id="blush-right" cx="80" cy="92" rx="11" ry="6" opacity="0.18" fill="var(--mascot-secondary)" />
        <g id="eyes" transform="translate(0,6)">
          <ellipse id="eyeL" cx="48" cy="74" rx="5.2" ry="6.2"></ellipse>
          <ellipse id="eyeR" cx="72" cy="74" rx="5.2" ry="6.2"></ellipse>
        </g>
        <path id="mouth" d="M46 92 Q60 99 74 92" />
      </svg>
    </div>
    <div id="shadow" class="mascot-shadow" style="opacity:0.9"></div>
    <div id="particles" class="particles" aria-hidden="true"></div>
  </div>
</div>

<script>
(function(){
  const SOUND_ENABLED = __SOUND_ENABLED__;
  const LAST_LOGGED = __LAST_LOGGED__;
  const CELEBRATE = __CELEBRATE__;
  const SHOW_ANIMATIONS = __ANIMATIONS__;
  const INITIAL_STATE = "__STATE__";

  let audioCtx = null;
  let audioReady = false;
  const mascot = document.getElementById('mascot');
  const shadow = document.getElementById('shadow');
  const container = document.querySelector('.mascot-container');
  const mouth = document.getElementById('mouth');

  function setState(nextState) {
    const safeState = nextState || 'idle';
    mascot.dataset.state = safeState;

    const mouthMap = {
      idle: 'M46 92 Q60 99 74 92',
      happy: 'M46 90 Q60 101 74 90',
      drinking: 'M48 92 Q60 102 72 92',
      excited: 'M44 90 Q60 102 76 90',
      warning: 'M44 92 Q60 82 76 92',
      sad: 'M46 96 Q60 84 74 96',
      thinking: 'M46 94 Q60 90 74 94',
      listening: 'M46 92 Q60 99 74 92',
      speaking: 'M44 92 Q60 108 76 92',
      achievement: 'M46 90 Q60 104 74 90',
    };

    mouth.setAttribute('d', mouthMap[safeState] || mouthMap.idle);

    mascot.classList.remove(
      'mascot-idle',
      'mascot-bounce',
      'mascot-celebrate',
      'mascot-nudge',
      'mascot-state-transition',
      'mascot-drinking',
      'mascot-happy',
      'mascot-excited',
      'mascot-warning',
      'mascot-sad',
      'mascot-thinking',
      'mascot-listening',
      'mascot-speaking'
    );

    mascot.classList.add('mascot-state-transition');

    if (SHOW_ANIMATIONS) {
      const stateClass = {
        idle: 'mascot-idle',
        happy: 'mascot-happy',
        drinking: 'mascot-drinking',
        excited: 'mascot-excited',
        warning: 'mascot-warning',
        sad: 'mascot-sad',
        thinking: 'mascot-thinking',
        listening: 'mascot-listening',
        speaking: 'mascot-speaking',
        achievement: 'mascot-celebrate',
      }[safeState];

      if (stateClass) mascot.classList.add(stateClass);
    }

    // State-specific facial/body reactions
    if (safeState === 'warning' || safeState === 'sad') {
      mascot.style.filter = 'saturate(0.72)';
      mascot.style.transform = 'translateY(4px) rotate(-2deg)';
      shadow.style.transform = 'translateX(-50%) scale(0.88)';
    } else if (safeState === 'excited' || safeState === 'achievement') {
      mascot.style.filter = 'saturate(1.18)';
      mascot.style.transform = 'translateY(-5px) scale(1.04)';
      shadow.style.transform = 'translateX(-50%) scale(1.12)';
    } else if (safeState === 'drinking') {
      mascot.style.filter = 'saturate(1.08)';
      mascot.style.transform = 'translateY(2px) scale(0.98)';
      shadow.style.transform = 'translateX(-50%) scale(0.96)';
    } else {
      mascot.style.filter = '';
      mascot.style.transform = '';
      shadow.style.transform = 'translateX(-50%) scale(1)';
    }

    setTimeout(() => {
      mascot.classList.remove('mascot-state-transition');
    }, 260);
  }

  function initAudio() {
    if (audioReady) return;
    try { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); audioReady = true; } catch (e) { audioReady = false; }
  }

  function playBlip() {
    if (!SOUND_ENABLED || !audioReady) return;
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.type = 'sine'; o.frequency.value = 900;
    g.gain.setValueAtTime(0, audioCtx.currentTime);
    g.gain.linearRampToValueAtTime(0.12, audioCtx.currentTime + 0.01);
    g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.28);
    o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime + 0.35);
  }

  function playCelebrate() {
    if (!SOUND_ENABLED || !audioReady) return;
    const now = audioCtx.currentTime; const master = audioCtx.createGain(); master.gain.value = 0.08; master.connect(audioCtx.destination);
    const freqs = [880, 1100, 1320];
    freqs.forEach((f, i) => {
      const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
      o.type = 'triangle'; o.frequency.setValueAtTime(f, now + i * 0.06);
      g.gain.setValueAtTime(0, now + i * 0.06); g.gain.linearRampToValueAtTime(1, now + i * 0.06 + 0.01);
      g.gain.exponentialRampToValueAtTime(0.001, now + i * 0.36);
      o.connect(g); g.connect(master); o.start(now + i * 0.06); o.stop(now + i * 0.36 + i * 0.06);
    });
  }

  function burst(x, y) {
    const containerEl = document.getElementById('particles');
  const colors = ['#ffd166', '#ff6b6b', '#9ef0ff', '#6de9ff', '#5fb0ff', '#c084fc', '#ffe4a8'];
  const count = 44;
  for (let i = 0; i < count; i += 1) {
    const el = document.createElement('div');
    el.className = 'particle';
    const c = colors[Math.floor(Math.random() * colors.length)];
    el.style.background = c; el.style.left = x + 'px'; el.style.top = y + 'px';
    const size = 6 + Math.random() * 14; el.style.width = size + 'px'; el.style.height = size + 'px'; el.style.borderRadius = (Math.random() > 0.5 ? '4px' : '50%');
    containerEl.appendChild(el);
    const dx = (Math.random() - 0.5) * 280;
    const dy = (Math.random() - 1.2) * 260 - 10;
    const rot = (Math.random() - 0.5) * 720;
    const dur = 900 + Math.random() * 600;
    el.animate([
      { transform: `translate(0px, 0px) rotate(0deg) scale(0.6)`, opacity: 1 },
      { transform: `translate(${dx}px, ${dy}px) rotate(${rot}deg) scale(1)`, opacity: 0 }
    ], { duration: dur, easing: 'cubic-bezier(.2,.9,.2,1)' });
    setTimeout(() => { try { el.remove(); } catch (e) {} }, dur + 200);
  }

  // add a few star shapes
  for (let s = 0; s < 6; s += 1) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = (x + (Math.random() - 0.5) * 40) + 'px';
    star.style.top = (y + (Math.random() - 0.5) * 10) + 'px';
    star.style.background = 'radial-gradient(circle at 30% 30%, #fff, transparent 40%), linear-gradient(45deg, #ffd166, #ff6b6b)';
    star.style.borderRadius = '3px';
    star.style.width = '10px'; star.style.height = '10px';
    containerEl.appendChild(star);
    const dx2 = (Math.random() - 0.5) * 140;
    const dy2 = -60 - Math.random() * 120;
    const dur2 = 900 + Math.random() * 600;
    star.animate([
      { transform: `translate(0px, 0px) scale(0.4)`, opacity: 0 },
      { transform: `translate(${dx2}px, ${dy2}px) scale(1.1) rotate(25deg)`, opacity: 1, offset: 0.25 },
      { transform: `translate(${dx2 * 1.2}px, ${dy2 - 30}px) scale(0.8) rotate(180deg)`, opacity: 0 }
    ], { duration: dur2, easing: 'cubic-bezier(.2,.9,.2,1)' });
    setTimeout(() => { try { star.remove(); } catch (e) {} }, dur2 + 200);
  }
  }

  function happy() {
    setState('happy');
    shadow.style.transform = 'translateX(-50%) scale(1.14)';
    initAudio(); if (audioReady) playBlip();
    setTimeout(() => { setState('idle'); shadow.style.transform = 'translateX(-50%) scale(1)'; }, 520);
  }

  function celebrateNow() {
    setState('achievement');
    shadow.style.opacity = '0.75';
    const r = container.getBoundingClientRect();
    // stronger celebration: multiple bursts + stars
    burst(r.width / 2, r.height / 3);
    setTimeout(() => burst(r.width / 2 - 10, r.height / 3 + 8), 120);
    setTimeout(() => burst(r.width / 2 + 12, r.height / 3 - 6), 240);
    initAudio(); if (audioReady) playCelebrate();
    // small arms raise / body pulse
    mascot.classList.add('mascot-celebrate');
    // show celebratory banner
    const banner = document.getElementById('celebrate-banner');
    if (banner) {
      banner.classList.add('banner-show');
      banner.setAttribute('aria-hidden', 'false');
    }
    mascot.style.transition = 'transform 260ms ease';
    mascot.style.transform = 'translateY(-8px) scale(1.06)';
    shadow.style.transform = 'translateX(-50%) scale(1.22)';
    setTimeout(() => {
      mascot.style.transform = '';
      mascot.classList.remove('mascot-celebrate');
      shadow.style.transform = 'translateX(-50%) scale(1)';
      if (banner) {
        banner.classList.remove('banner-show');
        banner.setAttribute('aria-hidden', 'true');
      }
      setState('idle');
      shadow.style.opacity = '0.9';
    }, 1100);
  }

  const reducedMotion = (() => {
    try { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
  })();

  if (!reducedMotion) {
    const maxTilt = 6;
    container.addEventListener('mousemove', (ev) => {
      const r = container.getBoundingClientRect();
      const cx = r.left + r.width / 2; const cy = r.top + r.height / 2;
      const dx = (ev.clientX - cx) / (r.width / 2);
      const dy = (ev.clientY - cy) / (r.height / 2);
      const rx = Math.max(-maxTilt, Math.min(maxTilt, -dy * maxTilt));
      const ry = Math.max(-maxTilt, Math.min(maxTilt, dx * maxTilt));
      mascot.style.transform = `perspective(700px) rotateX(${rx}deg) rotateY(${ry}deg) translateZ(8px)`;
      const s = 1 + Math.abs(dx) * 0.08 + Math.abs(dy) * 0.05;
      shadow.style.transform = `translateX(-50%) scale(${s})`;
    });
    container.addEventListener('mouseleave', () => { mascot.style.transform = ''; shadow.style.transform = 'translateX(-50%) scale(1)'; });
  }

  mascot.addEventListener('click', () => happy());

  setTimeout(() => {
    try {
      initAudio();

      // IMPORTANT: use the state supplied by Python.
      // Do not reset every mascot to idle.
      if (CELEBRATE && SHOW_ANIMATIONS) {
        setTimeout(() => celebrateNow(), 160);
      } else if (LAST_LOGGED) {
        setState('drinking');
        setTimeout(() => {
          setState(INITIAL_STATE || 'idle');
        }, 650);
      } else {
        setState(INITIAL_STATE || 'idle');
      }
    } catch (e) {}
  }, 120);

  if (!reducedMotion) {
    let idleTimer = null;
    function scheduleNudge() {
      const t = 30000 + Math.random() * 30000;
      idleTimer = setTimeout(() => {
        mascot.classList.add('mascot-nudge');
        setTimeout(() => mascot.classList.remove('mascot-nudge'), 560);
        scheduleNudge();
      }, t);
    }
    scheduleNudge();
    document.addEventListener('visibilitychange', () => { if (document.hidden) clearTimeout(idleTimer); else scheduleNudge(); });
  }
})();
</script>
</body>
</html>
"""
    html = html.replace("__PRIMARY__", palette["primary"])
    html = html.replace("__SECONDARY__", palette["secondary"])
    html = html.replace("__ACCENT__", palette["accent"])
    html = html.replace("__HIGHLIGHT__", palette["highlight"])
    html = html.replace("__EYE__", palette["eye"])
    html = html.replace("__SHADOW__", palette["shadow"])
    html = html.replace("__BODY_SVG__", body_svg)
    html = html.replace("__STATE__", state_name)
    html = html.replace("__SOUND_ENABLED__", str(snd_on).lower())
    html = html.replace("__LAST_LOGGED__", str(int(last_logged)))
    html = html.replace("__CELEBRATE__", str(bool(celebrate)).lower())
    html = html.replace("__ANIMATIONS__", str(bool(show_animations)).lower())
    from .utils import render_embedded_html

    render_embedded_html(html, height=180)
