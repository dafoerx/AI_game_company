"""
代码生成引擎：将设计文档转化为可运行的游戏代码。

流程：
1. 读取项目设计文档（active-context, task cards）
2. 按模块逐步生成代码
3. 生成完整的 HTML/CSS/JS 实现，包含动画效果
4. 输出到 game-output 目录
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
from .code_templates import (
    HTML_TEMPLATE, STYLE_CSS_TEMPLATE, ANIMATIONS_CSS_TEMPLATE,
    MAIN_JS_TEMPLATE, GAME_STATE_JS_TEMPLATE, UI_JS_TEMPLATE,
    EVENTS_JS_TEMPLATE, UTILS_JS_TEMPLATE, DATA_JS_TEMPLATE,
    get_color_scheme
)

# 代码生成系统提示 - 核心框架
CODE_ARCHITECT_PROMPT = """\
你是一位资深的全栈游戏开发工程师，专精于 Web 游戏开发。
你的任务是根据游戏设计文档，生成完整的、可直接运行的游戏代码。

技术栈要求：
- 使用纯 HTML5 + CSS3 + JavaScript（ES6+）
- 不使用任何外部框架（React/Vue/Angular），只使用原生 JS
- 可以使用 CDN 引入的轻量库（如 anime.js 用于动画）
- CSS 必须包含精美的动画效果和过渡
- 响应式设计，支持不同屏幕尺寸

代码质量要求：
- 代码必须完整可运行，不能有占位符或 TODO
- 包含详细的中文注释
- 模块化设计，代码结构清晰
- 错误处理完善

输出格式要求：
你必须严格按以下 JSON 格式输出（不要添加任何其他内容）：
{
  "files": [
    {
      "path": "相对路径，如 index.html 或 js/game.js",
      "content": "完整的文件内容",
      "description": "文件说明"
    }
  ],
  "run_instruction": "如何运行的说明"
}
"""

# 模块生成提示模板
MODULE_CODE_PROMPT = """\
你是一位资深的全栈游戏开发工程师。

当前任务：根据设计文档，实现【{module_name}】模块。

## 项目背景
{project_context}

## 当前模块设计
{module_design}

## 已有代码（如有）
{existing_code}

## 要求
1. 生成完整可运行的代码
2. 必须包含精美的 CSS 动画效果：
   - 元素出现/消失动画
   - 悬停效果
   - 点击反馈
   - 数值变化动画
   - 状态切换过渡
3. 视觉风格：{visual_style}
4. 代码要能与已有模块无缝集成

输出 JSON 格式：
{{
  "files": [
    {{
      "path": "文件路径",
      "content": "完整代码内容",
      "description": "文件说明"
    }}
  ],
  "integration_notes": "集成说明"
}}
"""

# UI 动画专项提示
UI_ANIMATION_PROMPT = """\
你是一位专精于 Web 动画的前端开发专家。

任务：为以下游戏界面添加精美的动画效果。

## 项目视觉风格
{visual_style}

## 当前界面代码
{current_code}

## 动画要求
1. 入场动画：元素逐个淡入或滑入
2. 交互动画：
   - 按钮 hover 发光/缩放效果
   - 点击波纹效果
   - 拖拽反馈
3. 状态动画：
   - 数值增减时的滚动效果
   - 进度条填充动画
   - 警告/危险状态的脉冲效果
4. 粒子/装饰效果：
   - 背景粒子（如星空、光点）
   - 成功/失败时的特效
5. 过渡动画：
   - 面板切换
   - 弹窗打开/关闭
   - 场景转换

