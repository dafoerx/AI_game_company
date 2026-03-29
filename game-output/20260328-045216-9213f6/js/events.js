const Events = {
  // 当前弹窗中的事件
  currentEvent: null,
  // 是否已完成初始化
  _inited: false,
  // 是否正在处理选项（防止连点）
  _processingChoice: false,

  // DOM 缓存
  dom: {
    modal: null,
    icon: null,
    title: null,
    description: null,
    choices: null,
    closeButtons: []
  },

  /**
   * 初始化事件系统
   * - 绑定关闭按钮
   * - 绑定 ESC/遮罩交互
   */
  init() {
    if (this._inited) return;
    this._inited = true;

    this.dom.modal = document.getElementById("event-modal");
    this.dom.icon = document.getElementById("event-icon");
    this.dom.title = document.getElementById("event-title");
    this.dom.description = document.getElementById("event-description");
    this.dom.choices = document.getElementById("event-choices");

    if (!this.dom.modal) {
      console.warn("[Events] 未找到 #event-modal，事件系统将不可见。");
      return;
    }

    // 兼容多种关闭按钮命名
    this.dom.closeButtons = Array.from(
      this.dom.modal.querySelectorAll(
        ".modal-close, .event-close, [data-close-event], .close-btn, .close"
      )
    );

    this.dom.closeButtons.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        this._handleCloseAttempt();
      });
    });

    // 点击遮罩尝试关闭
    this.dom.modal.addEventListener("click", (e) => {
      if (e.target === this.dom.modal) {
        this._handleCloseAttempt();
      }
    });

    // ESC 尝试关闭
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.isModalOpen()) {
        this._handleCloseAttempt();
      }
    });
  },

  /**
   * 根据回合、once、权重等条件触发随机事件
   * @returns {object|null} 被触发的事件对象
   */
  triggerRandomEvent() {
    if (this.currentEvent) return null;
    if (!GameData || !Array.isArray(GameData.events) || GameData.events.length === 0) return null;
    if (!Game || !Game.state) return null;

    const turn = Number(Game.state.turn || 0);
    const triggered = Array.isArray(Game.state.triggeredEvents) ? Game.state.triggeredEvents : [];

    // 过滤可触发事件
    const candidates = GameData.events.filter((event) => {
      if (!event || !event.id) return false;

      if (typeof event.minTurn === "number" && turn < event.minTurn) return false;
      if (typeof event.maxTurn === "number" && turn > event.maxTurn) return false;
      if (event.once === true && triggered.includes(event.id)) return false;

      // 必须有可选项
      if (!Array.isArray(event.choices) || event.choices.length === 0) return false;

      return true;
    });

    if (candidates.length === 0) return null;

    // 权重随机
    let totalWeight = 0;
    const normalized = candidates.map((event) => {
      let w = Number(event.weight);
      if (!Number.isFinite(w)) w = 1;
      if (w < 0) w = 0;
      totalWeight += w;
      return { event, weight: w };
    });

    let selected = null;

    if (totalWeight <= 0) {
      // 全部权重不可用时，等概率随机
      selected = candidates[Math.floor(Math.random() * candidates.length)];
    } else {
      let r = Math.random() * totalWeight;
      for (let i = 0; i < normalized.length; i++) {
        r -= normalized[i].weight;
        if (r <= 0) {
          selected = normalized[i].event;
          break;
        }
      }
      if (!selected) selected = normalized[normalized.length - 1].event;
    }

    this.showEvent(selected);
    return selected;
  },

  /**
   * 显示事件弹窗
   * @param {object} event 事件对象
   */
  showEvent(event) {
    if (!event) return;
    this.init();
    if (!this.dom.modal) return;

    this.currentEvent = event;
    this._processingChoice = false;

    if (this.dom.icon) this.dom.icon.textContent = event.icon || "📢";
    if (this.dom.title) this.dom.title.textContent = event.title || "突发事件";
    if (this.dom.description) this.dom.description.textContent = event.description || "";

    if (this.dom.choices) {
      this.dom.choices.innerHTML = "";

      const choices = Array.isArray(event.choices) ? event.choices : [];
      choices.forEach((choice, index) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "event-choice";

        const text = document.createElement("div");
        text.className = "choice-text";
        text.textContent = choice.text || `选项 ${index + 1}`;

        const effect = document.createElement("div");
        effect.className = "choice-effect";
        effect.textContent = this.formatEffect(choice.effect);

        btn.appendChild(text);
        btn.appendChild(effect);

        btn.addEventListener("click", () => {
          this.selectChoice(index, event.id);
        });

        this.dom.choices.appendChild(btn);
      });
    }

    this._openModal();
  },

  /**
   * 处理玩家选项
   * @param {number} choiceIndex 选项序号
   * @param {string} eventId 事件 ID
   */
  selectChoice(choiceIndex, eventId) {
    if (this._processingChoice) return;
    this._processingChoice = true;

    try {
      const event =
        (Array.isArray(GameData?.events) && GameData.events.find((e) => e.id === eventId)) ||
        this.currentEvent;

      if (!event || !Array.isArray(event.choices)) {
        this._processingChoice = false;
        this._closeModal();
        return;
      }

      const choice = event.choices[choiceIndex];
      if (!choice) {
        this._processingChoice = false;
        return;
      }

      // 契约：效果必须在 choice.effect
      const effect = choice.effect || {};

      // 应用事件效果
      if (Game?.state?.applyEventEffect) {
        Game.state.applyEventEffect(effect);
      }

      // 记录已触发事件（去重）
      if (Game?.state) {
        if (!Array.isArray(Game.state.triggeredEvents)) {
          Game.state.triggeredEvents = [];
        }
        if (event.id && !Game.state.triggeredEvents.includes(event.id)) {
          Game.state.triggeredEvents.push(event.id);
        }
      }

      // 日志信息
      const message =
        effect.message ||
        `你选择了「${choice.text || "未知选项"}」：${this.formatEffect(effect)}`;
      const messageType = effect.messageType || "info";

      if (UI?.addLog) {
        UI.addLog(message, messageType);
      }

      // 刷新 UI
      if (UI?.updateAll) {
        UI.updateAll();
      }

      this.currentEvent = null;
      this._closeModal();
    } finally {
      this._processingChoice = false;
    }
  },

  /**
   * 格式化效果文本
   * @param {object} effect
   * @returns {string}
   */
  formatEffect(effect) {
    if (!effect || typeof effect !== "object") return "无直接效果";

    const parts = [];
    const resourceMeta = Array.isArray(GameData?.resources) ? GameData.resources : [];
    const resourceMap = new Map(resourceMeta.map((r) => [r.id, r]));

    // 资源变化（扁平对象）
    const res = effect.resources;
    if (res && typeof res === "object") {
      Object.keys(res).forEach((resId) => {
        const delta = Number(res[resId] || 0);
        if (!Number.isFinite(delta) || delta === 0) return;

        const meta = resourceMap.get(resId);
        const sign = delta > 0 ? "+" : "";
        const label = meta ? `${meta.icon || "📦"}${meta.name || resId}` : resId;

        parts.push(`${label} ${sign}${this._fmtNum(delta)}`);
      });
    }

    // 人口变化（可选）
    if (typeof effect.population === "number" && effect.population !== 0) {
      const sign = effect.population > 0 ? "+" : "";
      parts.push(`👥人口 ${sign}${this._fmtNum(effect.population)}`);
    }

    return parts.length > 0 ? parts.join(" ｜ ") : "无直接效果";
  },

  // ---------- 内部工具 ----------

  isModalOpen() {
    if (!this.dom.modal) return false;
    return (
      this.dom.modal.classList.contains("show") ||
      this.dom.modal.classList.contains("active") ||
      this.dom.modal.classList.contains("visible") ||
      this.dom.modal.getAttribute("aria-hidden") === "false" ||
      this.dom.modal.style.display === "flex" ||
      this.dom.modal.style.display === "block"
    );
  },

  _openModal() {
    if (!this.dom.modal) return;
    this.dom.modal.classList.add("show", "active", "visible");
    this.dom.modal.setAttribute("aria-hidden", "false");
    if (!this.dom.modal.style.display || this.dom.modal.style.display === "none") {
      this.dom.modal.style.display = "flex";
    }
  },

  _closeModal() {
    if (!this.dom.modal) return;
    this.dom.modal.classList.remove("show", "active", "visible");
    this.dom.modal.setAttribute("aria-hidden", "true");
    this.dom.modal.style.display = "none";
  },

  _handleCloseAttempt() {
    // 事件需要玩家明确做出选择，防止无成本跳过
    if (this.currentEvent) {
      this._shakeModal();
      if (UI?.addLog) {
        UI.addLog("请先做出选择，毛孩子们正在等待你的决定。", "warning");
      }
      return;
    }
    this._closeModal();
  },

  _shakeModal() {
    if (!this.dom.modal) return;
    this.dom.modal.classList.remove("event-shake");
    // 强制重绘后再加类，确保动画可重复触发
    void this.dom.modal.offsetWidth;
    this.dom.modal.classList.add("event-shake");
    setTimeout(() => {
      if (this.dom.modal) this.dom.modal.classList.remove("event-shake");
    }, 380);
  },

  _fmtNum(n) {
    return Number(n).toLocaleString("zh-CN");
  }
};

// 暴露到全局
window.Events = Events;

// 自动初始化（同时支持外部手动再次调用，内部有幂等保护）
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => Events.init());
} else {
  Events.init();
}