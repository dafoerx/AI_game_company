/**
 * 沸腾掌柜：火锅店经营MVP - UI 管理
 * ═══════════════════════════════════════
 */

const UI = {
    /**
     * 初始化 UI
     */
    init() {
        this.initResourcePanel();
        this.initBuildMenu();
    },
    
    /**
     * 初始化资源面板
     */
    initResourcePanel() {
        const panel = document.getElementById('resource-panel');
        panel.innerHTML = GameData.resources.map(res => `
            <div class="resource-item" id="resource-${res.id}">
                <span class="resource-icon">${res.icon}</span>
                <div class="resource-info">
                    <span class="resource-name">${res.name}</span>
                    <span class="resource-value" id="res-value-${res.id}">0</span>
                    <span class="resource-change" id="res-change-${res.id}"></span>
                </div>
            </div>
        `).join('');
    },
    
    /**
     * 初始化建造菜单
     */
    initBuildMenu() {
        const menu = document.getElementById('build-menu');
        menu.innerHTML = GameData.buildings.map(building => `
            <div class="build-item hover-lift" onclick="UI.showBuildingInfo('${building.id}')">
                <span class="build-icon">${building.icon}</span>
                <div class="build-info">
                    <span class="build-name">${building.name}</span>
                    <span class="build-cost">${this.formatCost(building.cost)}</span>
                </div>
                <button class="build-btn btn-ripple" onclick="event.stopPropagation(); UI.build('${building.id}')">建造</button>
            </div>
        `).join('');
    },
    
    /**
     * 更新所有 UI
     */
    updateAll() {
        this.updateResources();
        this.updateTurn();
        this.updateStatusOverview();
        this.updateGameViewport();
    },
    
    /**
     * 更新资源显示
     */
    updateResources() {
        const state = Game.state;
        
        for (const res of GameData.resources) {
            const valueEl = document.getElementById(`res-value-${res.id}`);
            const changeEl = document.getElementById(`res-change-${res.id}`);
            const itemEl = document.getElementById(`resource-${res.id}`);
            
            if (!valueEl) continue;
            
            const current = Math.floor(state.resources[res.id].current);
            const change = state.calculateResourceChange(res.id);
            
            // 更新数值（带动画）
            const oldValue = parseInt(valueEl.textContent) || 0;
            if (current !== oldValue) {
                valueEl.classList.add('value-changed');
                if (current > oldValue) {
                    valueEl.classList.add('value-increased');
                } else {
                    valueEl.classList.add('value-decreased');
                }
                setTimeout(() => {
                    valueEl.classList.remove('value-changed', 'value-increased', 'value-decreased');
                }, 300);
            }
            
            valueEl.textContent = current;
            
            // 更新变化
            if (change !== 0) {
                changeEl.textContent = (change > 0 ? '+' : '') + change + '/回合';
                changeEl.className = 'resource-change ' + (change > 0 ? 'positive' : 'negative');
            } else {
                changeEl.textContent = '';
            }
            
            // 低资源警告
            if (res.warningThreshold && current <= res.warningThreshold) {
                valueEl.classList.add('low');
            } else {
                valueEl.classList.remove('low');
            }
        }
    },
    
    /**
     * 更新回合显示
     */
    updateTurn() {
        document.getElementById('game-time').textContent = `回合 ${Game.state.turn}`;
    },
    
    /**
     * 更新状态总览
     */
    updateStatusOverview() {
        const state = Game.state;
        const overview = document.getElementById('status-overview');
        
        overview.innerHTML = `
            <div class="status-item">
                <span>👥 人口</span>
                <span>${state.population.total}</span>
            </div>
            <div class="status-item">
                <span>🏠 建筑</span>
                <span>${state.buildings.length}</span>
            </div>
        `;
    },
    
    /**
     * 更新游戏主视图
     */
    updateGameViewport() {
        const viewport = document.getElementById('game-viewport');
        const state = Game.state;
        
        // 显示建筑
        let buildingsHtml = state.buildings.map((b, i) => {
            const data = GameData.buildings.find(bd => bd.id === b.type);
            return `
                <div class="building-card animate-scale-in" style="animation-delay: ${i * 0.1}s">
                    <span class="building-icon">${data?.icon || '🏢'}</span>
                    <span class="building-name">${data?.name || b.type}</span>
                    <span class="building-level">Lv.${b.level}</span>
                </div>
            `;
        }).join('');
        
        if (!buildingsHtml) {
            buildingsHtml = '<div class="empty-state">暂无建筑，从右侧菜单开始建造</div>';
        }
        
        viewport.innerHTML = `<div class="buildings-grid">${buildingsHtml}</div>`;
    },
    
    /**
     * 建造建筑
     */
    build(buildingId) {
        const result = Game.state.build(buildingId);
        
        if (result.success) {
            this.addLog(result.message, 'success');
            this.updateAll();
        } else {
            this.addLog(result.message, 'warning');
            // 添加抖动效果
            const menu = document.getElementById('build-menu');
            menu.classList.add('animate-shake');
            setTimeout(() => menu.classList.remove('animate-shake'), 500);
        }
    },
    
    /**
     * 显示建筑信息
     */
    showBuildingInfo(buildingId) {
        const building = GameData.buildings.find(b => b.id === buildingId);
        if (!building) return;
        
        this.addLog(`${building.name}: ${building.description || '暂无描述'}`, 'info');
    },
    
    /**
     * 格式化花费
     */
    formatCost(cost) {
        if (!cost) return '免费';
        return Object.entries(cost).map(([resId, amount]) => {
            const res = GameData.resources.find(r => r.id === resId);
            return `${res?.icon || '💰'}${amount}`;
        }).join(' ');
    },
    
    /**
     * 添加日志
     */
    addLog(message, type = 'info') {
        const logContainer = document.getElementById('game-log');
        const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        
        const entry = document.createElement('div');
        entry.className = 'log-entry animate-slide-up';
        entry.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-message ${type}">${message}</span>
        `;
        
        logContainer.insertBefore(entry, logContainer.firstChild);
        
        // 限制日志数量
        while (logContainer.children.length > 50) {
            logContainer.removeChild(logContainer.lastChild);
        }
    },
    
    /**
     * 初始化菜单粒子效果
     */
    initMenuParticles() {
        const container = document.getElementById('menu-particles');
        if (!container) return;
        
        container.innerHTML = '';
        
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (10 + Math.random() * 10) + 's';
            particle.style.opacity = 0.1 + Math.random() * 0.3;
            particle.style.width = (5 + Math.random() * 10) + 'px';
            particle.style.height = particle.style.width;
            container.appendChild(particle);
        }
    },
};
