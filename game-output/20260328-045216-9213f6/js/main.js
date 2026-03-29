'use strict';

/**
 * 游戏主入口对象
 * 负责：初始化、界面切换、回合推进、暂停、结算、弹窗管理
 */
const Game = {
  state: null,
  isPaused: false,
  currentScreen: 'loading-screen',

  // 内部状态
  _inited: false,
  _gameEnded: false,
  _eventsBound: false,
  _currentModalId: null,
  _loadingRAF: null,
  _loadingTipTimer: null,
  _screenIds: ['loading-screen', 'main-menu', 'game-screen', 'game-over'],

  /**
   * 初始化游戏
   */
  init() {
    if (this._inited) return;
    this._inited = true;

    // 创建游戏状态实例
    this.state = this._createGameState();

    // 绑定全局交互事件
    this._bindGlobalEvents();

    // 初始化 UI 模块
    if (typeof UI !== 'undefined' && UI && typeof UI.init === 'function') {
      try {
        UI.init(this, this.state, typeof GameData !== 'undefined' ? GameData : null);
      } catch (e1) {
        try {
          UI.init({ game: this, state: this.state, data: typeof GameData !== 'undefined' ? GameData : null });
        } catch (e2) {}
      }
    }

    // 初始化事件系统
    if (typeof Events !== 'undefined' && Events && typeof Events.init === 'function') {
      try {
        Events.init(this, this.state, typeof GameData !== 'undefined' ? GameData : null);
      } catch (e1) {
        try {
          Events.init({ game: this, state: this.state, data: typeof GameData !== 'undefined' ? GameData : null });
        } catch (e2) {}
      }
    }

    // 初始屏幕
    this.showScreen('loading-screen', true);
    this.simulateLoading();
  },

  /**
   * 模拟加载过程（2~3秒）
   */
  simulateLoading() {
    if (this._loadingRAF) cancelAnimationFrame(this._loadingRAF);
    if (this._loadingTipTimer) clearInterval(this._loadingTipTimer);

    const duration = typeof randomInt === 'function' ? randomInt(2000, 3000) : (2000 + Math.floor(Math.random() * 1000));
    const startTime = performance.now();

    const tips = [
      '正在整理动物档案…',
      '正在准备陪伴互动道具…',
      '正在清扫中转之家…',
      '正在匹配潜在领养家庭…',
      '正在生成回访相册…'
    ];

    const tipEl = this._findIn('#loading-screen', [
      '[data-role="loading-tip"]',
      '.loading-tip',
      '#loading-tip',
      '.tip-text'
    ]);

    if (tipEl) {
      tipEl.textContent = tips[0];
      let tipIndex = 0;
      this._loadingTipTimer = setInterval(() => {
        tipIndex = (tipIndex + 1) % tips.length;
        tipEl.style.opacity = '0.3';
        setTimeout(() => {
          tipEl.textContent = tips[tipIndex];
          tipEl.style.opacity = '1';
        }, 120);
      }, 500);
    }

    const tick = (now) => {
      const elapsed = now - startTime;
      const t = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3); // 缓出
      const progress = Math.min(100, Math.floor(eased * 100));

      this._updateLoadingProgress(progress);

      // 通知 UI（如果有）
      this._safeCall(UI, ['setLoadingProgress', 'updateLoading', 'onLoadingProgress'], progress);

      if (t < 1) {
        this._loadingRAF = requestAnimationFrame(tick);
      } else {
        this._loadingRAF = null;
        if (this._loadingTipTimer) {
          clearInterval(this._loadingTipTimer);
          this._loadingTipTimer = null;
        }
        setTimeout(() => {
          this.showScreen('main-menu');
        }, 220);
      }
    };

    this._loadingRAF = requestAnimationFrame(tick);
  },

  /**
   * 屏幕切换（淡入淡出）
   */
  showScreen(screenId, immediate = false) {
    const target = document.getElementById(screenId);
    if (!target) return;

    const prevId = this.currentScreen;
    const prevEl = document.getElementById(prevId);

    if (prevId === screenId && !immediate) return;

    // 先记录默认 display，避免 show/hide 破坏布局
    this._screenIds.forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (!el.dataset.defaultDisplay) {
        const computed = window.getComputedStyle(el).display;
        const fallbackMap = {
          'loading-screen': 'flex',
          'main-menu': 'flex',
          'game-screen': 'block',
          'game-over': 'flex'
        };
        el.dataset.defaultDisplay = computed !== 'none' ? computed : (fallbackMap[id] || 'block');
      }
    });

    const hideScreen = (el) => {
      if (!el) return;
      el.classList.remove('screen-active', 'active', 'show');
      el.classList.add('screen-hidden');
      el.style.display = 'none';
      el.style.opacity = '';
      el.style.transform = '';
      el.style.pointerEvents = 'none';
      el.style.transition = '';
    };

    const showScreenNow = (el) => {
      if (!el) return;
      el.classList.remove('screen-hidden');
      el.classList.add('screen-active', 'active', 'show');
      el.style.display = el.dataset.defaultDisplay || 'block';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
      el.style.pointerEvents = 'auto';
    };

    if (immediate || !prevEl) {
      this._screenIds.forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (id === screenId) showScreenNow(el);
        else hideScreen(el);
      });
    } else {
      // 准备新屏幕
      target.style.display = target.dataset.defaultDisplay || 'block';
      target.style.opacity = '0';
      target.style.transform = 'translateY(10px) scale(0.995)';
      target.style.pointerEvents = 'auto';
      target.classList.remove('screen-hidden');
      target.classList.add('screen-active', 'active', 'show');

      // 当前屏幕淡出
      prevEl.style.transition = 'opacity 280ms ease, transform 280ms ease';
      prevEl.style.opacity = '0';
      prevEl.style.transform = 'translateY(-8px) scale(0.995)';
      prevEl.style.pointerEvents = 'none';

      // 新屏幕淡入
      requestAnimationFrame(() => {
        target.style.transition = 'opacity 320ms ease, transform 320ms ease';
        target.style.opacity = '1';
        target.style.transform = 'translateY(0) scale(1)';
      });

      setTimeout(() => {
        hideScreen(prevEl);
        target.style.transition = '';
      }, 340);
    }

    this.currentScreen = screenId;
    this._safeCall(UI, ['onScreenChange', 'handleScreenChange'], screenId, prevId, this.state);
  },

  /**
   * 开始新游戏
   */
  startNewGame() {
    // 关闭弹窗，重置状态
    this.closeModal();
    this.isPaused = false;
    this._gameEnded = false;
    document.body.classList.remove('is-paused');

    // 优先走 state 自带重置方法
    if (this.state && typeof this.state.reset === 'function') {
      this.state.reset(typeof GameData !== 'undefined' ? GameData : null);
    } else {
      this.state = this._createGameState();
    }

    // 若 GameState 提供 startNewGame 则调用
    this._safeCall(this.state, ['startNewGame', 'initNewGame', 'begin'], typeof GameData !== 'undefined' ? GameData : null);

    // 兜底字段
    if (typeof this.state.day !== 'number') this.state.day = 1;
    if (!this.state.stats || typeof this.state.stats !== 'object') this.state.stats = {};

    // UI 重新绑定 state（如果 UI 需要）
    this._safeCall(UI, ['setState', 'bindState', 'attachState'], this.state);

    this.showScreen('game-screen');
    this._refreshUI({ reason: 'new-game' });

    // 事件系统通知
    if (typeof Events !== 'undefined' && Events) {
      if (typeof Events.onGameStart === 'function') Events.onGameStart(this.state, this);
      else if (typeof Events.emit === 'function') Events.emit('game-start', { state: this.state, game: this });
      else if (typeof Events.dispatch === 'function') Events.dispatch('game-start', { state: this.state, game: this });
    }
  },

  /**
   * 执行下一回合
   * 包含：资源结算、随机事件（30%）、胜负检查
   */
  nextTurn() {
    if (this.currentScreen !== 'game-screen') return;
    if (this.isPaused || this._gameEnded) return;

    // 回合前事件
    if (typeof Events !== 'undefined' && Events) {
      if (typeof Events.beforeNextTurn === 'function') Events.beforeNextTurn(this.state, this);
      else if (typeof Events.emit === 'function') Events.emit('turn-before', { state: this.state, game: this });
    }

    // 1) 日结算
    const settlementResult = this._runTurnSettlement();

    // 2) 30% 概率触发随机事件
    let eventResult = null;
    if (Math.random() < 0.3) {
      eventResult = this._triggerRandomEvent();
    }

    // 3) 刷新界面
    this._refreshUI({ reason: 'next-turn', settlementResult, eventResult });

    // 4) 胜负检查
    const gameOverState = this.checkGameOver();
    if (gameOverState && gameOverState.isOver) {
      this.endGame(!!gameOverState.victory, gameOverState.message || '');
      return;
    }

    // 回合后事件
    if (typeof Events !== 'undefined' && Events) {
      if (typeof Events.afterNextTurn === 'function') Events.afterNextTurn(this.state, this);
      else if (typeof Events.emit === 'function') Events.emit('turn-after', { state: this.state, game: this });
    }
  },

  /**
   * 检查是否游戏结束
   * 返回格式：{ isOver: boolean, victory: boolean, message: string }
   */
  checkGameOver() {
    // 优先用状态类自己的判断
    const external = this._safeCall(this.state, ['checkGameOver', 'isGameOver', 'getGameOverState'], typeof GameData !== 'undefined' ? GameData : null);
    const normalized = this._normalizeGameOverResult(external);
    if (normalized) return normalized;

    // 通用兜底逻辑
    const day = this._readState(['day', 'currentDay', 'stats.daysPlayed'], 1);
    const maxDays = this._readAny(
      typeof GameData !== 'undefined' ? GameData : {},
      ['config.maxDays', 'maxDays', 'game.maxDays'],
      30
    );

    const reputation = this._readState(
      ['reputation', 'publicTrust', 'trust', 'shelterReputation', 'resources.reputation'],
      50
    );

    const funds = this._readState(
      ['funds', 'money', 'budget', 'resources.funds', 'resources.money', 'resources.budget'],
      100
    );

    const adopted = this._readState(
      ['stats.adoptedCount', 'adoptedCount', 'stats.adopted', 'records.adopted'],
      0
    );

    const rescued = this._readState(
      ['stats.rescuedCount', 'rescuedCount', 'stats.rescued', 'records.rescued'],
      Math.max(adopted, 1)
    );

    // 失败条件
    if (typeof funds === 'number' && funds <= -100) {
      return {
        isOver: true,
        victory: false,
        message: '资金链断裂，中转之家暂时无法继续运营。'
      };
    }

    if (typeof reputation === 'number' && reputation <= 0) {
      return {
        isOver: true,
        victory: false,
        message: '公众信任跌至谷底，送养工作被迫中止。'
      };
    }

    // 达到天数后结算胜负
    if (typeof day === 'number' && typeof maxDays === 'number' && day > maxDays) {
      const target = Math.max(3, Math.floor((rescued || 6) * 0.5));
      const victory = adopted >= target;
      return {
        isOver: true,
        victory,
        message: victory
          ? '你让许多受伤的小生命重新相信了爱，也学会了温柔放手。'
          : '你已经尽力了，但还有更多心结等待被理解。再来一次吧。'
      };
    }

    return { isOver: false, victory: false, message: '' };
  },

  /**
   * 结束游戏
   */
  endGame(victory, message) {
    if (this._gameEnded) return;

    this._gameEnded = true;
    this.isPaused = true;
    document.body.classList.add('is-paused');

    // 状态类可选回调
    this._safeCall(this.state, ['endGame', 'finishGame'], { victory, message });

    // 更新结算界面
    const finalMessage = message || (victory
      ? '愿每一次相遇都有归处。'
      : '中转不是终点，重来依旧温柔。');

    this._updateGameOverUI(victory, finalMessage);

    // UI 模块回调
    this._safeCall(UI, ['showGameOver', 'onGameOver'], victory, finalMessage, this.state);

    // 切到结束屏
    this.showScreen('game-over');

    // 通知事件系统
    if (typeof Events !== 'undefined' && Events) {
      if (typeof Events.onGameOver === 'function') Events.onGameOver({ victory, message: finalMessage, state: this.state }, this);
      else if (typeof Events.emit === 'function') Events.emit('game-over', { victory, message: finalMessage, state: this.state, game: this });
      else if (typeof Events.dispatch === 'function') Events.dispatch('game-over', { victory, message: finalMessage, state: this.state, game: this });
    }
  },

  /**
   * 重新开始
   */
  restart() {
    this.startNewGame();
  },

  /**
   * 返回主菜单
   */
  backToMenu() {
    this.closeModal();
    this.isPaused = false;
    document.body.classList.remove('is-paused');
    this.showScreen('main-menu');
    this._safeCall(UI, ['refreshMenu', 'onBackToMenu'], this.state);
  },

  /**
   * 暂停/继续
   */
  togglePause() {
    if (this.currentScreen !== 'game-screen' || this._gameEnded) return;

    this.isPaused = !this.isPaused;
    document.body.classList.toggle('is-paused', this.isPaused);

    // 同步暂停按钮文本
    const btns = document.querySelectorAll('[data-action="toggle-pause"], #pause-btn, .pause-btn');
    btns.forEach((btn) => {
      const pausedText = btn.dataset.pausedText || '▶ 继续';
      const runningText = btn.dataset.runningText || '⏸ 暂停';
      if ('textContent' in btn) {
        btn.textContent = this.isPaused ? pausedText : runningText;
      }
    });

    // 可选暂停遮罩
    const pauseOverlay = document.getElementById('pause-overlay');
    if (pauseOverlay) {
      pauseOverlay.style.display = this.isPaused ? 'flex' : 'none';
      pauseOverlay.style.opacity = this.isPaused ? '1' : '0';
    }

    this._safeCall(UI, ['setPaused', 'onPauseChange'], this.isPaused, this.state);

    if (typeof Events !== 'undefined' && Events) {
      if (typeof Events.onPauseChange === 'function') Events.onPauseChange(this.isPaused, this.state, this);
      else if (typeof Events.emit === 'function') Events.emit('pause-change', { paused: this.isPaused, state: this.state, game: this });
    }
  },

  /**
   * 打开设置弹窗
   */
  showSettings() {
    this.showModal('settings-modal');
  },

  /**
   * 打开帮助弹窗
   */
  showHelp() {
    this.showModal('help-modal');
  },

  /**
   * 通用弹窗展示
   */
  showModal(modalId, payload = null) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    // 先让 UI 模块接管（若存在）
    this._safeCall(UI, ['showModal'], modalId, payload, this.state);

    // event-modal 填充内容（兜底）
    if (modalId === 'event-modal' && payload) {
      this._fillEventModal(modal, payload);
    }

    modal.removeAttribute('hidden');
    modal.setAttribute('aria-hidden', 'false');
    modal.style.display = 'flex';
    modal.style.pointerEvents = 'auto';

    requestAnimationFrame(() => {
      modal.classList.add('show', 'active', 'open');
      modal.style.opacity = '1';
      modal.style.transform = 'translateY(0) scale(1)';
    });

    this._currentModalId = modalId;
  },

  /**
   * 通用弹窗关闭
   */
  closeModal(modalId = null) {
    // 先通知 UI（若有）
    this._safeCall(UI, ['closeModal'], modalId);

    const closeOne = (modal) => {
      if (!modal) return;
      modal.classList.remove('show', 'active', 'open');
      modal.style.opacity = '0';
      modal.style.transform = 'translateY(8px) scale(0.98)';
      modal.setAttribute('aria-hidden', 'true');
      modal.style.pointerEvents = 'none';
      setTimeout(() => {
        modal.style.display = 'none';
      }, 220);
    };

    if (modalId) {
      closeOne(document.getElementById(modalId));
      if (this._currentModalId === modalId) this._currentModalId = null;
      return;
    }

    // 不指定时关闭全部常驻弹窗
    ['event-modal', 'settings-modal', 'help-modal'].forEach((id) => {
      const m = document.getElementById(id);
      if (m) closeOne(m);
    });

    // 兼容其他 modal
    document.querySelectorAll('.modal.show, .modal.active, .modal.open').forEach((m) => closeOne(m));
    this._currentModalId = null;
  },

  /* -------------------- 内部工具方法 -------------------- */

  _createGameState() {
    if (typeof GameState === 'function') {
      try {
        return new GameState(typeof GameData !== 'undefined' ? GameData : null);
      } catch (e1) {
        try {
          return new GameState();
        } catch (e2) {}
      }
    }

    // 无 GameState 时的最小兜底
    return {
      day: 1,
      maxDays: this._readAny(typeof GameData !== 'undefined' ? GameData : {}, ['config.maxDays', 'maxDays'], 30),
      reputation: 50,
      funds: 100,
      stats: {
        adoptedCount: 0,
        rescuedCount: 0,
        daysPlayed: 0
      }
    };
  },

  _bindGlobalEvents() {
    if (this._eventsBound) return;
    this._eventsBound = true;

    // 点击事件代理：按钮 data-action、ID、弹窗关闭等
    document.addEventListener('click', (e) => {
      const actionEl = e.target.closest('[data-action], button, .modal-close, .close-modal, [data-screen]');
      if (!actionEl) return;

      // 点击 modal 蒙层关闭（仅点到自身，不点内容区）
      if (actionEl.classList.contains('modal') && e.target === actionEl) {
        if (actionEl.dataset.closeOnBackdrop !== 'false') {
          this.closeModal(actionEl.id || null);
        }
        return;
      }

      // data-screen 快捷切换
      if (actionEl.dataset.screen) {
        this.showScreen(actionEl.dataset.screen);
        return;
      }

      // 关闭按钮
      if (
        actionEl.classList.contains('modal-close') ||
        actionEl.classList.contains('close-modal') ||
        actionEl.dataset.action === 'close-modal'
      ) {
        const targetModalId = actionEl.dataset.modal || actionEl.getAttribute('data-target') || actionEl.closest('.modal')?.id || null;
        this.closeModal(targetModalId);
        return;
      }

      const action = (actionEl.dataset.action || actionEl.id || '').trim();

      switch (action) {
        case 'start-game':
        case 'start-new-game':
        case 'new-game':
        case 'start-game-btn':
        case 'new-game-btn':
        case 'btn-start-game':
          this.startNewGame();
          break;

        case 'next-turn':
        case 'end-day':
        case 'next-day':
        case 'next-turn-btn':
          this.nextTurn();
          break;

        case 'toggle-pause':
        case 'pause-btn':
        case 'btn-pause':
          this.togglePause();
          break;

        case 'open-settings':
        case 'show-settings':
        case 'settings-btn':
          this.showSettings();
          break;

        case 'open-help':
        case 'show-help':
        case 'help-btn':
          this.showHelp();
          break;

        case 'restart':
        case 'restart-btn':
        case 'play-again':
          this.restart();
          break;

        case 'back-menu':
        case 'back-to-menu':
        case 'main-menu-btn':
          this.backToMenu();
          break;

        case 'continue-game':
          if (this.currentScreen !== 'game-screen') this.showScreen('game-screen');
          this.isPaused = false;
          document.body.classList.remove('is-paused');
          break;

        default:
          break;
      }
    });

    // ESC：优先关弹窗；否则在游戏内切换暂停
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const hasModal = !!document.querySelector('#event-modal.show, #settings-modal.show, #help-modal.show, .modal.active, .modal.open');
        if (hasModal || this._currentModalId) {
          this.closeModal();
        } else if (this.currentScreen === 'game-screen') {
          this.togglePause();
        }
        return;
      }

      // 空格：游戏内下一回合（避免在输入框触发）
      if (e.code === 'Space' || e.key === ' ') {
        const tag = (document.activeElement && document.activeElement.tagName) || '';
        if (/INPUT|TEXTAREA|SELECT/.test(tag)) return;
        if (this.currentScreen === 'game-screen' && !this.isPaused && !this._gameEnded) {
          e.preventDefault();
          this.nextTurn();
        }
      }
    });
  },

  _runTurnSettlement() {
    let usedHook = false;
    let result;

    const hooks = [
      'nextTurn',
      'advanceDay',
      'nextDay',
      'processDailySettlement',
      'applyDailySettlement',
      'resolveDay',
      'dailyUpdate'
    ];

    for (const name of hooks) {
      if (this.state && typeof this.state[name] === 'function') {
        result = this.state[name](typeof GameData !== 'undefined' ? GameData : null);
        usedHook = true;
        break;
      }
    }

    // 无状态方法时，使用最小兜底结算
    if (!usedHook && this.state) {
      if (typeof this.state.day !== 'number') this.state.day = 1;
      this.state.day += 1;

      if (!this.state.stats || typeof this.state.stats !== 'object') this.state.stats = {};
      this.state.stats.daysPlayed = (this.state.stats.daysPlayed || 0) + 1;

      // 轻量资金消耗
      if (typeof this.state.funds === 'number') this.state.funds -= 5;
      else if (this.state.resources && typeof this.state.resources.funds === 'number') this.state.resources.funds -= 5;

      result = { fallback: true, day: this.state.day };
    }

    return result;
  },

  _triggerRandomEvent() {
    let eventResult = null;

    if (typeof Events !== 'undefined' && Events) {
      // 常见 API 兼容
      if (typeof Events.triggerRandomEvent === 'function') {
        eventResult = Events.triggerRandomEvent(this.state, this, typeof GameData !== 'undefined' ? GameData : null);
      } else if (typeof Events.randomEvent === 'function') {
        eventResult = Events.randomEvent(this.state, this);
      } else if (typeof Events.getRandomEvent === 'function') {
        eventResult = Events.getRandomEvent(this.state, this);
      } else if (typeof Events.emit === 'function') {
        eventResult = Events.emit('random-event', { state: this.state, game: this });
      } else if (typeof Events.dispatch === 'function') {
        eventResult = Events.dispatch('random-event', { state: this.state, game: this });
      }
    }

    // 支持异步事件
    if (eventResult && typeof eventResult.then === 'function') {
      eventResult.then((payload) => {
        this._handleRandomEventPayload(payload);
      }).catch(() => {});
      return null;
    }

    this._handleRandomEventPayload(eventResult);
    return eventResult;
  },

  _handleRandomEventPayload(payload) {
    if (!payload) return;

    // 优先 UI 接管
    const uiHandled = this._safeCall(UI, ['showEventModal', 'openEvent', 'renderEvent'], payload, this.state, this);
    if (uiHandled !== undefined) return;

    // 兜底：直接打开 event-modal
    this.showModal('event-modal', payload);
  },

  _fillEventModal(modal, payload) {
    const data = (typeof payload === 'object' && payload !== null) ? payload : { description: String(payload) };
    const title = data.title || data.name || data.eventName || '今日小事件';
    const desc = data.description || data.text || data.content || data.message || '中转之家发生了一件新的事情。';

    const titleEl = modal.querySelector('[data-role="modal-title"], .modal-title, h2, h3');
    const contentEl = modal.querySelector('[data-role="modal-content"], .modal-content, .event-content, .content, p');
    const choicesEl = modal.querySelector('[data-role="event-choices"], .event-choices, .choices');

    if (titleEl) titleEl.textContent = title;
    if (contentEl) contentEl.textContent = desc;

    // 如果有选项，自动生成按钮
    if (choicesEl) {
      choicesEl.innerHTML = '';
      if (Array.isArray(data.choices) && data.choices.length) {
        data.choices.forEach((choice, idx) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'event-choice-btn';
          btn.textContent = choice.text || choice.label || `选项 ${idx + 1}`;
          btn.addEventListener('click', () => {
            // 选项效果函数（可选）
            if (typeof choice.effect === 'function') {
              choice.effect(this.state, this);
            }

            // 事件系统处理选项（可选）
            if (typeof Events !== 'undefined' && Events) {
              if (typeof Events.applyChoice === 'function') {
                Events.applyChoice(choice, data, this.state, this);
              } else if (typeof Events.emit === 'function') {
                Events.emit('event-choice', { choice, event: data, state: this.state, game: this });
              }
            }

            this.closeModal('event-modal');
            this._refreshUI({ reason: 'event-choice', event: data, choice });

            const over = this.checkGameOver();
            if (over && over.isOver) this.endGame(!!over.victory, over.message || '');
          });
          choicesEl.appendChild(btn);
        });
      } else {
        const okBtn = document.createElement('button');
        okBtn.type = 'button';
        okBtn.className = 'event-choice-btn';
        okBtn.textContent = '知道了';
        okBtn.addEventListener('click', () => this.closeModal('event-modal'));
        choicesEl.appendChild(okBtn);
      }
    }
  },

  _normalizeGameOverResult(result) {
    if (result === undefined || result === null) return null;

    if (typeof result === 'boolean') {
      return result ? { isOver: true, victory: false, message: '游戏结束。' } : { isOver: false, victory: false, message: '' };
    }

    if (typeof result === 'string') {
      return { isOver: true, victory: false, message: result };
    }

    if (typeof result === 'object') {
      if ('isOver' in result) {
        return {
          isOver: !!result.isOver,
          victory: !!result.victory,
          message: result.message || ''
        };
      }
      if ('gameOver' in result) {
        return {
          isOver: !!result.gameOver,
          victory: !!result.victory,
          message: result.message || ''
        };
      }
    }

    return null;
  },

  _updateGameOverUI(victory, message) {
    const gameOverEl = document.getElementById('game-over');
    if (gameOverEl) {
      gameOverEl.classList.toggle('victory', !!victory);
      gameOverEl.classList.toggle('defeat', !victory);
    }

    const titleEl =
      document.getElementById('game-over-title') ||
      this._findIn('#game-over', ['[data-role="result-title"]', '.result-title', 'h2', 'h1']);
    const messageEl =
      document.getElementById('game-over-message') ||
      this._findIn('#game-over', ['[data-role="result-message"]', '.result-message', 'p']);

    if (titleEl) titleEl.textContent = victory ? '❤️ 温柔圆满' : '🌧 暂别与重逢';
    if (messageEl) messageEl.textContent = message;

    const statsEl =
      document.getElementById('final-score') ||
      document.getElementById('game-over-stats') ||
      this._findIn('#game-over', ['[data-role="final-stats"]', '.final-stats', '.stats']);

    if (statsEl) {
      const day = this._readState(['day', 'currentDay', 'stats.daysPlayed'], 1);
      const adopted = this._readState(['stats.adoptedCount', 'adoptedCount', 'stats.adopted'], 0);
      const rescued = this._readState(['stats.rescuedCount', 'rescuedCount', 'stats.rescued'], 0);
      const revisit = this._readState(['stats.revisitCount', 'revisitCount', 'stats.revisit'], 0);

      statsEl.innerHTML =
        `📅 运营天数：${this._format(day)}<br>` +
        `🏡 成功送养：${this._format(adopted)}<br>` +
        `🐾 累计救助：${this._format(rescued)}<br>` +
        `📸 回访记录：${this._format(revisit)}`;
    }
  },

  _refreshUI(context = {}) {
    this._safeCall(UI, ['refresh', 'render', 'renderAll', 'update', 'updateAll', 'updateGameScreen'], this.state, context, this);
  },

  _updateLoadingProgress(progress) {
    const clamped = Math.max(0, Math.min(100, progress));

    const loadingRoot = document.getElementById('loading-screen') || document;
    const fillEl =
      loadingRoot.querySelector('[data-role="loading-fill"]') ||
      loadingRoot.querySelector('.loading-fill') ||
      loadingRoot.querySelector('.progress-fill') ||
      loadingRoot.querySelector('#loading-progress');

    const textEl =
      loadingRoot.querySelector('[data-role="loading-percent"]') ||
      loadingRoot.querySelector('.loading-percent') ||
      loadingRoot.querySelector('.progress-text') ||
      loadingRoot.querySelector('#loading-percent');

    if (fillEl) {
      if (fillEl.tagName === 'PROGRESS') {
        fillEl.value = clamped;
      } else {
        fillEl.style.width = `${clamped}%`;
      }
    }

    if (textEl) textEl.textContent = `${clamped}%`;
  },

  _safeCall(target, methodNames, ...args) {
    if (!target) return undefined;
    const names = Array.isArray(methodNames) ? methodNames : [methodNames];
    for (const name of names) {
      if (name && typeof target[name] === 'function') {
        try {
          return target[name](...args);
        } catch (e) {
          return undefined;
        }
      }
    }
    return undefined;
  },

  _readState(paths, defaultValue) {
    return this._readAny(this.state || {}, paths, defaultValue);
  },

  _readAny(source, paths, defaultValue) {
    const list = Array.isArray(paths) ? paths : [paths];
    for (const path of list) {
      const value = this._readPath(source, path);
      if (value !== undefined && value !== null) return value;
    }
    return defaultValue;
  },

  _readPath(source, path) {
    if (source == null || path == null) return undefined;
    if (typeof path !== 'string') return source[path];
    const segments = path.split('.');
    let cur = source;
    for (const key of segments) {
      if (cur == null) return undefined;
      if ((typeof cur === 'object' || typeof cur === 'function') && key in cur) {
        cur = cur[key];
      } else {
        return undefined;
      }
    }
    return cur;
  },

  _findIn(rootSelector, selectorList) {
    const root = document.querySelector(rootSelector);
    if (!root) return null;
    for (const sel of selectorList) {
      const el = root.querySelector(sel);
      if (el) return el;
    }
    return null;
  },

  _format(value) {
    if (typeof value === 'number' && typeof formatNumber === 'function') {
      return formatNumber(value);
    }
    return String(value ?? '-');
  }
};

// 暴露到全局，方便其他模块调用
window.Game = Game;

// 页面就绪后启动
document.addEventListener('DOMContentLoaded', () => {
  Game.init();
});