from __future__ import annotations

import hashlib

import streamlit as st
from datetime import date

from components.cards import render_hero_banner
from core.session_manager import safe_rerun
from services.weather import fetch_weather
from services.voice import VoiceService
from services.mascot_service import get_mascot_service


st.html("""
<style>
/* =========================================================
   WaterBuddy Voice Assistant — premium UI
   Functionality intentionally untouched.
   ========================================================= */

.voice-section {
    margin: 26px 0 12px;
}

.voice-section-label {
    color: #38bdf8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.voice-section-title {
    color: #f5fbff;
    font-family: "Manrope", "DM Sans", sans-serif;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -.025em;
    margin: 0;
}

/* Main informational panels */
[data-testid="stAlert"] {
    border-radius: 18px !important;
    border: 1px solid rgba(56,189,248,.12) !important;
    background:
        linear-gradient(
            135deg,
            rgba(10,28,43,.86),
            rgba(5,14,23,.92)
        ) !important;
    box-shadow:
        0 14px 38px rgba(0,0,0,.18),
        inset 0 1px 0 rgba(255,255,255,.025) !important;
}

/* Microphone recorder */
[data-testid="stAudioInput"] {
    margin: 12px 0 20px;
}

[data-testid="stAudioInput"] > div {
    border-radius: 22px !important;
    border: 1px solid rgba(56,189,248,.16) !important;
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(56,189,248,.055),
            transparent 55%
        ),
        rgba(7,19,30,.84) !important;
    box-shadow:
        0 18px 45px rgba(0,0,0,.22),
        inset 0 1px 0 rgba(255,255,255,.025) !important;
    padding: 8px !important;
}

/* Buttons */
.stButton > button {
    min-height: 44px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(56,189,248,.18) !important;
    background:
        linear-gradient(
            135deg,
            rgba(17,48,66,.92),
            rgba(7,24,37,.96)
        ) !important;
    color: #eafaff !important;
    font-weight: 700 !important;
    box-shadow:
        0 10px 26px rgba(0,0,0,.18),
        inset 0 1px 0 rgba(255,255,255,.025) !important;
    transition: all .18s ease !important;
}

.stButton > button:hover {
    border-color: rgba(56,189,248,.40) !important;
    background:
        linear-gradient(
            135deg,
            rgba(21,61,82,.96),
            rgba(8,29,44,.98)
        ) !important;
    box-shadow:
        0 12px 30px rgba(0,0,0,.24),
        0 0 24px rgba(56,189,248,.08) !important;
    transform: translateY(-1px);
}

/* Text fallback */
[data-testid="stTextInput"] > div {
    border-radius: 16px !important;
    background: rgba(7,19,30,.82) !important;
    border-color: rgba(56,189,248,.14) !important;
}

/* Audio player */
[data-testid="stAudio"] {
    margin: 12px 0 18px;
    padding: 10px;
    border-radius: 18px;
    background: rgba(7,19,30,.72);
    border: 1px solid rgba(56,189,248,.10);
}

/* Divider */
hr {
    border-color: rgba(255,255,255,.055) !important;
}

/* Section spacing */
.stMarkdown {
    margin-bottom: 4px;
}

/* Mobile */
@media (max-width: 640px) {
    .voice-section-title {
        font-size: 19px;
    }

    [data-testid="stAudioInput"] > div {
        border-radius: 18px !important;
    }

    .stButton > button {
        min-height: 42px !important;
    }
}
</style>
""")





def _reset_voice_state() -> None:
    for key in [
        "voice_audio_bytes",
        "voice_audio_id",
        "voice_audio_transcription_id",
        "voice_ready_for_ai",
        "voice_transcription",
        "voice_response_text",
        "voice_audio_output_bytes",
        "voice_audio_output_mime",
        "voice_error",
        "voice_player_key",
    ]:
        if key in st.session_state:
            del st.session_state[key]


