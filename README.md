# AI_game_company（餐饮项目改版）

这是一个用于沉淀 **餐饮经营原型规划、团队分工、MVP 范围、项目级 Skill 与执行节奏** 的仓库。

当前已经冻结的关键决策：

- **项目主题**：餐饮门店经营模拟（Web 原型验证版）
- **研发方式**：3 角执行模型 + AI 协作
- **临时角色模型**：`product-system` / `prototype-build` / `prototype-qa`
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
│  └─ 05-角色Skills/
│     └─ ROLE_SKILLS_INDEX.md
├─ project-drive/
│  ├─ README.md
│  ├─ 00-active-context.md
│  ├─ 01-role-boards/
│  ├─ 02-task-cards/
│  └─ 03-handoffs/
└─ .workbuddy/
   └─ skills/
      ├─ restaurant-product-system/
      ├─ restaurant-prototype-build/
      └─ restaurant-prototype-qa/
```

## 文档用途

- `00-项目总览`：固定主题、平台、商业目标与立项边界。
- `01-团队规划`：明确当前临时 3 角执行模型和 AI 协作方式。
- `02-MVP规划`：定义首个可玩版本要验证的餐饮经营闭环。
- `03-研发排期`：给出 8 周左右的推进节奏。
- `04-研发工具链`：固定工作方式、默认技术栈与提速原则。
- `05-角色Skills`：索引当前 3 个项目级 Skill。
- `project-drive`：保存当前阶段执行上下文、任务卡和轻量 handoff。
- `.workbuddy/skills`：项目级 Skill 实体文件，随仓库共享。

## 当前主题结论

当前项目方向调整为：

> **玩家经营一家餐饮门店，从选址、菜单、备料、出餐、顾客反馈到扩张升级之间做取舍，用最小 Web 原型先验证“经营闭环是否成立、是否愿意继续扩张”。**

这个题材的优势：

1. **易理解**：顾客、出餐、口碑、翻台、现金流这些经营要素天然直观。
2. **适合 Web 原型**：面板、订单列表、库存数字、顾客反馈和进度条就能表达核心乐趣。
3. **验证效率高**：不用高成本美术，也能先验证节奏、取舍和扩张动力。
4. **可扩展**：后续可自然扩展到菜单研发、分店扩张、员工培训、供应链与营销活动。

## 当前下一步建议

1. 先完成餐饮项目的首个经营闭环定义。
2. 把 `project-drive` 中的 `TASK-001` 收成可直接开工的版本。
3. 直接进入前端工程骨架搭建。
4. 在第一个可运行版本出来后，再补最小验证材料。
