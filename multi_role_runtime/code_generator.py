"""
代码生成引擎 v2：将设计文档转化为高质量可运行的游戏代码。

核心策略变更（相比 v1）：
  - 放弃"通用模板 + LLM 局部定制"，改为 **LLM 全量定制生成**
  - 每一步生成时，将前面已生成的代码作为上下文传入，确保模块间一致性
  - 提供精确的接口契约（data schema），确保 LLM 产出的数据结构与逻辑代码兼容
  - 强制主题定制：配色、布局、文案、动画全部围绕游戏主题

流程：
1. 读取项目设计文档
2. 生成游戏数据层（data.js）— LLM 产出，严格遵守 schema
3. 生成 HTML 骨架 — LLM 产出，围绕游戏主题定制布局
4. 生成 CSS 样式 — LLM 产出，主题配色+完整动画
5. 生成游戏逻辑（game-state.js）— LLM 产出，与 data.js schema 对齐
6. 生成 UI 层（ui.js）— LLM 产出，与 HTML + data.js 对齐
7. 生成事件系统（events.js）— LLM 产出，与 data.js 对齐
8. 生成主入口（main.js + utils.js）— LLM 产出，集成所有模块
9. 最终校验 + README
"""

import json
import os
import re
import threading
import uuid
from datetime import datetime
from pathlib import Path

from .config import load_config
from .llm import LLMClient
from .design_spec import (
    detect_theme,
    get_scaffolding,
    build_scaffolding_prompt_section,
    THEME_MECHANIC_LIBRARY,
)
from .validator import run_full_validation, validate_game_logic
from .gold_references import get_gold_reference, get_available_references

# ═══════════════════════════════════════════════════
# 数据层接口契约（DATA SCHEMA）
# 所有 LLM 生成的代码都必须遵守这个契约
# ═══════════════════════════════════════════════════

DATA_SCHEMA_DOC = """\
## GameData 接口契约（所有模块必须严格遵守）

```javascript
const GameData = {
  name: "游戏名称",
  description: "游戏描述",
  maxTurns: 30,          // 最大回合数（营业天数）
  initialPopulation: 0,   // 初始人口（如果游戏不需要可设 0）

  // ===== 资源定义 =====
  resources: [
    {
      id: "cash",               // 唯一标识，英文小写
      name: "现金",              // 中文显示名
      icon: "💴",               // emoji 图标
      initial: 10000,           // 初始值
      max: 999999,              // 上限
      perTurn: 0,               // 每回合基础变化量
      warningThreshold: 1000,   // 低于此值显示警告（可选）
      failIfZero: true,         // 归零是否判负（可选）
      consumedPerPopulation: 0, // 每人口消耗（可选，默认 0）
    },
    // ... 4~6 种资源
  ],

  // ===== 建筑/升级定义 =====
  buildings: [
    {
      id: "building_id",
      name: "建筑名称",
      icon: "🏪",
      description: "功能描述",
      cost: { cash: 1000, materials: 20 },   // 花费：{ 资源id: 数量 }
      produces: { cash: 100, reputation: 1 }, // 每回合产出：{ 资源id: 数量 }
      consumes: { food: 5 },                  // 每回合消耗：{ 资源id: 数量 }（可选）
    },
    // ... 5~8 种建筑
  ],

  // ===== 事件定义 =====
  events: [
    {
      id: "event_id",
      title: "事件标题",
      description: "事件描述文本",
      icon: "⚡",
      weight: 2,           // 触发权重
      minTurn: 1,          // 最早触发回合（可选）
      maxTurn: 100,        // 最晚触发回合（可选）
      once: false,         // 是否一次性事件（可选）
      choices: [
        {
          text: "选项文本",
          effect: {
            resources: { cash: -500, reputation: 3 },  // 资源变化
            population: 0,                              // 人口变化（可选）
            message: "效果说明文本",                     // 效果消息
            messageType: "success",                     // success/warning/danger/info
          }
        },
        // ... 2~3 个选项
      ]
    },
    // ... 4~6 个事件
  ],

  // ===== 胜利条件（可选）=====
  victoryCondition: null,  // 或函数 (state) => boolean
};
```

### 关键约束
1. `produces` 和 `consumes` 必须是**扁平对象** `{ 资源id: 数量 }`，不能嵌套
2. `cost` 必须是**扁平对象** `{ 资源id: 数量 }`
3. `choices[].effect` 字段名必须是 `effect`（不是 `effects`）
4. `effect.resources` 必须是扁平对象 `{ 资源id: 数量 }`
5. 不要使用 `deepFreeze`，不要使用 `Object.freeze`
6. 所有资源 id 必须在 resources 数组中定义过
"""

# ═══════════════════════════════════════════════════
# 代码生成的 System Prompt
# ═══════════════════════════════════════════════════

SYSTEM_PROMPT_BASE = """\
你是一位顶级的全栈 Web 游戏开发工程师，专精于创建精美的 HTML5 网页小游戏。
你的目标是生成**堪比 4399 网页小游戏水平**的高质量、完整可运行的游戏代码。

## 技术规范
- 纯 HTML5 + CSS3 + JavaScript（ES6+），不使用任何外部框架
- 代码必须完整、可直接运行，不能有 TODO 或占位符
- 必须包含中文注释
- 响应式设计

## 视觉质量标准（极其重要）
- 界面必须**精美**，有**游戏感**，不能像后台管理系统
- 必须有丰富的 CSS 动画效果（入场、交互、状态变化、粒子装饰）
- 配色必须符合游戏主题（如火锅店→暖色红橙，太空→冷色蓝紫）
- 所有按钮都要有 hover 效果和点击反馈
- 数值变化要有动画
- 背景不能是纯色，要有渐变或纹理
- emoji 图标要大而清晰

## 输出格式
只输出纯 JavaScript/HTML/CSS 代码，不要 markdown 代码块包裹，不要额外解释。
"""

# ═══════════════════════════════════════════════════


