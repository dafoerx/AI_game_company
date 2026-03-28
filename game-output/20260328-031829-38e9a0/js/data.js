const GameData = {
  // 游戏基础信息
  name: "沸腾掌柜：火锅店经营MVP",
  description:
    "在30个营业日内经营一家火锅店，围绕“备货—接待—出餐—结算—复盘”进行决策。你需要平衡现金流、食材库存与顾客口碑，在高峰期稳定翻台，努力从保本走向盈利。",
  maxTurns: 30,
  initialPopulation: 0,

  // ===== 资源定义 =====
  resources: [
    {
      id: "cash",
      name: "现金",
      icon: "💴",
      initial: 12000,
      max: 999999,
      perTurn: 0,
      warningThreshold: 1500,
      failIfZero: true,
      consumedPerPopulation: 0,
    },
    {
      id: "reputation",
      name: "口碑",
      icon: "⭐",
      initial: 55,
      max: 100,
      perTurn: -1,
      warningThreshold: 25,
      failIfZero: true,
      consumedPerPopulation: 0,
    },
    {
      id: "broth",
      name: "锅底",
      icon: "🍲",
      initial: 45,
      max: 500,
      perTurn: -1,
      warningThreshold: 10,
      failIfZero: false,
      consumedPerPopulation: 0,
    },
    {
      id: "meat",
      name: "肉类",
      icon: "🥩",
      initial: 80,
      max: 800,
      perTurn: -2,
      warningThreshold: 15,
      failIfZero: false,
      consumedPerPopulation: 0,
    },
    {
      id: "veggies",
      name: "蔬菜",
      icon: "🥬",
      initial: 90,
      max: 800,
      perTurn: -2,
      warningThreshold: 20,
      failIfZero: false,
      consumedPerPopulation: 0,
    },
    {
      id: "drinks",
      name: "饮品",
      icon: "🥤",
      initial: 60,
      max: 600,
      perTurn: -1,
      warningThreshold: 10,
      failIfZero: false,
      consumedPerPopulation: 0,
    },
  ],

  // ===== 建筑/升级定义 =====
  buildings: [
    {
      id: "prep_station",
      name: "备菜台",
      icon: "🔪",
      description: "提升日常切配效率，稳定补充肉类与蔬菜库存。",
      cost: { cash: 1800 },
      produces: { meat: 14, veggies: 18 },
      consumes: { cash: 320 },
    },
    {
      id: "broth_kitchen",
      name: "底料后厨",
      icon: "🫕",
      description: "强化锅底熬制能力，提升出锅稳定性与顾客评价。",
      cost: { cash: 2200 },
      produces: { broth: 16, reputation: 1 },
      consumes: { cash: 280 },
    },
    {
      id: "beverage_bar",
      name: "饮品台",
      icon: "🍹",
      description: "补充饮品并附带增收，提高客单价。",
      cost: { cash: 1500 },
      produces: { drinks: 14, cash: 220 },
      consumes: { cash: 120 },
    },
    {
      id: "dining_area",
      name: "餐桌区扩容",
      icon: "🪑",
      description: "增加接待能力，提升翻台效率并创造稳定营收。",
      cost: { cash: 2600 },
      produces: { cash: 520, reputation: 1 },
      consumes: { broth: 4, meat: 8, veggies: 8, drinks: 3 },
    },
    {
      id: "express_line",
      name: "出餐快线",
      icon: "🚀",
      description: "优化后厨动线，晚高峰出餐更快，收益与口碑双增。",
      cost: { cash: 3200 },
      produces: { cash: 780, reputation: 2 },
      consumes: { broth: 6, meat: 10, veggies: 9, drinks: 4 },
    },
    {
      id: "service_training",
      name: "服务培训站",
      icon: "🎓",
      description: "提升服务标准化，降低差评风险，稳步改善口碑。",
      cost: { cash: 2000 },
      produces: { reputation: 3, cash: 180 },
      consumes: { cash: 150, drinks: 2 },
    },
    {
      id: "cold_storage",
      name: "冷库保鲜仓",
      icon: "🧊",
      description: "减少食材浪费，缓冲高峰采购压力。",
      cost: { cash: 2800 },
      produces: { meat: 10, veggies: 10, cash: 120 },
      consumes: { cash: 180 },
    },
  ],

  // ===== 事件定义 =====
  events: [
    {
      id: "morning_market_discount",
      title: "清晨批发市场特价",
      description: "供应商放出短时折扣，适合补一波明后天库存。",
      icon: "🛒",
      weight: 3,
      minTurn: 1,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "大量囤货（高风险高回报）",
          effect: {
            resources: {
              cash: -1800,
              broth: 18,
              meat: 30,
              veggies: 24,
              drinks: 12,
              reputation: 1,
            },
            message: "你抓住折扣窗口，大幅补足库存，营业底气更足了。",
            messageType: "success",
          },
        },
        {
          text: "精准补货（稳健）",
          effect: {
            resources: {
              cash: -1000,
              broth: 10,
              meat: 15,
              veggies: 15,
              drinks: 8,
            },
            message: "按缺口补货，现金压力可控，库存结构更均衡。",
            messageType: "info",
          },
        },
        {
          text: "暂不采购",
          effect: {
            resources: { reputation: -2 },
            message: "你错过了低价窗口，员工觉得有些保守，士气略受影响。",
            messageType: "warning",
          },
        },
      ],
    },
    {
      id: "influencer_visit",
      title: "探店博主上门",
      description: "本地美食博主临时到店，是否借机拉升线上热度？",
      icon: "📸",
      weight: 2,
      minTurn: 4,
      maxTurn: 22,
      once: false,
      choices: [
        {
          text: "送上霸王套餐冲热度",
          effect: {
            resources: { cash: -600, meat: -10, veggies: -8, drinks: -6, reputation: 9 },
            message: "视频爆了！虽然当场让利，但店铺讨论度明显提升。",
            messageType: "success",
          },
        },
        {
          text: "正常接待，稳妥经营",
          effect: {
            resources: { cash: 400, reputation: 3 },
            message: "没有刻意营销，但服务到位，得到中规中矩好评。",
            messageType: "info",
          },
        },
        {
          text: "婉拒拍摄",
          effect: {
            resources: { reputation: -5 },
            message: "你避免了打扰堂食，但失去了宣传机会，口碑热度下滑。",
            messageType: "warning",
          },
        },
      ],
    },
    {
      id: "safety_inspection",
      title: "食安突击检查",
      description: "监管部门临时抽检后厨与冷藏流程，处理方式将影响长线口碑。",
      icon: "🧾",
      weight: 2,
      minTurn: 3,
      maxTurn: 28,
      once: false,
      choices: [
        {
          text: "全面自查并整改",
          effect: {
            resources: { cash: -1500, reputation: 6 },
            message: "你投入成本优化流程，获得了长期信任红利。",
            messageType: "success",
          },
        },
        {
          text: "临时应付检查",
          effect: {
            resources: { cash: -600, reputation: -2 },
            message: "短期省钱，但细节问题被顾客察觉，口碑受损。",
            messageType: "warning",
          },
        },
        {
          text: "侥幸压低处理",
          effect: {
            resources: { cash: 300, reputation: -10 },
            message: "你省下了一点开支，却埋下了严重的信任隐患。",
            messageType: "danger",
          },
        },
      ],
    },
    {
      id: "evening_power_outage",
      title: "晚高峰临时断电",
      description: "商圈电路波动导致设备停摆，晚高峰订单面临延误。",
      icon: "💡",
      weight: 1,
      minTurn: 6,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "启动备用发电机",
          effect: {
            resources: { cash: -900, reputation: 2 },
            message: "成本上升但服务稳定，顾客感受到你的专业。",
            messageType: "info",
          },
        },
        {
          text: "发放饮品券安抚顾客",
          effect: {
            resources: { cash: -500, drinks: -5, reputation: 1 },
            message: "你用补偿换取理解，损失可控，负评减少。",
            messageType: "warning",
          },
        },
        {
          text: "提前打烊止损",
          effect: {
            resources: { cash: -1200, reputation: -4, broth: -6, meat: -8, veggies: -8 },
            message: "你避免了更大混乱，但当晚营业损失明显。",
            messageType: "danger",
          },
        },
      ],
    },
    {
      id: "holiday_peak",
      title: "节假日晚市暴涨",
      description: "客流突然上扬，是否全力冲单将决定当日收益与口碑走势。",
      icon: "🔥",
      weight: 2,
      minTurn: 8,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "全员冲高峰，最大化营收",
          effect: {
            resources: {
              cash: 2800,
              reputation: 4,
              broth: -10,
              meat: -18,
              veggies: -14,
              drinks: -10,
            },
            message: "你抓住旺季窗口，单日收益亮眼，团队配合也更默契。",
            messageType: "success",
          },
        },
        {
          text: "控制节奏，稳住服务",
          effect: {
            resources: {
              cash: 1700,
              reputation: 2,
              broth: -6,
              meat: -10,
              veggies: -10,
              drinks: -6,
            },
            message: "你选择稳步接单，收入不错且顾客体验平稳。",
            messageType: "info",
          },
        },
        {
          text: "人手不足仍硬接单",
          effect: {
            resources: {
              cash: 2200,
              reputation: -5,
              broth: -8,
              meat: -12,
              veggies: -12,
              drinks: -8,
            },
            message: "短期收入提升，但出餐延迟引发大量抱怨。",
            messageType: "danger",
          },
        },
      ],
    },
    {
      id: "community_group_buy",
      title: "社区团购合作邀约",
      description: "附近社区发起团购联名，能快速引流但对出餐组织有要求。",
      icon: "🤝",
      weight: 1,
      minTurn: 10,
      maxTurn: 26,
      once: true,
      choices: [
        {
          text: "参加团购活动，扩大覆盖",
          effect: {
            resources: {
              cash: 1400,
              reputation: 5,
              broth: -6,
              meat: -10,
              veggies: -10,
              drinks: -6,
            },
            message: "活动带来新客，品牌曝光显著提升。",
            messageType: "success",
          },
        },
        {
          text: "只做堂食，保服务质量",
          effect: {
            resources: { cash: 500, reputation: 3 },
            message: "你守住了服务节奏，增长较慢但更稳健。",
            messageType: "info",
          },
        },
        {
          text: "放弃合作",
          effect: {
            resources: { reputation: -3 },
            message: "你避免了运营复杂度，但错失了一次口碑扩散机会。",
            messageType: "warning",
          },
        },
      ],
    },
  ],

  // ===== 胜利条件 =====
  victoryCondition: function (state) {
    const resources = state && state.resources ? state.resources : null;
    const turn = (state && (state.turn || state.currentTurn || state.day)) || 0;

    const getValue = function (id) {
      if (!resources) return 0;

      if (Array.isArray(resources)) {
        const found = resources.find(function (r) {
          return r && r.id === id;
        });
        if (!found) return 0;
        if (typeof found === "number") return found;
        if (typeof found.value === "number") return found.value;
        if (typeof found.amount === "number") return found.amount;
        if (typeof found.current === "number") return found.current;
        return 0;
      }

      if (typeof resources[id] === "number") return resources[id];
      if (resources[id] && typeof resources[id].value === "number") return resources[id].value;
      if (resources[id] && typeof resources[id].amount === "number") return resources[id].amount;
      if (resources[id] && typeof resources[id].current === "number") return resources[id].current;

      return 0;
    };

    const cash = getValue("cash");
    const reputation = getValue("reputation");
    return turn >= 30 && cash >= 45000 && reputation >= 75;
  },
};