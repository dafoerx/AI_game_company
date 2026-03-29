"""
Post-Generation Validator Module

Responsibilities:
1. JavaScript syntax validation (using subprocess + node)
2. Global object existence checking
3. HTML structure validation
4. Automated playtest via Playwright (optional, graceful degradation)
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


class ValidationReport:
    """Aggregated validation report for a generated game."""

    def __init__(self, gen_id: str):
        self.gen_id = gen_id
        self.checks = []
        self.passed = True
        self.critical_failures = []

    def add_check(self, name: str, passed: bool, details: str = "",
                  severity: str = "error"):
        """
        Add a validation check result.
        severity: 'error' (blocks), 'warning' (logged but doesn't block)
        """
        self.checks.append({
            "name": name,
            "passed": passed,
            "details": details,
            "severity": severity,
        })
        if not passed and severity == "error":
            self.passed = False
            self.critical_failures.append(f"{name}: {details}")

    def to_dict(self) -> dict:
        return {
            "gen_id": self.gen_id,
            "passed": self.passed,
            "total_checks": len(self.checks),
            "passed_checks": sum(1 for c in self.checks if c["passed"]),
            "failed_checks": sum(1 for c in self.checks if not c["passed"]),
            "critical_failures": self.critical_failures,
            "checks": self.checks,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Validation Report",
            "",
            f"**Generation ID**: {self.gen_id}",
            f"**Overall**: {'✅ PASSED' if self.passed else '❌ FAILED'}",
            f"**Checks**: {sum(1 for c in self.checks if c['passed'])}/{len(self.checks)} passed",
            "",
        ]

        if self.critical_failures:
            lines.append("## ❌ Critical Failures")
            lines.append("")
            for f in self.critical_failures:
                lines.append(f"- {f}")
            lines.append("")

        lines.append("## All Checks")
        lines.append("")
        lines.append("| Check | Status | Severity | Details |")
        lines.append("|:------|:-------|:---------|:--------|")
        for c in self.checks:
            status = "✅" if c["passed"] else "❌"
            details = c["details"][:80] if c["details"] else "-"
            lines.append(f"| {c['name']} | {status} | {c['severity']} | {details} |")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════
# 1. JavaScript Syntax Validation
# ═══════════════════════════════════════════════════

def validate_js_syntax(file_path: Path) -> tuple:
    """
    Validate JavaScript file syntax using Node.js.

    Returns (passed: bool, error_message: str)
    """
    if not file_path.exists():
        return False, f"File does not exist: {file_path}"

    content = file_path.read_text(encoding="utf-8", errors="ignore")

    # Quick check: is the content obviously not JavaScript?
    if len(content.strip()) < 50:
        return False, f"File content too short ({len(content.strip())} chars), likely not valid JS"

    # Check for known error patterns (e.g., API gateway errors written as file content)
    error_patterns = [
        r"^codex:\s*status=\d+",
        r"^error:\s*status=\d+",
        r"^internal server error$",
        r"^5\d{2}\s+",
    ]
    first_line = content.strip().split("\n")[0].strip()
    for pattern in error_patterns:
        if re.match(pattern, first_line, re.IGNORECASE):
            return False, f"File contains API error instead of code: {first_line}"

    # Try to parse with Node.js if available
    try:
        # Use Node.js --check flag for syntax validation
        result = subprocess.run(
            ["node", "--check", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True, ""
        else:
            error_msg = (result.stderr or result.stdout or "Unknown syntax error").strip()
            # Extract just the relevant error line
            for line in error_msg.split("\n"):
                if "SyntaxError" in line or "Error" in line:
                    return False, line.strip()
            return False, error_msg[:200]
    except FileNotFoundError:
        # Node.js not available, fall back to Python-based heuristic check
        return _heuristic_js_check(content)
    except subprocess.TimeoutExpired:
        return False, "Syntax check timed out"
    except Exception as e:
        return _heuristic_js_check(content)


def _heuristic_js_check(content: str) -> tuple:
    """
    Fallback heuristic JavaScript validation when Node.js is not available.
    Checks for basic structural validity.
    """
    # Check for balanced braces
    brace_count = 0
    paren_count = 0
    bracket_count = 0

    in_string = False
    string_char = None
    in_comment = False
    in_block_comment = False
    prev_char = ""

    for char in content:
        if in_block_comment:
            if prev_char == "*" and char == "/":
                in_block_comment = False
            prev_char = char
            continue

        if in_comment:
            if char == "\n":
                in_comment = False
            prev_char = char
            continue

        if in_string:
            if char == string_char and prev_char != "\\":
                in_string = False
            prev_char = char
            continue

        if char in ('"', "'", "`"):
            in_string = True
            string_char = char
        elif prev_char == "/" and char == "/":
            in_comment = True
        elif prev_char == "/" and char == "*":
            in_block_comment = True
        elif char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
        elif char == "(":
            paren_count += 1
        elif char == ")":
            paren_count -= 1
        elif char == "[":
            bracket_count += 1
        elif char == "]":
            bracket_count -= 1

        prev_char = char

    issues = []
    if brace_count != 0:
        issues.append(f"Unbalanced braces (diff={brace_count})")
    if paren_count != 0:
        issues.append(f"Unbalanced parentheses (diff={paren_count})")
    if bracket_count != 0:
        issues.append(f"Unbalanced brackets (diff={bracket_count})")

    if issues:
        return False, "; ".join(issues)

    # Check for minimum code indicators
    code_indicators = ["function", "const ", "let ", "var ", "class ", "return"]
    has_indicator = any(ind in content for ind in code_indicators)
    if not has_indicator:
        return False, "No JavaScript code indicators found"

    return True, ""


# ═══════════════════════════════════════════════════
# 2. Global Object Existence Checking
# ═══════════════════════════════════════════════════

def check_global_objects(gen_dir: Path, scaffolding: dict = None) -> list:
    """
    Check that expected global objects are defined in the generated JS files.

    Returns a list of (check_name, passed, details) tuples.
    """
    results = []

    # Default expected globals if no scaffolding provided
    expected_globals = {
        "js/data.js": ["GameData"],
        "js/game-state.js": ["GameState"],
        "js/ui.js": ["UI"],
        "js/events.js": ["Events"],
        "js/main.js": ["Game"],
    }

    # Override with scaffolding if provided
    if scaffolding and "js_modules" in scaffolding:
        expected_globals = {}
        for module_name, module_spec in scaffolding["js_modules"].items():
            file_path = f"js/{module_name}"
            global_var = module_spec.get("global_var")
            if global_var:
                expected_globals[file_path] = [global_var]

    for rel_path, expected_vars in expected_globals.items():
        file_path = gen_dir / rel_path
        if not file_path.exists():
            results.append((
                f"global_object_{rel_path}",
                False,
                f"File {rel_path} does not exist"
            ))
            continue

        content = file_path.read_text(encoding="utf-8", errors="ignore")

        for var_name in expected_vars:
            # Check for various declaration patterns
            patterns = [
                rf"(?:const|let|var|class)\s+{re.escape(var_name)}\b",
                rf"window\.{re.escape(var_name)}\s*=",
                rf"function\s+{re.escape(var_name)}\b",
            ]
            found = any(re.search(p, content) for p in patterns)
            results.append((
                f"global_{var_name}_in_{rel_path.replace('/', '_')}",
                found,
                "" if found else f"Global '{var_name}' not found in {rel_path}"
            ))

    return results


# ═══════════════════════════════════════════════════
# 3. HTML Structure Validation
# ═══════════════════════════════════════════════════

def validate_html_structure(gen_dir: Path, scaffolding: dict = None) -> list:
    """
    Validate that index.html contains required structural elements.

    Returns a list of (check_name, passed, details) tuples.
    """
    results = []
    index_path = gen_dir / "index.html"

    if not index_path.exists():
        results.append(("html_exists", False, "index.html does not exist"))
        return results

    content = index_path.read_text(encoding="utf-8", errors="ignore")
    results.append(("html_exists", True, ""))

    # Check basic HTML structure
    basic_checks = [
        ("html_doctype", r"<!DOCTYPE\s+html", "Missing <!DOCTYPE html>"),
        ("html_lang", r'<html[^>]*lang=', "Missing lang attribute on <html>"),
        ("html_charset", r'charset', "Missing charset declaration"),
        ("html_title", r'<title>', "Missing <title> tag"),
    ]

    for name, pattern, error_msg in basic_checks:
        found = bool(re.search(pattern, content, re.IGNORECASE))
        results.append((name, found, "" if found else error_msg))

    # Check for required JS file references
    js_files = ["utils.js", "data.js", "game-state.js", "ui.js", "events.js", "main.js"]
    for js_file in js_files:
        found = js_file in content
        results.append((
            f"html_includes_{js_file.replace('.', '_').replace('-', '_')}",
            found,
            "" if found else f"index.html does not reference {js_file}"
        ))

    # Check for required CSS file references
    css_files = ["style.css"]
    for css_file in css_files:
        found = css_file in content
        results.append((
            f"html_includes_{css_file.replace('.', '_')}",
            found,
            "" if found else f"index.html does not reference {css_file}"
        ))

    # Check for required screen sections
    required_screens = ["loading-screen", "main-menu", "game-screen", "game-over"]
    for screen_id in required_screens:
        found = screen_id in content
        results.append((
            f"html_screen_{screen_id.replace('-', '_')}",
            found,
            "" if found else f"Missing screen section #{screen_id}"
        ))

    # Check for scaffolding-specific HTML sections
    if scaffolding and "html_sections" in scaffolding:
        for section in scaffolding["html_sections"]:
            # Convert section description to likely ID
            section_id = section.split(" ")[0]  # Take first word as ID
            found = section_id in content
            results.append((
                f"html_scaffold_{section_id.replace('-', '_')}",
                found,
                "" if found else f"Missing scaffolding section: {section}"
            ))

    return results


# ═══════════════════════════════════════════════════
# 4. Scaffolding Content Validation
# ═══════════════════════════════════════════════════

def validate_scaffolding_content(gen_dir: Path, scaffolding: dict) -> list:
    """
    Validate that generated code contains the required content
    as specified by the scaffolding type.

    Returns a list of (check_name, passed, details) tuples.
    """
    results = []

    if not scaffolding or "js_modules" not in scaffolding:
        return results

    for module_name, module_spec in scaffolding["js_modules"].items():
        file_path = gen_dir / "js" / module_name
        if not file_path.exists():
            results.append((
                f"scaffold_{module_name}_exists",
                False,
                f"js/{module_name} does not exist"
            ))
            continue

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        content_lower = content.lower()

        # Check for must_contain items (heuristic keyword matching)
        for item in module_spec.get("must_contain", []):
            # Extract key terms from the requirement description
            key_terms = _extract_key_terms(item)
            found = any(term in content_lower for term in key_terms)
            results.append((
                f"scaffold_{module_name}_{_slugify(item[:30])}",
                found,
                "" if found else f"Missing in {module_name}: {item}"
            ))

    return results


def _extract_key_terms(description: str) -> list:
    """Extract searchable key terms from a requirement description."""
    # Remove parenthetical content
    clean = re.sub(r'\([^)]*\)', '', description).lower()
    # Split on common delimiters
    words = re.split(r'[\s,/]+', clean)
    # Filter to meaningful terms (length > 3)
    terms = [w.strip() for w in words if len(w.strip()) > 3]
    # Also try the full description as a search term
    terms.append(clean.strip()[:40])
    return terms


def _slugify(text: str) -> str:
    """Convert text to a safe slug for check names."""
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')[:30]


# ═══════════════════════════════════════════════════
# 5. Automated Playtest (Playwright)
# ═══════════════════════════════════════════════════

def run_automated_playtest(gen_dir: Path, timeout_ms: int = 15000) -> list:
    """
    Run automated playtest using Playwright.
    Opens index.html, checks for console errors, verifies buttons are clickable,
    and tests core flow.

    Returns a list of (check_name, passed, details) tuples.
    Gracefully degrades if Playwright is not installed.
    """
    results = []
    index_path = gen_dir / "index.html"

    if not index_path.exists():
        results.append(("playtest_html_exists", False, "index.html not found"))
        return results

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        results.append((
            "playtest_playwright_available",
            True,  # Not a failure, just skipped
            "Playwright not installed, skipping automated playtest. "
            "Install with: pip install playwright && playwright install chromium"
        ))
        return results

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Collect console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text)
                     if msg.type == "error" else None)

            # Collect page errors (uncaught exceptions)
            page_errors = []
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))

            # Navigate to the game
            file_url = f"file://{index_path.resolve()}"
            page.goto(file_url, wait_until="domcontentloaded",
                      timeout=timeout_ms)

            # Wait for loading to complete
            page.wait_for_timeout(4000)

            # Check 1: No page errors (uncaught exceptions)
            results.append((
                "playtest_no_page_errors",
                len(page_errors) == 0,
                "; ".join(page_errors[:3]) if page_errors else ""
            ))

            # Check 2: No critical console errors
            # Filter out non-critical errors (like favicon 404)
            critical_errors = [
                e for e in console_errors
                if not any(skip in e.lower() for skip in
                           ["favicon", "404", "manifest", "service-worker"])
            ]
            results.append((
                "playtest_no_console_errors",
                len(critical_errors) == 0,
                "; ".join(critical_errors[:3]) if critical_errors else ""
            ))

            # Check 3: Loading screen appeared and transitioned
            # After 4 seconds, we should be past loading
            loading_screen = page.query_selector("#loading-screen")
            main_menu = page.query_selector("#main-menu")

            loading_hidden = True
            if loading_screen:
                display = page.evaluate(
                    "el => window.getComputedStyle(el).display",
                    loading_screen
                )
                loading_hidden = display == "none"

            menu_visible = False
            if main_menu:
                display = page.evaluate(
                    "el => window.getComputedStyle(el).display",
                    main_menu
                )
                menu_visible = display != "none"

            results.append((
                "playtest_loading_completes",
                loading_hidden,
                "" if loading_hidden else "Loading screen still visible after 4s"
            ))

            results.append((
                "playtest_menu_appears",
                menu_visible,
                "" if menu_visible else "Main menu not visible after loading"
            ))

            # Check 4: Start game button exists and is clickable
            start_btn = page.query_selector(
                '[data-action="start-game"], '
                '[data-action="start-new-game"], '
                '[data-action="new-game"], '
                '#start-game-btn, '
                '#new-game-btn, '
                'button:has-text("开始")'
            )
            results.append((
                "playtest_start_button_exists",
                start_btn is not None,
                "" if start_btn else "No start game button found"
            ))

            # Check 5: Click start and verify game screen appears
            if start_btn:
                try:
                    start_btn.click(timeout=3000)
                    page.wait_for_timeout(1000)

                    game_screen = page.query_selector("#game-screen")
                    game_visible = False
                    if game_screen:
                        display = page.evaluate(
                            "el => window.getComputedStyle(el).display",
                            game_screen
                        )
                        game_visible = display != "none"

                    results.append((
                        "playtest_game_screen_appears",
                        game_visible,
                        "" if game_visible else "Game screen not visible after clicking start"
                    ))

                    # Check 6: Next turn button exists
                    next_btn = page.query_selector(
                        '[data-action="next-turn"], '
                        '[data-action="next-day"], '
                        '[data-action="end-day"], '
                        '#next-turn-btn, '
                        'button:has-text("下一")'
                    )
                    results.append((
                        "playtest_next_turn_button_exists",
                        next_btn is not None,
                        "" if next_btn else "No next turn button found"
                    ))

                    # Check 7: Click next turn and verify no crash
                    if next_btn:
                        pre_errors = len(page_errors)
                        try:
                            next_btn.click(timeout=3000)
                            page.wait_for_timeout(1000)
                            new_errors = page_errors[pre_errors:]
                            results.append((
                                "playtest_next_turn_no_crash",
                                len(new_errors) == 0,
                                "; ".join(new_errors[:3]) if new_errors else ""
                            ))
                        except Exception as e:
                            results.append((
                                "playtest_next_turn_no_crash",
                                False,
                                f"Error clicking next turn: {str(e)[:100]}"
                            ))

                except Exception as e:
                    results.append((
                        "playtest_game_screen_appears",
                        False,
                        f"Error clicking start: {str(e)[:100]}"
                    ))

            browser.close()

    except Exception as e:
        results.append((
            "playtest_execution",
            False,
            f"Playtest execution error: {str(e)[:200]}"
        ))

    return results


# ═════════════════════════════════════════════════
# 6. Game Logic Validation (P1)
# ═════════════════════════════════════════════════

def validate_game_logic(gen_dir: Path, scaffolding: dict = None) -> list:
    """
    P1: Validate game logic beyond syntax - check that core mechanics
    are actually implemented, not just stubbed.

    Returns a list of (check_name, passed, details) tuples.
    """
    results = []

    # ── Check 1: data.js entity richness ──
    data_path = gen_dir / "js" / "data.js"
    if data_path.exists():
        data_content = data_path.read_text(encoding="utf-8", errors="ignore")

        # Check for entity definitions in entity_lifecycle games
        scaffolding_type = ""
        if scaffolding:
            scaffolding_type = scaffolding.get("description", "")

        if "entity" in scaffolding_type.lower() or "lifecycle" in scaffolding_type.lower():
            # Entity lifecycle game: must have individual entities
            has_entities = "entities" in data_content and data_content.count("backstory") >= 3
            results.append((
                "logic_entity_definitions",
                has_entities,
                "" if has_entities else "Entity lifecycle game missing individual entity definitions with backstories"
            ))

            # Must have interactions
            has_interactions = "interactions" in data_content and data_content.count("effects_on_entity") >= 2
            results.append((
                "logic_interaction_definitions",
                has_interactions,
                "" if has_interactions else "Missing interaction definitions with per-entity effects"
            ))

            # Must have adopter families or matching targets
            has_families = any(kw in data_content for kw in ["adopter_families", "matching_targets", "families"])
            results.append((
                "logic_matching_targets",
                has_families,
                "" if has_families else "Missing adopter families / matching targets"
            ))

            # Must have farewell/revisit templates
            has_farewell = any(kw in data_content for kw in ["farewell", "revisit", "goodbye"])
            results.append((
                "logic_farewell_system",
                has_farewell,
                "" if has_farewell else "Missing farewell/revisit narrative templates"
            ))

        # General checks for all game types
        # Victory condition should not be purely numeric
        has_victory = "victoryCondition" in data_content
        results.append((
            "logic_victory_condition_exists",
            has_victory,
            "" if has_victory else "Missing victoryCondition definition"
        ))

    # ── Check 2: game-state.js core methods ──
    gs_path = gen_dir / "js" / "game-state.js"
    if gs_path.exists():
        gs_content = gs_path.read_text(encoding="utf-8", errors="ignore")

        # Must have processTurn
        has_process_turn = "processTurn" in gs_content
        results.append((
            "logic_process_turn",
            has_process_turn,
            "" if has_process_turn else "GameState missing processTurn() method"
        ))

        # Must have checkEndCondition
        has_end_check = "checkEndCondition" in gs_content or "checkGameOver" in gs_content
        results.append((
            "logic_end_condition",
            has_end_check,
            "" if has_end_check else "GameState missing end condition checking"
        ))

        # For entity lifecycle: must have interact method
        if scaffolding and "entity" in scaffolding.get("description", "").lower():
            has_interact = "interact" in gs_content and "entityId" in gs_content
            results.append((
                "logic_interact_method",
                has_interact,
                "" if has_interact else "Entity lifecycle game missing interact(entityId, interactionId) method"
            ))

            # Must have per-entity state tracking
            has_entity_states = any(kw in gs_content for kw in ["entityStates", "entity_states", "animalStates"])
            results.append((
                "logic_per_entity_state",
                has_entity_states,
                "" if has_entity_states else "Missing per-entity state tracking (entityStates object)"
            ))

            # Must have matching/adoption logic
            has_matching = any(kw in gs_content for kw in ["matchScore", "calculateMatch", "processAdoption", "adoption"])
            results.append((
                "logic_matching_algorithm",
                has_matching,
                "" if has_matching else "Missing matching/adoption algorithm"
            ))

    # ── Check 3: main.js game loop integrity ──
    main_path = gen_dir / "js" / "main.js"
    if main_path.exists():
        main_content = main_path.read_text(encoding="utf-8", errors="ignore")

        # Must call processTurn in nextTurn
        has_turn_call = "processTurn" in main_content
        results.append((
            "logic_main_calls_process_turn",
            has_turn_call,
            "" if has_turn_call else "main.js does not call processTurn() in game loop"
        ))

        # Must have event triggering
        has_events = "triggerRandomEvent" in main_content or "Events.trigger" in main_content
        results.append((
            "logic_main_triggers_events",
            has_events,
            "" if has_events else "main.js does not trigger random events"
        ))

    # ── Check 4: UI has entity display (for entity lifecycle) ──
    ui_path = gen_dir / "js" / "ui.js"
    if ui_path.exists() and scaffolding and "entity" in scaffolding.get("description", "").lower():
        ui_content = ui_path.read_text(encoding="utf-8", errors="ignore")

        has_entity_display = any(kw in ui_content for kw in [
            "entity", "animal", "character", "portrait",
            "entityStates", "entity_states",
        ])
        results.append((
            "logic_ui_entity_display",
            has_entity_display,
            "" if has_entity_display else "UI layer does not display individual entities"
        ))

        has_interaction_ui = any(kw in ui_content for kw in [
            "interact", "feed", "observe", "touch", "play",
        ])
        results.append((
            "logic_ui_interaction_buttons",
            has_interaction_ui,
            "" if has_interaction_ui else "UI layer missing interaction buttons/panel"
        ))

    return results


# ═════════════════════════════════════════════════
# 7. Full Validation Pipeline
# ═════════════════════════════════════════════════
def run_full_validation(gen_dir: Path, gen_id: str,
                        scaffolding: dict = None,
                        run_playtest: bool = True) -> ValidationReport:
    """
    Run the complete validation pipeline on a generated game.

    Steps:
    1. JS syntax validation for all .js files
    2. Global object existence checking
    3. HTML structure validation
    4. Scaffolding content validation (if scaffolding provided)
    5. Automated playtest (if enabled and Playwright available)
    6. Game logic validation (P1 - checks core mechanics implementation)

    Returns a ValidationReport.
    """
    report = ValidationReport(gen_id)

    # ── Step 1: JS Syntax Validation ──
    js_dir = gen_dir / "js"
    if js_dir.exists():
        for js_file in sorted(js_dir.glob("*.js")):
            passed, error = validate_js_syntax(js_file)
            report.add_check(
                f"js_syntax_{js_file.stem}",
                passed,
                error,
                severity="error"
            )
    else:
        report.add_check("js_directory_exists", False, "js/ directory not found")

    # ── Step 2: Global Object Checking ──
    for name, passed, details in check_global_objects(gen_dir, scaffolding):
        report.add_check(name, passed, details, severity="error")

    # ── Step 3: HTML Structure Validation ──
    for name, passed, details in validate_html_structure(gen_dir, scaffolding):
        severity = "error" if "exists" in name or "screen" in name else "warning"
        report.add_check(name, passed, details, severity=severity)

    # ── Step 4: Scaffolding Content Validation ──
    if scaffolding:
        for name, passed, details in validate_scaffolding_content(gen_dir, scaffolding):
            report.add_check(name, passed, details, severity="warning")

    # ── Step 5: Automated Playtest ──
    if run_playtest:
        for name, passed, details in run_automated_playtest(gen_dir):
            severity = "error" if "crash" in name or "page_error" in name else "warning"
            report.add_check(name, passed, details, severity=severity)

    # ── Step 6: Game Logic Validation (P1) ──
    for name, passed, details in validate_game_logic(gen_dir, scaffolding):
        severity = "warning"  # Logic issues are warnings, not blockers
        if "per_entity_state" in name or "interact_method" in name:
            severity = "error"  # But core mechanic absence is an error
        report.add_check(name, passed, details, severity=severity)

    return report