class CodeGenerator:
    """代码生成引擎 v2：LLM 全量定制生成。"""

    def __init__(self, config=None):
        self.config = config or load_config()
        self.llm = LLMClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            model=self.config.model,
        )
        self._lock = threading.Lock()
        self._generations = {}

        self.output_dir = self.config.project_drive_dir.parent / "game-output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Design spec and scaffolding (populated during generation)
        self._current_design_spec = None
        self._current_scaffolding = None
        self._current_theme_mapping = None

    # ── 公开 API ──────────────────────────────

    def list_generations(self):
        with self._lock:
            return sorted(
                self._generations.values(),
                key=lambda x: x["created_at"],
                reverse=True,
            )

    def get_generation(self, gen_id):
        with self._lock:
            return self._generations.get(gen_id)

    def start_generation(self, project_id=None, project_name=None):
        gen_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]

        state = {
            "gen_id": gen_id,
            "project_id": project_id,
            "project_name": project_name,
            "status": "initializing",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "finished_at": None,
            "current_phase": "reading_design",
            "phases_completed": [],
            "files_generated": [],
            "failed_files": [],
            "logs": [],
            "error": None,
            "output_dir": str(self.output_dir / gen_id),
        }

        with self._lock:
            self._generations[gen_id] = state

        t = threading.Thread(target=self._run_generation, args=(gen_id,))
        t.daemon = True
        t.start()

        return state

    # ── 内部流程 ──────────────────────────────

    def _log(self, state, message):
        entry = {
            "time": datetime.utcnow().isoformat() + "Z",
            "message": message,
        }
        state["logs"].append(entry)
        print(f"[CodeGen] {message}")

    def _run_generation(self, gen_id):
        state = self.get_generation(gen_id)
        if not state:
            return

        gen_dir = Path(state["output_dir"])
        gen_dir.mkdir(parents=True, exist_ok=True)

        try:
            # ═══ Phase 1: 读取设计文档 ═══
            self._log(state, "📖 读取项目设计文档...")
            state["status"] = "generating"
            state["current_phase"] = "reading_design"

            design = self._collect_design_context()
            if not design.get("project_name"):
                raise ValueError("未找到有效的项目设计文档，请先完成项目规划")

            self._log(state, f"✅ 项目：{design['project_name']}")
            # 如果创建时没有传入项目名称，从设计文档中获取
            if not state.get("project_name"):
                state["project_name"] = design['project_name']
            state["phases_completed"].append("reading_design")

            # ═══ Phase 1.5: Load design spec and scaffolding ═══
            self._log(state, "📐 加载设计规格与脚手架...")
            self._load_design_spec_and_scaffolding(design, state)
            self._persist_state(gen_dir, state)

            # ═══ Phase 2: 生成数据层 (data.js) ═══
            self._log(state, "🎲 生成游戏数据层 (data.js)...")
            state["current_phase"] = "data_layer"

            data_js = self._gen_data_js(design)
            self._write_file(gen_dir, "js/data.js", data_js)
            state["files_generated"].append("js/data.js")
            self._log(state, "✅ data.js 完成")

            # P0: Incremental validation - verify data.js quality before proceeding
            self._log(state, "🔍 验证 data.js 数据丰富度...")
            data_quality = self._validate_data_layer(data_js)
            if not data_quality["passed"]:
                self._log(state, f"⚠️ data.js 质量不足: {data_quality['reason']}，尝试重新生成...")
                data_js = self._gen_data_js(design)
                self._write_file(gen_dir, "js/data.js", data_js)
                self._log(state, "🔄 data.js 已重新生成")

            state["phases_completed"].append("data_layer")
            self._persist_state(gen_dir, state)

            # ═══ Phase 3: 生成工具函数 (utils.js) ═══
            self._log(state, "🔧 生成工具函数 (utils.js)...")
            state["current_phase"] = "utils"

            utils_js = self._gen_utils_js(design)
            self._write_file(gen_dir, "js/utils.js", utils_js)
            state["files_generated"].append("js/utils.js")
            self._log(state, "✅ utils.js 完成")
            state["phases_completed"].append("utils")
            self._persist_state(gen_dir, state)

            # ═══ Phase 4: 生成游戏状态 (game-state.js) ═══
            self._log(state, "🎮 生成游戏状态管理 (game-state.js)...")
            state["current_phase"] = "game_state"

            game_state_js = self._safe_gen(
                state, "js/game-state.js",
                lambda: self._gen_game_state_js(design, data_js),
                gen_dir,
            )
            state["phases_completed"].append("game_state")
            self._persist_state(gen_dir, state)

            # ═══ Phase 5: 生成 UI 层 (ui.js) ═══
            self._log(state, "🎨 生成 UI 管理层 (ui.js)...")
            state["current_phase"] = "ui_layer"

            ui_js = self._safe_gen(
                state, "js/ui.js",
                lambda: self._gen_ui_js(design, data_js, game_state_js or ""),
                gen_dir,
            )
            state["phases_completed"].append("ui_layer")
            self._persist_state(gen_dir, state)

            # ═══ Phase 6: 生成事件系统 (events.js) ═══
            self._log(state, "⚡ 生成事件系统 (events.js)...")
            state["current_phase"] = "events"

            events_js = self._safe_gen(
                state, "js/events.js",
                lambda: self._gen_events_js(design, data_js, game_state_js or ""),
                gen_dir,
            )
            state["phases_completed"].append("events")
            self._persist_state(gen_dir, state)

            # ═══ Phase 7: 生成主入口 (main.js) ═══
            self._log(state, "🚀 生成主入口 (main.js)...")
            state["current_phase"] = "main_entry"

            main_js = self._safe_gen(
                state, "js/main.js",
                lambda: self._gen_main_js(design, data_js, game_state_js or "", ui_js or "", events_js or ""),
                gen_dir,
            )
            state["phases_completed"].append("main_entry")
            self._persist_state(gen_dir, state)

            # ═══ Phase 8: 生成 HTML ═══
            self._log(state, "📄 生成 HTML 页面 (index.html)...")
            state["current_phase"] = "html"

            # 收集所有已生成的 JS 代码用于 HTML 参考
            all_js = self._collect_code(gen_dir, "js")
            index_html = self._safe_gen(
                state, "index.html",
                lambda: self._gen_index_html(design, all_js),
                gen_dir,
            )
            state["phases_completed"].append("html")
            self._persist_state(gen_dir, state)

            # 如果 HTML 生成失败，CSS 阶段无法继续（需要 HTML 作为输入）
            if not index_html:
                self._log(state, "❌ index.html 生成失败，跳过 CSS 阶段")
                state["failed_files"].extend(["css/style.css", "css/animations.css"])
            else:
                # ═══ Phase 9: 生成 CSS ═══
                self._log(state, "🎨 生成样式和动画 (style.css + animations.css)...")
                state["current_phase"] = "css"

                html_content = (gen_dir / "index.html").read_text(encoding="utf-8")

                css_content = self._safe_gen(
                    state, "css/style.css",
                    lambda: self._gen_css(design, html_content, ui_js or ""),
                    gen_dir,
                )

                animations_css = self._safe_gen(
                    state, "css/animations.css",
                    lambda: self._gen_animations_css(design, html_content, css_content or ""),
                    gen_dir,
                )
                self._log(state, "✅ CSS 完成")
                state["phases_completed"].append("css")
                self._persist_state(gen_dir, state)

            # ═══ Phase 10: 生成 README ═══
            self._log(state, "📦 生成 README...")
            state["current_phase"] = "finalizing"
            self._generate_readme(gen_dir, design, state)
            state["files_generated"].append("README.md")

            # ═══ Phase 10.5: Post-generation validation ═══
            self._log(state, "🔍 执行生成后自动校验...")
            state["current_phase"] = "validation"
            validation_report = self._run_post_generation_validation(
                gen_dir, state
            )
            state["validation_report"] = validation_report.to_dict()
            self._persist_state(gen_dir, state)

            # Write validation report as markdown
            (gen_dir / "validation_report.md").write_text(
                validation_report.to_markdown(), encoding="utf-8"
            )
            state["files_generated"].append("validation_report.md")

            if not validation_report.passed:
                self._log(
                    state,
                    f"⚠️ 校验发现 {len(validation_report.critical_failures)} 个严重问题"
                )
                # Attempt auto-fix for files that failed syntax check
                self._attempt_auto_fix(gen_dir, state, validation_report)

            # ═══ Phase 11: LLM Self-Review (P1) ═══
            self._log(state, "🤖 执行 LLM 自审环节...")
            state["current_phase"] = "llm_self_review"
            try:
                review_result = self._llm_self_review(gen_dir, design, state)
                state["llm_review"] = review_result
                if review_result.get("critical_issues"):
                    self._log(
                        state,
                        f"⚠️ LLM 自审发现 {len(review_result['critical_issues'])} 个关键问题"
                    )
                    # Attempt to fix critical issues found by LLM review
                    self._attempt_llm_review_fix(gen_dir, state, design, review_result)
                else:
                    self._log(state, "✅ LLM 自审通过")
            except Exception as review_exc:
                self._log(state, f"⚠️ LLM 自审跳过: {review_exc}")
            self._persist_state(gen_dir, state)

            # ═══ 完成 ═══
            if state["failed_files"]:
                state["status"] = "completed_with_errors"
                failed_list = ", ".join(state["failed_files"])
                self._log(state, f"⚠️ 代码生成完成，但以下文件生成失败: {failed_list}")
            elif not validation_report.passed:
                state["status"] = "completed_with_warnings"
                self._log(state, f"⚠️ 代码生成完成，但校验未完全通过")
            else:
                state["status"] = "completed"
            state["current_phase"] = "done"
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            self._log(state, f"🎉 代码生成完成！共 {len(state['files_generated'])} 个文件")
            self._persist_state(gen_dir, state)

        except Exception as exc:
            import traceback
            traceback.print_exc()
            state["status"] = "failed"
            state["error"] = str(exc)
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            self._log(state, f"❌ 代码生成失败: {str(exc)}")
            self._persist_state(gen_dir, state)

    # ═══════════════════════════════════════════════════
    # Design Spec & Scaffolding Integration
    # ═══════════════════════════════════════════════════

    def _load_design_spec_and_scaffolding(self, design, state):
        """
        Load design spec from consensus output and determine scaffolding type.
        This is the key bridge between consensus and code generation.
        """
        # Try to load design spec from the latest consensus run
        spec = self._find_latest_design_spec()
        if spec:
            self._current_design_spec = spec
            self._log(state, "✅ 已加载共识产出的设计规格")
            state["design_spec_source"] = "consensus"
        else:
            self._log(state, "⚠️ 未找到共识设计规格，将从设计文档推断")
            state["design_spec_source"] = "inferred"

        # Detect theme and get scaffolding
        theme_mapping = detect_theme(
            design.get("theme", ""),
            design.get("theme", ""),
            design.get("core_loop", ""),
        )
        self._current_theme_mapping = theme_mapping
        self._current_scaffolding = get_scaffolding(
            theme_mapping.get("scaffolding_type", "resource_management")
        )

        state["theme_detected"] = theme_mapping.get("label", "Unknown")
        state["scaffolding_type"] = theme_mapping.get("scaffolding_type", "resource_management")
        self._log(
            state,
            f"📐 游戏类型: {theme_mapping.get('label')} | "
            f"脚手架: {theme_mapping.get('scaffolding_type')}"
        )

    def _find_latest_design_spec(self):
        """Find the latest design_spec.json from consensus runs."""
        runs_dir = self.config.output_dir
        if not runs_dir.exists():
            return None

        # Look for design_spec.json in run directories, newest first
        run_dirs = sorted(
            [d for d in runs_dir.iterdir() if d.is_dir() and d.name != "projects"],
            reverse=True,
        )

        for run_dir in run_dirs[:10]:  # Check last 10 runs
            spec_path = run_dir / "design_spec.json"
            if spec_path.exists():
                try:
                    content = spec_path.read_text(encoding="utf-8")
                    spec = json.loads(content)
                    if spec and not spec.get("error"):
                        return spec
                except (json.JSONDecodeError, IOError):
                    continue

        return None

    def _build_design_spec_prompt_section(self):
        """
        Build a prompt section from the design spec that can be injected
        into each module's generation prompt.
        """
        if not self._current_design_spec:
            return ""

        spec = self._current_design_spec
        sections = ["\n## 结构化设计规格（来自多角色共识，必须严格遵循）"]

        # Entity definitions
        entities = spec.get("entity_definitions", [])
        if entities:
            sections.append("\n### 实体定义（每个实体必须有独立的状态追踪）")
            for e in entities[:8]:
                sections.append(
                    f"- {e.get('id', '?')}: {e.get('name', '?')} "
                    f"({e.get('species', '?')}) - {e.get('backstory', '')[:60]}... "
                    f"初始状态: trust={e.get('initial_state', {}).get('trust', 0)}, "
                    f"stress={e.get('initial_state', {}).get('stress', 0)}"
                )

        # Interactions
        interactions = spec.get("interaction_definitions", [])
        if interactions:
            sections.append("\n### 互动定义")
            for i in interactions[:6]:
                sections.append(
                    f"- {i.get('id', '?')}: {i.get('name', '?')} "
                    f"({i.get('icon', '?')}) - {i.get('description', '')[:50]}"
                )

        # State machine
        sm = spec.get("state_machine", {})
        if sm.get("states"):
            sections.append("\n### 状态机")
            sections.append(f"状态: {', '.join(sm['states'])}")
            for t in sm.get("transitions", [])[:8]:
                sections.append(
                    f"  {t.get('from', '?')} → {t.get('to', '?')}: {t.get('condition', '?')}"
                )

        # Adopter families / matching targets
        families = spec.get("adopter_families", [])
        if families:
            sections.append("\n### 领养家庭/匹配目标")
            for f in families[:5]:
                sections.append(
                    f"- {f.get('id', '?')}: {f.get('name', '?')} - {f.get('description', '')[:50]}"
                )

        # Victory conditions
        vc = spec.get("victory_conditions", [])
        if vc:
            sections.append("\n### 胜利条件")
            for v in vc:
                sections.append(
                    f"- {v.get('type', '?')}: {v.get('description', '?')} "
                    f"({v.get('formula', '')})"
                )

        return "\n".join(sections)

    # ═══════════════════════════════════════════════════
    # P0: Incremental Data Layer Validation
    # ═══════════════════════════════════════════════════

    def _validate_data_layer(self, data_js):
        """
        Validate data.js quality before proceeding to next generation phase.
        Checks for minimum content richness based on scaffolding type.

        Returns: { passed: bool, reason: str, metrics: dict }
        """
        scaffolding_type = "resource_management"
        if self._current_theme_mapping:
            scaffolding_type = self._current_theme_mapping.get(
                "scaffolding_type", "resource_management"
            )

        metrics = {
            "resources_count": 0,
            "buildings_count": 0,
            "events_count": 0,
            "entities_count": 0,
            "interactions_count": 0,
            "families_count": 0,
        }

        # Count resources
        metrics["resources_count"] = len(
            re.findall(r"id:\s*['\"](\w+)['\"]", data_js.split("buildings")[0])
            if "buildings" in data_js else
            re.findall(r"id:\s*['\"](\w+)['\"]", data_js)
        )

        # Count buildings/facilities
        buildings_section = ""
        for keyword in ["buildings", "facilities"]:
            if keyword in data_js:
                start = data_js.find(keyword)
                # Find the next top-level array
                end = data_js.find("],", start)
                if end > start:
                    buildings_section = data_js[start:end]
                    break
        metrics["buildings_count"] = buildings_section.count("id:")

        # Count events
        if "events" in data_js:
            events_start = data_js.rfind("events")
            events_section = data_js[events_start:]
            metrics["events_count"] = events_section.count("title:")

        # Count entities (for entity_lifecycle scaffolding)
        if "entities" in data_js:
            entities_start = data_js.find("entities")
            entities_end = data_js.find("],", entities_start)
            if entities_end > entities_start:
                entities_section = data_js[entities_start:entities_end]
                metrics["entities_count"] = entities_section.count("id:")

        # Count interactions
        if "interactions" in data_js:
            interactions_start = data_js.find("interactions")
            interactions_end = data_js.find("],", interactions_start)
            if interactions_end > interactions_start:
                interactions_section = data_js[interactions_start:interactions_end]
                metrics["interactions_count"] = interactions_section.count("id:")

        # Count adopter families
        if "adopter_families" in data_js:
            families_start = data_js.find("adopter_families")
            families_end = data_js.find("],", families_start)
            if families_end > families_start:
                families_section = data_js[families_start:families_end]
                metrics["families_count"] = families_section.count("id:")

        # Validate based on scaffolding type
        if scaffolding_type == "entity_lifecycle":
            if metrics["entities_count"] < 4:
                return {
                    "passed": False,
                    "reason": f"实体数量不足（{metrics['entities_count']} < 4），entity_lifecycle 类型至少需要 4 个实体",
                    "metrics": metrics,
                }
            if metrics["interactions_count"] < 3:
                return {
                    "passed": False,
                    "reason": f"互动方式不足（{metrics['interactions_count']} < 3），至少需要 3 种互动",
                    "metrics": metrics,
                }
            if metrics["events_count"] < 4:
                return {
                    "passed": False,
                    "reason": f"事件数量不足（{metrics['events_count']} < 4），至少需要 4 个事件",
                    "metrics": metrics,
                }
        else:
            # resource_management / exploration_management
            if metrics["resources_count"] < 3:
                return {
                    "passed": False,
                    "reason": f"资源种类不足（{metrics['resources_count']} < 3）",
                    "metrics": metrics,
                }
            if metrics["buildings_count"] < 3:
                return {
                    "passed": False,
                    "reason": f"建筑种类不足（{metrics['buildings_count']} < 3）",
                    "metrics": metrics,
                }
            if metrics["events_count"] < 3:
                return {
                    "passed": False,
                    "reason": f"事件数量不足（{metrics['events_count']} < 3）",
                    "metrics": metrics,
                }

        return {"passed": True, "reason": "", "metrics": metrics}

    # ═══════════════════════════════════════════════════
    # P1: LLM Self-Review
    # ═══════════════════════════════════════════════════

    LLM_REVIEW_SYSTEM_PROMPT = """\
你是一位资深的游戏代码审查专家。你的任务是审查 AI 生成的游戏代码，
判断代码是否真正实现了设计文档中描述的核心玩法和情感体验。

你必须输出严格的 JSON 格式（不要 markdown 代码块包裹）：

{
  "overall_score": 0-100,
  "design_match_score": 0-100,
  "critical_issues": [
    {
      "file": "文件名",
      "issue": "问题描述",
      "severity": "critical/major/minor",
      "fix_suggestion": "修复建议"
    }
  ],
  "positive_aspects": ["做得好的方面1", "做得好的方面2"],
  "summary": "一句话总结"
}

审查维度：
1. 设计-实现匹配度：代码是否真正实现了设计文档中的核心机制？
2. 数据丰富度：实体/事件/互动的数量和质量是否足够？
3. 核心循环完整性：玩家的主要行为循环是否可以走通？
4. 情感体验：题材的情感内核是否被机制承载？
5. 胜利条件：胜利条件是否与题材相关（而非通用数值达标）？
"""

    def _llm_self_review(self, gen_dir, design, state):
        """
        P1: Let another LLM review the generated code against the design spec.
        Returns a review result dict.
        """
        # Collect key files for review
        review_files = {}
        for filename in ["data.js", "game-state.js", "main.js"]:
            filepath = gen_dir / "js" / filename
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                # Truncate to avoid token limits
                review_files[filename] = content[:4000] if len(content) > 4000 else content

        if not review_files:
            return {"overall_score": 0, "critical_issues": [], "summary": "No files to review"}

        # Build review prompt
        files_section = "\n\n".join(
            f"### {fname}\n```javascript\n{content}\n```"
            for fname, content in review_files.items()
        )

        spec_section = self._build_design_spec_prompt_section()

        user_prompt = f"""
## 游戏设计信息
- 名称：{design.get('project_name', '未知')}
- 主题：{design.get('theme', '未知')}
- 核心循环：{design.get('core_loop', '未知')}
- 视觉风格：{design.get('visual_style', '未知')}

{spec_section}

## 生成的代码（需要审查）

{files_section}

请审查以上代码，判断是否真正实现了设计文档中描述的核心玩法。
特别关注：
1. data.js 中是否有足够的实体/事件/互动定义？
2. game-state.js 中是否实现了核心机制（如实体状态追踪、互动处理、匹配算法）？
3. 胜利条件是否与题材相关？
4. 是否存在"设计文档描述了但代码没有实现"的功能？
"""

        raw = self.llm.complete(self.LLM_REVIEW_SYSTEM_PROMPT, user_prompt)

        # Parse JSON response
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1)

        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end + 1]

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {
                "overall_score": 50,
                "critical_issues": [],
                "summary": "Review response could not be parsed",
                "_raw": raw[:500],
            }

        return result

    def _attempt_llm_review_fix(self, gen_dir, state, design, review_result):
        """
        Attempt to fix critical issues found by LLM self-review.
        Only fixes issues with severity 'critical'.
        """
        critical_issues = [
            i for i in review_result.get("critical_issues", [])
            if i.get("severity") == "critical"
        ]

        if not critical_issues:
            return

        for issue in critical_issues[:3]:  # Fix at most 3 critical issues
            target_file = issue.get("file", "")
            fix_suggestion = issue.get("fix_suggestion", "")
            issue_desc = issue.get("issue", "")

            if not target_file or not fix_suggestion:
                continue

            file_path = gen_dir / "js" / target_file
            if not file_path.exists():
                continue

            self._log(
                state,
                f"🔧 LLM 自审修复: {target_file} - {issue_desc[:50]}..."
            )

            try:
                current_code = file_path.read_text(encoding="utf-8", errors="ignore")

                fix_prompt = f"""
以下是游戏「{design.get('project_name', '')}」的 {target_file} 文件，
LLM 审查发现了一个关键问题需要修复：

## 问题描述
{issue_desc}

## 修复建议
{fix_suggestion}

## 当前代码
```javascript
{current_code[:6000]}
```

请输出修复后的完整 {target_file} 代码。
保持原有的所有功能，只修复上述问题。
直接输出 JavaScript 代码，不要 markdown 包裹。
"""
                fixed_code = self._call_llm_for_code(fix_prompt)
                self._write_file(gen_dir, f"js/{target_file}", fixed_code)
                self._log(state, f"✅ {target_file} 已修复")

            except Exception as exc:
                self._log(state, f"⚠️ {target_file} 修复失败: {exc}")

    # ═══════════════════════════════════════════════════
    # Post-Generation Validation
    # ═══════════════════════════════════════════════════

    def _run_post_generation_validation(self, gen_dir, state):
        """Run the full validation pipeline after code generation."""
        gen_id = state.get("gen_id", "unknown")
        return run_full_validation(
            gen_dir=gen_dir,
            gen_id=gen_id,
            scaffolding=self._current_scaffolding,
            run_playtest=True,
        )

    def _attempt_auto_fix(self, gen_dir, state, report):
        """
        Attempt to auto-fix critical validation failures.
        Currently handles: files with API error content instead of code.
        """
        for check in report.checks:
            if not check["passed"] and check["severity"] == "error":
                # Check if it's a file with API error content
                if "API error instead of code" in check.get("details", ""):
                    file_stem = check["name"].replace("js_syntax_", "")
                    file_path = gen_dir / "js" / f"{file_stem}.js"
                    if file_path.exists():
                        self._log(
                            state,
                            f"🔄 尝试重新生成 {file_stem}.js..."
                        )
                        try:
                            design = self._collect_design_context()
                            data_js = ""
                            data_path = gen_dir / "js" / "data.js"
                            if data_path.exists():
                                data_js = data_path.read_text(
                                    encoding="utf-8", errors="ignore"
                                )

                            if file_stem == "game-state":
                                code = self._gen_game_state_js(design, data_js)
                            elif file_stem == "ui":
                                code = self._gen_ui_js(design, data_js, "")
                            elif file_stem == "events":
                                code = self._gen_events_js(design, data_js, "")
                            elif file_stem == "main":
                                code = self._gen_main_js(
                                    design, data_js, "", "", ""
                                )
                            else:
                                continue

                            self._write_file(gen_dir, f"js/{file_stem}.js", code)
                            self._log(
                                state,
                                f"✅ {file_stem}.js 重新生成成功"
                            )
                            # Remove from failed_files if it was there
                            rel = f"js/{file_stem}.js"
                            if rel in state["failed_files"]:
                                state["failed_files"].remove(rel)
                        except Exception as exc:
                            self._log(
                                state,
                                f"❌ {file_stem}.js 重新生成失败: {exc}"
                            )

    # ═══════════════════════════════════════════════════
    # 各模块生成方法（LLM 全量定制）
    # ═══════════════════════════════════════════════════

    def _safe_gen(self, state, rel_path, gen_fn, gen_dir):
        """
        安全地生成单个文件。

        如果 gen_fn() 抛出异常（LLM 返回错误/校验不通过），
        不中断整体流程，而是：
        1. 记录到 state["failed_files"]
        2. 打印警告日志
        3. 返回 None（后续阶段可以根据 None 做降级处理）
        """
        try:
            code = gen_fn()
            self._write_file(gen_dir, rel_path, code)
            state["files_generated"].append(rel_path)
            self._log(state, f"✅ {rel_path} 完成")
            return code
        except Exception as exc:
            state["failed_files"].append(rel_path)
            self._log(state, f"⚠️ {rel_path} 生成失败: {exc}")
            return None

    def _gen_data_js(self, design):
        """生成游戏数据层（P0 改进：注入黄金标准参考 + 多轮增量验证）。"""
        # Build scaffolding requirements
        scaffolding_section = ""
        if self._current_scaffolding:
            scaffolding_section = build_scaffolding_prompt_section(
                self._current_scaffolding, "data.js"
            )

        # Build design spec section
        spec_section = self._build_design_spec_prompt_section()

        # Build anti-patterns section
        anti_patterns = ""
        if self._current_theme_mapping:
            aps = self._current_theme_mapping.get("anti_patterns", [])
            if aps:
                anti_patterns = "\n## 反模式警告（绝对不要犯以下错误）\n" + "\n".join(
                    f"- {ap}" for ap in aps
                )

        # P0: Inject gold standard reference
        scaffolding_type = self._current_theme_mapping.get("scaffolding_type", "resource_management") if self._current_theme_mapping else "resource_management"
        gold_ref = get_gold_reference(scaffolding_type, "data.js")
        reference_section = ""
        if gold_ref:
            # Truncate if too long to avoid token limits
            ref_truncated = gold_ref[:6000] if len(gold_ref) > 6000 else gold_ref
            reference_section = f"""
## 黄金标准参考实现（请严格参考此代码的结构和质量水平，但内容替换为新游戏主题）

以下是一个高质量的参考实现，你的代码必须达到同等的完整度和质量：

```javascript
{ref_truncated}
```

**关键要求**：你的代码必须包含与参考实现相同层次的数据丰富度（实体数量、互动种类、事件数量等），
不能比参考实现更简陋。
"""

        prompt = f"""
请为以下游戏生成完整的 data.js 文件。

## 游戏信息
- 名称：{design['project_name']}
- 主题：{design['theme']}
- 核心循环：{design['core_loop']}
- 视觉风格：{design['visual_style']}

## 接口契约（必须严格遵守！）
{DATA_SCHEMA_DOC}
{scaffolding_section}
{spec_section}
{anti_patterns}
{reference_section}

## 要求
1. 所有内容必须围绕游戏主题定制（比如火锅店→食材资源、厨房设备建筑、经营事件）
2. **produces 和 consumes 必须是扁平对象**，如 `{{ cash: 100, reputation: 1 }}`，绝对不能嵌套
3. **cost 必须是扁平对象**，如 `{{ cash: 1000 }}`
4. **choices[].effect**（不是 effects），包含 resources（扁平对象）、message、messageType
5. **不要使用 deepFreeze 或 Object.freeze**
6. 不要添加 validateGameData 之类的校验函数
7. 变量名必须是 `GameData`，使用 const 声明
8. 可以定义 victoryCondition 为一个函数
9. 如果设计规格中定义了实体（如动物、角色），必须在 GameData 中包含完整的实体数组
10. 如果设计规格中定义了互动方式，必须在 GameData 中包含互动定义数组
11. 如果设计规格中定义了匹配目标（如领养家庭），必须在 GameData 中包含匹配目标数组

直接输出 JavaScript 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_utils_js(self, design):
        """生成工具函数。"""
        prompt = f"""
