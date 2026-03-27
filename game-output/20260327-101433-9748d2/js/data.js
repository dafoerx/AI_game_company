/**
 * 霓虹边疆：轨道殖民计划 - 游戏数据定义
 * ═══════════════════════════════════════
 */

const GameData = {
    // 游戏名称
    name: '霓虹边疆：轨道殖民计划',
    
    // 游戏描述
    description: '这是一款Web端的太空殖民模拟原型，玩家作为赛博企业任命的殖民主管，在近地轨道与废弃卫星带建立新据点，在资源稀缺、系统故障与企业审计压力下，平衡人口生存、设施扩张与能源稳定，体验“高科技低生存”的赛博',
    
    // 最大回合数
    maxTurns: 100,
    
    // 初始人口
    initialPopulation: 10,
    
    // 资源定义
    resources: [
        {
            id: 'energy',
            name: '能源',
            icon: '⚡',
            initial: 100,
            max: 500,
            perTurn: 5,
            warningThreshold: 20,
            failIfZero: true,
        },
        {
            id: 'materials',
            name: '材料',
            icon: '🔩',
            initial: 50,
            max: 300,
            perTurn: 2,
            warningThreshold: 10,
        },
        {
            id: 'food',
            name: '食物',
            icon: '🍞',
            initial: 80,
            max: 200,
            perTurn: 3,
            consumedPerPopulation: 0.5,
            warningThreshold: 20,
            failIfZero: true,
        },
        {
            id: 'credits',
            name: '资金',
            icon: '💰',
            initial: 200,
            max: 10000,
            perTurn: 10,
        },
    ],
    
    // 建筑定义
    buildings: [
        {
            id: 'generator',
            name: '发电站',
            icon: '🏭',
            description: '提供稳定的能源供应',
            cost: { materials: 30, credits: 50 },
            produces: { energy: 10 },
        },
        {
            id: 'mine',
            name: '采矿场',
            icon: '⛏️',
            description: '开采材料资源',
            cost: { energy: 20, credits: 40 },
            produces: { materials: 5 },
        },
        {
            id: 'farm',
            name: '农场',
            icon: '🌾',
            description: '生产食物',
            cost: { materials: 25, credits: 30 },
            produces: { food: 8 },
        },
        {
            id: 'housing',
            name: '居住区',
            icon: '🏠',
            description: '增加人口上限',
            cost: { materials: 50, energy: 30, credits: 100 },
        },
        {
            id: 'market',
            name: '贸易站',
            icon: '🏪',
            description: '增加资金收入',
            cost: { materials: 40, energy: 20, credits: 80 },
            produces: { credits: 15 },
        },
    ],
    
    // 事件定义
    events: [
        {
            id: 'power_surge',
            title: '能源波动',
            description: '检测到能源网络不稳定，需要紧急处理。',
            icon: '⚡',
            weight: 2,
            choices: [
                {
                    text: '紧急维修',
                    effect: {
                        resources: { energy: -20, credits: -30 },
                        message: '成功稳定了能源网络',
                        messageType: 'success',
                    },
                },
                {
                    text: '暂时忽略',
                    effect: {
                        resources: { energy: -50 },
                        message: '能源损失严重！',
                        messageType: 'danger',
                    },
                },
            ],
        },
        {
            id: 'trade_opportunity',
            title: '贸易机会',
            description: '一支商队路过，愿意进行交易。',
            icon: '🤝',
            weight: 2,
            choices: [
                {
                    text: '购买物资',
                    effect: {
                        resources: { credits: -100, materials: 30, food: 20 },
                        message: '获得了宝贵的物资',
                        messageType: 'success',
                    },
                },
                {
                    text: '出售能源',
                    effect: {
                        resources: { energy: -50, credits: 80 },
                        message: '获得了一笔资金',
                        messageType: 'info',
                    },
                },
                {
                    text: '礼貌拒绝',
                    effect: {
                        message: '商队继续前行了',
                    },
                },
            ],
        },
        {
            id: 'natural_disaster',
            title: '自然灾害',
            description: '一场风暴正在逼近，可能造成破坏。',
            icon: '🌪️',
            weight: 1,
            minTurn: 5,
            choices: [
                {
                    text: '加固防御',
                    effect: {
                        resources: { materials: -40, energy: -20 },
                        message: '成功抵御了风暴',
                        messageType: 'success',
                    },
                },
                {
                    text: '冒险继续',
                    effect: {
                        resources: { materials: -60, food: -30 },
                        message: '风暴造成了较大损失',
                        messageType: 'danger',
                    },
                },
            ],
        },
        {
            id: 'discovery',
            title: '意外发现',
            description: '探索队在附近发现了一处资源矿脉！',
            icon: '🎉',
            weight: 1,
            minTurn: 10,
            once: true,
            choices: [
                {
                    text: '立即开采',
                    effect: {
                        resources: { materials: 100, energy: -30 },
                        message: '获得了大量材料！',
                        messageType: 'success',
                    },
                },
                {
                    text: '标记位置，稍后开采',
                    effect: {
                        resources: { materials: 30 },
                        message: '记录了矿脉位置',
                    },
                },
            ],
        },
    ],
    
    // 胜利条件（可选）
    victoryCondition: (state) => {
        // 例如：累计资金达到 5000
        return state.resources.credits.current >= 5000;
    },
};
