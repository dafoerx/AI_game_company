const UI = {
  elements: {},
  prevResources: {},
  particleTimer: null,
  logLimit: 80,
  _styleInjected: false,
  _lastBuildingCount: 0,

  // 初始化 UI
  init() {
    this.injectStyles();
    this.createBaseLayout();
    this.cacheElements();

    this.initResourcePanel();
    this.initBuildMenu();
    this.initMenuParticles();
    this.updateAll();

    if (this.elements.log && this.elements.log.children.length === 0) {
      const welcomeText =
        (typeof GameData !== "undefined" && GameData.description) ||
        "欢迎来到《中转之家：放心去爱》";
      this.addLog(`🌤️ ${welcomeText}`, "info");
    }
  },

  // 注入基础样式（提供兜底视觉，避免页面无样式）
  injectStyles() {
    if (this._styleInjected || document.getElementById("ui-painted-style")) return;
    const style = document.createElement("style");
    style.id = "ui-painted-style";
    style.textContent = `
      :root{
        --ui-bg-1:#f7f1ea;
        --ui-bg-2:#f2e9dd;
        --ui-card:#fffaf5;
        --ui-ink:#5b4b43;
        --ui-sub:#8a786d;
        --ui-accent:#d28f7a;
        --ui-accent-2:#87b5a0;
        --ui-good:#59a26b;
        --ui-bad:#d06767;
        --ui-warn:#d7a655;
        --ui-shadow:0 8px 22px rgba(121, 94, 78, .14);
      }

      body{
        background:
          radial-gradient(1200px 500px at 15% -10%, rgba(255,220,190,.55), transparent 70%),
          radial-gradient(900px 500px at 90% -10%, rgba(198,219,208,.45), transparent 65%),
          linear-gradient(180deg, var(--ui-bg-1), var(--ui-bg-2));
        color:var(--ui-ink);
      }

      #ui-game-shell, #ui-game-shell *{ box-sizing:border-box; font-family:"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif; }

      #ui-game-shell{
        max-width:1320px;
        margin:0 auto;
        padding:16px;
        display:flex;
        flex-direction:column;
        gap:12px;
      }

      #ui-topbar{
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:12px;
        background:linear-gradient(135deg, rgba(255,250,245,.88), rgba(250,239,228,.9));
        border:1px solid rgba(162,127,106,.22);
        box-shadow:var(--ui-shadow);
        border-radius:18px;
        padding:12px 16px;
        animation:uiSoftIn .55s ease both;
      }

      #game-title{
        font-size:20px;
        font-weight:800;
        letter-spacing:.5px;
      }

      #turn-display{
        min-width:230px;
        text-align:right;
      }

      .turn-label{
        font-size:12px;
        color:var(--ui-sub);
        display:block;
      }
      .turn-value{
        font-size:16px;
        font-weight:700;
      }
      .turn-progress{
        margin-top:6px;
        width:100%;
        height:7px;
        background:rgba(160,120,100,.16);
        border-radius:999px;
        overflow:hidden;
      }
      .turn-progress i{
        display:block;
        height:100%;
        width:0;
        border-radius:999px;
        background:linear-gradient(90deg, #e8b07e, #d28f7a);
        transition:width .5s ease;
      }

      #resource-panel{
        display:grid;
        grid-template-columns:repeat(auto-fit, minmax(170px,1fr));
        gap:10px;
      }

      .resource-item{
        position:relative;
        display:flex;
        align-items:center;
        gap:10px;
        padding:10px 12px;
        border-radius:14px;
        background:linear-gradient(150deg, rgba(255,250,245,.92), rgba(248,239,230,.9));
        border:1px solid rgba(169,132,109,.2);
        box-shadow:var(--ui-shadow);
        overflow:hidden;
        transition:transform .2s ease, box-shadow .25s ease;
        animation:uiSoftIn .55s ease both;
      }
      .resource-item:hover{ transform:translateY(-2px); box-shadow:0 12px 28px rgba(119,92,79,.18); }
      .resource-item.warning{ border-color:rgba(215,166,85,.6); }
      .resource-item.danger-empty{ border-color:rgba(208,103,103,.7); }
      .resource-item::after{
        content:"";
        position:absolute;
        inset:auto -40% -65% auto;
        width:120px;height:120px;
        background:radial-gradient(circle, rgba(255,255,255,.45), transparent 65%);
        transform:rotate(20deg);
      }

      .resource-icon{ font-size:28px; line-height:1; filter:drop-shadow(0 2px 2px rgba(0,0,0,.08)); }
      .resource-info{ flex:1; min-width:0; }
      .resource-name{ font-size:12px; color:var(--ui-sub); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
      .resource-value{
        font-size:18px;
        font-weight:800;
        color:var(--ui-ink);
        margin:2px 0;
        transition:color .2s;
      }
      .resource-change{ font-size:12px; color:var(--ui-sub); }
      .resource-change.trend-up{ color:var(--ui-good); }
      .resource-change.trend-down{ color:var(--ui-bad); }

      .resource-bar{
        margin-top:6px;
        height:6px;
        border-radius:99px;
        background:rgba(132,102,88,.14);
        overflow:hidden;
      }
      .resource-fill{
        height:100%;
        width:0%;
        border-radius:99px;
        background:linear-gradient(90deg, #eec792, #d89e88);
        transition:width .35s ease;
      }

      #status-overview{
        display:grid;
        grid-template-columns:repeat(auto-fit, minmax(140px,1fr));
        gap:10px;
      }

      .status-item{
        border-radius:12px;
        background:linear-gradient(135deg, rgba(255,250,246,.88), rgba(245,236,226,.9));
        border:1px solid rgba(158,122,101,.2);
        box-shadow:var(--ui-shadow);
        padding:10px 12px;
      }
      .status-label{ font-size:12px; color:var(--ui-sub); }
      .status-value{ margin-top:3px; font-size:16px; font-weight:800; color:var(--ui-ink); }

      #ui-main{
        display:grid;
        grid-template-columns:minmax(260px, 300px) minmax(420px, 1fr) minmax(260px, 300px);
        gap:12px;
        align-items:start;
      }

      #build-menu-wrap, #game-viewport-wrap, #game-log-wrap{
        position:relative;
        background:linear-gradient(155deg, rgba(255,250,245,.92), rgba(247,238,229,.92));
        border:1px solid rgba(160,126,104,.2);
        border-radius:18px;
        box-shadow:var(--ui-shadow);
        min-height:420px;
        overflow:hidden;
      }

      .panel-title{
        font-size:15px;
        font-weight:800;
        padding:12px 14px;
        border-bottom:1px solid rgba(160,125,101,.16);
        background:linear-gradient(180deg, rgba(255,255,255,.55), rgba(255,255,255,.15));
      }

      #build-menu, #game-viewport, #game-log{
        padding:10px;
      }

      #build-menu{
        max-height:calc(100vh - 300px);
        overflow:auto;
      }
      #build-menu::-webkit-scrollbar, #game-viewport::-webkit-scrollbar, #game-log::-webkit-scrollbar{ width:8px; }
      #build-menu::-webkit-scrollbar-thumb, #game-viewport::-webkit-scrollbar-thumb, #game-log::-webkit-scrollbar-thumb{
        background:rgba(132,102,88,.24); border-radius:99px;
      }

      .build-item{
        display:grid;
        grid-template-columns:42px 1fr auto;
        gap:10px;
        align-items:start;
        padding:10px;
        border-radius:14px;
        border:1px solid rgba(162,126,105,.17);
        background:linear-gradient(145deg, rgba(255,255,255,.82), rgba(248,241,234,.9));
        box-shadow:0 5px 15px rgba(129,97,81,.09);
        margin-bottom:10px;
        transition:transform .2s ease, box-shadow .24s ease;
        animation:uiSoftIn .45s ease both;
      }
      .build-item:hover{ transform:translateY(-2px); box-shadow:0 10px 20px rgba(129,97,81,.14); }
      .build-item.cannot-build{ opacity:.76; }

      .build-icon{ font-size:30px; line-height:1; margin-top:2px; }
      .build-info{ min-width:0; }
      .build-name{ font-weight:800; font-size:15px; }
      .build-desc{ font-size:12px; color:var(--ui-sub); margin-top:2px; line-height:1.45; }
      .build-cost{ margin-top:6px; font-size:12px; color:#7f6558; }
      .build-flow{ margin-top:4px; font-size:12px; color:#6f9d89; display:flex; flex-wrap:wrap; gap:8px; }
      .build-flow .consume{ color:#b97979; }

      .build-btn{
        border:none;
        border-radius:11px;
        padding:9px 12px;
        font-size:13px;
        font-weight:800;
        color:#fff;
        background:linear-gradient(135deg, #d7a188, #c68873);
        cursor:pointer;
        box-shadow:0 5px 12px rgba(165,100,78,.32);
        transition:transform .15s ease, box-shadow .2s ease, filter .2s;
        align-self:center;
      }
      .build-btn:hover{ transform:translateY(-1px); filter:brightness(1.05); box-shadow:0 8px 16px rgba(165,100,78,.38); }
      .build-btn:active{ transform:scale(.95); }
      .build-btn:disabled{
        cursor:not-allowed;
        background:linear-gradient(135deg, #b8aba3, #a69a93);
        box-shadow:none;
      }

      .buildings-grid{
        display:grid;
        grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));
        gap:10px;
      }

      .building-card{
        border-radius:14px;
        border:1px solid rgba(158,123,102,.18);
        background:
          radial-gradient(300px 100px at 110% -20%, rgba(255,255,255,.5), transparent 65%),
          linear-gradient(155deg, rgba(255,253,250,.86), rgba(247,237,228,.88));
        box-shadow:0 8px 18px rgba(129,95,79,.12);
        padding:10px;
        animation:uiRiseIn .35s ease both;
      }
      .building-top{ display:flex; align-items:center; gap:8px; }
      .building-icon{ font-size:28px; width:34px; text-align:center; }
      .building-name{ font-size:14px; font-weight:800; }
      .building-level{ font-size:12px; color:var(--ui-sub); }
      .building-desc{ margin-top:7px; font-size:12px; color:#7f6c61; line-height:1.45; min-height:34px; }
      .building-meta{
        margin-top:7px;
        display:flex;
        flex-wrap:wrap;
        gap:8px;
        font-size:12px;
      }
      .meta-produce{ color:#5f9a75; }
      .meta-consume{ color:#b37676; }

      .empty-state{
        border:1px dashed rgba(162,126,105,.35);
        border-radius:14px;
        background:rgba(255,255,255,.4);
        min-height:200px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        gap:6px;
        color:var(--ui-sub);
      }
      .empty-state .emoji{ font-size:46px; animation:uiFloat 2.2s ease-in-out infinite; }
      .empty-state .title{ font-size:16px; font-weight:700; color:var(--ui-ink); }

      #game-log{
        max-height:calc(100vh - 300px);
        overflow:auto;
      }
      .log-entry{
        opacity:0;
        transform:translateY(6px);
        display:grid;
        grid-template-columns:22px 1fr auto;
        gap:8px;
        align-items:start;
        margin-bottom:8px;
        padding:8px 10px;
        border-radius:10px;
        border:1px solid rgba(156,122,102,.16);
        background:rgba(255,255,255,.62);
        font-size:12px;
        transition:all .25s ease;
      }
      .log-entry.show{ opacity:1; transform:none; }
      .log-entry .i{ font-size:14px; line-height:1; margin-top:1px; }
      .log-entry .t{ color:#6f5d53; }
      .log-entry .time{ color:#998579; font-size:11px; white-space:nowrap; }
      .log-success{ border-left:3px solid var(--ui-good); }
      .log-warning{ border-left:3px solid var(--ui-warn); }
      .log-danger{ border-left:3px solid var(--ui-bad); }
      .log-info{ border-left:3px solid #8da9c2; }

      .menu-particles{
        position:absolute;
        inset:0;
        pointer-events:none;
        overflow:hidden;
      }
      .menu-particle{
        position:absolute;
        bottom:-20px;
        opacity:.75;
        animation:uiParticle linear forwards;
        filter:drop-shadow(0 2px 3px rgba(0,0,0,.12));
      }

      .floating-delta{
        position:absolute;
        right:8px;
        top:8px;
        font-size:12px;
        font-weight:800;
        pointer-events:none;
        animation:uiDelta .8s ease forwards;
      }
      .floating-delta.up{ color:var(--ui-good); }
      .floating-delta.down{ color:var(--ui-bad); }

      .resource-value.value-up{ animation:uiValueUp .55s ease; }
      .resource-value.value-down{ animation:uiValueDown .55s ease; }

      @media (max-width:1100px){
        #ui-main{ grid-template-columns:1fr; }
        #build-menu, #game-log{ max-height:none; }
      }

      @keyframes uiSoftIn{
        from{ opacity:0; transform:translateY(8px);}
        to{ opacity:1; transform:none;}
      }
      @keyframes uiRiseIn{
        from{ opacity:0; transform:translateY(12px) scale(.98);}
        to{ opacity:1; transform:none;}
      }
      @keyframes uiParticle{
        from{ transform:translateY(0) translateX(0) rotate(0); opacity:0; }
        15%{ opacity:.78; }
        to{ transform:translateY(-120%) translateX(14px) rotate(18deg); opacity:0; }
      }
      @keyframes uiFloat{
        0%,100%{ transform:translateY(0); }
        50%{ transform:translateY(-4px); }
      }
      @keyframes uiDelta{
        0%{ opacity:0; transform:translateY(6px);}
        20%{ opacity:1; transform:translateY(0);}
        100%{ opacity:0; transform:translateY(-18px);}
      }
      @keyframes uiValueUp{
        0%{ color:var(--ui-ink); text-shadow:none; transform:scale(1);}
        40%{ color:var(--ui-good); text-shadow:0 0 10px rgba(89,162,107,.35); transform:scale(1.08);}
        100%{ color:var(--ui-ink); transform:scale(1);}
      }
      @keyframes uiValueDown{
        0%{ color:var(--ui-ink); text-shadow:none; transform:scale(1);}
        40%{ color:var(--ui-bad); text-shadow:0 0 10px rgba(208,103,103,.35); transform:scale(1.08);}
        100%{ color:var(--ui-ink); transform:scale(1);}
      }
    `;
    document.head.appendChild(style);
    this._styleInjected = true;
  },

  // 创建基础布局（若 HTML 中未提供容器）
  createBaseLayout() {
    const requiredIds = [
      "resource-panel",
      "build-menu",
      "game-viewport",
      "status-overview",
      "turn-display",
      "game-log"
    ];
    const hasAll = requiredIds.every((id) => document.getElementById(id));
    if (hasAll) return;

    let shell = document.getElementById("ui-game-shell");
    if (!shell) {
      shell = document.createElement("div");
      shell.id = "ui-game-shell";
      const mount = document.getElementById("game-container") || document.getElementById("app") || document.body;
      mount.appendChild(shell);
    }

    const gameName = (typeof GameData !== "undefined" && GameData.name) || "《中转之家：放心去爱》";

    shell.innerHTML = `
      <div id="ui-topbar">
        <div id="game-title">🐾 ${gameName}</div>
        <div id="turn-display"></div>
      </div>
      <div id="resource-panel"></div>
      <div id="status-overview"></div>
      <div id="ui-main">
        <aside id="build-menu-wrap">
          <div class="panel-title">🧰 修复与建设</div>
          <div id="build-menu"></div>
        </aside>
        <section id="game-viewport-wrap">
          <div class="panel-title">🏡 中转之家</div>
          <div id="game-viewport"></div>
        </section>
        <aside id="game-log-wrap">
          <div class="panel-title">📷 记录墙</div>
          <div id="game-log"></div>
        </aside>
      </div>
    `;
  },

  // 缓存常用 DOM 元素
  cacheElements() {
    this.elements = {
      resourcePanel: document.getElementById("resource-panel"),
      buildMenu: document.getElementById("build-menu"),
      viewport: document.getElementById("game-viewport"),
      statusOverview: document.getElementById("status-overview"),
      turnDisplay: document.getElementById("turn-display"),
      log: document.getElementById("game-log")
    };
  },

  // 初始化资源面板
  initResourcePanel() {
    if (!this.elements.resourcePanel || typeof GameData === "undefined") return;
    this.elements.resourcePanel.innerHTML = "";

    (GameData.resources || []).forEach((res) => {
      const item = document.createElement("div");
      item.className = "resource-item";
      item.dataset.resId = res.id;
      item.innerHTML = `
        <div class="resource-icon">${res.icon || "🔹"}</div>
        <div class="resource-info">
          <div class="resource-name">${res.name || res.id}</div>
          <div class="resource-value">0</div>
          <div class="resource-change">+0/回合</div>
          <div class="resource-bar"><div class="resource-fill"></div></div>
        </div>
      `;
      this.elements.resourcePanel.appendChild(item);

      // 首次渲染前记录初值，防止启动时闪烁
      const current = Game?.state?.resources?.[res.id]?.current ?? res.initial ?? 0;
      this.prevResources[res.id] = Number(current) || 0;
    });
  },

  // 初始化建造菜单
  initBuildMenu() {
    if (!this.elements.buildMenu || typeof GameData === "undefined") return;
    this.elements.buildMenu.innerHTML = "";

    (GameData.buildings || []).forEach((building, idx) => {
      const item = document.createElement("div");
      item.className = "build-item";
      item.style.animationDelay = `${idx * 0.03}s`;
      item.dataset.buildingId = building.id;

      const produceText = this.formatFlow(building.produces, "produce");
      const consumeText =
        building.consumes && Object.keys(building.consumes).length
          ? this.formatFlow(building.consumes, "consume")
          : "";

      item.innerHTML = `
        <div class="build-icon">${building.icon || "🏠"}</div>
        <div class="build-info">
          <div class="build-name">${building.name || building.id}</div>
          <div class="build-desc">${building.description || "暂无描述"}</div>
          <div class="build-cost">花费：${this.formatCost(building.cost)}</div>
          <div class="build-flow">
            <span>${produceText}</span>
            ${consumeText ? `<span class="consume">${consumeText}</span>` : ""}
          </div>
        </div>
        <button class="build-btn" type="button">建造</button>
      `;

      const btn = item.querySelector(".build-btn");
      btn.addEventListener("click", () => this.build(building.id));
      this.elements.buildMenu.appendChild(item);
    });

    this.updateBuildButtons();
  },

  // 更新全部 UI
  updateAll() {
    this.updateTurn();
    this.updateResources();
    this.updateStatusOverview();
    this.updateGameViewport();
    this.updateBuildButtons();
  },

  // 更新资源数值（带变化动画）
  updateResources() {
    if (!this.elements.resourcePanel || typeof GameData === "undefined" || !Game?.state) return;

    (GameData.resources || []).forEach((res) => {
      const item = this.elements.resourcePanel.querySelector(`.resource-item[data-res-id="${res.id}"]`);
      if (!item) return;

      const stateRes = Game.state.resources?.[res.id];
      const current = Number(stateRes?.current ?? 0);
      const max = Number(stateRes?.max ?? res.max ?? 0);

      const valueEl = item.querySelector(".resource-value");
      const changeEl = item.querySelector(".resource-change");
      const fillEl = item.querySelector(".resource-fill");

      const previous = this.prevResources[res.id];
      const delta = (typeof previous === "number") ? current - previous : 0;

      valueEl.textContent = max > 0
        ? `${this.formatNumber(current)} / ${this.formatNumber(max)}`
        : this.formatNumber(current);

      const perTurnRaw = Game.state.calculateResourceChange ? Game.state.calculateResourceChange(res.id) : 0;
      const perTurn = Number(perTurnRaw || 0);
      changeEl.textContent = `${perTurn >= 0 ? "+" : ""}${this.formatNumber(perTurn)}/回合`;
      changeEl.classList.remove("trend-up", "trend-down");
      if (perTurn > 0) changeEl.classList.add("trend-up");
      if (perTurn < 0) changeEl.classList.add("trend-down");

      if (fillEl) {
        const ratio = max > 0 ? Math.max(0, Math.min(1, current / max)) : 0;
        fillEl.style.width = `${Math.round(ratio * 100)}%`;
      }

      // 资源阈值告警样式
      const warningThreshold = typeof res.warningThreshold === "number" ? res.warningThreshold : null;
      item.classList.toggle("warning", warningThreshold !== null && current <= warningThreshold);
      item.classList.toggle("danger-empty", !!res.failIfZero && current <= 0);

      // 触发增减闪烁与浮动数值
      if (typeof previous === "number" && delta !== 0) {
        this.animateValueChange(valueEl, delta, item);
      }

      this.prevResources[res.id] = current;
    });
  },

  // 更新回合显示
  updateTurn() {
    if (!this.elements.turnDisplay || !Game?.state) return;

    const turn = Number(Game.state.turn || 0);
    const maxTurns = Number(GameData?.maxTurns || 0);
    const ratio = maxTurns > 0 ? Math.min(100, (turn / maxTurns) * 100) : 0;

    this.elements.turnDisplay.innerHTML = `
      <span class="turn-label">营业日程</span>
      <span class="turn-value">第 ${turn}${maxTurns > 0 ? ` / ${maxTurns}` : ""} 天</span>
      <div class="turn-progress"><i style="width:${ratio}%"></i></div>
    `;
  },

  // 更新状态总览
  updateStatusOverview() {
    if (!this.elements.statusOverview || typeof GameData === "undefined" || !Game?.state) return;

    const buildings = Array.isArray(Game.state.buildings) ? Game.state.buildings : [];
    const population = Number(Game.state.population?.total || 0);

    let warningCount = 0;
    let ratioSum = 0;
    let ratioCount = 0;
    let netPerTurn = 0;

    (GameData.resources || []).forEach((res) => {
      const current = Number(Game.state.resources?.[res.id]?.current ?? 0);
      const max = Number(Game.state.resources?.[res.id]?.max ?? res.max ?? 0);
      if (typeof res.warningThreshold === "number" && current <= res.warningThreshold) warningCount++;

      if (max > 0) {
        ratioSum += Math.max(0, Math.min(1, current / max));
        ratioCount++;
      }

      const c = Number(Game.state.calculateResourceChange ? Game.state.calculateResourceChange(res.id) : 0);
      netPerTurn += c;
    });

    const avgRatio = ratioCount > 0 ? ratioSum / ratioCount : 0;
    let moodText = "平稳";
    if (warningCount === 0 && avgRatio > 0.75) moodText = "温暖稳定";
    else if (warningCount <= 1 && avgRatio > 0.45) moodText = "可持续";
    else if (warningCount >= 2) moodText = "需要关注";

    const statuses = [
      { label: "在院动物", value: `${population} 位` },
      { label: "已建设施", value: `${buildings.length} 处` },
      { label: "净变化", value: `${netPerTurn >= 0 ? "+" : ""}${this.formatNumber(netPerTurn)}/回合` },
      { label: "整体氛围", value: moodText }
    ];

    this.elements.statusOverview.innerHTML = statuses
      .map((s) => `
        <div class="status-item">
          <div class="status-label">${s.label}</div>
          <div class="status-value">${s.value}</div>
        </div>
      `)
      .join("");
  },

  // 更新主视图（显示已建造建筑）
  updateGameViewport() {
    if (!this.elements.viewport || !Game?.state || typeof GameData === "undefined") return;

    const list = Array.isArray(Game.state.buildings) ? Game.state.buildings : [];
    if (list.length === 0) {
      this.elements.viewport.innerHTML = `
        <div class="empty-state">
          <div class="emoji">🐾</div>
          <div class="title">这里还空空的</div>
          <div>先从第一处设施开始，让受伤的小生命有安全角落。</div>
        </div>
      `;
      this._lastBuildingCount = 0;
      return;
    }

    const grid = document.createElement("div");
    grid.className = "buildings-grid";

    list.forEach((b, index) => {
      const def = this.getBuildingData(b.type) || {
        id: b.type,
        name: b.type,
        icon: "🏚️",
        description: "未知设施",
        produces: {},
        consumes: {}
      };

      const level = Number(b.level || 1);
      const builtAt = b.builtAt ? `第${b.builtAt}天` : "今日";

      const produceText = this.formatFlow(def.produces, "produce");
      const consumeText =
        def.consumes && Object.keys(def.consumes).length
          ? this.formatFlow(def.consumes, "consume")
          : "";

      const card = document.createElement("div");
      card.className = "building-card";
      card.style.animationDelay = `${index * 0.025}s`;

      card.innerHTML = `
        <div class="building-top">
          <div class="building-icon">${def.icon || "🏠"}</div>
          <div>
            <div class="building-name">${def.name || def.id}</div>
            <div class="building-level">Lv.${level} · 建于${builtAt}</div>
          </div>
        </div>
        <div class="building-desc">${def.description || "温柔陪伴，慢慢修复。"} </div>
        <div class="building-meta">
          <span class="meta-produce">${produceText}</span>
          ${consumeText ? `<span class="meta-consume">${consumeText}</span>` : ""}
        </div>
      `;
      grid.appendChild(card);
    });

    this.elements.viewport.innerHTML = "";
    this.elements.viewport.appendChild(grid);

    this._lastBuildingCount = list.length;
  },

  // 触发建造
  build(buildingId) {
    if (!Game?.state || typeof Game.state.build !== "function") {
      this.addLog("系统未就绪，暂时无法建造。", "danger");
      return { success: false, message: "系统未就绪" };
    }

    const result = Game.state.build(buildingId);
    const bData = this.getBuildingData(buildingId);
    const bName = bData?.name || buildingId;

    if (result?.success) {
      this.addLog(result.message || `🧱 成功建造：${bName}`, "success");

      const targetItem = this.elements.buildMenu?.querySelector(`.build-item[data-building-id="${buildingId}"]`);
      if (targetItem) {
        targetItem.animate(
          [
            { transform: "scale(1)" },
            { transform: "scale(1.03)" },
            { transform: "scale(1)" }
          ],
          { duration: 260, easing: "ease-out" }
        );
      }
    } else {
      this.addLog(result?.message || `建造失败：${bName}`, "warning");
    }

    this.updateAll();
    return result;
  },

  // 添加日志
  addLog(message, type = "info") {
    if (!this.elements.log) return;

    const typeIcon = {
      success: "✅",
      warning: "⚠️",
      danger: "❌",
      info: "📌"
    };

    const safeType = ["success", "warning", "danger", "info"].includes(type) ? type : "info";
    const entry = document.createElement("div");
    entry.className = `log-entry log-${safeType}`;

    const time = new Date().toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit"
    });

    entry.innerHTML = `
      <div class="i">${typeIcon[safeType]}</div>
      <div class="t">${message}</div>
      <div class="time">${time}</div>
    `;

    this.elements.log.appendChild(entry);
    requestAnimationFrame(() => entry.classList.add("show"));

    while (this.elements.log.children.length > this.logLimit) {
      this.elements.log.removeChild(this.elements.log.firstElementChild);
    }

    this.elements.log.scrollTop = this.elements.log.scrollHeight;
  },

  // 菜单粒子效果
  initMenuParticles() {
    const wrap = document.getElementById("build-menu-wrap") || this.elements.buildMenu;
    if (!wrap) return;
    if (wrap.querySelector(".menu-particles")) return;

    const layer = document.createElement("div");
    layer.className = "menu-particles";
    wrap.appendChild(layer);

    const symbols = ["🐾", "✨", "💛", "🍃", "🫧", "📸"];

    const spawn = () => {
      if (document.hidden) return;
      const p = document.createElement("span");
      p.className = "menu-particle";
      p.textContent = symbols[Math.floor(Math.random() * symbols.length)];
      p.style.left = `${Math.random() * 100}%`;
      p.style.fontSize = `${12 + Math.random() * 14}px`;
      p.style.animationDuration = `${7 + Math.random() * 5}s`;
      p.style.animationDelay = `${Math.random() * 0.6}s`;
      layer.appendChild(p);
      setTimeout(() => p.remove(), 13000);
    };

    for (let i = 0; i < 8; i++) {
      setTimeout(spawn, i * 280);
    }

    if (this.particleTimer) clearInterval(this.particleTimer);
    this.particleTimer = setInterval(spawn, 1300);
  },

  // 格式化花费（cost 为扁平对象）
  formatCost(cost) {
    if (!cost || typeof cost !== "object") return "无消耗";

    const entries = Object.entries(cost).filter(([, v]) => Number(v) !== 0);
    if (!entries.length) return "无消耗";

    return entries
      .map(([resId, value]) => {
        const resMeta = (GameData?.resources || []).find((r) => r.id === resId);
        const icon = resMeta?.icon || "🔹";
        const name = resMeta?.name || resId;
        return `${icon}${name} ${this.formatNumber(value)}`;
      })
      .join(" · ");
  },

  // 更新建造按钮状态（是否可建）
  updateBuildButtons() {
    if (!this.elements.buildMenu || typeof GameData === "undefined") return;

    const items = this.elements.buildMenu.querySelectorAll(".build-item");
    items.forEach((item) => {
      const buildingId = item.dataset.buildingId;
      const building = this.getBuildingData(buildingId);
      const btn = item.querySelector(".build-btn");
      if (!building || !btn) return;

      const affordable = this.canAfford(building.cost);
      btn.disabled = !affordable;
      item.classList.toggle("cannot-build", !affordable);

      if (affordable) {
        btn.textContent = "建造";
        btn.title = "点击建造";
      } else {
        btn.textContent = "资源不足";
        const lack = this.getLackCostText(building.cost);
        btn.title = lack ? `缺少：${lack}` : "资源不足";
      }
    });
  },

  // 判断是否可负担
  canAfford(cost) {
    if (!cost || typeof cost !== "object") return true;
    if (!Game?.state?.resources) return false;

    return Object.entries(cost).every(([resId, need]) => {
      const current = Number(Game.state.resources?.[resId]?.current ?? 0);
      return current >= Number(need || 0);
    });
  },

  // 获取缺失资源文本
  getLackCostText(cost) {
    if (!cost || typeof cost !== "object" || !Game?.state?.resources) return "";
    const lacks = [];

    Object.entries(cost).forEach(([resId, need]) => {
      const current = Number(Game.state.resources?.[resId]?.current ?? 0);
      const needNum = Number(need || 0);
      if (current < needNum) {
        const meta = (GameData?.resources || []).find((r) => r.id === resId);
        lacks.push(`${meta?.icon || "🔹"}${meta?.name || resId} ${this.formatNumber(needNum - current)}`);
      }
    });

    return lacks.join("、");
  },

  // 将产出/消耗对象格式化为可读文本（扁平对象）
  formatFlow(obj, mode = "produce") {
    if (!obj || typeof obj !== "object") return "";
    const entries = Object.entries(obj).filter(([, v]) => Number(v) !== 0);
    if (!entries.length) return "";

    const isConsume = mode === "consume";
    return entries
      .map(([resId, value]) => {
        const meta = (GameData?.resources || []).find((r) => r.id === resId);
        const icon = meta?.icon || "🔹";
        const name = meta?.name || resId;
        const sign = isConsume ? "-" : "+";
        return `${icon}${name} ${sign}${this.formatNumber(Math.abs(Number(value) || 0))}`;
      })
      .join(" · ");
  },

  // 资源值变化动画
  animateValueChange(valueEl, delta, itemEl) {
    if (!valueEl || !delta) return;
    const cls = delta > 0 ? "value-up" : "value-down";
    valueEl.classList.remove("value-up", "value-down");
    void valueEl.offsetWidth;
    valueEl.classList.add(cls);

    if (itemEl) {
      const float = document.createElement("div");
      float.className = `floating-delta ${delta > 0 ? "up" : "down"}`;
      float.textContent = `${delta > 0 ? "+" : ""}${this.formatNumber(delta)}`;
      itemEl.appendChild(float);
      setTimeout(() => float.remove(), 900);
    }
  },

  // 根据 id 取建筑定义
  getBuildingData(buildingId) {
    return (GameData?.buildings || []).find((b) => b.id === buildingId);
  },

  // 数字显示格式化
  formatNumber(value) {
    const num = Number(value || 0);
    if (!Number.isFinite(num)) return "0";
    if (Math.abs(num) >= 1000) {
      return num.toLocaleString("zh-CN", { maximumFractionDigits: 1 });
    }
    if (Math.abs(num) % 1 !== 0) {
      return num.toFixed(1);
    }
    return `${num}`;
  }
};

window.UI = UI;