请为游戏「{design['project_name']}」生成 utils.js 工具函数文件。

包含以下函数：
1. formatNumber(num) - 格式化数字（K/M 单位）
2. randomInt(min, max) - 随机整数
3. randomChoice(array) - 随机选择
4. delay(ms) - Promise 延迟
5. deepClone(obj) - 深拷贝
6. clamp(value, min, max) - 限制范围
7. lerp(start, end, t) - 线性插值
8. animateNumber(element, from, to, duration) - 数值滚动动画（DOM 元素数字逐步变化）
9. createParticle(container, options) - 创建粒子效果
10. showFloatingText(text, x, y, type) - 显示浮动文字（+100 金币 之类的效果）

每个函数都要有中文注释。
直接输出 JavaScript 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_game_state_js(self, design, data_js):
        """生成游戏状态管理（P0 改进：注入黄金标准参考）。"""
        # 提取 data.js 中的资源和建筑 id 列表（而不是传完整代码）
        data_summary = self._extract_data_summary(data_js)

        # Build scaffolding requirements
        scaffolding_section = ""
        if self._current_scaffolding:
            scaffolding_section = build_scaffolding_prompt_section(
                self._current_scaffolding, "game-state.js"
            )

        # Build design spec section
        spec_section = self._build_design_spec_prompt_section()

        # Build anti-patterns section
        anti_patterns = ""
        if self._current_theme_mapping:
            aps = self._current_theme_mapping.get("anti_patterns", [])
            if aps:
                anti_patterns = "\n## 反模式警告\n" + "\n".join(
                    f"- {ap}" for ap in aps
                )

        # P0: Inject gold standard reference for game-state.js
        scaffolding_type = self._current_theme_mapping.get("scaffolding_type", "resource_management") if self._current_theme_mapping else "resource_management"
        gold_ref = get_gold_reference(scaffolding_type, "game-state.js")
        reference_section = ""
        if gold_ref:
            ref_truncated = gold_ref[:8000] if len(gold_ref) > 8000 else gold_ref
            reference_section = f"""
## 黄金标准参考实现（请严格参考此代码的结构、方法签名和质量水平）

以下是一个高质量的参考实现，你的代码必须达到同等的完整度和质量：

```javascript
{ref_truncated}
```

**关键要求**：
- 必须包含与参考实现相同层次的方法（interact, calculateMatchScore, processAdoption 等）
- 必须为每个实体维护独立的状态对象（不是全局资源数字）
- 必须实现完整的互动成功率计算（考虑实体特性和创伤标签）
- 必须实现领养匹配算法
"""

        prompt = f"""
请为游戏「{design['project_name']}」生成 game-state.js 文件。

## 游戏主题
{design['theme']}

## 核心循环
{design['core_loop']}

## data.js 中定义的数据概要
{data_summary}

## 接口契约
{DATA_SCHEMA_DOC}
{scaffolding_section}
{spec_section}
{anti_patterns}

## 要求
1. 定义 GameState class，包含：
   - constructor() / reset() - 初始化状态
   - processTurn() - 处理一个回合，返回 {{ resourceChanges, messages }}
   - calculateResourceChange(resourceId) - 计算单个资源的回合变化
   - build(buildingId) - 建造建筑，返回 {{ success, message }}
   - checkEndCondition() - 检查游戏结束，返回 {{ ended, victory, message }}
   - applyEventEffect(effect) - 应用事件效果
   - getStats() - 获取统计数据
2. **关键**：读取 GameData.buildings[x].produces 时，直接作为扁平对象使用
   - 例如：`buildingData.produces[resourceId]` 直接获取数值
3. **关键**：读取 GameData.buildings[x].consumes 时，同样是扁平对象
4. **关键**：applyEventEffect(effect) 接收的 effect 结构为：
   - `effect.resources` = 扁平对象 `{{ cash: -500, reputation: 3 }}`
   - `effect.population` = 数值
   - `effect.message` = 字符串
5. 不要重新定义 GameData，它来自 data.js（在 HTML 中先加载）
6. 如果脚手架要求实体状态追踪，必须为每个实体维护独立的状态对象
7. 如果脚手架要求互动处理，必须实现 interact(entityId, interactionId) 方法
8. 如果脚手架要求匹配算法，必须实现 calculateMatchScore(entityId, familyId) 方法
{reference_section}

直接输出 JavaScript 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_ui_js(self, design, data_js, game_state_js):
        """生成 UI 管理层。"""
        data_summary = self._extract_data_summary(data_js)

        # Build scaffolding requirements
        scaffolding_section = ""
        if self._current_scaffolding:
            scaffolding_section = build_scaffolding_prompt_section(
                self._current_scaffolding, "ui.js"
            )

        # Build design spec section
        spec_section = self._build_design_spec_prompt_section()

        prompt = f"""
