# AI_game_company

这是一个用于沉淀 **模拟经营类游戏项目规划、团队分工、MVP 范围、角色 Skill 与推进记录** 的仓库。

当前已经冻结的关键决策：

- **游戏主题**：AI 游戏公司经营模拟（Web 原型验证版）
- **研发方式**：3～5 人真人核心团队 + AI 员工协作
- **推荐配置**：4 人核心团队（制作人/主策划、Web 技术负责人、视觉/UI 负责人、系统/数值/内容策划）
- **目标平台**：Web
- **商业目标**：原型验证
- **研发工作流**：OpenCode + GPT-5.3-Codex

## 仓库目录

```text
.
├─ README.md
├─ docs/
│  ├─ 00-项目总览/
│  │  ├─ PROJECT_BRIEF.md
│  │  └─ THEME_PLATFORM_GOAL.md
│  ├─ 01-团队规划/
│  │  └─ TEAM_ROLES_AI.md
│  ├─ 02-MVP规划/
│  │  └─ MVP_SCOPE.md
│  ├─ 03-研发排期/
│  │  └─ ROADMAP_8_WEEKS.md
│  ├─ 04-研发工具链/
│  │  └─ DEV_TOOLCHAIN.md
│  ├─ 05-角色Skills/
│  │  └─ ROLE_SKILLS_INDEX.md
│  └─ 99-过程记录/
│     ├─ 2026-03-26_项目启动记录.md
│     └─ 2026-03-26_主题平台与Skills定稿.md
└─ .workbuddy/
   └─ skills/
      ├─ ai-game-company-producer/
      ├─ ai-game-company-web-tech-lead/
      ├─ ai-game-company-visual-ui/
      ├─ ai-game-company-systems-economy/
      └─ ai-game-company-prototype-qa/
```

## 文档用途

- `00-项目总览`：沉淀项目定位、主题选择依据、平台与商业目标。
- `01-团队规划`：明确 3～5 人团队下的岗位设计，以及 AI 员工如何协作。
- `02-MVP规划`：定义首个可玩版本必须包含的系统与明确不做的内容。
- `03-研发排期`：给出 8 周左右的初版推进节奏。
- `04-研发工具链`：固定研发工作流、工程协作方式与默认技术建议。
- `05-角色Skills`：索引项目级角色 Skill，便于按岗位直接调用。
- `99-过程记录`：记录关键决策、阶段性结论与后续动作。
- `.workbuddy/skills`：项目级 Skill 实体文件，随仓库共享。

## 当前主题结论

基于对“游戏开发/公司经营”题材和 Web 原型适配性的调研，当前最适合本项目的方向是：

> **玩家经营一家 AI 原生游戏创业公司，在现金、口碑、算力、团队与项目之间做取舍，用 AI 员工与少量核心骨干持续推出产品并扩张公司。**

这个题材的优势：

1. **很适合 Web 原型**：以面板、卡片、进度条、表格和弹窗为主，低成本即可验证核心乐趣。
2. **题材自洽**：与“AI 员工协作”这个项目现实背景天然一致。
3. **系统延展性强**：容易从项目管理、招聘、研发、宣发、服务器、社区等模块逐步扩展。
4. **原型验证友好**：即便视觉资源不多，也能通过数值、任务和决策反馈快速验证是否好玩。

## 建议使用方式

1. 先阅读 `PROJECT_BRIEF.md` 和 `THEME_PLATFORM_GOAL.md`，确认主题与边界。
2. 以 `TEAM_ROLES_AI.md` 作为组织结构基线。
3. 以 `MVP_SCOPE.md` 控制范围，避免功能膨胀。
4. 以 `DEV_TOOLCHAIN.md` 对齐 OpenCode + GPT-5.3-Codex 的研发方式。
5. 通过 `ROLE_SKILLS_INDEX.md` 找到对应岗位 Skill 并直接使用。
6. 每次关键决策、范围调整、试玩反馈都追加到 `99-过程记录/`。

## 运行与协作（Producer 主导 + 多角色共识系统）

仓库内已提供可单机运行的 **Producer 主导项目引擎 + 多角色共识系统**，支持：

- 🚀 **一句话启动项目**：输入方向描述，Producer 自动完成完整项目规划
- 📋 **Producer 自动拆解任务**：生成结构化任务卡片，按优先级排序
- 🤝 **多角色共识推进**：逐任务发起多角色讨论，Producer 收口决策
- 📊 **实时可视化**：Web 页面实时查看项目进展、任务状态、共识记录

