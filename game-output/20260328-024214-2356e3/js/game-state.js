/**
 * 沸腾掌柜：火锅店经营MVP - 游戏状态管理
 * ═══════════════════════════════════════
 */

class GameState {
    constructor() {
        this.reset();
    }
    
    /**
     * 重置游戏状态
     */
    reset() {
        // 回合数
        this.turn = 1;
        
        // 资源
        this.resources = {};
        for (const res of GameData.resources) {
            this.resources[res.id] = {
                current: res.initial,
                max: res.max || Infinity,
                perTurn: res.perTurn || 0,
            };
        }
        
        // 建筑
        this.buildings = [];
        
        // 人口/单位
        this.population = {
            total: GameData.initialPopulation || 10,
            available: GameData.initialPopulation || 10,
            assigned: {},
        };
        
        // 已触发的事件
        this.triggeredEvents = [];
        
        // 成就/里程碑
        this.achievements = [];
        
        // 游戏统计
        this.stats = {
            totalTurns: 0,
            resourcesGained: {},
            resourcesSpent: {},
            eventsTriggered: 0,
            buildingsBuilt: 0,
        };
    }
    
    /**
     * 处理一个回合
     */
    processTurn() {
        const results = {
            resourceChanges: {},
            events: [],
            messages: [],
        };
        
        // 1. 计算资源产出
        for (const [resId, res] of Object.entries(this.resources)) {
            const change = this.calculateResourceChange(resId);
            results.resourceChanges[resId] = change;
            
            const newValue = Math.max(0, Math.min(res.max, res.current + change));
            res.current = newValue;
            
            // 记录统计
            if (change > 0) {
                this.stats.resourcesGained[resId] = (this.stats.resourcesGained[resId] || 0) + change;
            } else if (change < 0) {
                this.stats.resourcesSpent[resId] = (this.stats.resourcesSpent[resId] || 0) + Math.abs(change);
            }
        }
        
        // 2. 处理建筑效果
        for (const building of this.buildings) {
            this.processBuildingEffect(building, results);
        }
        
        // 3. 更新人口
        this.updatePopulation();
        
        // 4. 增加回合数
        this.turn++;
        this.stats.totalTurns++;
        
        return results;
    }
    
    /**
     * 计算资源变化
     */
    calculateResourceChange(resourceId) {
        let change = this.resources[resourceId].perTurn || 0;
        
        // 建筑产出
        for (const building of this.buildings) {
            const buildingData = GameData.buildings.find(b => b.id === building.type);
            if (buildingData && buildingData.produces && buildingData.produces[resourceId]) {
                change += buildingData.produces[resourceId] * (building.level || 1);
            }
            if (buildingData && buildingData.consumes && buildingData.consumes[resourceId]) {
                change -= buildingData.consumes[resourceId] * (building.level || 1);
            }
        }
        
        // 人口消耗
        const resData = GameData.resources.find(r => r.id === resourceId);
        if (resData && resData.consumedPerPopulation) {
            change -= resData.consumedPerPopulation * this.population.total;
        }
        
        return change;
    }
    
    /**
     * 处理建筑效果
     */
    processBuildingEffect(building, results) {
        // 可以在这里添加建筑特殊效果
    }
    
    /**
     * 更新人口
     */
    updatePopulation() {
        // 简单的人口增长逻辑
        // 可以根据游戏设计调整
    }
    
    /**
     * 建造建筑
     */
    build(buildingId) {
        const buildingData = GameData.buildings.find(b => b.id === buildingId);
        if (!buildingData) return { success: false, message: '建筑不存在' };
        
        // 检查资源
        for (const [resId, amount] of Object.entries(buildingData.cost || {})) {
            if (!this.resources[resId] || this.resources[resId].current < amount) {
                return { success: false, message: '资源不足' };
            }
        }
        
        // 扣除资源
        for (const [resId, amount] of Object.entries(buildingData.cost || {})) {
            this.resources[resId].current -= amount;
        }
        
        // 添加建筑
        this.buildings.push({
            type: buildingId,
            level: 1,
            builtAt: this.turn,
        });
        
        this.stats.buildingsBuilt++;
        
        return { success: true, message: `成功建造 ${buildingData.name}` };
    }
    
    /**
     * 检查游戏结束条件
     */
    checkEndCondition() {
        // 检查失败条件
        for (const res of GameData.resources) {
            if (res.failIfZero && this.resources[res.id].current <= 0) {
                return {
                    ended: true,
                    victory: false,
                    message: `${res.name}耗尽，游戏失败！`,
                };
            }
        }
        
        // 检查胜利条件
        if (GameData.victoryCondition) {
            const victory = GameData.victoryCondition(this);
            if (victory) {
                return {
                    ended: true,
                    victory: true,
                    message: '恭喜达成目标！',
                };
            }
        }
        
        // 默认回合数胜利
        if (this.turn >= (GameData.maxTurns || 100)) {
            return {
                ended: true,
                victory: true,
                message: `成功存活了 ${this.turn} 回合！`,
            };
        }
        
        return { ended: false };
    }
    
    /**
     * 获取统计数据
     */
    getStats() {
        return {
            '总回合数': this.stats.totalTurns,
            '建筑数量': this.buildings.length,
            '触发事件': this.stats.eventsTriggered,
        };
    }
    
    /**
     * 应用事件效果
     */
    applyEventEffect(effect) {
        if (effect.resources) {
            for (const [resId, amount] of Object.entries(effect.resources)) {
                if (this.resources[resId]) {
                    this.resources[resId].current = Math.max(0, 
                        Math.min(this.resources[resId].max, this.resources[resId].current + amount)
                    );
                }
            }
        }
        
        if (effect.population) {
            this.population.total = Math.max(0, this.population.total + effect.population);
            this.population.available = Math.max(0, this.population.available + effect.population);
        }
        
        this.stats.eventsTriggered++;
    }
}
