from pathlib import Path
import ast
import importlib
import sys
import traceback

ROOT = Path(__file__).resolve().parent

passed = 0
failed = 0
warnings = 0

def ok(msg):
    global passed
    passed += 1
    print(f"✅ {msg}")

def fail(msg):
    global failed
    failed += 1
    print(f"❌ {msg}")

def warn(msg):
    global warnings
    warnings += 1
    print(f"⚠️  {msg}")

def section(msg):
    print("\n" + "=" * 65)
    print(msg)
    print("=" * 65)

# ============================================================
section("1. PROJECT STRUCTURE")

required = [
    "app.py",
    "core/theme.py",
    "core/navigation.py",
    "core/session_manager.py",
    "services/hydration.py",
    "services/ai.py",
    "services/mascot_service.py",
    "components/mascot_v2.py",
    "components/reminder.py",
    "pages/dashboard.py",
    "pages/analytics.py",
    "pages/achievements.py",
    "pages/profile.py",
    "pages/settings.py",
    "pages/ai_coach.py",
    "pages/voice_assistant.py",
    "styles/glassmorphism.css",
    ".streamlit/config.toml",
]

for item in required:
    if (ROOT / item).exists():
        ok(f"Exists: {item}")
    else:
        fail(f"Missing: {item}")

# ============================================================
section("2. PYTHON SYNTAX")

py_files = list(ROOT.rglob("*.py"))

for path in py_files:
    if any(x in path.parts for x in [".git", ".venv", "venv", "__pycache__"]):
        continue

    try:
        ast.parse(path.read_text())
        ok(f"Syntax: {path.relative_to(ROOT)}")
    except Exception as e:
        fail(f"Syntax error: {path.relative_to(ROOT)} -> {e}")

# ============================================================
section("3. IMPORT TESTS")

modules = [
    "core.theme",
    "core.navigation",
    "core.session_manager",
    "services.hydration",
    "services.ai",
    "services.mascot_service",
    "components.mascot_v2",
    "components.reminder",
    "pages.dashboard",
    "pages.analytics",
    "pages.achievements",
    "pages.profile",
    "pages.settings",
    "pages.ai_coach",
    "pages.voice_assistant",
]

for module in modules:
    try:
        importlib.import_module(module)
        ok(f"Import: {module}")
    except Exception as e:
        fail(f"Import FAILED: {module} -> {type(e).__name__}: {e}")

# ============================================================
section("4. NAVIGATION")

try:
    from core.navigation import get_navigation_pages

    pages = get_navigation_pages()

    expected = {
        "Dashboard",
        "Analytics",
        "AI Coach",
        "Voice Assistant",
        "Achievements",
        "Profile",
        "Settings",
    }

    actual = set(pages.keys())

    if actual == expected:
        ok("Navigation contains exactly the expected pages")
    else:
        fail(f"Navigation mismatch. Found: {sorted(actual)}")

    if "Hydration" not in actual:
        ok("Hydration tab successfully removed")
    else:
        fail("Hydration tab STILL exists")

except Exception as e:
    fail(f"Navigation test crashed: {e}")

# ============================================================
section("5. THEME SYSTEM")

try:
    from core.theme import THEMES

    expected_themes = {
        "water",
        "green",
        "neon",
        "yin_yang",
    }

    for theme in expected_themes:
        if theme in THEMES:
            ok(f"Theme exists: {theme}")
        else:
            fail(f"Missing theme: {theme}")

except Exception as e:
    fail(f"Theme test crashed: {e}")

# Search source for dangerous light-mode fallbacks
for filename in [
    "app.py",
    "core/theme.py",
    "core/session_manager.py",
    "pages/settings.py",
]:
    path = ROOT / filename

    if path.exists():
        text = path.read_text()

        if 'get("dark_mode", False)' in text:
            warn(f"{filename} still contains a False dark-mode fallback")

        if "dark_mode\"] = False" in text:
            # False can legitimately be used when switching modes,
            # so only warn rather than fail.
            warn(f"{filename} contains an explicit dark_mode=False assignment")

# ============================================================
section("6. ACHIEVEMENTS")