请为游戏「{design['project_name']}」生成 ui.js 文件。

## 游戏主题与视觉风格
{design['visual_style']}
{design['theme']}
{scaffolding_section}
{spec_section}

## data.js 数据概要（UI 需要读取这些数据）
{data_summary}

## GameState 提供的方法
- Game.state.resources[resId].current — 当前资源值
- Game.state.resources[resId].max — 资源上限
- Game.state.calculateResourceChange(resId) — 计算每回合变化量
- Game.state.build(buildingId) — 建造建筑，返回 {{ success, message }}
- Game.state.buildings — 已建造建筑数组，每项 {{ type, level, builtAt }}
- Game.state.turn — 当前回合数
- Game.state.population.total — 总人口

{DATA_SCHEMA_DOC}

## 要求
1. 定义 UI 对象（const UI = {{ ... }}），包含：
   - init() - 初始化 UI
   - initResourcePanel() - 渲染资源面板（读取 GameData.resources）
   - initBuildMenu() - 渲染建造菜单（读取 GameData.buildings）
   - updateAll() - 更新所有 UI
   - updateResources() - 更新资源数值（带数值变化动画）
   - updateTurn() - 更新回合显示
   - updateStatusOverview() - 更新状态总览
   - updateGameViewport() - 更新游戏主视图（显示已建造的建筑）
   - build(buildingId) - 调用 Game.state.build() 并更新 UI
   - addLog(message, type) - 添加日志
   - initMenuParticles() - 菜单粒子效果
   - formatCost(cost) - 格式化花费显示