输出增强后的完整代码（JSON 格式）：
{{
  "files": [
    {{
      "path": "文件路径",
      "content": "包含动画的完整代码",
      "description": "动画增强说明"
    }}
  ]
}}
"""


class CodeGenerator:
    """代码生成引擎：将设计转化为可运行代码。"""

    def __init__(self, config=None):
        self.config = config or load_config()
        self.llm = LLMClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            model=self.config.model,
        )
        self._lock = threading.Lock()
        self._generations = {}  # 代码生成任务状态
        
        # 代码输出目录
        self.output_dir = self.config.project_drive_dir.parent / "game-output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def list_generations(self):
        """列出所有代码生成任务。"""
        with self._lock:
            return sorted(
                self._generations.values(),
                key=lambda x: x["created_at"],
                reverse=True,
            )

    def get_generation(self, gen_id):
        """获取指定的代码生成任务。"""
        with self._lock:
            return self._generations.get(gen_id)

    def start_generation(self, project_id=None):
        """
        启动代码生成流程。
        如果提供 project_id，则基于该项目的设计生成代码；
        否则基于当前 active-context 生成。
        """
        gen_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        
        state = {
            "gen_id": gen_id,
            "project_id": project_id,
            "status": "initializing",  # initializing -> generating -> completed / failed
            "created_at": datetime.utcnow().isoformat() + "Z",
            "finished_at": None,
            "current_phase": "reading_design",
            "phases_completed": [],
            "files_generated": [],
            "logs": [],
            "error": None,
            "output_dir": str(self.output_dir / gen_id),
        }

        with self._lock:
            self._generations[gen_id] = state

        # 后台启动生成流程
        t = threading.Thread(target=self._run_generation, args=(gen_id,))
        t.daemon = True
        t.start()

        return state

    def _log(self, state, message):
        """记录日志。"""
        entry = {
            "time": datetime.utcnow().isoformat() + "Z",
            "message": message,
        }
        state["logs"].append(entry)

    def _run_generation(self, gen_id):
        """主生成流程。"""
        state = self.get_generation(gen_id)
        if not state:
            return

        gen_dir = Path(state["output_dir"])
        gen_dir.mkdir(parents=True, exist_ok=True)

        try:
            # ═══════════════════════════════════════
            # Phase 1: 读取设计文档
            # ═══════════════════════════════════════
            self._log(state, "📖 读取项目设计文档...")
            state["status"] = "generating"
            state["current_phase"] = "reading_design"
            
            design_context = self._collect_design_context()
            if not design_context.get("project_name"):
                raise ValueError("未找到有效的项目设计文档，请先完成项目规划")
            
            self._log(state, f"✅ 读取完成：{design_context.get('project_name', '未命名项目')}")
            state["phases_completed"].append("reading_design")
            self._persist_state(gen_dir, state)

            # ═══════════════════════════════════════
            # Phase 2: 生成项目骨架
            # ═══════════════════════════════════════
            self._log(state, "🏗️ 生成项目基础框架...")
            state["current_phase"] = "generating_skeleton"
            
            skeleton_files = self._generate_skeleton(design_context)
            self._write_files(gen_dir, skeleton_files)
            state["files_generated"].extend([f["path"] for f in skeleton_files])
            
            self._log(state, f"✅ 基础框架生成完成，包含 {len(skeleton_files)} 个文件")
            state["phases_completed"].append("generating_skeleton")
            self._persist_state(gen_dir, state)

            # ═══════════════════════════════════════
            # Phase 3: 逐模块生成核心代码
            # ═══════════════════════════════════════
            modules = self._plan_modules(design_context)
            
            for i, module in enumerate(modules):
                module_name = module.get("name", f"模块{i+1}")
                self._log(state, f"🔧 生成模块 [{i+1}/{len(modules)}]: {module_name}")
                state["current_phase"] = f"module_{i+1}_{module_name}"
                
                # 收集已有代码作为上下文
                existing_code = self._collect_existing_code(gen_dir)
                
                module_files = self._generate_module(
                    module=module,
                    design_context=design_context,
                    existing_code=existing_code,
                )
                self._write_files(gen_dir, module_files)
                state["files_generated"].extend([f["path"] for f in module_files if f["path"] not in state["files_generated"]])
                
                self._log(state, f"✅ 模块 {module_name} 生成完成")
                state["phases_completed"].append(f"module_{module_name}")
                self._persist_state(gen_dir, state)

            # ═══════════════════════════════════════
            # Phase 4: 添加动画效果
            # ═══════════════════════════════════════
            self._log(state, "✨ 增强 UI 动画效果...")
            state["current_phase"] = "enhancing_animations"
            
            existing_code = self._collect_existing_code(gen_dir)
            enhanced_files = self._enhance_animations(design_context, existing_code)
            self._write_files(gen_dir, enhanced_files)
            
            self._log(state, "✅ 动画效果增强完成")
            state["phases_completed"].append("enhancing_animations")
            self._persist_state(gen_dir, state)

            # ═══════════════════════════════════════
            # Phase 5: 生成启动文件和说明
            # ═══════════════════════════════════════
            self._log(state, "📦 生成启动文件...")
            state["current_phase"] = "finalizing"
            
            self._generate_readme(gen_dir, design_context, state)
            
            # ═══════════════════════════════════════
            # 完成
            # ═══════════════════════════════════════
            state["status"] = "completed"
            state["current_phase"] = "done"
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            self._log(state, f"🎉 代码生成完成！共 {len(state['files_generated'])} 个文件")
            self._log(state, f"📁 输出目录: {gen_dir}")
            self._persist_state(gen_dir, state)

        except Exception as exc:
            state["status"] = "failed"
            state["error"] = str(exc)
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            self._log(state, f"❌ 代码生成失败: {str(exc)}")
            self._persist_state(gen_dir, state)

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

        # 读取 active-context
        active_ctx_path = pd / "00-active-context.md"
        if active_ctx_path.exists():
            content = active_ctx_path.read_text(encoding="utf-8", errors="ignore")
            context["raw_context"] = content
            
            # 解析关键信息
            for line in content.splitlines():
                if line.startswith("**项目名称**"):
                    context["project_name"] = line.split("：", 1)[-1].strip()
                elif line.startswith("**视觉风格**"):
                    context["visual_style"] = line.split("：", 1)[-1].strip()
                elif line.startswith("**目标平台**"):
                    context["platform"] = line.split("：", 1)[-1].strip()

            # 提取主题
            if "## 1. 项目主题" in content:
                start = content.find("## 1. 项目主题")
                end = content.find("## 2.", start)
                if end > start:
                    context["theme"] = content[start:end].replace("## 1. 项目主题", "").strip()

            # 提取核心循环
            if "## 2. 核心循环" in content:
                start = content.find("## 2. 核心循环")
                end = content.find("## 3.", start)
                if end > start:
                    context["core_loop"] = content[start:end].replace("## 2. 核心循环", "").strip()

        # 读取任务卡
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

    def _plan_modules(self, design_context):
        """根据设计文档规划代码模块。"""
        # 基于 MVP 范围和任务列表规划模块
        modules = [
            {
                "name": "游戏状态管理",
                "description": "游戏核心状态、数据模型、存档系统",
                "priority": 1,
            },
            {
                "name": "资源与数值系统",
                "description": "资源定义、产出消耗计算、回合结算",
                "priority": 2,
            },
            {
                "name": "UI界面系统",
                "description": "主界面、各功能面板、信息展示",
                "priority": 3,
            },
            {
                "name": "交互与事件系统",
                "description": "用户操作处理、随机事件、反馈系统",
                "priority": 4,
            },
            {
                "name": "动画与特效",
                "description": "UI动画、状态变化效果、粒子特效",
                "priority": 5,
            },
        ]
        return modules

    def _generate_skeleton(self, design_context):
        """生成项目基础骨架（使用预设模板）。"""
        game_title = design_context.get('project_name', '未命名游戏')
        visual_style = design_context.get('visual_style', '现代简约')
        theme = design_context.get('theme', '')
        core_loop = design_context.get('core_loop', '')
        
        # 获取配色方案
        colors = get_color_scheme(visual_style)
        
        # 生成 HTML
        html_content = HTML_TEMPLATE.format(
            game_title=game_title,
            game_subtitle=theme[:50] if theme else '一款精彩的游戏',
            game_objective=core_loop[:200] if core_loop else '体验游戏的乐趣',
        )
        
        # 生成主样式 CSS
        style_content = STYLE_CSS_TEMPLATE.format(
            game_title=game_title,
            visual_style=visual_style,
            **colors,
        )
        
        # 生成动画 CSS
        animations_content = ANIMATIONS_CSS_TEMPLATE.format(game_title=game_title)
        
        return [
            {'path': 'index.html', 'content': html_content, 'description': '游戏主入口页面'},
            {'path': 'css/style.css', 'content': style_content, 'description': '主样式表'},
            {'path': 'css/animations.css', 'content': animations_content, 'description': '动画效果样式'},
        ]

    def _generate_module(self, module, design_context, existing_code):
        """生成单个功能模块的代码（使用预设模板 + LLM 定制）。"""
        game_title = design_context.get('project_name', '未命名游戏')
        theme = design_context.get('theme', '')
        core_loop = design_context.get('core_loop', '')
        visual_style = design_context.get('visual_style', '现代简约')
        
        module_name = module.get('name', '')
        files = []
        
        # 根据模块类型生成对应代码
        if '状态' in module_name or 'state' in module_name.lower():
            # 游戏状态管理模块
            content = GAME_STATE_JS_TEMPLATE.format(game_title=game_title)
            files.append({
                'path': 'js/game-state.js',
                'content': content,
                'description': '游戏状态管理模块',
            })
            
        elif '资源' in module_name or '数值' in module_name:
            # 数据定义模块 - 使用 LLM 定制
            data_content = self._generate_custom_data(design_context)
            files.append({
                'path': 'js/data.js',
                'content': data_content,
                'description': '游戏数据定义',
            })
            
        elif 'UI' in module_name or '界面' in module_name:
            # UI 模块
            content = UI_JS_TEMPLATE.format(game_title=game_title)
            files.append({
                'path': 'js/ui.js',
                'content': content,
                'description': 'UI 管理模块',
            })
            
        elif '交互' in module_name or '事件' in module_name:
            # 事件系统模块
            content = EVENTS_JS_TEMPLATE.format(game_title=game_title)
            files.append({
                'path': 'js/events.js',
                'content': content,
                'description': '事件系统模块',
            })
            
        elif '动画' in module_name or '特效' in module_name:
            # 工具函数和主入口
            utils_content = UTILS_JS_TEMPLATE.format(game_title=game_title)
            main_content = MAIN_JS_TEMPLATE.format(game_title=game_title)
            
            files.append({
                'path': 'js/utils.js',
                'content': utils_content,
                'description': '工具函数',
            })
            files.append({
                'path': 'js/main.js',
                'content': main_content,
                'description': '游戏主入口',
            })
        
        return files
    
    def _generate_custom_data(self, design_context):
        """使用 LLM 生成定制的游戏数据。"""
        game_title = design_context.get('project_name', '未命名游戏')
        theme = design_context.get('theme', '')
        core_loop = design_context.get('core_loop', '')
        
        # 先使用基础模板
        base_data = DATA_JS_TEMPLATE.format(
            game_title=game_title,
            game_description=theme[:100] if theme else '一款精彩的游戏',
        )
        
        # 尝试用 LLM 定制（如果失败则使用基础模板）
        try:
            prompt = f"""
