1) **本角色判断（systems-economy）**

1. **TASK-005可以开工，但必须先冻结“数值展示口径”**。  
   UI一旦先画后改，最容易因字段变更返工。先锁字段、单位、刷新频率，再做视觉集成，效率最高。

2. **“接入真实数据”的判定应从经济口径定义**：  
   页面展示值必须来自统一状态层（非硬编码），且与日结计算同源（同一套selector/计算函数），避免“看起来对、结算不对”。

3. **点击路径≤3步可达成，但前提是采购界面做单屏闭环**：  
   建议路径定义为：  
   - 采购：主界面→采购面板→确认采购（3步内）  
   - 营业：主界面直接查看信息条核心指标（0~1步）  
   - 结算：主界面结束营业→日结面板→进入次日（3步内）

4. **营业信息条必须优先保证“经营决策最小集”可读**：  
   现金、当日营收、当日成本、库存预警、满意度、当前时段。  
   这6项足够支持“买不买、开不开、何时结”的即时决策。

5. **当前验收口径仍不完整，需要修订后再算“可验收”**：  
   缺少字段字典、公式归属、步数统计方法与埋点定义。按当前描述直接做，后续高概率反复修改。

---

2) **对其他角色的冲突点 / 共识点**

- **与 producer**
  - 共识：先可用可测，后美术精修；不扩功能。
  - 冲突点：若只谈流程不锁数值口径，最终验收仍会卡在“数据对不对”。

- **与 web-tech-lead**
  - 共识：统一状态层、组件化、可追踪。
  - 冲突点：不建议在UI层重复计算利润/成本；应由系统层输出已定义口径，UI只展示。

- **与 visual-ui**
  - 共识：信息层级清晰、按钮大、低成本高辨识。
  - 冲突点：若压缩信息过度（只留图标/弱化数字），会损失经营判断效率，影响核心玩法验证。

- **与 prototype-qa**
  - 共识：点击路径和可读性必须量化。
  - 冲突点：若不提前准备“亏损/保本/盈利”三组测试数据，无法验证UI是否正确传达经济反馈。

---

3) **下一步建议（可执行）**

1. **D0（今天）—systems-economy输出《TASK-005字段与口径v1》**（半天）  
   至少包含：字段名、单位、刷新时机、来源、显示精度。  
   - 主界面/信息条：cash, revenueToday, costToday, satisfaction, inventoryWarningCount, dayPhase  
   - 采购：itemPrice, stock, safetyStock, buyQty, buyCostTotal, cashAfterBuy  
   - 日结：revenueDay, purchaseCostDay, wasteCostDay, profitDay, satisfactionDelta, turnoverRate

2. **D1—web-tech-lead完成状态契约与埋点**  
   - 提供统一selector：`selectTopBarMetrics` / `selectPurchaseMetrics` / `selectSettlementMetrics`  
   - 埋点事件：`ui_enter_purchase`、`ui_confirm_purchase`、`ui_end_day`、`ui_settlement_next_day`  
   - 输出点击步数统计脚本（自动汇总平均步数）

3. **D2-D3—visual-ui按“先流程后皮肤”落地**  
   - 先灰度线框接真数据，再上暖色视觉资源  
   - 强制加入两种经济提示：  
     - 库存低于安全值红色高亮  
     - 采购超现金预算红色阻断提示  
   - 不做动画扩展、不加新系统入口

4. **D4—prototype-qa进行快速验收**  
   - 10条用例覆盖采购-营业-结算主路径  
   - 必测3个经济场景：亏损、保本、盈利  
   - 验收门槛：  
     - 三界面全真数据  
     - 平均点击路径≤3  
     - 显示值与结算值误差=0（同源计算）

5. **D4结束前由producer统一文档状态**  
   - 修正active-context与任务总览冲突  
   - 在TASK-005任务卡写明DoD与依赖冻结版本号（字段v1）

CONSENSUS: REVISE