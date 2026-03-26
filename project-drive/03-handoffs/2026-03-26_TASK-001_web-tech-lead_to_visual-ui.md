# HANDOFF: TASK-001 技术评审答复

## 基本信息

- **任务编号**：TASK-001
- **发送角色**：web-tech-lead
- **接收角色**：visual-ui
- **日期**：2026-03-26
- **状态**：已答复

## 本轮完成内容

- 评审TASK-001设计的技术可行性
- 分析前端单体架构的承载能力
- 设计最小实现架构方案
- 制定首批开发任务拆分方向

## Tech Lead 确认项

### 1. 架构确认
- **前端框架**：React + TypeScript + Vite + Tailwind CSS（符合DEV_TOOLCHAIN.md）
- **状态管理**：初期使用React Context + useReducer，复杂后迁移至Zustand
- **数据存储**：localStorage + IndexedDB（大型存档）
- **时间推进**：混合方案（手动推进为主，可选定时器自动推进）

### 2. 技术可行性评估
- **5个核心资源状态管理**：✅ 可行，适合单一前端状态树
- **三类数据结构**：✅ 足够支撑首版（公司/员工/项目）
- **交互复杂度**：⚠️ 拖拽分配建议降级为首版点击分配
- **本地存档**：✅ 可行，使用JSON序列化+压缩

### 3. 实现边界确认
- 坚持前端单体原型，不引入后端
- 优先保证15～30分钟体验节奏
- 异常处理和恢复机制必须完善
- 性能监控和调试工具集成

## Tech Lead 答复项

### 问题1：技术可行性 - 5个核心资源的状态管理
**答复**：完全可行。5个核心资源（现金、算力、士气、口碑、进度）适合单一状态树管理。

**建议架构**：
```typescript
interface GameState {
  company: CompanyState;
  employees: Employee[];
  projects: Project[];
  events: GameEvent[];
  time: GameTime;
}

interface CompanyState {
  cash: number;
  computePower: number;
  computeMax: number;
  morale: number;
  reputation: number;
  officeLevel: number;
  serverLevel: number;
}
```

**状态管理方案**：
- 初期：React Context + useReducer（简单可控）
- 中期：Zustand（当状态复杂度增加时）
- 存档：自动序列化整个状态树到localStorage

### 问题2：时间推进方案
**答复**：推荐混合方案，以手动推进为主，可选定时器自动推进。

**方案设计**：
```typescript
// 方案A：手动推进（玩家点击"推进一周"）
const advanceTime = (days: number) => {
  // 计算资源变化
  // 触发事件
  // 更新进度
};

// 方案B：定时器自动推进（可选功能）
const startAutoAdvance = (intervalMs: number) => {
  // 按现实时间间隔推进游戏时间
};
```

**建议**：首版实现手动推进，验证核心循环后再考虑自动推进选项。

### 问题3：数据结构是否足够
**答复**：公司/员工/项目三类数据结构足够支撑首版。

**数据结构优化建议**：
```typescript
// 1. 公司状态（扁平化设计）
type CompanyState = {
  // 基础资源
  cash: number;
  computePower: number;
  computeMax: number;
  morale: number;
  reputation: number;
  
  // 基础设施
  officeLevel: number;
  serverLevel: number;
  toolLevel: number;
  
  // 时间相关
  currentDate: string;
  gameSpeed: number;
};

// 2. 员工数据（最小字段集）
type Employee = {
  id: string;
  name: string;
  type: 'human' | 'ai';
  level: number;
  specialty: EmployeeSpecialty;
  currentTask: string | null;
  fatigue: number; // 0-100
  salary: number;
};

// 3. 项目数据（进度管理）
type Project = {
  id: string;
  name: string;
  type: ProjectType;
  size: 'small' | 'medium' | 'large';
  progress: number; // 0-100
  expectedRevenue: number;
  computeCost: number;
  startDate: string;
  estimatedEnd: string;
  assignedEmployees: string[]; // 员工ID数组
};
```

### 问题4：交互复杂度控制
**答复**：建议对交互进行适当降级，确保首版可快速实现。

**降级建议**：
1. **拖拽分配 → 点击分配**
   - 原设计：拖拽员工到项目卡片
   - 降级后：点击员工→点击"分配"按钮→选择项目
   - 理由：实现简单，交互明确，移动端友好

2. **复杂事件弹窗 → 简化决策界面**
   - 原设计：多选项复杂决策弹窗
   - 降级后：简单确认/取消对话框，重要决策才用多选项
   - 理由：减少决策疲劳，加快原型验证节奏

3. **多级导航 → 单屏主界面+模态窗口**
   - 原设计：多页面导航结构
   - 降级后：单屏主界面，次要功能通过侧边栏或模态窗口访问
   - 理由：减少页面跳转，保持上下文

### 问题5：首批开发任务拆分建议
**答复**：建议按"状态流→核心页面→辅助功能"顺序拆分。

#### 第一阶段：核心状态管理（2-3天）
1. **游戏状态模型**：实现CompanyState/Employee/Project类型定义
2. **状态管理基础**：创建React Context + useReducer状态管理
3. **时间推进系统**：实现手动时间推进逻辑
4. **本地存档系统**：实现状态保存/加载到localStorage

#### 第二阶段：主界面实现（3-4天）
5. **顶部状态栏**：显示5种核心资源
6. **项目列表组件**：显示当前项目及进度
7. **员工列表组件**：显示员工状态和分配
8. **基本操作面板**：推进时间、分配员工、开始项目

#### 第三阶段：核心循环实现（2-3天）
9. **项目分配流程**：员工分配到项目的完整流程
10. **资源计算系统**：时间推进时的资源自动计算
11. **事件触发系统**：随机事件和决策处理
12. **项目完成流程**：项目完成后的收入计算

#### 第四阶段：增强功能（2-3天）
13. **公司升级界面**：升级办公室、服务器、工具
14. **数值平衡调试**：数值调整界面和工具
15. **性能优化**：状态计算优化和性能监控
16. **测试工具集成**：集成QA测试数据收集工具

## 可直接实现的功能
- 核心状态管理架构
- 手动时间推进系统
- 本地存档/读档
- 基础UI组件（状态栏、卡片列表）
- 简单点击分配交互

## 建议降级的功能
- 拖拽分配 → 点击分配
- 复杂多级导航 → 单屏主界面+模态窗口
- 实时自动推进 → 手动推进为主
- 复杂事件决策 → 简化决策界面

## 预计风险
1. **性能风险**：状态计算可能影响UI响应
   - 缓解：使用useMemo优化计算，批量状态更新
2. **数据一致性风险**：多状态同时更新可能导致不一致
   - 缓解：集中状态管理，事务性更新
3. **存档兼容性风险**：数据结构变更导致存档失效
   - 缓解：版本化存档格式，迁移工具
4. **浏览器兼容性风险**：IndexedDB和localStorage行为差异
   - 缓解：特性检测，降级方案

## 下一角色
- **visual-ui**：请基于此技术方案评审界面表达和交互设计

## 备注
- 技术方案已考虑首版MVP范围，确保2周内可产出可玩原型
- 所有建议降级的功能都可在后续版本迭代中恢复
- 建议visual-ui重点关注信息密度和操作流畅度
- 预计visual-ui评审完成后，可立即开始第一阶段开发

---
*发送者：ai-game-company-web-tech-lead*
*发送时间：2026-03-26 15:50 GMT+8*