基于以下游戏设计，生成定制的游戏数据定义。

游戏名称：{game_title}
游戏主题：{theme}
核心循环：{core_loop}

请输出一个完整的 JavaScript 文件内容（GameData 对象），包含：
1. 符合游戏主题的资源定义（4-6种资源，包含 id, name, icon, initial, max, perTurn 等）
2. 符合游戏主题的建筑定义（5-8种建筑，包含 id, name, icon, description, cost, produces 等）
3. 符合游戏主题的事件定义（4-6个事件，包含 id, title, description, icon, choices 等）

只输出 JavaScript 代码，不要 markdown 代码块包裹。
确保代码完整可运行。
"""
            custom_data = self.llm.complete(CODE_ARCHITECT_PROMPT, prompt)
            
            # 验证返回的是否是有效的 JS 代码
            if 'GameData' in custom_data and 'resources' in custom_data:
                return custom_data
        except Exception as e:
            print(f"LLM 定制数据生成失败: {e}")
        
        return base_data

    def _enhance_animations(self, design_context, existing_code):
        """增强 UI 动画效果（模板已包含完整动画，此处做额外增强）。"""
        # 模板已包含完整的动画效果
        # 这里可以根据需要添加额外的自定义动画
        visual_style = design_context.get('visual_style', '')
        
        # 根据视觉风格添加特殊效果
        extra_css = ""
        
        if '赛博' in visual_style.lower():
            extra_css = """