def render_voice_assistant_page() -> None:
    render_hero_banner(
        "Voice Assistant",
        "Press the microphone, speak naturally, and hear WaterBuddy reply out loud.",
    )

    def _safe_rerun() -> None:
        """Delegate to the central safe_rerun helper."""
        st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()

    # Monkey-patch WaveSurfer (if present) to avoid "Container not found" errors
    # This guards third-party waveform initialization (used by some Streamlit audio widgets)
    # by ensuring the target container exists before WaveSurfer creates a player.
    st.markdown(
        """
        <script>
        (function(){
            try {
                if (window.WaveSurfer && typeof window.WaveSurfer.create === 'function') {
                    const origCreate = window.WaveSurfer.create;
                    window.WaveSurfer.create = function(opts) {
                        try {
                            const container = opts && opts.container;
                            if (!container) {
                                console.warn('WaveSurfer.create called without container; skipping creation');
                                return null;
                            }
                            // If container is a selector, verify element exists
                            if (typeof container === 'string') {
                                if (!document.querySelector(container)) {
                                    console.warn('WaveSurfer container not found: ' + container);
                                    return null;
                                }
                            } else if (container && container.nodeType && container.nodeType === 1) {
                                // DOM node provided - OK
                            } else if (container && container.current) {
                                // React ref-like object
                                if (!document.contains(container.current)) {
                                    console.warn('WaveSurfer container node not in document');
                                    return null;
                                }
                            }
                            return origCreate.call(this, opts);
                        } catch (err) {
                            console.warn('WaveSurfer.create wrapper error:', err);
                            return null;
                        }
                    };
                }
            } catch (e) {
                // best-effort guard; do not interrupt page render
                console.warn('WaveSurfer guard initialization failed', e);
            }
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "🎙️ Voice Assistant is powered by OpenRouter. Ask WaterBuddy anything about hydration."
    )

    st.html("""
    <div style="
        margin: 18px 0 22px;
        padding: 20px 22px;
        border-radius: 20px;
        border: 1px solid rgba(56,189,248,.10);
        background: linear-gradient(135deg, rgba(9,25,39,.78), rgba(5,14,23,.88));
        box-shadow: 0 14px 38px rgba(0,0,0,.16);
    ">
        <div style="
            color:#38bdf8;
            font-size:10px;
            font-weight:800;
            letter-spacing:.16em;
            text-transform:uppercase;
            margin-bottom:7px;
        ">How it works</div>

        <div style="
            color:#f5fbff;
            font-size:16px;
            font-weight:750;
            margin-bottom:6px;
        ">Speak naturally to WaterBuddy.</div>

        <div style="
            color:#718696;
            font-size:13px;
            line-height:1.6;
        ">
            Your voice is transcribed, sent to the AI coach, and returned as spoken audio.
        </div>
    </div>
    """)

    # Weather integration removed — no city/units inputs shown.
    weather_city = None
    weather_units = None
    st.markdown("---")

    try:
        audio_input = st.audio_input(
                "Tap the microphone to record a question",
                sample_rate=16000,
                )
    except Exception as exc:  # pragma: no cover - browser may not support audio input widget
        st.error(
            "Microphone input is unavailable in this browser. Please allow microphone access, try a supported browser, or refresh the page."
        )
        audio_input = None

    if audio_input is not None:
        try:
            audio_bytes = audio_input.read()
        except Exception as exc:  # pragma: no cover - fallback for unexpected uploaded file behavior
            st.error(
                "There was a problem reading the recorded audio. Please try again, and ensure your browser has microphone permission."
            )
            audio_bytes = b""
        if not audio_bytes:
            st.warning("The recording was empty. Please speak clearly and try again.")
        else:
            audio_id = hashlib.sha256(audio_bytes).hexdigest()
            if st.session_state.get("voice_audio_id") != audio_id:
                st.session_state["voice_audio_id"] = audio_id
                st.session_state["voice_audio_bytes"] = audio_bytes
                st.session_state["voice_audio_transcription_id"] = None
                st.session_state["voice_ready_for_ai"] = False
                st.session_state["voice_transcription"] = ""
                st.session_state["voice_response_text"] = ""
                st.session_state["voice_audio_output_bytes"] = b""
                st.session_state["voice_audio_output_mime"] = ""
                st.session_state["voice_error"] = ""
                st.session_state["voice_player_key"] = 0

    if not st.session_state.get("voice_audio_bytes"):
        if audio_input is None:
            st.error(
                "Microphone input is unavailable in this browser. Please allow microphone access, try a supported browser, or use the typed fallback below."
            )
            typed_question = st.text_input("Or type your hydration question", key="voice_typed_question")
            if typed_question and st.button("Send typed question to WaterBuddy"):
                st.session_state["voice_transcription"] = typed_question.strip()
                st.session_state["voice_ready_for_ai"] = True
        else:
            st.info(
                "Press the microphone and speak. When you are finished, stop recording and then transcribe your speech."
            )

    ms = get_mascot_service()
    if st.session_state.get("voice_audio_bytes") and not st.session_state.get("voice_transcription"):
        st.info("Recording received. Ready to transcribe.")
        if st.button("Transcribe recording"):
            with st.spinner("Transcribing..."):
                try:
                    # user tapped to transcribe — show listening/thinking feedback
                    ms.trigger_event('voice_listening')
                    voice_service = VoiceService()
                    ms.trigger_event('ai_thinking')
                    transcript = voice_service.transcribe_audio(st.session_state["voice_audio_bytes"])
                    st.session_state["voice_transcription"] = transcript
                    st.session_state["voice_audio_transcription_id"] = st.session_state["voice_audio_id"]
                    st.session_state["voice_ready_for_ai"] = True
                    st.session_state["voice_error"] = ""
                except Exception as exc:
                    st.session_state["voice_error"] = str(exc)

    if st.session_state.get("voice_transcription"):
        st.html("""
        <div class="voice-section">
            <div class="voice-section-label">Transcript</div>
            <div class="voice-section-title">What I heard</div>
        </div>
        """)
        st.info(st.session_state["voice_transcription"])

    if st.session_state.get("voice_ready_for_ai") and not st.session_state.get("voice_response_text"):
        # If a rate-limit cooldown is active, show a friendly message and avoid sending requests
        import time
        retry_until = st.session_state.get("ai_retry_until")
        now = time.time()
        if retry_until and retry_until > now:
            remaining = int(retry_until - now)
            st.warning(f"AI service is rate-limited. Please try again in {remaining} seconds.")
        else:
            if st.button("Send to WaterBuddy"):
                ms = get_mascot_service()
                ms.trigger_event('ai_thinking')
                with st.spinner("Thinking..."):
                    try:
                        voice_service = VoiceService()
                        response_text, audio_output, output_mime = voice_service.create_audio_response(
                            st.session_state["voice_transcription"],
                            st.session_state.get("profile_name", "friend"),
                            int(st.session_state.get("daily_intake_ml", 0)),
                            int(st.session_state.get("goal_ml", 2500)),
                            "",
                        )
                        # AI produced response and TTS audio
                        ms.trigger_event('ai_speaking')
                        ms.show_message(response_text, context='voice')
                        st.session_state["voice_response_text"] = response_text
                        st.session_state["voice_audio_output_bytes"] = audio_output
                        st.session_state["voice_audio_output_mime"] = output_mime
                        st.session_state["voice_audio_output_size"] = len(audio_output) if audio_output else 0
                        st.session_state["voice_error"] = ""
                        st.session_state["voice_ready_for_ai"] = False
                        # Technical info for debugging (no raw audio or keys)
                        st.info(f"Audio generated: {st.session_state['voice_audio_output_size']} bytes, format={output_mime}")
                    except Exception as exc:
                        # Handle API rate limit specially (provide friendly fallback and TTS)
                        from services.ai import ApiRateLimitError
                        from services.tts import TextToSpeechService

                        if isinstance(exc, ApiRateLimitError):
                            retry = exc.retry_seconds or 60
                            st.session_state["ai_retry_until"] = time.time() + retry
                            canned = (
                                "I’m temporarily unable to access my AI coach because of usage limits. "
                                f"Please try again in about {retry} seconds. In the meantime, keep taking small sips — you’re doing great!"
                            )
                            try:
                                tts = TextToSpeechService()
                                audio_bytes, mime = tts.synthesize(canned)
                            except Exception:
                                audio_bytes, mime = b"", ""
                            st.session_state["voice_response_text"] = canned
                            st.session_state["voice_audio_output_bytes"] = audio_bytes
                            st.session_state["voice_audio_output_mime"] = mime
                            st.session_state["voice_audio_output_size"] = len(audio_bytes) if audio_bytes else 0
                        else:
                            st.session_state["voice_error"] = str(exc)

    if st.session_state.get("voice_error"):
        st.error(st.session_state["voice_error"])

    if st.session_state.get("voice_response_text"):
        st.html("""
        <div class="voice-section">
            <div class="voice-section-label">AI response</div>
            <div class="voice-section-title">WaterBuddy says</div>
        </div>
        """)
        st.success(st.session_state["voice_response_text"])

    if st.session_state.get("voice_audio_output_bytes"):
        st.html("""
        <div class="voice-section">
            <div class="voice-section-label">Voice playback</div>
            <div class="voice-section-title">Audio response</div>
        </div>
        """)
        cols = st.columns([1, 1, 1, 4])
        replay = cols[0].button("Replay")
        reset = cols[1].button("Reset")
        cols[2].markdown("&nbsp;")
        if replay:
            st.session_state["voice_player_key"] = st.session_state.get("voice_player_key", 0) + 1
        if reset:
            _reset_voice_state()
            st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()

        # Optional debug panel to help diagnose playback issues
        debug_mode = st.checkbox("Enable voice debug info", key="voice_debug_toggle")
        if debug_mode:
            from core.config import get_setting
            gemini_present = bool(get_setting("GEMINI_API_KEY", ""))
            st.write({
                "transcription_present": bool(st.session_state.get("voice_transcription")),
                "transcription": st.session_state.get("voice_transcription", ""),
                "ai_response_length": len(st.session_state.get("voice_response_text", "")),
                "audio_bytes_size": st.session_state.get("voice_audio_output_size", 0),
                "audio_mime": st.session_state.get("voice_audio_output_mime", ""),
                "gemini_key_present": gemini_present,
            })

        # Streamlit accepts file-like objects for audio; wrap bytes in BytesIO to be safe
        import io
        audio_bytes = st.session_state.get("voice_audio_output_bytes")
        if audio_bytes:
            audio_stream = io.BytesIO(audio_bytes)
            try:
                st.info("Audio response is ready. Press play to listen to WaterBuddy.")
                # Use a dedicated container so re-renders reliably replace the audio element
                audio_container = st.empty()
                audio_container.audio(audio_stream, format=st.session_state.get("voice_audio_output_mime", "audio/mpeg"))

                # Download button to let developers verify the generated audio file
                st.download_button(
                    "Download audio",
                    data=audio_bytes,
                    file_name="waterbuddy_response.mp3",
                    mime=st.session_state.get("voice_audio_output_mime", "audio/mpeg"),
                )
            except Exception as exc:
                st.error(f"There was a problem playing the generated audio: {exc}")
        else:
            st.error("No audio data available to play.")


def _build_weather_summary(city: str, units: str) -> str:
    return "Weather data disabled"
