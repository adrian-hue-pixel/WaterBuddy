from __future__ import annotations

import streamlit as st


def render_progress_visual(percent: int, intake_ml: int, goal_ml: int, celebrate: bool = False) -> None:
    fill_height = max(6, min(percent, 100))
    celebration_class = " celebrate" if celebrate else ""
    html = """
        <div class="bottle-shell{celebration_class}">
            <div class="bottle-fill" style="height: <<FILL>>%;">
                <div class="wave" aria-hidden="true"></div>
            </div>
            <div class="bottle-label"><<INTAKE>> ml / <<GOAL>> ml</div>
        </div>
        <script>
        (function(){
            try {
                if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
                const shell = document.querySelector('.bottle-shell');
                if (!shell) return;
                const maxTilt = 6; // degrees
                function onMove(e){
                    const r = shell.getBoundingClientRect();
                    const cx = r.left + r.width/2; const cy = r.top + r.height/2;
                    const dx = (e.clientX - cx) / (r.width/2);
                    const dy = (e.clientY - cy) / (r.height/2);
                    const rx = Math.max(-maxTilt, Math.min(maxTilt, -dy * maxTilt));
                    const ry = Math.max(-maxTilt, Math.min(maxTilt, dx * maxTilt));
                    shell.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg)`;
                }
                function onLeave(){ shell.style.transform = ''; }
                shell.addEventListener('mousemove', onMove);
                shell.addEventListener('mouseleave', onLeave);
            } catch(e){}
        })();
        </script>
        """
    html = html.replace('<<FILL>>', str(fill_height)).replace('<<INTAKE>>', str(intake_ml)).replace('<<GOAL>>', str(goal_ml)).replace('{celebration_class}', celebration_class)
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(
        f"<div class='progress-caption'><span>Progress {percent}%</span></div>",
        unsafe_allow_html=True,
    )