try:
    from pages.achievements import ACHIEVEMENTS

    if len(ACHIEVEMENTS) >= 15:
        ok(f"Achievement variety: {len(ACHIEVEMENTS)} achievements")
    else:
        warn(f"Only {len(ACHIEVEMENTS)} achievements found")

    ids = [x[0] for x in ACHIEVEMENTS]

    if len(ids) == len(set(ids)):
        ok("Achievement IDs are unique")
    else:
        fail("Duplicate achievement IDs detected")

    names = [x[1] for x in ACHIEVEMENTS]

    if len(names) == len(set(names)):
        ok("Achievement names are unique")
    else:
        fail("Duplicate achievement names detected")

    required_achievements = [
        "365day",
        "182day",
        "250day",
        "150day",
    ]

    for achievement in required_achievements:
        if achievement in ids:
            ok(f"Achievement exists: {achievement}")
        else:
            warn(f"Expected achievement missing: {achievement}")

except Exception as e:
    fail(f"Achievement test crashed: {e}")

# ============================================================
section("7. ACHIEVEMENT CELEBRATION WIRING")

checks = {
    "services/hydration.py": [
        "_new_achievements",
        "achievement_unlocked",
    ],
    "pages/dashboard.py": [
        "_new_achievements",
        "Achievement unlocked",
        "confetti",
    ],
    "components/mascot_v2.py": [
        "achievement_unlocked",
        "CELEBRATE",
    ],
}

for filename, needles in checks.items():
    path = ROOT / filename

    if not path.exists():
        fail(f"Missing: {filename}")
        continue

    text = path.read_text()

    for needle in needles:
        if needle in text:
            ok(f"{filename}: {needle}")
        else:
            fail(f"{filename}: missing {needle}")

# ============================================================
section("8. MASCOT ANIMATION")

path = ROOT / "components/mascot_v2.py"

if path.exists():
    text = path.read_text()

    for needle in [
        "show_animations",
        "SHOW_ANIMATIONS",
        "mascot-idle",
        "CELEBRATE",
    ]:
        if needle in text:
            ok(f"Mascot supports: {needle}")
        else:
            fail(f"Mascot missing: {needle}")

# ============================================================
section("9. SETTINGS PERSISTENCE")

path = ROOT / "pages/settings.py"

if path.exists():
    text = path.read_text()

    settings_checks = [
        "show_animations",
        "sound_on",
        "reminder_enabled",
        "reminder_minutes",
        "st.session_state",
    ]

    for needle in settings_checks:
        if needle in text:
            ok(f"Settings contains: {needle}")
        else:
            fail(f"Settings missing: {needle}")

# ============================================================
section("10. REMINDER SYSTEM")

path = ROOT / "components/reminder.py"

if path.exists():
    text = path.read_text()

    for needle in [
        "localStorage",
        "setTimeout",
        "Notification",
        "AudioContext",
        "waterbuddy_next_reminder",
    ]:
        if needle in text:
            ok(f"Reminder contains: {needle}")
        else:
            fail(f"Reminder missing: {needle}")

    if "setTimeout" in text and "AudioContext" in text:
        ok("Reminder timer + alarm implementation detected")

# ============================================================
section("11. AI / VOICE DAILY LIMIT")

for filename in [
    "pages/ai_coach.py",
    "pages/voice_assistant.py",
]:
    path = ROOT / filename

    if not path.exists():
        fail(f"Missing: {filename}")
        continue

    text = path.read_text()

    for needle in [
        "ai_usage_count",
        "ai_usage_date",
    ]:
        if needle in text:
            ok(f"{filename}: shared limit variable {needle}")
        else:
            fail(f"{filename}: missing shared limit variable {needle}")

    if "2" in text:
        ok(f"{filename}: 2-use limit references detected")
    else:
        warn(f"{filename}: couldn't detect 2-use limit")

if all(
    x in (ROOT / "pages/ai_coach.py").read_text()
    for x in ["COME AGAIN TMRW UNTIL THEN DRINK WATER!", "disabled"]
):
    ok("AI Coach has locked-state message + disabled control")
else:
    warn("AI Coach locked-state wording/control needs review")

