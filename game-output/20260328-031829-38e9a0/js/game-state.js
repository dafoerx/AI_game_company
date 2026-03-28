"use strict";

(function () {
  class GameState {
    constructor() {
      if (typeof GameData === "undefined") {
        throw new Error("GameData 未定义，请先加载 data.js");
      }
      this.reset();
    }

    // 初始化/重置游戏状态
    reset() {
      this.maxTurns = this._num(GameData.maxTurns, 30);
      if (this.maxTurns <= 0) this.maxTurns = 30;

      this.turn = 1;
      this.population = Math.max(0, Math.floor(this._num(GameData.initialPopulation, 0)));

      // 资源与建筑定义映射
      this.resourceDefs = Array.isArray(GameData.resources) ? GameData.resources : [];
      this.resourceDefsById = {};
      this.resourceOrder = [];

      this.resources = {};
      for (const def of this.resourceDefs) {
        if (!def || !def.id) continue;
        this.resourceDefsById[def.id] = def;
        this.resourceOrder.push(def.id);

        const initial = Math.max(0, this._num(def.initial, 0));
        const maxValue = this._getMax(def);
        this.resources[def.id] = Math.min(initial, maxValue);
      }

      this.buildingDefs = Array.isArray(GameData.buildings) ? GameData.buildings : [];
      this.buildingDefsById = {};
      this.buildings = {};
      for (const b of this.buildingDefs) {
        if (!b || !b.id) continue;
        this.buildingDefsById[b.id] = b;
        this.buildings[b.id] = 0;
      }

      // 统计数据（用于复盘）
      this.stats = {
        initialResources: { ...this.resources },
        turnsProcessed: 0,
        buildingsConstructed: 0,
        eventsApplied: 0,
        totalIncome: 0, // 现金总流入
        totalExpense: 0, // 现金总流出
        totalWaste: 0, // 资源溢出浪费
        peakCash: this.resources.cash || 0,
        lowestCash: this.resources.cash || 0,
        reputationHistory:
          typeof this.resources.reputation === "number" ? [this.resources.reputation] : [],
        dailySnapshots: [],
      };

      return this;
    }

    // 处理一个营业回合（一天）
    processTurn() {
      const preEnd = this.checkEndCondition();
      if (preEnd.ended) {
        return {
          resourceChanges: {},
          messages: [{ type: preEnd.victory ? "success" : "danger", text: preEnd.message }],
        };
      }

      const plan = this._calculateTurnPlan();
      const resourceChanges = {};
      const messages = [];

      // 建筑运转不足提示
      for (const buildingId in plan.buildingReport) {
        const report = plan.buildingReport[buildingId];
        if (!report || report.skipped <= 0) continue;
        const bDef = this.buildingDefsById[buildingId];
        const bName = bDef ? bDef.name : buildingId;
        messages.push({
          type: "warning",
          text: `${bName} 有 ${report.skipped} 次未能运转（库存不足）。`,
        });
      }

      // 应用资源变化并处理上下限
      for (const resourceId of this.resourceOrder) {
        const def = this.resourceDefsById[resourceId];
        const before = this.resources[resourceId] || 0;
        const plannedDelta = this._num(plan.deltas[resourceId], 0);
        const rawAfter = before + plannedDelta;
        const after = this._clampResource(resourceId, rawAfter);
        const actualDelta = after - before;

        this.resources[resourceId] = after;
        resourceChanges[resourceId] = actualDelta;

        // 现金流水统计
        if (resourceId === "cash") {
          this._trackCash(actualDelta);
        }

        // 溢出浪费统计（非现金更有意义）
        const maxValue = this._getMax(def);
        if (rawAfter > maxValue && resourceId !== "cash") {
          const waste = rawAfter - maxValue;
          this.stats.totalWaste += waste;
          if (waste > 0) {
            messages.push({
              type: "info",
              text: `${def.name} 超出库存上限，浪费 ${Math.floor(waste)}。`,
            });
          }
        }

        // 低库存警告
        if (
          typeof def.warningThreshold === "number" &&
          after <= def.warningThreshold
        ) {
          messages.push({
            type: "warning",
            text: `${def.name} 偏低（当前 ${Math.floor(after)}），建议尽快补给。`,
          });
        }
      }

      this.stats.turnsProcessed += 1;
      this.turn += 1;

      if (typeof this.resources.reputation === "number") {
        this.stats.reputationHistory.push(this.resources.reputation);
      }

      this.stats.dailySnapshots.push({
        turn: this.turn - 1,
        resourceChanges: { ...resourceChanges },
        resources: { ...this.resources },
        buildingReport: this._cloneSimple(plan.buildingReport),
      });

      const end = this.checkEndCondition();
      if (end.ended) {
        messages.push({
          type: end.victory ? "success" : "danger",
          text: end.message,
        });
      }

      return { resourceChanges, messages };
    }

    // 计算某个资源在当前回合的变化值（含上下限修正后的实际值）
    calculateResourceChange(resourceId) {
      if (!this.resourceDefsById[resourceId]) return 0;
      const plan = this._calculateTurnPlan();
      const before = this.resources[resourceId] || 0;
      const rawAfter = before + this._num(plan.deltas[resourceId], 0);
      const after = this._clampResource(resourceId, rawAfter);
      return after - before;
    }

    // 建造建筑
    build(buildingId) {
      const buildingData = this.buildingDefsById[buildingId];
      if (!buildingData) {
        return { success: false, message: "建造失败：建筑不存在。" };
      }

      const cost = buildingData.cost || {};
      const lacks = [];

      // 检查资源是否足够
      for (const resourceId in cost) {
        const need = this._num(cost[resourceId], 0);
        if (need <= 0) continue;
        const have = this.resources[resourceId] || 0;
        if (have < need) {
          const name = this.resourceDefsById[resourceId]
            ? this.resourceDefsById[resourceId].name
            : resourceId;
          lacks.push(`${name}(${Math.ceil(need - have)})`);
        }
      }

      if (lacks.length > 0) {
        return {
          success: false,
          message: `建造失败：资源不足，缺少 ${lacks.join("、")}。`,
        };
      }

      // 扣除建造消耗
      for (const resourceId in cost) {
        const need = this._num(cost[resourceId], 0);
        if (need <= 0) continue;
        if (typeof this.resources[resourceId] !== "number") continue;

        const before = this.resources[resourceId];
        const after = this._clampResource(resourceId, before - need);
        const actualDelta = after - before;
        this.resources[resourceId] = after;

        if (resourceId === "cash") {
          this._trackCash(actualDelta);
        }
      }

      this.buildings[buildingId] = (this.buildings[buildingId] || 0) + 1;
      this.stats.buildingsConstructed += 1;

      return {
        success: true,
        message: `成功建造 ${buildingData.name}，当前数量：${this.buildings[buildingId]}。`,
      };
    }

    // 检查结束条件
    checkEndCondition() {
      // 失败条件：关键资源归零
      for (const def of this.resourceDefs) {
        if (!def || !def.id) continue;
        if (def.failIfZero && (this.resources[def.id] || 0) <= 0) {
          return {
            ended: true,
            victory: false,
            message: `${def.name} 归零，经营失败，店铺被迫停业。`,
          };
        }
      }

      // 到达最大营业天数
      if (this.turn > this.maxTurns) {
        let victory = true;
        if (typeof GameData.victoryCondition === "function") {
          try {
            victory = !!GameData.victoryCondition(this);
          } catch (e) {
            victory = true;
          }
        }

        const net = this.stats.totalIncome - this.stats.totalExpense;
        return {
          ended: true,
          victory,
          message: victory
            ? `30天经营结束！你稳住了门店运营，净现金流 ${Math.floor(net)}。`
            : `30天经营结束，但未达到目标，净现金流 ${Math.floor(net)}。`,
        };
      }

      return { ended: false, victory: false, message: "" };
    }

    // 应用事件效果（effect.resources 为扁平对象）
    applyEventEffect(effect) {
      const safeEffect = effect || {};
      const changes = {};
      let populationChange = 0;

      const resourcesEffect =
        safeEffect.resources && typeof safeEffect.resources === "object"
          ? safeEffect.resources
          : {};

      for (const resourceId in resourcesEffect) {
        if (!this.resourceDefsById[resourceId]) continue;

        const delta = this._num(resourcesEffect[resourceId], 0);
        const before = this.resources[resourceId] || 0;
        const rawAfter = before + delta;
        const after = this._clampResource(resourceId, rawAfter);
        const actualDelta = after - before;

        this.resources[resourceId] = after;
        changes[resourceId] = actualDelta;

        if (resourceId === "cash") {
          this._trackCash(actualDelta);
        }

        const def = this.resourceDefsById[resourceId];
        const maxValue = this._getMax(def);
        if (rawAfter > maxValue && resourceId !== "cash") {
          this.stats.totalWaste += rawAfter - maxValue;
        }
      }

      if (typeof safeEffect.population === "number") {
        const beforePop = this.population;
        this.population = Math.max(0, Math.floor(beforePop + safeEffect.population));
        populationChange = this.population - beforePop;
      }

      this.stats.eventsApplied += 1;

      return {
        resourceChanges: changes,
        populationChange,
        message: safeEffect.message || "",
        messageType: safeEffect.messageType || "info",
      };
    }

    // 获取当前统计与状态
    getStats() {
      const resourcesArray = this.resourceOrder.map((id) => {
        const def = this.resourceDefsById[id];
        const value = this.resources[id] || 0;
        const max = this._getMax(def);
        const ratio = max > 0 && Number.isFinite(max) ? value / max : 0;
        return {
          id,
          name: def.name,
          icon: def.icon || "",
          value,
          max,
          ratio,
          warning:
            typeof def.warningThreshold === "number" ? value <= def.warningThreshold : false,
        };
      });

      const buildingsArray = this.buildingDefs.map((b) => ({
        id: b.id,
        name: b.name,
        icon: b.icon || "",
        count: this.buildings[b.id] || 0,
        cost: this._cloneSimple(b.cost || {}),
        produces: this._cloneSimple(b.produces || {}),
        consumes: this._cloneSimple(b.consumes || {}),
      }));

      const netProfit = this.stats.totalIncome - this.stats.totalExpense;

      return {
        name: GameData.name || "未命名游戏",
        turn: this.turn,
        maxTurns: this.maxTurns,
        remainingTurns: Math.max(0, this.maxTurns - this.turn + 1),
        population: this.population,
        resources: { ...this.resources },
        resourcesArray,
        buildings: { ...this.buildings },
        buildingsArray,
        finance: {
          cash: this.resources.cash || 0,
          totalIncome: this.stats.totalIncome,
          totalExpense: this.stats.totalExpense,
          netProfit,
          peakCash: this.stats.peakCash,
          lowestCash: this.stats.lowestCash,
        },
        operation: {
          buildingsConstructed: this.stats.buildingsConstructed,
          eventsApplied: this.stats.eventsApplied,
          totalWaste: this.stats.totalWaste,
          turnsProcessed: this.stats.turnsProcessed,
        },
        history: {
          reputationHistory: [...this.stats.reputationHistory],
          dailySnapshots: this._cloneSimple(this.stats.dailySnapshots),
        },
      };
    }

    // ===== 内部方法 =====

    // 计算本回合整体计划（不直接修改状态）
    _calculateTurnPlan() {
      const deltas = {};
      const temp = {};
      const buildingReport = {};

      // 初始化
      for (const id of this.resourceOrder) {
        deltas[id] = 0;
        temp[id] = this.resources[id] || 0;
      }

      // 资源基础变化（perTurn + 人口消耗）
      for (const def of this.resourceDefs) {
        const id = def.id;
        if (!id) continue;

        const base = this._num(def.perTurn, 0);
        const popCost =
          Math.max(0, this._num(def.consumedPerPopulation, 0)) * this.population;
        const baseDelta = base - popCost;

        deltas[id] += baseDelta;
        temp[id] = Math.max(0, (temp[id] || 0) + baseDelta);
      }

      // 建筑运转（关键：produces / consumes 都是扁平对象，直接读取）
      for (const bDef of this.buildingDefs) {
        const bid = bDef.id;
        const count = this.buildings[bid] || 0;
        if (count <= 0) continue;

        const report = { active: 0, skipped: 0 };

        for (let i = 0; i < count; i++) {
          const consumes = bDef.consumes || {};
          let canRun = true;

          // 先判断是否能支付消耗
          for (const resourceId in consumes) {
            if (!this.resourceDefsById[resourceId]) continue;
            const need = this._num(consumes[resourceId], 0);
            if (need <= 0) continue;
            if ((temp[resourceId] || 0) < need) {
              canRun = false;
              break;
            }
          }

          if (!canRun) {
            report.skipped += 1;
            continue;
          }

          // 扣除消耗
          for (const resourceId in consumes) {
            if (!this.resourceDefsById[resourceId]) continue;
            const need = this._num(consumes[resourceId], 0);
            if (need <= 0) continue;
            temp[resourceId] -= need;
            deltas[resourceId] -= need;
          }

          // 增加产出
          const produces = bDef.produces || {};
          for (const resourceId in produces) {
            if (!this.resourceDefsById[resourceId]) continue;
            const gain = this._num(produces[resourceId], 0);
            if (gain === 0) continue;
            temp[resourceId] = (temp[resourceId] || 0) + gain;
            deltas[resourceId] += gain;
          }

          report.active += 1;
        }

        buildingReport[bid] = report;
      }

      return { deltas, temp, buildingReport };
    }

    _trackCash(delta) {
      const d = this._num(delta, 0);
      if (d > 0) this.stats.totalIncome += d;
      if (d < 0) this.stats.totalExpense += -d;

      const cash = this.resources.cash || 0;
      if (cash > this.stats.peakCash) this.stats.peakCash = cash;
      if (cash < this.stats.lowestCash) this.stats.lowestCash = cash;
    }

    _clampResource(resourceId, value) {
      const def = this.resourceDefsById[resourceId];
      const max = this._getMax(def);
      let v = this._num(value, 0);
      if (v < 0) v = 0;
      if (v > max) v = max;
      return v;
    }

    _getMax(def) {
      const m = Number(def && def.max);
      if (Number.isFinite(m) && m >= 0) return m;
      return Infinity;
    }

    _num(v, fallback = 0) {
      const n = Number(v);
      return Number.isFinite(n) ? n : fallback;
    }

    _cloneSimple(obj) {
      try {
        return JSON.parse(JSON.stringify(obj));
      } catch (e) {
        return obj;
      }
    }
  }

  if (typeof window !== "undefined") {
    window.GameState = GameState;
  }
  if (typeof globalThis !== "undefined") {
    globalThis.GameState = GameState;
  }
})();