2. **UI 渲染要有游戏感**：
   - 建造菜单每个项目要有图标、名称、描述、花费、建造按钮
   - 建筑卡片要有漂亮的卡片样式（渐变背景、圆角、阴影）
   - 资源面板要有图标+数值+变化趋势
   - 所有数值变化要有颜色动画（增加=绿色闪烁，减少=红色闪烁）
   - 空状态要有引导提示

3. **关键**：
   - formatCost 读取的 cost 是扁平对象 {{ cash: 1000 }}
   - 建筑的 produces 是扁平对象 {{ cash: 100 }}
   - Game.state 是 GameState 的实例

4. 生成建造菜单 HTML 时，请确保使用以下 CSS 类名（后续 CSS 会定义这些样式）：
   - .build-item, .build-icon, .build-info, .build-name, .build-desc, .build-cost, .build-btn
   - .building-card, .building-icon, .building-name, .building-level
   - .buildings-grid, .empty-state
   - .status-item, .status-label, .status-value
   - .resource-item, .resource-icon, .resource-info, .resource-name, .resource-value, .resource-change

直接输出 JavaScript 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_events_js(self, design, data_js, game_state_js):
        """生成事件系统。"""
        data_summary = self._extract_data_summary(data_js)

        # Build scaffolding requirements
        scaffolding_section = ""
        if self._current_scaffolding:
            scaffolding_section = build_scaffolding_prompt_section(
                self._current_scaffolding, "events.js"
            )

        # Build design spec section
        spec_section = self._build_design_spec_prompt_section()

        prompt = f"""
请为游戏「{design['project_name']}」生成 events.js 文件。

## data.js 数据概要
{data_summary}
{scaffolding_section}
{spec_section}

## GameState 提供的方法
- Game.state.applyEventEffect(effect) — 应用事件效果
- Game.state.turn — 当前回合数
- Game.state.triggeredEvents — 已触发的事件ID数组

## UI 提供的方法
- UI.updateAll() — 更新全部 UI
- UI.addLog(message, type) — 添加日志（type: success/warning/danger/info）

{DATA_SCHEMA_DOC}

## 要求
1. 定义 Events 对象（const Events = {{ ... }}），包含：
   - init() - 初始化事件系统（绑定模态框关闭等）
   - triggerRandomEvent() - 根据条件和权重随机触发一个事件
   - showEvent(event) - 显示事件弹窗
   - selectChoice(choiceIndex, eventId) - 处理选择
   - formatEffect(effect) - 格式化效果显示

2. **关键**：
   - 事件数据在 GameData.events 中
   - 每个选项的效果在 `choice.effect`（不是 effects！）
   - `choice.effect.resources` 是扁平对象
   - 调用 `Game.state.applyEventEffect(choice.effect)` 应用效果
   - 调用 `UI.updateAll()` 更新界面
   - 调用 `UI.addLog()` 添加日志

3. HTML 中已有事件弹窗结构：
   - #event-modal（模态框容器）
   - #event-icon、#event-title、#event-description（事件信息）
   - #event-choices（选项容器）
   - .event-choice（选项按钮类名）
   - .choice-effect（效果文本类名）

直接输出 JavaScript 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_main_js(self, design, data_js, game_state_js, ui_js, events_js):
        """生成主入口。"""
        # Build scaffolding requirements
        scaffolding_section = ""
        if self._current_scaffolding:
            scaffolding_section = build_scaffolding_prompt_section(
                self._current_scaffolding, "main.js"
            )

        prompt = f"""