if all(
    x in (ROOT / "pages/voice_assistant.py").read_text()
    for x in ["COME AGAIN TMRW UNTIL THEN DRINK WATER!", "disabled"]
):
    ok("Voice Assistant has locked-state message + disabled control")
else:
    warn("Voice Assistant locked-state wording/control needs review")

# ============================================================
section("12. ANALYTICS")

path = ROOT / "pages/analytics.py"

if path.exists():
    text = path.read_text()

    if "go.Bar" in text:
        ok("Analytics uses Bar chart")
    else:
        fail("Analytics does NOT contain go.Bar")

    if "GRAPH" in text:
        ok("Analytics has GRAPH title")
    else:
        fail("Analytics GRAPH title missing")

    for needle in [
        "paper_bgcolor",
        "plot_bgcolor",
        "font=dict",
    ]:
        if needle in text:
            ok(f"Analytics theme support: {needle}")
        else:
            warn(f"Analytics missing theme support: {needle}")

# ============================================================
section("13. PROFILE HYDRATION GOAL")

path = ROOT / "pages/profile.py"

if path.exists():
    text = path.read_text()

    for needle in [
        "goal_minus",
        "goal_plus",
        "goal_ml_input",
        "suggested_goal",
        "goal_override",
    ]:
        if needle in text:
            ok(f"Profile contains: {needle}")
        else:
            fail(f"Profile missing: {needle}")

# ============================================================
section("14. DEV CELEBRATION TRIGGER REMOVAL")

all_text = ""

for path in (ROOT / "pages").glob("*.py"):
    try:
        all_text += path.read_text() + "\n"
    except:
        pass

bad_dev_terms = [
    "dev trigger celebration",
    "dev_trigger_celebration",
    "trigger celebration",
]

found_bad = False

for term in bad_dev_terms:
    if term.lower() in all_text.lower():
        found_bad = True
        fail(f"Possible development celebration trigger remains: {term}")

if not found_bad:
    ok("No obvious dev celebration trigger remains")

# ============================================================
section("15. STREAMLIT CONFIG")

path = ROOT / ".streamlit/config.toml"

if path.exists():
    text = path.read_text()

    if "showSidebarNavigation = false" in text:
        ok("Automatic Streamlit sidebar navigation disabled")
    else:
        warn("Automatic Streamlit sidebar navigation setting not found")

# ============================================================
section("16. DANGEROUS SECRET CHECK")

secret_patterns = [
    "AIza",
    "GEMINI_API_KEY=",
    "GOOGLE_API_KEY=",
]

for path in ROOT.rglob("*"):
    if (
        not path.is_file()
        or ".git" in path.parts
        or ".venv" in path.parts
        or "venv" in path.parts
        or "__pycache__" in path.parts
    ):
        continue

    try:
        text = path.read_text(errors="ignore")
    except:
        continue

    # .env is expected to contain the secret locally.
    if path.name == ".env":
        continue

    for pattern in secret_patterns:
        if pattern in text:
            fail(f"Possible API credential exposed in: {path.relative_to(ROOT)}")

ok("Secret scan completed")

# ============================================================
section("17. GIT STATUS")

import subprocess

try:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    print(result.stdout if result.stdout.strip() else "Working tree clean.")

    if ".env" in result.stdout:
        fail(".env appears in git status — DO NOT COMMIT IT")
    else:
        ok(".env is not shown in git status")

except Exception as e:
    warn(f"Git status check unavailable: {e}")

# ============================================================
section("FINAL REPORT")

print()
print(f"PASSED   : {passed}")
print(f"WARNINGS : {warnings}")
print(f"FAILED   : {failed}")
print()

if failed == 0:
    print("🔥 NO AUTOMATED FAILURES FOUND.")
    print("The remaining issues, if any, are likely UI/browser/runtime behavior.")
else:
    print("🚨 HOLES FOUND.")
    print("Fix the ❌ items before doing browser QA.")

if warnings:
    print("⚠️  Warnings should also be reviewed.")

print()
print("=" * 65)
print("END OF WATER BUDDY FULL APP TEST")
print("=" * 65)
