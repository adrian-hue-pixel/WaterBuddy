#!/bin/bash

set -u

PASS=0
FAIL=0
WARN=0

pass() {
    echo "  ✅ PASS — $1"
    PASS=$((PASS + 1))
}

fail() {
    echo "  ❌ FAIL — $1"
    FAIL=$((FAIL + 1))
}

warn() {
    echo "  ⚠️  WARN — $1"
    WARN=$((WARN + 1))
}

section() {
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔎 $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

check_file() {
    if [ -f "$1" ]; then
        pass "File exists: $1"
    else
        fail "Missing file: $1"
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        pass "Directory exists: $1"
    else
        fail "Missing directory: $1"
    fi
}

run_check() {
    local description="$1"
    shift

    if "$@" >/tmp/wb_test_output 2>&1; then
        pass "$description"
    else
        fail "$description"
        echo "      Output:"
        sed 's/^/      /' /tmp/wb_test_output | head -80
    fi
}

echo
echo "💧 WATER BUDDY — GOATED FULL BUG TEST"
echo "======================================"
echo "Started: $(date)"
echo

# ------------------------------------------------------------
# 0. ENVIRONMENT
# ------------------------------------------------------------

section "0. ENVIRONMENT"

if [ -d ".venv" ]; then
    pass ".venv exists"
else
    warn ".venv directory not found"
fi

if command -v python >/dev/null 2>&1; then
    pass "Python executable available"
    echo "      Python: $(python --version 2>&1)"
else
    fail "Python executable unavailable"
fi

if python -c "import streamlit" >/dev/null 2>&1; then
    pass "Streamlit import works"
    echo "      Streamlit: $(python -c 'import streamlit; print(streamlit.__version__)')"
else
    fail "Streamlit cannot be imported"
fi

# ------------------------------------------------------------
# 1. PROJECT STRUCTURE
# ------------------------------------------------------------

section "1. PROJECT STRUCTURE"

FILES=(
    "app.py"
    "components/mascot_v2.py"
    "components/reminder.py"
    "components/cards.py"
    "components/hydrate_visual.py"
    "core/navigation.py"
    "core/session_manager.py"
    "core/theme.py"
    "pages/achievements.py"
    "pages/ai_coach.py"
    "pages/analytics.py"
    "pages/dashboard.py"
    "pages/profile.py"
    "pages/settings.py"
    "pages/voice_assistant.py"
    "pages/reminder.py"
    "pages/water_scan.py"
    "pages/goals.py"
    "pages/daily_tasks.py"
    "pages/ai_hydration.py"
    "services/ai.py"
    "services/hydration.py"
    "services/mascot_service.py"
    "services/hydration_twin.py"
    "services/goal_optimizer.py"
    "services/context_engine.py"
    "services/personalization.py"
    "styles/glassmorphism.css"
)

for file in "${FILES[@]}"; do
    check_file "$file"
done

check_dir "components"
check_dir "core"
check_dir "pages"
check_dir "services"
check_dir "styles"

# ------------------------------------------------------------
# ------------------------------------------------------------
# 2. PYTHON SYNTAX
# ------------------------------------------------------------

section "2. PYTHON SYNTAX"

for f in app.py pages/*.py components/*.py core/*.py services/*.py; do
    if [ -f "$f" ]; then
        if python -m py_compile "$f" >/dev/null 2>&1; then
            pass "Python syntax OK: $f"
        else
            fail "Python syntax error: $f"
        fi
    fi
done

# 3. CRITICAL IMPORTS
# ------------------------------------------------------------

section "3. CRITICAL IMPORTS"

IMPORT_TEST='
import app
import core.navigation
import core.session_manager
import core.theme
import components.cards
import components.hydrate_visual
import components.mascot_v2
import components.reminder
import pages.dashboard
import pages.settings
import pages.achievements
import pages.ai_coach
import pages.ai_hydration
import pages.analytics
import pages.profile
import pages.voice_assistant
import pages.reminder
import pages.water_scan
import pages.goals
import pages.daily_tasks
import services.ai
import services.hydration
import services.mascot_service
import services.hydration_twin
import services.goal_optimizer
import services.context_engine
import services.personalization
print("ALL_IMPORTS_OK")
'

if python -c "$IMPORT_TEST" >/tmp/wb_imports 2>&1; then
    pass "All critical modules import successfully"
else
    fail "Critical module import failure"
    sed 's/^/      /' /tmp/wb_imports | head -100
fi

# ------------------------------------------------------------
# 4. DASHBOARD INTEGRITY
# ------------------------------------------------------------

section "4. DASHBOARD INTEGRITY"

DASH="pages/dashboard.py"

if grep -q "render_mascot" "$DASH"; then
    pass "Dashboard renders mascot"
else
    fail "Dashboard mascot rendering missing"
fi

if grep -q "render_progress_visual" "$DASH"; then
    pass "Dashboard renders hydration visual"
else
    fail "Dashboard hydration visual missing"
fi

if grep -q "get_hydration_prediction" "$DASH"; then
    pass "Hydration prediction is wired into Dashboard"
else
    fail "Hydration prediction missing from Dashboard"
fi

if grep -q "Hydration prediction" "$DASH"; then
    pass "Hydration Prediction heading exists"
else
    fail "Hydration Prediction heading missing"
fi

if grep -q "Your day so far" "$DASH"; then
    pass "\"Your day so far\" section exists"
else
    fail "\"Your day so far\" section missing"
fi

if grep -q "Gentle tip" "$DASH"; then
    pass "Gentle tip exists"
else
    fail "Gentle tip missing"
fi

if grep -q '+250 ml' "$DASH"; then
    pass "+250 ml quick-log button exists"
else
    fail "+250 ml quick-log button missing"
fi

if grep -q '+500 ml' "$DASH"; then
    pass "+500 ml quick-log button exists"
else
    fail "+500 ml quick-log button missing"
fi

if grep -q 'Reset' "$DASH"; then
    pass "Reset control exists"
else
    fail "Reset control missing"
fi

if grep -q 'custom_amount_ml' "$DASH"; then
    pass "Custom amount input exists"
else
    fail "Custom amount input missing"
fi

# Ensure the old empty spacer did NOT come back.
if grep -q 'height: 20px' "$DASH"; then
    warn "20px spacer still exists somewhere in Dashboard"
else
    pass "Old 20px mascot/prediction spacer is absent"
fi

# ------------------------------------------------------------
# 5. DASHBOARD ORDER
# ------------------------------------------------------------

section "5. DASHBOARD VISUAL ORDER"

MASCOT_LINE=$(grep -n "render_mascot(" "$DASH" | head -1 | cut -d: -f1)
PREDICTION_LINE=$(grep -n "Hydration prediction" "$DASH" | head -1 | cut -d: -f1)
DAY_LINE=$(grep -n "Your day so far" "$DASH" | head -1 | cut -d: -f1)
TIP_LINE=$(grep -n "Gentle tip" "$DASH" | head -1 | cut -d: -f1)

if [ -n "$MASCOT_LINE" ] && [ -n "$PREDICTION_LINE" ] && [ "$MASCOT_LINE" -lt "$PREDICTION_LINE" ]; then
    pass "Mascot appears before Hydration Prediction"
else
    fail "Mascot/Prediction order is incorrect"
fi

if [ -n "$PREDICTION_LINE" ] && [ -n "$DAY_LINE" ] && [ "$PREDICTION_LINE" -lt "$DAY_LINE" ]; then
    pass "Hydration Prediction appears before Your day so far"
else
    fail "Prediction/Today order is incorrect"
fi

if [ -n "$DAY_LINE" ] && [ -n "$TIP_LINE" ] && [ "$DAY_LINE" -lt "$TIP_LINE" ]; then
    pass "Your day so far appears before Gentle tip"
else
    fail "Today/Tip order is incorrect"
fi

# ------------------------------------------------------------
# 6. HYDRATION LOGIC
# ------------------------------------------------------------

section "6. HYDRATION LOGIC"

HYD="services/hydration.py"

check_file "$HYD"

if grep -q "update_daily_intake" "$HYD"; then
    pass "update_daily_intake exists"
else
    fail "update_daily_intake missing"
fi

if grep -q "reset_daily_intake" "$HYD"; then
    pass "reset_daily_intake exists"
else
    fail "reset_daily_intake missing"
fi

if grep -q "calculate_progress" "$HYD"; then
    pass "calculate_progress exists"
else
    fail "calculate_progress missing"
fi

if grep -q "get_hydration_prediction" "$HYD"; then
    pass "get_hydration_prediction exists"
else
    fail "get_hydration_prediction missing"
fi

if grep -q "get_tip" "$HYD"; then
    pass "get_tip exists"
else
    fail "get_tip missing"
fi

# ------------------------------------------------------------
# 7. MASCOT INTEGRITY
# ------------------------------------------------------------

section "7. MASCOT INTEGRITY"

MASCOT="components/mascot_v2.py"

check_file "$MASCOT"

if grep -q 'return "aqua"' "$MASCOT"; then
    pass "Mascot variant is aqua"
else
    warn "Could not confirm aqua mascot variant"
fi

if grep -q 'def _get_state' "$MASCOT"; then
    pass "Mascot state system exists"
else
    fail "Mascot state system missing"
fi

if grep -q '"celebrate"' "$MASCOT"; then
    pass "Mascot celebration state exists"
else
    fail "Mascot celebration state missing"
fi

if grep -qE '"happy_25"|"happy_50"' "$MASCOT"; then
    pass "Mascot happy states exist"
else
    fail "Mascot happy states missing"
fi

if grep -q '"thirsty"' "$MASCOT"; then
    pass "Mascot 0% state exists"
else
    fail "Mascot 0% state missing"
fi

if grep -q '<svg' "$MASCOT"; then
    pass "Mascot SVG exists"
else
    fail "Mascot SVG opening tag missing"
fi

if grep -q '</svg>' "$MASCOT"; then
    pass "Mascot SVG closing tag exists"
else
    fail "Mascot SVG closing tag missing"
fi

SVG_TEST='
from components.mascot_v2 import _mascot_svg

for state in ("idle", "happy", "celebrate"):
    svg = _mascot_svg(state)
    assert "<svg" in svg, f"{state}: opening SVG missing"
    assert "</svg>" in svg, f"{state}: closing SVG missing"
    assert svg.count("<svg") == 1, f"{state}: multiple SVG roots"
    assert svg.count("</svg>") == 1, f"{state}: multiple SVG closings"
    assert len(svg) > 1000, f"{state}: SVG unexpectedly tiny"
print("MASCOT_SVG_OK")
'

if python -c "$SVG_TEST" >/tmp/wb_mascot 2>&1; then
    pass "Idle/happy/celebrate mascot SVGs are structurally valid"
else
    fail "Mascot SVG structural test failed"
    sed 's/^/      /' /tmp/wb_mascot
fi

# ------------------------------------------------------------
# 8. MASCOT DEBUG LEFTOVERS
# ------------------------------------------------------------

section "8. DEBUG / TEST LEFTOVERS"

DEBUG_MATCHES=$(grep -RniE \
    "MASCOT RENDER TEST|MASCOT REMINDER TEST|Trigger celebration \(dev\)|WB_MASCOT_DEBUG|DBG: state=" \
    components pages app.py core services \
    --exclude-dir=__pycache__ 2>/dev/null || true)

if [ -z "$DEBUG_MATCHES" ]; then
    pass "No known mascot debug/test leftovers found"
else
    warn "Debug/test instrumentation still exists:"
    echo "$DEBUG_MATCHES" | sed 's/^/      /'
fi

# ------------------------------------------------------------
# 9. ACHIEVEMENTS
# ------------------------------------------------------------

section "9. ACHIEVEMENTS"

ACH="pages/achievements.py"

REQUIRED_ACHIEVEMENTS=(
    "first_sip"
    "500ml"
    "1000ml"
    "halfway"
    "75percent"
    "goal"
    "125percent"
    "2day"
    "3day"
    "7day"
    "14day"
    "30day"
    "50day"
    "75day"
    "100day"
    "150day"
    "182day"
    "250day"
    "365day"
    "early_bird"
    "night_owl"
    "comeback"
    "perfect_week"
    "perfect_month"
)

for achievement in "${REQUIRED_ACHIEVEMENTS[@]}"; do
    if grep -q "\"$achievement\"" "$ACH"; then
        pass "Achievement exists: $achievement"
    else
        fail "Achievement missing: $achievement"
    fi
done

# ------------------------------------------------------------
# 10. THEMES
# ------------------------------------------------------------

section "10. THEMES"

THEME="core/theme.py"
SETTINGS="pages/settings.py"
SESSION="core/session_manager.py"

THEMES=(
    "water"
    "sun"
    "green"
    "neon"
    "yin_yang"
)

for theme in "${THEMES[@]}"; do
    if grep -q "\"$theme\"" "$THEME"; then
        pass "Theme exists in theme system: $theme"
    else
        fail "Theme missing from theme system: $theme"
    fi

    if grep -q "\"$theme\"" "$SETTINGS"; then
        pass "Theme exists in Settings: $theme"
    else
        fail "Theme missing from Settings: $theme"
    fi

    if grep -q "\"$theme\"" "$SESSION"; then
        pass "Theme exists in session system: $theme"
    else
        fail "Theme missing from session system: $theme"
    fi
done

if grep -q 'dark_mode' "$SETTINGS"; then
    pass "Light/Dark mode control exists in Settings"
else
    fail "Light/Dark mode control missing from Settings"
fi

if grep -q 'selected_mode == "Dark"' "$SETTINGS"; then
    pass "Settings saves Dark/Light mode state"
else
    warn "Could not confirm Dark/Light save logic"
fi

# ------------------------------------------------------------
# 11. GREEN LIGHT PALETTE
# ------------------------------------------------------------

section "11. GREEN LIGHT THEME"

if grep -q '#effaf4' "$THEME"; then
    pass "Green Light background #effaf4 exists"
else
    warn "Green Light background #effaf4 not found"
fi

if grep -q '#dcf4e6' "$THEME"; then
    pass "Green Light background-end #dcf4e6 exists"
else
    warn "Green Light background-end #dcf4e6 not found"
fi

# ------------------------------------------------------------
# 12. NAVIGATION
# ------------------------------------------------------------

section "12. NAVIGATION"

NAV="core/navigation.py"

NAV_ITEMS=(
    "Dashboard"
    "Analytics"
    "AI Coach"
    "AI Hydration"
    "Voice Assistant"
    "Water Scan"
    "Daily Tasks"
    "Achievements"
    "Profile"
    "Reminder"
    "Settings"
)

if grep -q "render_ai_hydration_page" "$NAV"; then
    pass "AI Hydration page is registered"
else
    fail "AI Hydration page registration missing"
fi

for item in "${NAV_ITEMS[@]}"; do
    if grep -qi "$item" "$NAV"; then
        pass "Navigation contains: $item"
    else
        fail "Navigation missing: $item"
    fi
done

# ------------------------------------------------------------
# 13. AI HYDRATION PAGE
# ------------------------------------------------------------

section "13. AI HYDRATION PAGE"

AIH="pages/ai_hydration.py"

AI_SYSTEMS=(
    "Smart Hydration Autopilot"
    "Hydration Digital Twin"
    "AI Goal Optimizer"
    "WaterBuddy Context Engine"
)

for system in "${AI_SYSTEMS[@]}"; do
    if grep -q "$system" "$AIH"; then
        pass "AI Hydration contains: $system"
    else
        fail "AI Hydration missing: $system"
    fi
done

# ------------------------------------------------------------
# 14. AI SERVICES
# ------------------------------------------------------------

section "14. AI SERVICE WIRING"

SERVICES=(
    "services/ai.py"
    "services/hydration_twin.py"
    "services/goal_optimizer.py"
    "services/context_engine.py"
    "services/mascot_service.py"
)

for service in "${SERVICES[@]}"; do
    check_file "$service"
done

if grep -q "get_hydration_autopilot" "services/ai.py"; then
    pass "Hydration Autopilot service exists"
else
    fail "Hydration Autopilot service missing"
fi

if grep -q "get_hydration_twin" "services/hydration_twin.py"; then
    pass "Hydration Digital Twin service exists"
else
    fail "Hydration Digital Twin service missing"
fi

if grep -q "get_goal_optimizer_summary" "services/goal_optimizer.py"; then
    pass "Goal Optimizer service exists"
else
    fail "Goal Optimizer service missing"
fi

if grep -q "get_context_snapshot" "services/context_engine.py"; then
    pass "Context Engine service exists"
else
    fail "Context Engine service missing"
fi

# ------------------------------------------------------------
# 15. REMINDER
# ------------------------------------------------------------

section "15. REMINDER"

REM="components/reminder.py"

if grep -q "reminder_enabled" "$REM"; then
    pass "Reminder enabled state exists"
else
    fail "Reminder enabled state missing"
fi

if grep -q "reminder_minutes" "$REM"; then
    pass "Reminder interval state exists"
else
    fail "Reminder interval state missing"
fi

if grep -q "def render_reminder" "$REM"; then
    pass "Reminder renderer exists"
else
    fail "Reminder renderer missing"
fi

if grep -q "pages/reminder.py" <(printf '%s\n' "${FILES[@]}"); then
    pass "Reminder page exists in project"
else
    fail "Reminder page missing from project list"
fi

# ------------------------------------------------------------
# 16. WATER SCAN
# ------------------------------------------------------------

section "16. WATER SCAN"

SCAN="pages/water_scan.py"

check_file "$SCAN"

if grep -qi "camera" "$SCAN"; then
    pass "Water Scan camera flow exists"
else
    warn "Camera keyword not found in Water Scan"
fi

# ------------------------------------------------------------
# 17. GLASSMORPHISM CSS
# ------------------------------------------------------------

section "17. PREMIUM CSS"

CSS="styles/glassmorphism.css"

check_file "$CSS"

CSS_CLASSES=(
    "glass-card"
    "wb-section-kicker"
    "wb-section-title"
    "wb-prediction-header"
    "wb-forecast-panel"
    "wb-live-pill"
    "bottle-shell"
    "bottle-fill"
)

for class in "${CSS_CLASSES[@]}"; do
    if grep -q "\\.$class" "$CSS"; then
        pass "CSS class exists: .$class"
    else
        warn "CSS class missing: .$class"
    fi
done

# ------------------------------------------------------------
# 18. BROKEN MARKUP / OBVIOUS CODE DAMAGE
# ------------------------------------------------------------

section "18. OBVIOUS CODE DAMAGE SCAN"

# Unmatched obvious Python artifact.
if grep -RniE '^[[:space:]]*,[[:space:]]*$' \
    pages components core services \
    --include='*.py' \
    --exclude-dir=__pycache__ >/tmp/wb_commas 2>/dev/null; then

    warn "Suspicious standalone comma lines found:"
    sed 's/^/      /' /tmp/wb_commas | head -50
else
    pass "No suspicious standalone comma lines"
fi

# Merge-conflict markers.
if grep -RniE '^(<<<<<<<|=======|>>>>>>>)' \
    . \
    --exclude-dir=.git \
    --exclude-dir=.venv \
    --exclude-dir=__pycache__ >/tmp/wb_conflicts 2>/dev/null; then

    fail "Git merge-conflict markers detected"
    sed 's/^/      /' /tmp/wb_conflicts | head -50
else
    pass "No Git merge-conflict markers"
fi

# ------------------------------------------------------------
# 19. PYTEST
# ------------------------------------------------------------

section "19. PYTEST"
if python -m pytest --version >/dev/null 2>&1; then
    if python -m pytest -q; then
        pass "Pytest suite passed"
    else
        fail "Pytest suite has failures"
    fi
else
    warn "pytest is not installed"
fi

# ------------------------------------------------------------
# 20. STREAMLIT BOOT TEST
# ------------------------------------------------------------

section "20. STREAMLIT BOOT TEST"

LOG="/tmp/waterbuddy_streamlit.log"
PID=""

rm -f "$LOG"

python -m streamlit run app.py \
    --server.headless true \
    --server.port 8501 \
    --browser.gatherUsageStats false \
    >"$LOG" 2>&1 &

PID=$!

echo "      Streamlit PID: $PID"

sleep 6

if kill -0 "$PID" 2>/dev/null; then
    pass "Streamlit process stayed alive after startup"
else
    fail "Streamlit process died during startup"
fi

# ------------------------------------------------------------
# 21. HTTP HEALTH CHECK
# ------------------------------------------------------------

section "21. HTTP HEALTH CHECK"

HTTP_OK=0

for i in $(seq 1 10); do
    if curl -fsS http://localhost:8501/ >/tmp/wb_http 2>/dev/null; then
        HTTP_OK=1
        break
    fi
    sleep 1
done

if [ "$HTTP_OK" -eq 1 ]; then
    pass "Streamlit HTTP endpoint responds"
else
    fail "Streamlit HTTP endpoint did not respond"
fi

if [ -f "$LOG" ]; then
    if grep -qiE "Traceback|Exception|SyntaxError|IndentationError" "$LOG"; then
        fail "Streamlit startup log contains Python error"
        grep -iE "Traceback|Exception|SyntaxError|IndentationError" "$LOG" \
            | tail -30 \
            | sed 's/^/      /'
    else
        pass "No obvious Python exception in Streamlit startup log"
    fi
fi

# ------------------------------------------------------------
# 22. CLEANUP STREAMLIT
# ------------------------------------------------------------

section "22. CLEANUP"

if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    sleep 1

    if kill -0 "$PID" 2>/dev/null; then
        kill -9 "$PID" 2>/dev/null || true
    fi

    pass "Stopped temporary Streamlit test server"
else
    pass "No Streamlit process needed cleanup"
fi

# ------------------------------------------------------------
# 23. GIT SAFETY CHECK
# ------------------------------------------------------------

section "23. GIT SAFETY"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    pass "Git repository detected"

    echo
    echo "      Current branch:"
    git branch --show-current | sed 's/^/        /'

    echo
    echo "      Working tree:"
    git status --short | sed 's/^/        /'

    if git diff --quiet; then
        echo "      No unstaged content changes."
    else
        echo "      Local changes exist — expected during development."
    fi

    echo
    echo "      Latest local commit:"
    git log -1 --oneline | sed 's/^/        /'

    echo
    echo "      🚫 No git push command was executed."
else
    warn "Not inside a Git repository"
fi

# ------------------------------------------------------------
# FINAL REPORT
# ------------------------------------------------------------

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏁 GOATED TEST COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  ✅ Passed : $PASS"
echo "  ❌ Failed : $FAIL"
echo "  ⚠️  Warnings: $WARN"
echo

if [ "$FAIL" -eq 0 ]; then
    echo "🔥 RESULT: NO AUTOMATED FAILURES DETECTED."
    echo "💧 Water Buddy survived the machine-level bug hunt."
    echo
    echo "⚠️  Manual UI testing is still required for visual/layout bugs."
    exit 0
else
    echo "🚨 RESULT: FAILURES DETECTED."
    echo "Fix the ❌ items above before considering the build clean."
    exit 1
fi
