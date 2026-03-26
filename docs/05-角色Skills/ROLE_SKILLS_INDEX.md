# 角色 Skills 索引

> 参考 `小红书科技运营专家.md` 的思路，本项目的角色 Skill 采用：
>
> - YAML frontmatter 明确触发场景
> - 主文档直接写清“何时使用、怎么做、输出什么”
> - 尽量做到单个 `SKILL.md` 即可进入工作状态

## 1. 当前技能清单

| 角色 | Skill 名称 | 路径 | 用途 |
|---|---|---|---|
| 制作人 / 主策划 | `ai-game-company-producer` | `.workbuddy/skills/ai-game-company-producer/SKILL.md` | 做方向判断、范围控制、版本规划、决策文档 |
| Web 技术负责人 | `ai-game-company-web-tech-lead` | `.workbuddy/skills/ai-game-company-web-tech-lead/SKILL.md` | 做 Web 原型架构、前端实现切片、工程拆分 |
| 视觉 / UI 负责人 | `ai-game-company-visual-ui` | `.workbuddy/skills/ai-game-company-visual-ui/SKILL.md` | 做信息架构、界面风格、组件规则、视觉边界 |
| 系统 / 数值 / 内容策划 | `ai-game-company-systems-economy` | `.workbuddy/skills/ai-game-company-systems-economy/SKILL.md` | 做资源系统、经济循环、成长节奏、配置框架 |
| 原型验证 / QA | `ai-game-company-prototype-qa` | `.workbuddy/skills/ai-game-company-prototype-qa/SKILL.md` | 做测试点、验证指标、Bug 分级、试玩复盘 |

## 2. 推荐使用顺序

对于当前阶段，最推荐的顺序是：

1. **制作人 / 主策划 Skill**：明确要做什么、不做什么
2. **系统 / 数值 / 内容策划 Skill**：确定资源流和成长节奏
3. **Web 技术负责人 Skill**：拆前端切片与实现路径
4. **视觉 / UI 负责人 Skill**：统一界面结构和视觉风格
5. **原型验证 / QA Skill**：定义验证标准和试玩问题

## 3. 每个 Skill 的定位原则

### 制作人 / 主策划
- 解决“方向对不对”
- 解决“做什么、不做什么”
- 输出决定性文档，而不是泛泛讨论

### Web 技术负责人
- 解决“怎么落地”
- 优先做 Web 原型的最短可玩路径
- 代码与结构以可演示、可迭代为核心

### 视觉 / UI 负责人
- 解决“信息怎么看、怎么点、怎么反馈”
- 不追求一开始高保真，先追求清晰统一

### 系统 / 数值 / 内容策划
- 解决“为什么想继续玩”
- 把资源、升级、口碑、算力、团队效率串成正反馈

### 原型验证 / QA
- 解决“是否真的成立”
- 围绕理解成本、策略感、连续游玩意愿建立验证标准

## 4. 当前建议

这些 Skill 都已经按项目级方式放进仓库里，后续可继续迭代：

- 如果角色职责变化，直接改对应 `SKILL.md`
- 如果某个角色开始依赖模板或脚本，再往该 Skill 目录里增加 `references/`、`scripts/` 或 `assets/`
- 如果主题或平台变化，优先同步更新所有 Skill 中的项目假设