请为游戏「{design['project_name']}」生成 main.js 主入口文件。

## 游戏信息
- 名称：{design['project_name']}
- 主题：{design['theme']}
- 核心循环：{design['core_loop']}
{scaffolding_section}

## 已有模块（main.js 需要调用这些）
- GameData（来自 data.js）：游戏数据
- GameState（来自 game-state.js）：游戏状态类
- UI（来自 ui.js）：UI 管理
- Events（来自 events.js）：事件系统
- 工具函数（来自 utils.js）：formatNumber, randomInt 等

## 要求
1. 定义 Game 对象（const Game = {{ ... }}），包含：
   - state: null（GameState 实例）
   - isPaused: false
   - currentScreen: 'loading-screen'
   - init() - 初始化游戏（创建 GameState，初始化 UI 和 Events，开始加载动画）
   - simulateLoading() - 模拟加载过程（进度条动画，2-3秒后进入主菜单）
   - showScreen(screenId) - 切换屏幕（淡入淡出）
   - startNewGame() - 开始新游戏
   - nextTurn() - 执行下一回合（包含资源结算、随机事件触发、胜负检查）
   - checkGameOver() - 检查游戏结束
   - endGame(victory, message) - 结束游戏
   - restart() - 重新开始
   - backToMenu() - 返回主菜单
   - togglePause() - 暂停/继续
   - showSettings() / showHelp() / showModal() / closeModal() - 弹窗管理

2. 在 DOMContentLoaded 事件中调用 Game.init()

3. nextTurn 中事件触发概率约 30%

4. HTML 中的屏幕 ID：
   - loading-screen（加载屏幕）
   - main-menu（主菜单）
   - game-screen（游戏主界面）
   - game-over（游戏结束）

5. HTML 中的弹窗 ID：
   - event-modal、settings-modal、help-modal

直接输出 JavaScript 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_index_html(self, design, all_js_context):
        """生成 HTML 页面。"""
        prompt = f"""
请为游戏「{design['project_name']}」生成完整的 index.html 文件。

## 游戏信息
- 名称：{design['project_name']}
- 主题：{design['theme']}
- 视觉风格：{design['visual_style']}
- 核心循环：{design['core_loop']}

## 页面结构要求

### 1. 加载屏幕 (#loading-screen)
- 游戏标题（大字+主题色渐变）
- 副标题（主题描述）
- 加载进度条
- 加载状态文本

### 2. 主菜单 (#main-menu)
- 游戏标题（更大的字+发光效果）
- 开始游戏按钮（onclick="Game.startNewGame()"）
- 游戏设置按钮（onclick="Game.showSettings()"）
- 游戏帮助按钮（onclick="Game.showHelp()"）
- 背景粒子效果容器 (#menu-particles)

### 3. 游戏主界面 (#game-screen)
- **顶部栏** (.game-header)：回合数(#game-time)、当前阶段(#current-phase)、暂停/菜单按钮
- **资源面板** (.resource-panel #resource-panel)：由 JS 动态生成
- **主区域** (.game-main)：
  - 左侧面板 (.side-panel .left-panel)：状态总览(#status-overview)、任务列表(#task-list)
  - 中央区域 (.center-area)：游戏视口(#game-viewport) + 操作按钮区(.action-bar 含"下一回合"按钮)
  - 右侧面板 (.side-panel .right-panel)：建造菜单(#build-menu)、游戏日志(#game-log)
- **底部栏** (.game-footer)：提示信息

### 4. 事件弹窗 (#event-modal)
- .modal-content.event-content
- #event-icon、#event-title、#event-description、#event-choices

### 5. 设置弹窗 (#settings-modal)
- 游戏速度滑块、音效开关、动画开关
- 关闭按钮

### 6. 帮助弹窗 (#help-modal)
- 游戏操作说明和目标说明
- 关闭按钮

### 7. 游戏结束 (#game-over)
- #game-over-title、#game-over-message、#game-over-stats
- 重新开始和返回菜单按钮

## CSS 引入
```html
<link rel="stylesheet" href="css/style.css">
<link rel="stylesheet" href="css/animations.css">
```

## JS 引入顺序（在 body 末尾）
```html
<script src="js/utils.js"></script>
<script src="js/data.js"></script>
<script src="js/game-state.js"></script>
<script src="js/ui.js"></script>
<script src="js/events.js"></script>
<script src="js/main.js"></script>
```

## 关键要求
- 所有 screen 默认 display:none，只有 .active 的显示
- loading-screen 默认有 class="screen active"
- 其他 screen 默认只有 class="screen"
- 模态框(modal)默认 display:none，通过 .active 显示
- 不要内联任何 CSS 或 JS
- lang="zh-CN"

直接输出 HTML 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_css(self, design, html_content, ui_js):
        """生成主样式表。"""
        # 解析主题关键词来指导配色
        theme_hints = self._get_theme_color_hints(design)

        prompt = f"""