### 1) 环境准备

```bash
cd AI_game_company
pip install -r requirements.txt
```

### 2) 启动服务

```bash
python run_server.py
```

启动后在浏览器打开：`http://127.0.0.1:8000`

### 3) 启动新项目（核心用法）

1. 打开 Web 页面，在顶部 **"🚀 启动新项目"** 区域输入一句话方向描述
2. 示例输入：
   - `火锅店运营，Web端，水墨画风`
   - `太空殖民模拟，移动端，赛博朋克风格`
   - `咖啡馆经营，Web端，像素复古风`
3. 点击 **"🚀 启动项目"** 按钮
4. **Producer 自动执行**：
   - 调用 LLM 生成完整项目规划（项目名称、主题、MVP 范围、里程碑、任务拆分）
   - 将规划写入 `project-drive`（active-context、task-cards）
   - 按任务优先级逐个发起多角色共识
   - 在每个阶段做收口决策并推进到下一任务

### 4) 页面功能

| 区域 | 说明 |
|------|------|
| **启动新项目** | 输入一句话方向，一键启动 |
| **项目列表** | 查看所有项目及状态（规划中 / 进行中 / 已完成） |
| **项目详情** | 点击项目查看：进度条、任务列表、当前阶段 |
| **📝 实时日志** | 项目推进过程的实时 log |
| **📑 任务总览** | 所有任务卡片及状态（pending / in_progress / done） |
| **🤝 共识记录** | 每个任务的多角色共识详情 |
| **当前活跃 TASK** | 从 active-context 自动识别（兼容旧流程） |
| **自定义共识** | 手动输入目标发起共识（兼容旧流程） |

### 5) 输出文件位置

项目规划和运行过程写入：

```text
project-drive/
├─ 00-active-context.md          # 当前活跃项目上下文
├─ 02-task-cards/
│  ├─ pending/                   # 待处理任务
│  └─ in-progress/               # 进行中任务
└─ runtime/runs/<run_id>/
   ├─ state.json                 # 运行状态
   ├─ round-*/<role>.md          # 每轮各角色输出
   └─ consensus.md               # 共识结论
```

### 6) 模型配置

当前默认模型配置：

- `CUSTOM_LLM_BASE_URL=https://capi.quan2go.com/v1`
- `CUSTOM_LLM_MODEL=gpt-5.3-codex`
- `CUSTOM_LLM_API_KEY=<你的key>`

也可通过环境变量覆盖：

```bash
# Linux / macOS
export CUSTOM_LLM_BASE_URL="https://capi.quan2go.com/v1"
export CUSTOM_LLM_MODEL="gpt-5.3-codex"
export CUSTOM_LLM_API_KEY="<你的key>"
python run_server.py

# Windows PowerShell
$env:CUSTOM_LLM_BASE_URL="https://capi.quan2go.com/v1"
$env:CUSTOM_LLM_MODEL="gpt-5.3-codex"
$env:CUSTOM_LLM_API_KEY="<你的key>"
python run_server.py
```

### 7) API 接口

#### 项目管理（新）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/projects` | 启动新项目，body: `{"direction": "火锅店运营，Web端，水墨画风"}` |
| `GET` | `/api/projects` | 获取所有项目列表 |
| `GET` | `/api/projects/<id>` | 获取项目详情（含任务状态、共识记录） |

#### 共识系统（兼容）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `GET` | `/api/active-task` | 获取当前活跃任务 |
| `POST` | `/api/runs` | 发起自定义共识 |
| `POST` | `/api/runs/active-task` | 一键发起活跃任务共识 |
| `GET` | `/api/runs` | 获取所有运行记录 |
| `GET` | `/api/runs/<run_id>` | 获取运行详情 |

### 8) 典型工作流

```
用户输入: "火锅店运营，Web端，水墨画风"
       ↓
  Producer LLM 规划
       ↓
  生成项目结构（名称/主题/MVP/里程碑/任务）
       ↓
  写入 project-drive
       ↓
  ┌─ 任务 1: 核心玩法设计 ──→ 多角色共识 ──→ Producer 收口
  ├─ 任务 2: UI 原型设计   ──→ 多角色共识 ──→ Producer 收口
  ├─ 任务 3: 后端架构      ──→ 多角色共识 ──→ Producer 收口
  └─ ...
       ↓
  项目完成 ✅
```
