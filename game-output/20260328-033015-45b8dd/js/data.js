const GameData = {
  name: "沸腾掌柜：火锅店经营MVP",
  description:
    "在30个营业日内经营一家火锅店，围绕“备货—接待—出餐—结算—复盘”循环，平衡现金流、食材库存与顾客口碑，在高峰与突发事件中从保本走向盈利。",
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
      perTurn: -280,
      warningThreshold: 1500,
      failIfZero: true,
      consumedPerPopulation: 0,
    },
    {
      id: "ingredients",
      name: "食材",
      icon: "🥩",
      initial: 140,
      max: 999,
      perTurn: -5,
      warningThreshold: 30,
      failIfZero: false,
      consumedPerPopulation: 0,
    },
    {
      id: "broth",
      name: "锅底包",
      icon: "🍲",
      initial: 70,
      max: 500,
      perTurn: -2,
      warningThreshold: 12,
      failIfZero: false,
      consumedPerPopulation: 0,
    },
    {
      id: "drinks",
      name: "饮品库存",
      icon: "🧋",
      initial: 80,
      max: 500,
      perTurn: -1,
      warningThreshold: 10,
      failIfZero: false,
      consumedPerPopulation: 0,
    },
    {
      id: "reputation",
      name: "口碑",
      icon: "🌟",
      initial: 55,
      max: 100,
      perTurn: 0,
      warningThreshold: 20,
      failIfZero: true,
      consumedPerPopulation: 0,
    },
  ],

  // ===== 建筑/升级定义 =====
  buildings: [
    {
      id: "morning_market",
      name: "晨采合作点",
      icon: "🧺",
      description: "与批发市场签约，稳定补充基础食材，但需要日常现金周转。",
      cost: { cash: 900 },
      produces: { ingredients: 38 },
      consumes: { cash: 120 },
    },
    {
      id: "broth_kitchen",
      name: "锅底研发灶",
      icon: "🔥",
      description: "标准化熬制红汤与清汤锅底，提升出餐稳定性与口碑。",
      cost: { cash: 1200, ingredients: 20 },
      produces: { broth: 18, reputation: 1 },
      consumes: { cash: 160, ingredients: 8 },
    },
    {
      id: "prep_station",
      name: "鲜切配菜台",
      icon: "🔪",
      description: "优化切配流程，减少浪费，让备菜效率更高。",
      cost: { cash: 800 },
      produces: { ingredients: 16, reputation: 1 },
      consumes: { cash: 90 },
    },
    {
      id: "drink_counter",
      name: "冰饮台",
      icon: "🥤",
      description: "提供高毛利饮品，提升客单价并补充饮品库存。",
      cost: { cash: 1000, ingredients: 6 },
      produces: { drinks: 20, cash: 120 },
      consumes: { cash: 70 },
    },
    {
      id: "service_team",
      name: "前厅服务组",
      icon: "🙋",
      description: "强化迎宾、点单与上菜衔接，带来稳定营业收入。",
      cost: { cash: 1500, broth: 12, ingredients: 18 },
      produces: { cash: 560, reputation: 3 },
      consumes: { ingredients: 20, broth: 8, drinks: 6 },
    },
    {
      id: "turnover_flow",
      name: "翻台管理器",
      icon: "⏱️",
      description: "优化排队与清台节奏，在高峰期显著提升翻台效率。",
      cost: { cash: 1800, reputation: 8 },
      produces: { cash: 420, reputation: 2 },
      consumes: { ingredients: 14, broth: 6, drinks: 4 },
    },
    {
      id: "member_club",
      name: "会员社群",
      icon: "📣",
      description: "建立社群与储值活动，增强复购并持续提升品牌口碑。",
      cost: { cash: 1300, reputation: 5 },
      produces: { cash: 260, reputation: 4 },
      consumes: { cash: 80, drinks: 3 },
    },
  ],

  // ===== 事件定义 =====
  events: [
    {
      id: "weekend_rush",
      title: "周末爆满",
      description: "商圈客流暴涨，门口排队拉满。你决定如何接待这波高峰？",
      icon: "📈",
      weight: 3,
      minTurn: 3,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "加开临时桌位，全力接客",
          effect: {
            resources: { cash: 900, ingredients: -25, broth: -10, drinks: -8, reputation: 2 },
            message: "冲量成功，营业额飙升，但库存压力明显。",
            messageType: "success",
          },
        },
        {
          text: "控制接待节奏，保证体验",
          effect: {
            resources: { cash: 450, ingredients: -12, broth: -5, drinks: -4, reputation: 4 },
            message: "收入稳健，服务评价更高。",
            messageType: "info",
          },
        },
        {
          text: "人手不足，提前限号",
          effect: {
            resources: { cash: -150, reputation: -3 },
            message: "错失部分营收，顾客口碑有所下滑。",
            messageType: "warning",
          },
        },
      ],
    },
    {
      id: "supplier_discount",
      title: "供应商让利档",
      description: "上游供货商给出限时折扣，今天下单越多越划算。",
      icon: "🧾",
      weight: 2,
      minTurn: 1,
      maxTurn: 25,
      once: false,
      choices: [
        {
          text: "大单囤货，锁定低价",
          effect: {
            resources: { cash: -1800, ingredients: 70, broth: 30 },
            message: "库存充足，短期现金流吃紧。",
            messageType: "info",
          },
        },
        {
          text: "适量补货，保持稳健",
          effect: {
            resources: { cash: -900, ingredients: 30, broth: 12 },
            message: "兼顾成本与现金流，风险可控。",
            messageType: "success",
          },
        },
        {
          text: "暂不采购，继续观望",
          effect: {
            resources: { reputation: -1 },
            message: "虽然省下现金，但备货保守影响了菜单丰富度。",
            messageType: "warning",
          },
        },
      ],
    },
    {
      id: "food_safety_check",
      title: "食安抽检",
      description: "监管部门临时抽检门店后厨，处理方式将直接影响品牌形象。",
      icon: "🧪",
      weight: 1,
      minTurn: 5,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "全面停档自检，严格整改",
          effect: {
            resources: { cash: -1200, reputation: 6, ingredients: -10, broth: -6, drinks: -4 },
            message: "短期损失不小，但口碑与信任度大幅提升。",
            messageType: "success",
          },
        },
        {
          text: "快速整改，边营业边优化",
          effect: {
            resources: { cash: -600, reputation: 2 },
            message: "成本可控，顺利通过检查。",
            messageType: "info",
          },
        },
        {
          text: "侥幸应付，尽量不影响营业",
          effect: {
            resources: { reputation: -10 },
            message: "被顾客拍到后厨问题，口碑遭受重创。",
            messageType: "danger",
          },
        },
      ],
    },
    {
      id: "influencer_visit",
      title: "探店博主到访",
      description: "本地美食博主突然到店拍摄，可能带来流量，也可能翻车。",
      icon: "📹",
      weight: 2,
      minTurn: 4,
      maxTurn: 25,
      once: true,
      choices: [
        {
          text: "赠送招牌套餐，重点展示",
          effect: {
            resources: { cash: -300, ingredients: -8, broth: -4, drinks: -3, reputation: 8 },
            message: "视频出圈，门店热度和好评显著上涨。",
            messageType: "success",
          },
        },
        {
          text: "正常接待，不做特殊安排",
          effect: {
            resources: { cash: 200, ingredients: -5, broth: -2, drinks: -2, reputation: 3 },
            message: "获得中规中矩的曝光，稳定加分。",
            messageType: "info",
          },
        },
        {
          text: "高峰太忙，婉拒拍摄",
          effect: {
            resources: { reputation: -5 },
            message: "错过流量机会，还引发部分网友吐槽。",
            messageType: "warning",
          },
        },
      ],
    },
    {
      id: "staff_fatigue",
      title: "员工疲劳",
      description: "连续高强度营业后，团队状态下降，服务波动开始出现。",
      icon: "😵",
      weight: 2,
      minTurn: 8,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "发放补贴并安排轮休",
          effect: {
            resources: { cash: -700, reputation: 4 },
            message: "团队士气回升，服务质量恢复。",
            messageType: "success",
          },
        },
        {
          text: "缩减接待，优先老客",
          effect: {
            resources: { cash: -250, ingredients: 6, broth: 3, drinks: 2, reputation: -2 },
            message: "库存压力减轻，但营收和评价小幅下降。",
            messageType: "warning",
          },
        },
        {
          text: "咬牙硬撑，继续满负荷",
          effect: {
            resources: { cash: 350, reputation: -6 },
            message: "短期多赚一些，但差评明显增多。",
            messageType: "danger",
          },
        },
      ],
    },
    {
      id: "cold_wave",
      title: "寒潮来袭",
      description: "气温骤降，火锅需求暴涨。是否趁机冲刺当日营业额？",
      icon: "❄️",
      weight: 2,
      minTurn: 10,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "全力冲量，延长营业",
          effect: {
            resources: { cash: 1200, ingredients: -35, broth: -16, drinks: -6, reputation: 2 },
            message: "单日流水大涨，但库存被快速消耗。",
            messageType: "success",
          },
        },
        {
          text: "平衡出餐，稳住节奏",
          effect: {
            resources: { cash: 700, ingredients: -18, broth: -8, drinks: -3, reputation: 3 },
            message: "收益与体验兼顾，整体运营更健康。",
            messageType: "info",
          },
        },
        {
          text: "担心断货，提前打烊",
          effect: {
            resources: { cash: -200, reputation: -4 },
            message: "错失旺季窗口，顾客评价受挫。",
            messageType: "warning",
          },
        },
      ],
    },
  ],

  // ===== 胜利条件 =====
  victoryCondition: (state) => {
    const turn = state?.turn ?? state?.currentTurn ?? state?.day ?? 0;
    const cash = state?.resources?.cash ?? 0;
    const reputation = state?.resources?.reputation ?? 0;
    return turn >= 30 && cash >= 38000 && reputation >= 75;
  },
};