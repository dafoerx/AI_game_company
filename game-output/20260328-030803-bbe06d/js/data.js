const GameData = {
  name: "沸腾掌柜：火锅店经营MVP",
  description:
    "在有限营业天数内经营一家火锅店，围绕备货、接待、出餐、结算与复盘展开循环。你需要平衡食材成本、翻台效率与口碑，努力从保本走向稳定盈利。",
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
      consumedPerPopulation: 0
    },
    {
      id: "reputation",
      name: "口碑",
      icon: "⭐",
      initial: 55,
      max: 100,
      perTurn: 0,
      warningThreshold: 25,
      failIfZero: true,
      consumedPerPopulation: 0
    },
    {
      id: "broth",
      name: "锅底库存",
      icon: "🍲",
      initial: 40,
      max: 300,
      perTurn: -1,
      warningThreshold: 8,
      failIfZero: false,
      consumedPerPopulation: 0
    },
    {
      id: "meat",
      name: "肉类库存",
      icon: "🥩",
      initial: 60,
      max: 450,
      perTurn: -2,
      warningThreshold: 12,
      failIfZero: false,
      consumedPerPopulation: 0
    },
    {
      id: "veggie",
      name: "蔬菜库存",
      icon: "🥬",
      initial: 70,
      max: 450,
      perTurn: -2,
      warningThreshold: 16,
      failIfZero: false,
      consumedPerPopulation: 0
    },
    {
      id: "drinks",
      name: "饮品库存",
      icon: "🥤",
      initial: 50,
      max: 320,
      perTurn: -1,
      warningThreshold: 10,
      failIfZero: false,
      consumedPerPopulation: 0
    }
  ],

  // ===== 建筑/升级定义 =====
  buildings: [
    {
      id: "front_hall",
      name: "迎宾前厅",
      icon: "🧧",
      description: "优化排队与引导效率，提升翻台速度与首单转化。",
      cost: { cash: 1800, drinks: 5 },
      produces: { cash: 260, reputation: 2 },
      consumes: { broth: 1, meat: 2, veggie: 2, drinks: 1 }
    },
    {
      id: "prep_kitchen",
      name: "备料后厨",
      icon: "🔪",
      description: "标准化切配流程，降低断货风险并补充核心食材。",
      cost: { cash: 2400 },
      produces: { broth: 3, meat: 5, veggie: 5 },
      consumes: { cash: 80 }
    },
    {
      id: "sauce_bar",
      name: "自助蘸料台",
      icon: "🥣",
      description: "增强顾客体验，带来口碑提升和附加消费。",
      cost: { cash: 1500, veggie: 8 },
      produces: { cash: 180, reputation: 3 },
      consumes: { veggie: 2, drinks: 1 }
    },
    {
      id: "cold_storage",
      name: "冷链冰柜",
      icon: "🧊",
      description: "提升冷藏能力，减少损耗并稳定肉菜供应。",
      cost: { cash: 2800, meat: 10 },
      produces: { meat: 4, veggie: 3 },
      consumes: { cash: 90 }
    },
    {
      id: "smart_cashier",
      name: "智能收银台",
      icon: "🧾",
      description: "缩短结算时间，提升高峰处理能力与复购意愿。",
      cost: { cash: 2200, drinks: 5 },
      produces: { cash: 320, reputation: 1 },
      consumes: { broth: 1, meat: 1, veggie: 1 }
    },
    {
      id: "delivery_window",
      name: "外卖打包窗",
      icon: "🛵",
      description: "拓展外卖收入，但出品稳定性与口碑存在压力。",
      cost: { cash: 2600, broth: 8 },
      produces: { cash: 350, reputation: -1 },
      consumes: { broth: 2, meat: 2, veggie: 2, drinks: 1 }
    },
    {
      id: "waiting_lounge",
      name: "等位区升级",
      icon: "🛋️",
      description: "改善等位体验，缓和排队焦虑，稳步提高评分。",
      cost: { cash: 2000, drinks: 10 },
      produces: { cash: 160, reputation: 4 },
      consumes: { drinks: 2 }
    }
  ],

  // ===== 事件定义 =====
  events: [
    {
      id: "lunch_rush",
      title: "午市暴涨",
      description: "写字楼团体临时到店，门口瞬间排起长队，前厅压力陡增。",
      icon: "🔥",
      weight: 4,
      minTurn: 1,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "全员冲刺接待",
          effect: {
            resources: { cash: 900, reputation: -3, broth: -3, meat: -6, veggie: -5, drinks: -2 },
            message: "你抓住了营业额，但服务细节下降，口碑略受影响。",
            messageType: "warning"
          }
        },
        {
          text: "限号保质保量",
          effect: {
            resources: { cash: 520, reputation: 2, broth: -2, meat: -3, veggie: -3, drinks: -1 },
            message: "收入略少，但顾客体验更稳，评价上升。",
            messageType: "success"
          }
        },
        {
          text: "临时关闭外卖通道",
          effect: {
            resources: { cash: 300, broth: -1, meat: -2, veggie: -2 },
            message: "压力被缓解，前厅秩序恢复，但错失部分营收。",
            messageType: "info"
          }
        }
      ]
    },
    {
      id: "supplier_discount",
      title: "供应商促销日",
      description: "食材批发商放出限时折扣，今天进货可享更高性价比。",
      icon: "📦",
      weight: 3,
      minTurn: 2,
      maxTurn: 28,
      once: false,
      choices: [
        {
          text: "大批量囤货",
          effect: {
            resources: { cash: -1200, broth: 12, meat: 20, veggie: 18, drinks: 10, reputation: 1 },
            message: "库存充足，后续几日经营更从容。",
            messageType: "success"
          }
        },
        {
          text: "只补紧缺食材",
          effect: {
            resources: { cash: -700, broth: 6, meat: 10, veggie: 8, drinks: 4 },
            message: "稳健采购，现金压力可控。",
            messageType: "info"
          }
        },
        {
          text: "现金紧张先观望",
          effect: {
            resources: { reputation: -1 },
            message: "错过折扣窗口，后续备货弹性下降。",
            messageType: "warning"
          }
        }
      ]
    },
    {
      id: "safety_inspection",
      title: "食安突击检查",
      description: "监管人员临检，后厨规范与卫生细节将直接影响品牌信任。",
      icon: "🧪",
      weight: 2,
      minTurn: 4,
      maxTurn: 30,
      once: true,
      choices: [
        {
          text: "停业半日深度清洁",
          effect: {
            resources: { cash: -800, reputation: 6 },
            message: "短期损失营业额，但通过高标准整改赢得信任。",
            messageType: "success"
          }
        },
        {
          text: "正常营业并加强巡检",
          effect: {
            resources: { cash: -300, reputation: 2 },
            message: "基本达标，影响可控。",
            messageType: "info"
          }
        },
        {
          text: "侥幸应对抽查",
          effect: {
            resources: { cash: -1500, reputation: -10 },
            message: "被发现细节问题，罚款并引发差评。",
            messageType: "danger"
          }
        }
      ]
    },
    {
      id: "influencer_visit",
      title: "探店博主来访",
      description: "本地美食博主到店直播，处理得当可迅速扩大知名度。",
      icon: "📸",
      weight: 2,
      minTurn: 5,
      maxTurn: 25,
      once: false,
      choices: [
        {
          text: "赠送招牌拼盘并重点服务",
          effect: {
            resources: { cash: -400, meat: -4, veggie: -3, drinks: -2, reputation: 8 },
            message: "直播反响极佳，门店热度明显上升。",
            messageType: "success"
          }
        },
        {
          text: "按常规流程接待",
          effect: {
            resources: { cash: 220, reputation: 2, broth: -1, meat: -2, veggie: -2 },
            message: "表现平稳，获得中规中矩的曝光。",
            messageType: "info"
          }
        },
        {
          text: "婉拒拍摄避免打扰",
          effect: {
            resources: { reputation: -6 },
            message: "部分网友认为服务不够开放，评价下滑。",
            messageType: "warning"
          }
        }
      ]
    },
    {
      id: "staff_fatigue",
      title: "员工疲劳预警",
      description: "连续高峰导致后厨与前厅疲劳累积，团队状态下降。",
      icon: "😵",
      weight: 3,
      minTurn: 8,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "发放夜班补贴并轮休",
          effect: {
            resources: { cash: -600, reputation: 4 },
            message: "团队士气回升，服务稳定性提升。",
            messageType: "success"
          }
        },
        {
          text: "缩短营业1小时",
          effect: {
            resources: { cash: -350, reputation: 1, broth: 1, meat: 2, veggie: 2, drinks: 1 },
            message: "营收略降，但避免了更大的人力透支。",
            messageType: "info"
          }
        },
        {
          text: "继续满负荷营业",
          effect: {
            resources: { cash: 450, reputation: -5 },
            message: "短期收入增加，但顾客体验显著下降。",
            messageType: "danger"
          }
        }
      ]
    },
    {
      id: "cold_wave_demand",
      title: "寒潮来袭",
      description: "气温骤降，火锅需求激增，若能承接住将获得可观收益。",
      icon: "❄️",
      weight: 2,
      minTurn: 10,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "加推暖冬双人套餐",
          effect: {
            resources: { cash: 1000, reputation: 3, broth: -4, meat: -5, veggie: -4, drinks: -1 },
            message: "爆单成功，营收与好评同步增长。",
            messageType: "success"
          }
        },
        {
          text: "保持常规出餐节奏",
          effect: {
            resources: { cash: 500, broth: -2, meat: -3, veggie: -2 },
            message: "稳步盈利，没有出现严重拥堵。",
            messageType: "info"
          }
        },
        {
          text: "备货不足被迫限售",
          effect: {
            resources: { cash: 150, reputation: -4 },
            message: "顾客等待过久且菜品缺货，口碑受损。",
            messageType: "warning"
          }
        }
      ]
    }
  ],

  // ===== 胜利条件 =====
  victoryCondition: (state) => {
    const turn =
      typeof state?.turn === "number"
        ? state.turn
        : typeof state?.currentTurn === "number"
        ? state.currentTurn
        : 0;

    const getResourceValue = (id) => {
      const pool = state?.resources;
      if (!pool) return 0;

      if (Array.isArray(pool)) {
        const found = pool.find((r) => r && r.id === id);
        if (!found) return 0;
        if (typeof found.value === "number") return found.value;
        if (typeof found.amount === "number") return found.amount;
        if (typeof found.current === "number") return found.current;
        return 0;
      }

      if (typeof pool[id] === "number") return pool[id];
      if (pool[id] && typeof pool[id].value === "number") return pool[id].value;
      if (pool[id] && typeof pool[id].amount === "number") return pool[id].amount;
      return 0;
    };

    return turn >= 30 && getResourceValue("cash") >= 28000 && getResourceValue("reputation") >= 75;
  }
};