请为游戏「{design['project_name']}」生成完整的 style.css 主样式表。

## 游戏视觉风格
{design['visual_style']}

## 配色指导
{theme_hints}

## HTML 结构中使用的主要 class 和 ID（CSS 需要覆盖这些）
```html
{html_content[:4000]}
```

## UI 层动态生成的类名（也需要定义样式）
以下类名在 ui.js 中被动态生成，必须在 CSS 中定义：
- .build-item：建造菜单项（卡片样式，有图标+信息+按钮）
- .build-icon：建筑图标（大 emoji）
- .build-info：建筑信息区
- .build-name：建筑名称
- .build-desc：建筑描述
- .build-cost：建筑花费
- .build-btn：建造按钮
- .building-card：已建造的建筑卡片
- .building-icon：建筑卡片图标
- .building-name：建筑卡片名称
- .building-level：建筑等级
- .buildings-grid：建筑卡片网格
- .empty-state：空状态提示
- .status-item：状态项
- .status-label：状态标签
- .status-value：状态数值

## 要求
1. **配色必须符合游戏主题**（不是通用的暗色科技风！）
   - 例如火锅店 → 暖色系（红、橙、金色）、温暖的深色背景
   - 太空游戏 → 冷色系（蓝、紫、银色）、深邃的黑色背景
2. 使用 CSS 变量（:root）定义所有颜色
3. 背景用渐变（不要纯色）
4. 所有按钮都要有 hover/active 效果
5. 建造菜单项要有卡片感（背景、边框、圆角、hover 浮起效果）
6. 建筑卡片要有精美的卡片样式
7. 资源面板要有清晰的布局
8. 模态框要有背景模糊效果
9. 日志容器要有滚动条样式
10. 整体要有**游戏感**，不能像后台管理系统
11. 滚动条也要自定义样式
12. 所有 transition 都要平滑

