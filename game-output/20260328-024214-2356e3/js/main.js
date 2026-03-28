/**
 * 沸腾掌柜：火锅店经营MVP - 主入口
 * ═══════════════════════════════════════
 */

// 游戏主对象
const Game = {
    // 游戏状态
    state: null,
    
    // 是否暂停
    isPaused: false,
    
    // 当前屏幕
    currentScreen: 'loading-screen',
    
    /**
     * 初始化游戏
     */
    init() {
        console.log('🎮 沸腾掌柜：火锅店经营MVP 初始化中...');
        
        // 初始化游戏状态
        this.state = new GameState();
        
        // 初始化 UI
        UI.init();
        
        // 初始化事件系统
        Events.init();
        
        // 模拟加载过程
        this.simulateLoading();
    },
    
    /**
     * 模拟加载过程
     */
    simulateLoading() {
        const loadingBar = document.querySelector('.loading-progress');
        const loadingText = document.querySelector('.loading-text');
        
        const steps = [
            { progress: 20, text: '加载游戏资源...' },
            { progress: 40, text: '初始化游戏系统...' },
            { progress: 60, text: '准备游戏数据...' },
            { progress: 80, text: '加载界面组件...' },
            { progress: 100, text: '准备就绪！' },
        ];
        
        let stepIndex = 0;
        
        const loadStep = () => {
            if (stepIndex >= steps.length) {
                setTimeout(() => this.showScreen('main-menu'), 500);
                return;
            }
            
            const step = steps[stepIndex];
            loadingBar.style.width = step.progress + '%';
            loadingText.textContent = step.text;
            stepIndex++;
            
            setTimeout(loadStep, 400);
        };
        
        setTimeout(loadStep, 500);
    },
    
    /**
     * 切换屏幕
     */
    showScreen(screenId) {
        // 隐藏当前屏幕
        const currentEl = document.getElementById(this.currentScreen);
        if (currentEl) {
            currentEl.classList.remove('active');
        }
        
        // 显示新屏幕
        const newEl = document.getElementById(screenId);
        if (newEl) {
            setTimeout(() => {
                newEl.classList.add('active');
            }, 100);
        }
        
        this.currentScreen = screenId;
        
        // 如果是主菜单，初始化粒子效果
        if (screenId === 'main-menu') {
            UI.initMenuParticles();
        }
    },
    
    /**
     * 开始新游戏
     */
    startNewGame() {
        console.log('🎮 开始新游戏');
        
        // 重置游戏状态
        this.state.reset();
        this.isPaused = false;
        
        // 切换到游戏屏幕
        this.showScreen('game-screen');
        
        // 初始化游戏 UI
        UI.updateAll();
        
        // 添加开局日志
        UI.addLog('游戏开始！欢迎来到 沸腾掌柜：火锅店经营MVP', 'success');
        UI.addLog('提示：合理分配资源，保持稳定发展');
    },
    
    /**
     * 下一回合
     */
    nextTurn() {
        if (this.isPaused) return;
        
        console.log('⏭️ 执行回合 ' + this.state.turn);
        
        // 执行回合逻辑
        const result = this.state.processTurn();
        
        // 更新 UI
        UI.updateAll();
        
        // 触发随机事件
        if (Math.random() < 0.3) {
            Events.triggerRandomEvent();
        }
        
        // 检查游戏结束条件
        this.checkGameOver();
    },
    
    /**
     * 检查游戏结束
     */
    checkGameOver() {
        const result = this.state.checkEndCondition();
        
        if (result.ended) {
            this.endGame(result.victory, result.message);
        }
    },
    
    /**
     * 结束游戏
     */
    endGame(victory, message) {
        console.log(victory ? '🏆 胜利！' : '💀 失败...');
        
        const titleEl = document.getElementById('game-over-title');
        const messageEl = document.getElementById('game-over-message');
        const statsEl = document.getElementById('game-over-stats');
        
        titleEl.textContent = victory ? '🏆 胜利！' : '💀 游戏结束';
        titleEl.className = victory ? 'victory' : 'defeat';
        messageEl.textContent = message || (victory ? '恭喜你完成了目标！' : '很遗憾，你失败了...');
        
        // 显示统计数据
        const stats = this.state.getStats();
        statsEl.innerHTML = Object.entries(stats).map(([key, value]) => `
            <div class="stat-item">
                <div class="stat-value">${value}</div>
                <div class="stat-label">${key}</div>
            </div>
        `).join('');
        
        this.showScreen('game-over');
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
        this.showScreen('main-menu');
    },
    
    /**
     * 切换暂停
     */
    togglePause() {
        this.isPaused = !this.isPaused;
        const icon = document.getElementById('pause-icon');
        icon.textContent = this.isPaused ? '▶️' : '⏸️';
        
        UI.addLog(this.isPaused ? '游戏已暂停' : '游戏继续', 'info');
    },
    
    /**
     * 打开菜单
     */
    openMenu() {
        // 暂停游戏并显示菜单选项
        this.isPaused = true;
        this.showSettings();
    },
    
    /**
     * 显示设置
     */
    showSettings() {
        this.showModal('settings-modal');
    },
    
    /**
     * 显示帮助
     */
    showHelp() {
        this.showModal('help-modal');
    },
    
    /**
     * 显示模态框
     */
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    },
    
    /**
     * 关闭模态框
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    },
};

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    Game.init();
});
