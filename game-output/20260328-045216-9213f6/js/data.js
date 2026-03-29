const GameData = {
  // 游戏基础信息
  name: "中转之家：放心去爱",
  description:
    "你将经营一家流浪动物中转之家：观察行为、安抚陪伴、修复创伤、发布领养故事，并在建立深厚感情后学会温柔放手。每一次送养，都是一次双向治愈。",
  maxTurns: 30,
  initialPopulation: 4,

  // 资源定义
  resources: [
    {
      id: "cash",
      name: "运营资金",
      icon: "💴",
      initial: 9000,
      max: 999999,
      perTurn: 0,
      warningThreshold: 1200,
      failIfZero: true,
      consumedPerPopulation: 0
    },
    {
      id: "food",
      name: "口粮储备",
      icon: "🍲",
      initial: 120,
      max: 999,
      perTurn: 0,
      warningThreshold: 20,
      failIfZero: false,
      consumedPerPopulation: 1
    },
    {
      id: "medicine",
      name: "医护包",
      icon: "🩹",
      initial: 35,
      max: 300,
      perTurn: 0,
      warningThreshold: 6,
      failIfZero: false,
      consumedPerPopulation: 0
    },
    {
      id: "trust",
      name: "信任度",
      icon: "🤝",
      initial: 20,
      max: 999,
      perTurn: 0,
      warningThreshold: 15,
      failIfZero: false,
      consumedPerPopulation: 0
    },
    {
      id: "calm",
      name: "安定度",
      icon: "🫧",
      initial: 25,
      max: 999,
      perTurn: 0,
      warningThreshold: 10,
      failIfZero: true,
      consumedPerPopulation: 0
    },
    {
      id: "reputation",
      name: "公益声望",
      icon: "🌟",
      initial: 15,
      max: 999,
      perTurn: 0,
      warningThreshold: 8,
      failIfZero: false,
      consumedPerPopulation: 0
    }
  ],

  // 建筑/功能区定义
  buildings: [
    {
      id: "reception_observe",
      name: "接待观察区",
      icon: "🪟",
      description: "新入所动物先在这里熟悉气味与环境，降低初始戒备。",
      cost: { cash: 1000, food: 20 },
      produces: { trust: 3, calm: 2 },
      consumes: { cash: 20 }
    },
    {
      id: "comfort_room",
      name: "安抚陪伴室",
      icon: "🧸",
      description: "志愿者一对一陪伴，帮助动物建立稳定依恋与安全感。",
      cost: { cash: 1800, food: 30, medicine: 8 },
      produces: { trust: 6, calm: 5 },
      consumes: { food: 3, cash: 30 }
    },
    {
      id: "rehab_clinic",
      name: "行为修复诊疗间",
      icon: "🩺",
      description: "针对应激、攻击、防御等行为进行分级修复训练。",
      cost: { cash: 2600, medicine: 20 },
      produces: { calm: 9, trust: 4, reputation: 1 },
      consumes: { medicine: 2, cash: 60 }
    },
    {
      id: "volunteer_kitchen",
      name: "志愿者后勤厨房",
      icon: "🍳",
      description: "组织后勤与募捐物资，保障日常喂养和基础医护。",
      cost: { cash: 1500, reputation: 8 },
      produces: { food: 14, medicine: 2 },
      consumes: { cash: 40 }
    },
    {
      id: "story_studio",
      name: "影像故事工坊",
      icon: "🎬",
      description: "制作领养短片与照片卡，放大每只动物的独特魅力。",
      cost: { cash: 2400, trust: 20 },
      produces: { reputation: 6, cash: 160 },
      consumes: { cash: 50, calm: 1 }
    },
    {
      id: "match_consult",
      name: "匹配咨询室",
      icon: "📋",
      description: "进行家访筛选与领养沟通，提高送养成功率与稳定性。",
      cost: { cash: 3000, reputation: 20, trust: 30 },
      produces: { cash: 220, reputation: 5, calm: 2 },
      consumes: { cash: 70, trust: 1 }
    },
    {
      id: "revisit_center",
      name: "回访联络中心",
      icon: "📮",
      description: "持续回访已领养家庭，沉淀真实案例并反哺救助工作。",
      cost: { cash: 2800, reputation: 28 },
      produces: { trust: 5, reputation: 4, cash: 120 },
      consumes: { cash: 45 }
    }
  ],

  // 事件定义
  events: [
    {
      id: "rainy_rescue",
      title: "暴雨夜紧急求助",
      description: "大雨中发现两只蜷缩在纸箱里的幼崽，体温偏低且高度紧张。",
      icon: "🌧️",
      weight: 3,
      minTurn: 1,
      maxTurn: 12,
      once: false,
      choices: [
        {
          text: "全部接收并立刻急救",
          effect: {
            resources: { cash: -800, food: -20, medicine: -6, trust: 8, reputation: 4, calm: -3 },
            population: 2,
            message: "你们通宵守护，两只幼崽都挺了过来，社会评价上升。",
            messageType: "success"
          }
        },
        {
          text: "仅接收一只，另一只联系合作机构",
          effect: {
            resources: { cash: -350, food: -8, medicine: -2, trust: 3, reputation: 1 },
            population: 1,
            message: "在能力范围内做出选择，压力可控但仍有遗憾。",
            messageType: "info"
          }
        },
        {
          text: "转交合作机构统一安置",
          effect: {
            resources: { cash: -100, reputation: -1, calm: 2 },
            population: 0,
            message: "你保存了运转空间，但错失了当晚建立信任的机会。",
            messageType: "warning"
          }
        }
      ]
    },
    {
      id: "touch_setback",
      title: "首次触碰失败",
      description: "一只已逐渐放松的犬在洗护时突然应激，出现防御性低吼。",
      icon: "🐾",
      weight: 3,
      minTurn: 3,
      maxTurn: 20,
      once: false,
      choices: [
        {
          text: "请行为师进行一对一脱敏训练",
          effect: {
            resources: { cash: -600, medicine: -3, calm: 7, trust: 5 },
            message: "循序渐进的训练重新建立了边界感与安全感。",
            messageType: "success"
          }
        },
        {
          text: "暂停肢体接触，仅做远距陪伴",
          effect: {
            resources: { calm: 3, trust: -2 },
            message: "关系没有恶化，但修复进度明显放缓。",
            messageType: "info"
          }
        },
        {
          text: "强行推进洗护流程",
          effect: {
            resources: { cash: -200, trust: -6, calm: -5, reputation: -2 },
            message: "短期省事却造成二次创伤，团队士气也受到打击。",
            messageType: "danger"
          }
        }
      ]
    },
    {
      id: "viral_clip",
      title: "短视频意外爆火",
      description: "一段“从躲角落到主动贴贴”的对比视频登上热门推荐。",
      icon: "📱",
      weight: 2,
      minTurn: 5,
      maxTurn: 22,
      once: true,
      choices: [
        {
          text: "开启直播科普，稳定输出内容",
          effect: {
            resources: { cash: 1200, reputation: 10, trust: 4, calm: -2 },
            message: "流量转化为支持，更多人理解了创伤修复的长期性。",
            messageType: "success"
          }
        },
        {
          text: "接受品牌合作，优先补充资金",
          effect: {
            resources: { cash: 2200, reputation: 4, trust: -3 },
            message: "资金压力缓解明显，但部分观众质疑商业化倾向。",
            messageType: "warning"
          }
        },
        {
          text: "不追热点，保持照护节奏",
          effect: {
            resources: { reputation: 2, calm: 4, trust: 2 },
            message: "你选择把精力留给动物，进度慢却更稳。",
            messageType: "info"
          }
        }
      ]
    },
    {
      id: "perfect_application",
      title: "看似完美的领养申请",
      description: "一位条件优越的申请人希望尽快带走最受欢迎的猫咪。",
      icon: "🏠",
      weight: 3,
      minTurn: 8,
      maxTurn: 26,
      once: false,
      choices: [
        {
          text: "坚持完整家访后再决定",
          effect: {
            resources: { cash: -300, reputation: 5, trust: 6, calm: 2 },
            message: "流程虽慢，但你守住了“匹配优先于速度”的原则。",
            messageType: "success"
          }
        },
        {
          text: "立即同意送养，抢占时机",
          effect: {
            resources: { cash: 600, reputation: -4, trust: -5, calm: -3 },
            population: -1,
            message: "短期看似高效，后续风险与争议同步上升。",
            messageType: "danger"
          }
        },
        {
          text: "婉拒并推荐其先参加试养课程",
          effect: {
            resources: { cash: -100, reputation: 2, trust: 1 },
            message: "你留下了转圜空间，也筛掉了冲动型申请。",
            messageType: "info"
          }
        }
      ]
    },
    {
      id: "farewell_day",
      title: "告别日",
      description: "陪伴最久的那只终于被匹配到温柔家庭，你站在门口迟迟不舍。",
      icon: "🧳",
      weight: 2,
      minTurn: 12,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "拍完整告别纪录并认真交接",
          effect: {
            resources: { cash: -500, trust: 10, reputation: 6, calm: -2 },
            population: -1,
            message: "这次告别很难，但它成为了更多人愿意领养的理由。",
            messageType: "success"
          }
        },
        {
          text: "简化流程，快速完成送养",
          effect: {
            resources: { cash: 200, trust: -3, calm: 1 },
            population: -1,
            message: "效率更高，却在团队心里留下了空落落的后劲。",
            messageType: "warning"
          }
        },
        {
          text: "临时反悔，继续留养观察",
          effect: {
            resources: { trust: 4, calm: -4, reputation: -3 },
            message: "你暂时留住了它，但也打乱了既定匹配节奏。",
            messageType: "danger"
          }
        }
      ]
    },
    {
      id: "revisit_album",
      title: "回访相册寄到门口",
      description: "已送养家庭寄来照片：曾经怕人的它，正趴在窗边安心晒太阳。",
      icon: "📸",
      weight: 2,
      minTurn: 15,
      maxTurn: 30,
      once: false,
      choices: [
        {
          text: "举办分享会，鼓励志愿者坚持下去",
          effect: {
            resources: { cash: -300, reputation: 7, trust: 6, calm: 5 },
            message: "大家被真实变化打动，团队凝聚力显著提升。",
            messageType: "success"
          }
        },
        {
          text: "只做内部存档，低调记录",
          effect: {
            resources: { trust: 3, calm: 2 },
            message: "你把感动留在内部，节奏平稳推进。",
            messageType: "info"
          }
        },
        {
          text: "公开回访故事并发起募捐",
          effect: {
            resources: { cash: 900, reputation: 3 },
            message: "故事带来了新的支持，也让更多人看见送养后的幸福。",
            messageType: "success"
          }
        }
      ]
    }
  ],

  // 胜利条件：在后期建立稳定运营，并完成“疗愈+放手”的正循环
  victoryCondition: (state) => {
    const turn = state && (state.turn ?? state.currentTurn ?? 0);
    const r = (state && state.resources) || {};
    const cash = r.cash ?? 0;
    const trust = r.trust ?? 0;
    const calm = r.calm ?? 0;
    const reputation = r.reputation ?? 0;
    return turn >= 20 && cash >= 5000 && trust >= 180 && calm >= 140 && reputation >= 130;
  }
};