/**
 * 霓虹边疆：轨道殖民计划 - 事件系统
 * ═══════════════════════════════════════
 */

const Events = {
    /**
     * 初始化事件系统
     */
    init() {
        // 绑定模态框关闭事件
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });
    },
    
    /**
     * 触发随机事件
     */
    triggerRandomEvent() {
        const eligibleEvents = GameData.events.filter(event => {
            // 检查触发条件
            if (event.minTurn && Game.state.turn < event.minTurn) return false;
            if (event.maxTurn && Game.state.turn > event.maxTurn) return false;
            if (event.condition && !event.condition(Game.state)) return false;
            
            // 检查是否已触发过（一次性事件）
            if (event.once && Game.state.triggeredEvents.includes(event.id)) return false;
            
            return true;
        });
        
        if (eligibleEvents.length === 0) return;
        
        // 根据权重随机选择
        const totalWeight = eligibleEvents.reduce((sum, e) => sum + (e.weight || 1), 0);
        let random = Math.random() * totalWeight;
        
        let selectedEvent = eligibleEvents[0];
        for (const event of eligibleEvents) {
            random -= (event.weight || 1);
            if (random <= 0) {
                selectedEvent = event;
                break;
            }
        }
        
        this.showEvent(selectedEvent);
    },
    
    /**
     * 显示事件
     */
    showEvent(event) {
        const modal = document.getElementById('event-modal');
        const iconEl = document.getElementById('event-icon');
        const titleEl = document.getElementById('event-title');
        const descEl = document.getElementById('event-description');
        const choicesEl = document.getElementById('event-choices');
        
        iconEl.textContent = event.icon || '❓';
        titleEl.textContent = event.title;
        descEl.textContent = event.description;
        
        // 生成选项
        choicesEl.innerHTML = event.choices.map((choice, index) => `
            <button class="event-choice btn-ripple" onclick="Events.selectChoice(${index}, '${event.id}')">
                ${choice.text}
                <span class="choice-effect">${this.formatEffect(choice.effect)}</span>
            </button>
        `).join('');
        
        modal.classList.add('active');
        
        // 记录已触发
        if (event.once) {
            Game.state.triggeredEvents.push(event.id);
        }
        
        UI.addLog(`📢 事件：${event.title}`, 'warning');
    },
    
    /**
     * 选择事件选项
     */
    selectChoice(choiceIndex, eventId) {
        const event = GameData.events.find(e => e.id === eventId);
        if (!event) return;
        
        const choice = event.choices[choiceIndex];
        if (!choice) return;
        
        // 应用效果
        Game.state.applyEventEffect(choice.effect);
        
        // 关闭模态框
        document.getElementById('event-modal').classList.remove('active');
        
        // 更新 UI
        UI.updateAll();
        
        // 日志
        UI.addLog(`选择了：${choice.text}`, 'info');
        
        if (choice.effect.message) {
            UI.addLog(choice.effect.message, choice.effect.messageType || 'info');
        }
    },
    
    /**
     * 格式化效果显示
     */
    formatEffect(effect) {
        const parts = [];
        
        if (effect.resources) {
            for (const [resId, amount] of Object.entries(effect.resources)) {
                const res = GameData.resources.find(r => r.id === resId);
                const prefix = amount > 0 ? '+' : '';
                parts.push(`${res?.icon || '💰'}${prefix}${amount}`);
            }
        }
        
        if (effect.population) {
            const prefix = effect.population > 0 ? '+' : '';
            parts.push(`👥${prefix}${effect.population}`);
        }
        
        return parts.join(' ') || '无直接效果';
    },
};