/* 赛博朋克特效增强 */
.glitch-effect {
    animation: glitch 0.3s infinite;
}

@keyframes glitch {
    0%, 100% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
}

.scanline::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 255, 255, 0.03) 2px,
        rgba(0, 255, 255, 0.03) 4px
    );
    pointer-events: none;
    animation: scanlines 0.1s linear infinite;
}

@keyframes scanlines {
    0% { background-position: 0 0; }
    100% { background-position: 0 4px; }
}
"""
        
        if extra_css:
            return [{
                'path': 'css/effects.css',
                'content': extra_css,
                'description': '特殊视觉效果',
            }]
        
        return []

    def _extract_relevant_tasks(self, design_context, module):
        """提取与模块相关的任务设计。"""
        relevant = []
        keywords = module["name"].lower()
        
        for task in design_context.get("tasks", []):
            content = task.get("content", "").lower()
            # 简单关键词匹配
            if any(kw in content for kw in keywords.split()):
                relevant.append(task["content"][:1000])
        
        return "\n\n".join(relevant[:3]) if relevant else "（无特定任务设计）"

    def _call_llm_for_code(self, system_prompt, user_prompt):
        """调用 LLM 生成代码。"""
        raw = self.llm.complete(system_prompt, user_prompt)
        
        # 提取 JSON
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1)
        
        # 找到 JSON 边界
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end + 1]
        
        try:
            result = json.loads(raw)
            return result.get("files", [])
        except json.JSONDecodeError:
            # 返回原始文本作为单个文件
            return [{
                "path": "generated_output.txt",
                "content": raw,
                "description": "LLM 原始输出（JSON 解析失败）",
            }]

    def _collect_existing_code(self, gen_dir):
        """收集已生成的代码作为上下文。"""
        code_parts = []
        
        for ext in ["html", "css", "js"]:
            for path in gen_dir.rglob(f"*.{ext}"):
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    rel_path = path.relative_to(gen_dir)
                    code_parts.append(f"=== {rel_path} ===\n{content}")
                except Exception:
                    pass
        
        return "\n\n".join(code_parts)

    def _write_files(self, gen_dir, files):
        """写入生成的文件。"""
        for f in files:
            path = gen_dir / f["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f["content"], encoding="utf-8")

    def _generate_readme(self, gen_dir, design_context, state):
        """生成 README 和启动说明。"""
        readme = f"""# {design_context.get('project_name', '游戏项目')}

## 项目简介

{design_context.get('theme', '')}

## 视觉风格

{design_context.get('visual_style', '')}

## 核心玩法

{design_context.get('core_loop', '')}

## 如何运行

1. 直接用浏览器打开 `index.html` 文件
2. 或使用本地服务器：
   ```bash
   # Python 3
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

- HTML5
- CSS3 (动画、Flexbox、Grid)
- JavaScript (ES6+)
- 无外部框架依赖

---

*由 AI Game Company 自动生成*
"""
        (gen_dir / "README.md").write_text(readme, encoding="utf-8")
        state["files_generated"].append("README.md")

    def _generate_tree(self, gen_dir):
        """生成目录树结构。"""
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
        """持久化状态。"""
        (gen_dir / "generation_state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
