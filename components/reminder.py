from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def render_reminder() -> None:
    enabled = bool(st.session_state.get("reminder_enabled", False))
    minutes = int(st.session_state.get("reminder_minutes", 60))

    if not enabled:
        return

    milliseconds = max(minutes, 1) * 60 * 1000

    components.html(
        f"""
        <script>
        (() => {{
            const INTERVAL = {milliseconds};
            const KEY = "waterbuddy_next_reminder";
            const now = Date.now();

            let next = Number(localStorage.getItem(KEY) || 0);

            if (!next || next <= now) {{
                next = now + INTERVAL;
                localStorage.setItem(KEY, String(next));
            }}

            const wait = Math.max(next - Date.now(), 1000);

            setTimeout(() => {{
                try {{
                    if ("Notification" in window) {{
                        if (Notification.permission === "granted") {{
                            new Notification("💧 WaterBuddy", {{
                                body: "Time for a water break! Drink some water.",
                            }});
                        }} else if (Notification.permission !== "denied") {{
                            Notification.requestPermission();
                        }}
                    }}
                }} catch (e) {{}}

                try {{
                    const AudioContext =
                        window.AudioContext || window.webkitAudioContext;

                    if (AudioContext) {{
                        const ctx = new AudioContext();
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();

                        osc.frequency.value = 880;
                        gain.gain.value = 0.08;

                        osc.connect(gain);
                        gain.connect(ctx.destination);

                        osc.start();
                        osc.stop(ctx.currentTime + 0.45);
                    }}
                }} catch (e) {{}}

                localStorage.setItem(
                    KEY,
                    String(Date.now() + INTERVAL)
                );
            }}, wait);
        }})();
        </script>
        """,
        height=0,
    )