直接输出 CSS 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    def _gen_animations_css(self, design, html_content, style_css):
        """生成动画样式。"""
        prompt = f"""
请为游戏「{design['project_name']}」生成完整的 animations.css 动画效果文件。

## 视觉风格
{design['visual_style']}

## 已有的主样式表使用的 CSS 变量
```css
{style_css[:2000]}
```

## 需要包含的动画

### @keyframes 定义
1. titleGlow - 标题发光
2. loadingProgress - 加载进度条
3. pulse - 脉冲
4. modalSlideIn - 模态框滑入
5. eventIconPulse - 事件图标脉冲
6. fadeIn - 淡入
7. slideInUp / slideInDown / slideInLeft / slideInRight - 四方向滑入
8. scaleIn - 缩放弹出
9. shake - 抖动
10. float - 浮动
11. heartbeat - 心跳
12. ripple - 波纹
13. numberChange - 数值变化
14. warningPulse - 警告脉冲
15. successFlash - 成功闪烁
16. particleFloat - 粒子漂浮
17. glow - 光晕
18. shimmer - 微光流动效果（适合卡片和按钮）

### 工具类
- .animate-fade-in, .animate-slide-up, .animate-slide-down, .animate-slide-left, .animate-slide-right
- .animate-scale-in, .animate-shake, .animate-float, .animate-heartbeat, .animate-glow, .animate-pulse
- .delay-100 到 .delay-500
- .hover-lift（hover 浮起）, .hover-glow（hover 发光）, .hover-scale（hover 放大）
- .btn-ripple（按钮点击波纹）
- .value-changed, .value-increased, .value-decreased
- .particle（粒子基础样式）

直接输出 CSS 代码，不要 markdown 包裹。
"""
        return self._call_llm_for_code(prompt)

    # ═══════════════════════════════════════════════════
    # 辅助方法
    # ═══════════════════════════════════════════════════

    def _extract_data_summary(self, data_js):
        """从 data.js 代码中提取精简的数据概要，避免传递太多代码导致 LLM 超时。"""
        summary_parts = []
        
        # 提取资源 ID 和名称
        # 注意：data.js 中 id 和 name 通常不在同一行，需要 re.DOTALL 跨行匹配
        import re as _re
        resource_ids = _re.findall(r"id:\s*['\"](\w+)['\"].*?name:\s*['\"]([^'\"]+)['\"]", data_js, _re.DOTALL)
        if resource_ids:
            summary_parts.append("资源列表：" + ", ".join(f"{rid}({rname})" for rid, rname in resource_ids[:10]))
        
        # 提取建筑 ID 和名称
        building_matches = _re.findall(r"id:\s*['\"](\w+)['\"].*?name:\s*['\"]([^'\"]+)['\"].*?cost:\s*\{([^}]+)\}", data_js, _re.DOTALL)
        if building_matches:
            buildings_desc = []
            for bid, bname, bcost in building_matches[:10]:
                buildings_desc.append(f"{bid}({bname}), cost={{{bcost.strip()}}}")
            summary_parts.append("建筑列表：\n" + "\n".join(f"  - {b}" for b in buildings_desc))
        
        # 提取事件信息
        event_titles = _re.findall(r"title:\s*['\"]([^'\"]+)['\"]", data_js)
        if event_titles:
            summary_parts.append("事件列表：" + ", ".join(event_titles[:10]))
        
        summary_parts.append("""
关键数据结构：
- GameData.resources: 数组，每项有 id, name, icon, initial, max, perTurn 等
- GameData.buildings: 数组，每项有 id, name, icon, description, cost(扁平对象), produces(扁平对象), consumes(扁平对象，可选)
- GameData.events: 数组，每项有 id, title, description, icon, weight, choices
- choices 每项有 text, effect（含 resources 扁平对象, message, messageType）
""")
        
        return "\n\n".join(summary_parts)

    def _get_theme_color_hints(self, design):
        """根据游戏主题推断配色指导。"""
        name = design.get('project_name', '').lower()
        style = design.get('visual_style', '').lower()
        theme = design.get('theme', '').lower()
        combined = name + style + theme

        if any(w in combined for w in ['火锅', '烧烤', '餐厅', '美食', '厨房', '料理']):
            return """
餐饮/火锅主题配色：
- 主色：#E65100（火锅橙红）
- 辅色：#FF8F00（金黄）、#BF360C（深红）
- 强调色：#FFD600（金色）
- 背景：深暖棕色渐变（#1A0A00 → #2D1400 → #3E1C00）
- 文字：#FFF3E0（暖白）、#FFE0B2（暖灰）
- 发光：rgba(255, 143, 0, 0.4)（橙色光晕）
- 整体氛围：温暖、热闹、食欲感
"""
        elif any(w in combined for w in ['太空', '星际', '宇宙', '外星', '银河', '轨道']):
            return """
太空科幻主题配色：
- 主色：#4DA6FF（星空蓝）
- 辅色：#7C4DFF（紫色）
- 强调色：#00E5FF（青色）
- 背景：深蓝黑渐变
- 发光：蓝色光晕
"""
        elif any(w in combined for w in ['赛博', '朋克', 'cyber', '霓虹']):
            return """
赛博朋克主题配色：
- 主色：#00F0FF（霓虹青）
- 辅色：#FF00FF（霓虹紫）
- 强调色：#FFFF00（霓虹黄）
- 背景：极深蓝黑
- 发光：青色光晕 + 扫描线效果
"""
        elif any(w in combined for w in ['水墨', '中国风', '国风', '古典', '武侠']):
            return """
中国风/水墨主题配色：
- 主色：#C9A06C（古铜金）
- 辅色：#8B4513（棕色）
- 强调色：#DC143C（朱红）
- 背景：深褐色渐变
- 发光：暖金色光晕
"""
        elif any(w in combined for w in ['像素', 'pixel', '复古', '8bit']):
            return """
复古像素主题配色：
- 主色：#4CAF50（像素绿）
- 辅色：#FF9800（橙色）
- 强调色：#FFEB3B（黄色）
- 背景：深紫蓝渐变
- 字体：等宽像素风格
"""
        else:
            return """
现代简约主题配色：
- 主色：#2196F3（蓝色）
- 辅色：#00BCD4（青色）
- 强调色：#FF4081（粉红）
- 背景：深灰渐变
"""

    # 代码文件的最小合理长度（字节）
    _MIN_CODE_LENGTH = 100
    # 合法代码中应至少包含的关键词之一
    _CODE_INDICATORS = [
        'function', 'class', 'const ', 'let ', 'var ', 'return',  # JS
        '<html', '<div', '<script', '<!DOCTYPE',                   # HTML
        '{', '}', ':', ';',                                        # CSS / 通用
        '@keyframes', '@media', '.animate',                        # CSS 动画
    ]

    def _call_llm_for_code(self, prompt, max_retries=2):
        """
        调用 LLM 生成代码并提取纯代码。

        增加质量校验：
        1. 长度检查：合法代码不应短于 _MIN_CODE_LENGTH
        2. 内容检查：必须包含至少一个代码关键词
        3. 错误检查：不应包含已知的错误模式
        如果校验不通过，会重试 max_retries 次。
        """
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                raw = self.llm.complete(SYSTEM_PROMPT_BASE, prompt)
                code = self._extract_code(raw)

                # ── 质量校验 ──
                self._validate_code_output(code)

                return code

            except (ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt < max_retries:
                    import time
                    wait = 5 * attempt
                    print(f"[CodeGen] ⚠️ 代码质量校验失败（第 {attempt} 次）: {exc}，{wait}s 后重试...")
                    time.sleep(wait)
                else:
                    print(f"[CodeGen] ❌ 代码生成重试 {max_retries} 次仍失败: {exc}")
                    raise

        raise last_error  # 不应到达这里，但作为安全兜底

    def _extract_code(self, raw):
        """从 LLM 原始返回中提取纯代码内容。"""
        # 去除可能的 markdown 代码块包裹
        # 匹配 ```javascript ... ``` 或 ```html ... ``` 或 ```css ... ```
        code_block = re.search(r'```(?:javascript|html|css|js)?\s*\n(.*?)```', raw, re.DOTALL)
        if code_block:
            return code_block.group(1).strip()

        # 如果没有代码块包裹，检查是否开头有 ```
        if raw.startswith('```'):
            lines = raw.split('\n')
            # 去掉第一行和最后一行的 ```
            if lines[-1].strip() == '```':
                lines = lines[1:-1]
            elif lines[0].strip().startswith('```'):
                lines = lines[1:]
            return '\n'.join(lines).strip()

        return raw.strip()

    def _validate_code_output(self, code):
        """
        校验 LLM 生成的代码内容是否合理。

        Raises:
            ValueError: 内容不符合代码文件的最低质量要求
        """
        if not code:
            raise ValueError("LLM 返回了空内容")

        # 长度校验
        if len(code) < self._MIN_CODE_LENGTH:
            raise ValueError(
                f"LLM 生成的内容过短（{len(code)} 字符 < {self._MIN_CODE_LENGTH}），"
                f"可能是错误信息: {code[:200]}"
            )

        # 关键词校验：至少包含一个代码指示符
        code_lower = code.lower()
        has_code_indicator = any(indicator.lower() in code_lower for indicator in self._CODE_INDICATORS)
        if not has_code_indicator:
            raise ValueError(
                f"LLM 生成的内容不像有效代码（缺少任何代码关键词），"
                f"内容前200字符: {code[:200]}"
            )

    def _collect_design_context(self):
        """收集设计文档上下文。"""
        pd = self.config.project_drive_dir
        context = {
            "project_name": "",
            "theme": "",
            "visual_style": "",
            "platform": "",
            "core_loop": "",
            "mvp_scope": {},
            "tasks": [],
            "raw_context": "",
        }

        active_ctx_path = pd / "00-active-context.md"
        if active_ctx_path.exists():
            content = active_ctx_path.read_text(encoding="utf-8", errors="ignore")
            context["raw_context"] = content

            for line in content.splitlines():
                if line.startswith("**项目名称**"):
                    context["project_name"] = line.split("：", 1)[-1].strip()
                elif line.startswith("**视觉风格**"):
                    context["visual_style"] = line.split("：", 1)[-1].strip()
                elif line.startswith("**目标平台**"):
                    context["platform"] = line.split("：", 1)[-1].strip()

            if "## 1. 项目主题" in content:
                start = content.find("## 1. 项目主题")
                end = content.find("## 2.", start)
                if end > start:
                    context["theme"] = content[start:end].replace("## 1. 项目主题", "").strip()

            if "## 2. 核心循环" in content:
                start = content.find("## 2. 核心循环")
                end = content.find("## 3.", start)
                if end > start:
                    context["core_loop"] = content[start:end].replace("## 2. 核心循环", "").strip()

        task_dirs = [
            pd / "02-task-cards" / "in-progress",
            pd / "02-task-cards" / "pending",
        ]
        for task_dir in task_dirs:
            if task_dir.exists():
                for path in sorted(task_dir.glob("*.md")):
                    task_content = path.read_text(encoding="utf-8", errors="ignore")
                    context["tasks"].append({
                        "file": path.name,
                        "content": task_content[:3000],
                    })

        return context

    def _collect_code(self, gen_dir, subdir=""):
        """收集已生成的代码。"""
        target = gen_dir / subdir if subdir else gen_dir
        parts = []
        for ext in ["js", "html", "css"]:
            for path in sorted(target.rglob(f"*.{ext}")):
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    rel = path.relative_to(gen_dir)
                    parts.append(f"=== {rel} ===\n{content}")
                except Exception:
                    pass
        return "\n\n".join(parts)

    def _write_file(self, gen_dir, rel_path, content):
        """写入单个文件。"""
        path = gen_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _generate_readme(self, gen_dir, design, state):
        """生成 README。"""
        readme = f"""# {design.get('project_name', '游戏项目')}

## 项目简介

{design.get('theme', '')}

## 视觉风格

{design.get('visual_style', '')}

## 核心玩法

{design.get('core_loop', '')}

## 如何运行

1. 直接用浏览器打开 `index.html` 文件
2. 或使用本地服务器：
   ```bash
   python -m http.server 8888
   # 然后访问 http://localhost:8888
   ```

## 生成信息

- 生成时间：{state['created_at']}
- 生成ID：{state['gen_id']}
- 文件数量：{len(state['files_generated'])}

## 文件结构

```
{self._generate_tree(gen_dir)}
```

## 技术栈

- HTML5 + CSS3 + JavaScript (ES6+)
- 无外部框架依赖
- 全部由 AI 自动生成

---

*由 AI Game Company v2 代码生成引擎生成*
"""
        (gen_dir / "README.md").write_text(readme, encoding="utf-8")

    def _generate_tree(self, gen_dir):
        lines = []
        for path in sorted(gen_dir.rglob("*")):
            if path.is_file() and not path.name.startswith("."):
                rel = path.relative_to(gen_dir)
                depth = len(rel.parts) - 1
                prefix = "  " * depth + "├── " if depth > 0 else ""
                lines.append(f"{prefix}{path.name}")
        return "\n".join(lines)

    @staticmethod
    def _persist_state(gen_dir, state):
        (gen_dir / "generation_state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
