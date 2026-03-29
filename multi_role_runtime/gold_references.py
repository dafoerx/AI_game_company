"""
Gold Standard Reference Implementations

Provides high-quality, hand-crafted reference code for each scaffolding type.
These references serve as few-shot examples for the LLM code generator,
dramatically improving output quality by giving the model a concrete target
to adapt rather than generating from scratch.

Usage:
    from .gold_references import get_gold_reference
    ref = get_gold_reference("entity_lifecycle", "data.js")
"""

# ═══════════════════════════════════════════════════
# Entity Lifecycle Gold References
# (e.g., animal rescue, character nurturing, plant growing)
# ═══════════════════════════════════════════════════

ENTITY_LIFECYCLE_DATA_JS = r'''
/**
 * Gold Reference: Entity Lifecycle - data.js
 * Theme: Animal Rescue Shelter
 */
const GameData = {
  name: "温暖之家",
  description: "经营一家流浪动物救助站，治愈每一只受伤的心灵",
  maxTurns: 30,
  initialPopulation: 0,

  // ===== Global Resources =====
  resources: [
    {
      id: "funds",
      name: "救助基金",
      icon: "💰",
      initial: 5000,
      max: 99999,
      perTurn: 200,
      warningThreshold: 500,
      failIfZero: true,
    },
    {
      id: "reputation",
      name: "口碑",
      icon: "⭐",
      initial: 10,
      max: 100,
      perTurn: 0,
      warningThreshold: 5,
    },
    {
      id: "supplies",
      name: "物资",
      icon: "📦",
      initial: 30,
      max: 100,
      perTurn: 3,
      warningThreshold: 5,
    },
    {
      id: "energy",
      name: "精力",
      icon: "💪",
      initial: 10,
      max: 10,
      perTurn: 10,
      warningThreshold: 2,
      description: "Each turn resets to max. Interactions consume energy.",
    },
  ],

  // ===== Entity Definitions (Individual Animals) =====
  entities: [
    {
      id: "mimi",
      name: "咪咪",
      species: "cat",
      breed: "橘猫",
      portrait_emoji: "🐱",
      backstory: "曾经的家猫，主人搬家后被遗弃在小区。独自流浪三个月，对人类既渴望又害怕。",
      trauma_tags: ["abandonment", "trust_issues"],
      personality: "cautious_hopeful",
      initial_state: {
        trust: 25,
        stress: 60,
        attachment: 10,
        health: 70,
        adoptability: 0,
      },
      unlock_turn: 1,
      special_trait: "会在信任度达到50时主动蹭人",
    },
    {
      id: "dahuang",
      name: "大黄",
      species: "dog",
      breed: "中华田园犬",
      portrait_emoji: "🐕",
      backstory: "工地看门犬，工地完工后被抛弃。性格忠厚但因长期被锁链拴住，对束缚极度敏感。",
      trauma_tags: ["confinement", "abandonment"],
      personality: "loyal_anxious",
      initial_state: {
        trust: 35,
        stress: 50,
        attachment: 20,
        health: 60,
        adoptability: 0,
      },
      unlock_turn: 1,
      special_trait: "不能使用牵绳类互动，否则应激值暴增",
    },
    {
      id: "snowball",
      name: "雪球",
      species: "rabbit",
      breed: "垂耳兔",
      portrait_emoji: "🐰",
      backstory: "宠物店滞销后被丢弃在公园。曾被小孩粗暴对待，极度怕生，蜷缩在角落不敢动。",
      trauma_tags: ["abuse", "fear_of_touch"],
      personality: "timid_gentle",
      initial_state: {
        trust: 10,
        stress: 85,
        attachment: 5,
        health: 50,
        adoptability: 0,
      },
      unlock_turn: 2,
      special_trait: "触摸互动成功率极低，但喂食互动效果翻倍",
    },
    {
      id: "captain",
      name: "船长",
      species: "cat",
      breed: "黑白猫",
      portrait_emoji: "🐈‍⬛",
      backstory: "码头流浪猫群的首领，带着三只幼崽来到救助站。极度护崽，对陌生人充满敌意。",
      trauma_tags: ["protective_parent", "territorial"],
      personality: "fierce_protective",
      initial_state: {
        trust: 15,
        stress: 70,
        attachment: 5,
        health: 65,
        adoptability: 0,
      },
      unlock_turn: 3,
      special_trait: "必须先安顿好幼崽（建造育婴室）才能开始互动",
    },
    {
      id: "lucky",
      name: "来福",
      species: "dog",
      breed: "拉布拉多",
      portrait_emoji: "🦮",
      backstory: "导盲犬退役后被送到救助站。训练有素但年事已高，需要一个安静温暖的家。",
      trauma_tags: ["aging", "separation"],
      personality: "gentle_wise",
      initial_state: {
        trust: 60,
        stress: 30,
        attachment: 40,
        health: 45,
        adoptability: 30,
      },
      unlock_turn: 1,
      special_trait: "初始信任度高，但健康值低，需要特别的医疗关注",
    },
    {
      id: "pepper",
      name: "花椒",
      species: "cat",
      breed: "三花猫",
      portrait_emoji: "🐱",
      backstory: "从繁殖场救出的母猫，经历过多次怀孕。身体虚弱但眼神温柔，渴望被爱。",
      trauma_tags: ["exploitation", "health_issues"],
      personality: "resilient_loving",
      initial_state: {
        trust: 40,
        stress: 45,
        attachment: 30,
        health: 35,
        adoptability: 0,
      },
      unlock_turn: 4,
      special_trait: "医疗互动效果翻倍，恢复速度快",
    },
  ],

  // ===== Interaction Definitions =====
  interactions: [
    {
      id: "feed",
      name: "喂食",
      icon: "🍖",
      description: "提供食物，满足基本需求，建立初步信任",
      cost: { supplies: 2, energy: 1 },
      effects_on_entity: {
        trust: 5,
        stress: -3,
        health: 3,
        attachment: 2,
      },
      success_rate_base: 0.85,
      success_message: "{name}小心翼翼地吃完了食物，偷偷看了你一眼",
      failure_message: "{name}警惕地后退，不敢靠近食物",
      cooldown_turns: 0,
      available_for: ["all"],
    },
    {
      id: "observe",
      name: "静静观察",
      icon: "👀",
      description: "保持距离，安静地观察动物的行为和状态",
      cost: { energy: 1 },
      effects_on_entity: {
        trust: 3,
        stress: -5,
        attachment: 1,
      },
      success_rate_base: 0.95,
      success_message: "你安静地坐在远处，{name}渐渐放松了警惕",
      failure_message: "{name}注意到你的目光，紧张地躲到了角落",
      cooldown_turns: 0,
      available_for: ["all"],
    },
    {
      id: "gentle_touch",
      name: "轻柔触摸",
      icon: "🤝",
      description: "尝试轻轻触摸动物，需要一定信任基础",
      cost: { energy: 2 },
      effects_on_entity: {
        trust: 8,
        stress: -2,
        attachment: 5,
      },
      success_rate_formula: "base + trust * 0.006 - stress * 0.004",
      success_rate_base: 0.3,
      success_message: "{name}犹豫了一下，最终靠了过来，让你摸了摸头",
      failure_message: "{name}受惊后退，发出低沉的警告声",
      failure_effects: { stress: 8, trust: -3 },
      cooldown_turns: 0,
      min_trust: 20,
      available_for: ["all"],
    },
    {
      id: "play",
      name: "陪伴玩耍",
      icon: "🎾",
      description: "用玩具和动物互动，增进感情",
      cost: { supplies: 1, energy: 2 },
      effects_on_entity: {
        trust: 6,
        stress: -8,
        attachment: 8,
        health: 2,
      },
      success_rate_formula: "base + trust * 0.005 - stress * 0.003",
      success_rate_base: 0.5,
      success_message: "{name}开心地追着玩具跑，第一次露出了快乐的表情！",
      failure_message: "{name}对玩具没有兴趣，蜷缩在角落",
      cooldown_turns: 1,
      min_trust: 30,
      available_for: ["cat", "dog"],
    },
    {
      id: "medical",
      name: "医疗检查",
      icon: "💊",
      description: "进行健康检查和治疗，改善身体状况",
      cost: { funds: 200, supplies: 3, energy: 2 },
      effects_on_entity: {
        health: 15,
        stress: 5,
        trust: -2,
      },
      success_rate_base: 0.9,
      success_message: "{name}虽然不太情愿，但配合完成了检查。健康状况有所改善",
      failure_message: "检查过程中{name}过于紧张，只完成了部分项目",
      cooldown_turns: 2,
      available_for: ["all"],
    },
    {
      id: "photo_shoot",
      name: "拍摄征婚照",
      icon: "📸",
      description: "为动物拍摄可爱的照片，制作领养卡片",
      cost: { energy: 3 },
      effects_on_entity: {
        stress: 3,
        adoptability: 10,
      },
      success_rate_formula: "base + trust * 0.008",
      success_rate_base: 0.4,
      success_message: "拍到了{name}超可爱的照片！领养卡片已更新",
      failure_message: "{name}不太配合拍摄，照片效果一般",
      cooldown_turns: 3,
      min_trust: 40,
      available_for: ["all"],
    },
  ],

  // ===== Adopter Family Definitions =====
  adopter_families: [
    {
      id: "young_couple",
      name: "年轻情侣",
      description: "住在公寓，工作繁忙但充满爱心，适合独立性强的猫咪",
      portrait_emoji: "👫",
      preferences: { cat: 3, independent: 2, low_maintenance: 2 },
      environment: "apartment",
      experience_level: "beginner",
      patience: 60,
      match_bonus: { trust: 50, stress_max: 40 },
    },
    {
      id: "retired_grandpa",
      name: "退休老爷爷",
      description: "独居老人，有院子，时间充裕，渴望陪伴",
      portrait_emoji: "👴",
      preferences: { dog: 3, gentle: 3, companion: 2 },
      environment: "house_with_yard",
      experience_level: "experienced",
      patience: 90,
      match_bonus: { trust: 40, health: 40 },
    },
    {
      id: "family_with_kids",
      name: "有孩子的家庭",
      description: "郊区别墅，两个孩子，需要性格温顺、不怕吵闹的动物",
      portrait_emoji: "👨‍👩‍👧‍👦",
      preferences: { dog: 2, friendly: 3, patient: 2, robust: 2 },
      environment: "suburban_house",
      experience_level: "intermediate",
      patience: 70,
      match_bonus: { trust: 60, stress_max: 30, health: 50 },
    },
    {
      id: "cat_lady",
      name: "资深猫奴",
      description: "已有两只猫，经验丰富，专门收养有特殊需求的猫咪",
      portrait_emoji: "👩",
      preferences: { cat: 5, special_needs: 3 },
      environment: "large_apartment",
      experience_level: "expert",
      patience: 95,
      match_bonus: { trust: 30, health: 30 },
    },
    {
      id: "rural_farmer",
      name: "乡村农户",
      description: "有大片农田和谷仓，适合需要大空间活动的动物",
      portrait_emoji: "🧑‍🌾",
      preferences: { dog: 3, active: 3, outdoor: 2 },
      environment: "farm",
      experience_level: "experienced",
      patience: 80,
      match_bonus: { trust: 45, health: 50 },
    },
  ],

  // ===== Farewell Templates =====
  farewell_templates: [
    {
      condition: "trust >= 80",
      narrative: "{name}在离开的那一刻回头看了你一眼，眼里满是不舍。但你知道，{family}会给{pronoun}一个温暖的家。",
      photo_description: "{name}坐在新家的窗台上，阳光洒在{pronoun}身上",
      emotion_type: "bittersweet",
    },
    {
      condition: "attachment >= 70",
      narrative: "你蹲下来最后摸了摸{name}的头，{pronoun}蹭了蹭你的手心。'去吧，去享受新生活。'",
      photo_description: "{name}在新家的院子里奔跑",
      emotion_type: "hopeful",
    },
    {
      condition: "default",
      narrative: "{name}被{family}小心翼翼地抱上了车。你挥了挥手，心里既开心又有些空落落的。",
      photo_description: "{name}在车后座安静地看着窗外",
      emotion_type: "gentle",
    },
  ],

  // ===== Revisit Templates =====
  revisit_templates: [
    {
      delay_turns: 3,
      narrative: "收到{family}发来的照片！{name}已经完全适应了新家，{detail}",
      photo_description: "{name}在新家{scene}",
      mood: "joyful",
      details: [
        "正趴在沙发上晒太阳，肚皮朝天",
        "和家里的小朋友玩得不亦乐乎",
        "已经胖了一圈，看起来幸福极了",
        "学会了新技能，会自己开门了",
      ],
    },
    {
      delay_turns: 7,
      narrative: "{family}发来了{name}的近况视频。曾经那个{old_trait}的小家伙，现在已经是家里的'小霸王'了！",
      photo_description: "{name}霸占了全家最舒服的位置",
      mood: "heartwarming",
    },
  ],

  // ===== Facility Definitions (Buildings) =====
  facilities: [
    {
      id: "basic_shelter",
      name: "基础收容间",
      icon: "🏠",
      description: "提供基本的遮风挡雨空间",
      cost: { funds: 500 },
      produces: { supplies: 2 },
      capacity: 3,
      unlocks_interactions: [],
    },
    {
      id: "medical_room",
      name: "医疗室",
      icon: "🏥",
      description: "配备基础医疗设备，可以进行健康检查",
      cost: { funds: 1500, supplies: 10 },
      produces: {},
      capacity: 0,
      unlocks_interactions: ["medical"],
    },
    {
      id: "play_area",
      name: "活动区",
      icon: "🎪",
      description: "宽敞的活动空间，让动物们可以自由玩耍",
      cost: { funds: 1000, supplies: 8 },
      produces: {},
      capacity: 0,
      unlocks_interactions: ["play"],
      global_effect: { stress_reduction_per_turn: 2 },
    },
    {
      id: "nursery",
      name: "育婴室",
      icon: "🍼",
      description: "专门照顾幼崽的温暖空间",
      cost: { funds: 2000, supplies: 15 },
      produces: {},
      capacity: 0,
      unlocks_interactions: [],
      special: "unlock_captain_interactions",
    },
    {
      id: "photo_studio",
      name: "摄影角",
      icon: "📷",
      description: "布置精美的拍摄区域，为动物拍摄领养照片",
      cost: { funds: 800, supplies: 5 },
      produces: { reputation: 1 },
      capacity: 0,
      unlocks_interactions: ["photo_shoot"],
    },
    {
      id: "social_media_office",
      name: "新媒体工作室",
      icon: "📱",
      description: "运营社交账号，扩大影响力",
      cost: { funds: 1200, supplies: 5 },
      produces: { reputation: 2, funds: 100 },
      capacity: 0,
      unlocks_interactions: [],
    },
  ],

  // ===== Event Definitions =====
  events: [
    {
      id: "rainy_night_rescue",
      title: "暴雨夜救助",
      description: "深夜暴雨，有人在门口发现了一只浑身湿透的小猫。要收留它吗？",
      icon: "🌧️",
      weight: 2,
      minTurn: 2,
      choices: [
        {
          text: "立刻收留，紧急处理",
          effect: {
            resources: { funds: -300, supplies: -5 },
            new_entity: true,
            message: "你救下了一个小生命！虽然花了些资源，但这就是我们存在的意义。",
            messageType: "success",
          },
        },
        {
          text: "联系其他救助站帮忙",
          effect: {
            resources: { reputation: -2 },
            message: "其他救助站表示也已满员...希望小猫能撑到明天。",
            messageType: "warning",
          },
        },
      ],
    },
    {
      id: "first_touch_fail",
      title: "信任的试探",
      description: "你伸出手想摸摸{entity}，但{pronoun}突然缩成一团，浑身发抖。你的心揪了一下。",
      icon: "💔",
      weight: 1,
      entity_bound: true,
      trigger_condition: "entity.trust < 30 && entity.stress > 50",
      choices: [
        {
          text: "慢慢收回手，轻声安慰",
          effect: {
            entity_effects: { stress: -5, trust: 3 },
            message: "你没有强迫{name}，而是安静地陪在旁边。{pronoun}的呼吸渐渐平稳了。",
            messageType: "info",
          },
        },
        {
          text: "放下一块零食，默默离开",
          effect: {
            resources: { supplies: -1 },
            entity_effects: { stress: -8, trust: 5 },
            message: "你离开后，{name}小心翼翼地吃掉了零食。这是信任的开始。",
            messageType: "success",
          },
        },
      ],
    },
    {
      id: "viral_video",
      title: "短视频爆火",
      description: "你发布的一条救助日常视频突然火了！评论区满是暖心留言和领养咨询。",
      icon: "📱",
      weight: 1,
      minTurn: 5,
      once: true,
      choices: [
        {
          text: "趁热打铁，发起线上募捐",
          effect: {
            resources: { funds: 2000, reputation: 10 },
            message: "募捐非常成功！收到了大量爱心捐款和物资。",
            messageType: "success",
          },
        },
        {
          text: "借机推广领养信息",
          effect: {
            resources: { reputation: 15 },
            all_entity_effects: { adoptability: 5 },
            message: "领养咨询量暴增！好几只动物收到了领养申请。",
            messageType: "success",
          },
        },
      ],
    },
    {
      id: "perfect_match",
      title: "完美领养申请",
      description: "收到了一份非常合适的领养申请！{family}对{entity}很感兴趣。",
      icon: "💌",
      weight: 2,
      entity_bound: true,
      trigger_condition: "entity.adoptability >= 60",
      choices: [
        {
          text: "安排见面，开始匹配流程",
          effect: {
            message: "见面非常顺利！{name}似乎也很喜欢{family}。",
            messageType: "success",
            start_matching: true,
          },
        },
        {
          text: "再等等，{name}还没完全准备好",
          effect: {
            entity_effects: { attachment: 3 },
            message: "你决定再多陪{name}一段时间。{pronoun}蹭了蹭你的手。",
            messageType: "info",
          },
        },
      ],
    },
    {
      id: "farewell_day",
      title: "告别的日子",
      description: "今天是{entity}去新家的日子。你站在门口，看着{pronoun}被{family}温柔地抱起。",
      icon: "🌅",
      weight: 0,
      entity_bound: true,
      trigger_condition: "entity.matched && entity.match_confirmed",
      choices: [
        {
          text: "微笑着说再见",
          effect: {
            resources: { reputation: 5, funds: 500 },
            complete_adoption: true,
            message: "再见了，{name}。去享受你的新生活吧。",
            messageType: "success",
          },
        },
      ],
    },
    {
      id: "revisit_album",
      title: "回访相册",
      description: "收到了{family}发来的{entity}近况照片！",
      icon: "📸",
      weight: 0,
      entity_bound: true,
      trigger_condition: "entity.adopted && turns_since_adoption >= 3",
      choices: [
        {
          text: "打开相册查看",
          effect: {
            resources: { reputation: 3 },
            message: "{name}在新家过得很好！看到{pronoun}幸福的样子，一切都值得了。",
            messageType: "success",
            show_revisit: true,
          },
        },
      ],
    },
    {
      id: "volunteer_visit",
      title: "志愿者来访",
      description: "一群大学生志愿者想来帮忙！他们热情满满但缺乏经验。",
      icon: "🙋",
      weight: 2,
      minTurn: 3,
      choices: [
        {
          text: "欢迎！安排简单的清洁和喂食工作",
          effect: {
            resources: { supplies: 5, energy: 3 },
            all_entity_effects: { stress: -2 },
            message: "志愿者们干劲十足！救助站焕然一新。",
            messageType: "success",
          },
        },
        {
          text: "先培训再上岗",
          effect: {
            resources: { energy: -2 },
            message: "花了些精力培训，但志愿者们学到了正确的动物护理知识。下次会更有帮助。",
            messageType: "info",
          },
        },
      ],
    },
    {
      id: "donation_drive",
      title: "爱心捐赠",
      description: "一位匿名好心人送来了一大批物资和捐款！",
      icon: "🎁",
      weight: 1,
      minTurn: 5,
      choices: [
        {
          text: "感恩接受，发布感谢信",
          effect: {
            resources: { funds: 1500, supplies: 20, reputation: 3 },
            message: "收到了满满的爱心！救助站的运营压力大大减轻。",
            messageType: "success",
          },
        },
      ],
    },
  ],

  // ===== Victory Conditions =====
  victoryCondition: (state) => {
    // Win: successfully adopt out at least 3 animals with good outcomes
    const successfulAdoptions = state.adoptionHistory
      ? state.adoptionHistory.filter(a => a.matchScore >= 70).length
      : 0;
    return successfulAdoptions >= 3 && state.reputation >= 50;
  },

  // ===== Defeat Conditions =====
  defeatConditions: [
    {
      check: (state) => state.resources.funds.current <= 0,
      message: "救助基金耗尽，救助站被迫关闭...",
    },
    {
      check: (state) => {
        const unhappy = state.entityStates
          ? Object.values(state.entityStates).filter(e => e.health <= 0).length
          : 0;
        return unhappy >= 2;
      },
      message: "有动物因为健康问题离开了...我们需要做得更好。",
    },
  ],
};
'''

ENTITY_LIFECYCLE_GAME_STATE_JS = r'''
/**
 * Gold Reference: Entity Lifecycle - game-state.js
 * Core: Per-entity state tracking, interaction processing, matching algorithm
 */
class GameState {
  constructor() {
    this.reset();
  }

  reset() {
    this.turn = 1;

    // Global resources
    this.resources = {};
    for (const res of GameData.resources) {
      this.resources[res.id] = {
        current: res.initial,
        max: res.max || Infinity,
        perTurn: res.perTurn || 0,
      };
    }

    // Per-entity state tracking (the CORE of entity lifecycle games)
    this.entityStates = {};
    for (const entity of GameData.entities) {
      if (!entity.unlock_turn || entity.unlock_turn <= 1) {
        this._initEntity(entity);
      }
    }

    // Unlocked entities list
    this.unlockedEntities = Object.keys(this.entityStates);

    // Built facilities
    this.facilities = [];

    // Interaction cooldowns: { entityId_interactionId: turnsRemaining }
    this.cooldowns = {};

    // Adoption tracking
    this.adoptionHistory = [];
    this.pendingMatches = []; // { entityId, familyId, matchScore, turnsToConfirm }
    this.pendingRevisits = []; // { entityId, familyId, revisitTurn, template }

    // Triggered events
    this.triggeredEvents = [];

    // Stats
    this.stats = {
      totalTurns: 0,
      interactionsPerformed: 0,
      successfulInteractions: 0,
      adoptionsCompleted: 0,
      totalMatchScore: 0,
    };

    // Reputation (also tracked in resources, but used for victory)
    this.reputation = GameData.resources.find(r => r.id === "reputation")?.initial || 0;
  }

  _initEntity(entityDef) {
    this.entityStates[entityDef.id] = {
      ...JSON.parse(JSON.stringify(entityDef.initial_state)),
      id: entityDef.id,
      status: "in_shelter", // in_shelter | matched | adopted
      matched_family: null,
      adopted_turn: null,
      interaction_history: [],
      turns_in_shelter: 0,
    };
  }

  // ── Turn Processing ──

  processTurn() {
    const results = {
      resourceChanges: {},
      entityUpdates: {},
      messages: [],
      newEntities: [],
      revisits: [],
    };

    // 1. Reset energy to max each turn
    const energyRes = GameData.resources.find(r => r.id === "energy");
    if (energyRes && this.resources.energy) {
      this.resources.energy.current = energyRes.max || energyRes.initial;
    }

    // 2. Process global resource changes
    for (const [resId, res] of Object.entries(this.resources)) {
      if (resId === "energy") continue; // Energy resets, not accumulates
      let change = res.perTurn || 0;

      // Facility production
      for (const facility of this.facilities) {
        const fDef = GameData.facilities.find(f => f.id === facility.type);
        if (fDef && fDef.produces && fDef.produces[resId]) {
          change += fDef.produces[resId];
        }
      }

      results.resourceChanges[resId] = change;
      res.current = Math.max(0, Math.min(res.max, res.current + change));
    }

    // 3. Per-entity state decay/recovery
    for (const [entityId, state] of Object.entries(this.entityStates)) {
      if (state.status !== "in_shelter") continue;

      state.turns_in_shelter++;

      // Natural trust decay if no interaction this turn
      const hadInteraction = state.interaction_history.some(
        h => h.turn === this.turn - 1
      );
      if (!hadInteraction && state.trust > 10) {
        state.trust = Math.max(0, state.trust - 1);
      }

      // Stress natural recovery (slow)
      if (state.stress > 20) {
        state.stress = Math.max(0, state.stress - 1);
      }

      // Facility global effects
      for (const facility of this.facilities) {
        const fDef = GameData.facilities.find(f => f.id === facility.type);
        if (fDef && fDef.global_effect) {
          if (fDef.global_effect.stress_reduction_per_turn) {
            state.stress = Math.max(0, state.stress - fDef.global_effect.stress_reduction_per_turn);
          }
        }
      }

      // Recalculate adoptability
      state.adoptability = this._calculateAdoptability(state);

      results.entityUpdates[entityId] = { ...state };
    }

    // 4. Unlock new entities based on turn
    for (const entityDef of GameData.entities) {
      if (entityDef.unlock_turn === this.turn && !this.entityStates[entityDef.id]) {
        this._initEntity(entityDef);
        this.unlockedEntities.push(entityDef.id);
        results.newEntities.push(entityDef);
        results.messages.push({
          text: `新动物到来：${entityDef.name}（${entityDef.breed}）- ${entityDef.backstory.substring(0, 30)}...`,
          type: "info",
        });
      }
    }

    // 5. Process cooldowns
    for (const key of Object.keys(this.cooldowns)) {
      this.cooldowns[key]--;
      if (this.cooldowns[key] <= 0) {
        delete this.cooldowns[key];
      }
    }

    // 6. Process pending matches
    for (const match of this.pendingMatches) {
      match.turnsToConfirm--;
    }

    // 7. Check for revisits
    const dueRevisits = this.pendingRevisits.filter(r => r.revisitTurn === this.turn);
    for (const revisit of dueRevisits) {
      results.revisits.push(revisit);
    }
    this.pendingRevisits = this.pendingRevisits.filter(r => r.revisitTurn !== this.turn);

    // 8. Advance turn
    this.turn++;
    this.stats.totalTurns++;

    return results;
  }

  // ── Interaction Processing ──

  interact(entityId, interactionId) {
    const entityState = this.entityStates[entityId];
    if (!entityState || entityState.status !== "in_shelter") {
      return { success: false, message: "该动物不在救助站中" };
    }

    const interactionDef = GameData.interactions.find(i => i.id === interactionId);
    if (!interactionDef) {
      return { success: false, message: "未知的互动方式" };
    }

    // Check cooldown
    const cooldownKey = `${entityId}_${interactionId}`;
    if (this.cooldowns[cooldownKey] > 0) {
      return { success: false, message: `${interactionDef.name}还在冷却中（${this.cooldowns[cooldownKey]}回合）` };
    }

    // Check min trust
    if (interactionDef.min_trust && entityState.trust < interactionDef.min_trust) {
      return { success: false, message: `${entityState.id}的信任度不够（需要${interactionDef.min_trust}）` };
    }

    // Check resource cost
    for (const [resId, amount] of Object.entries(interactionDef.cost || {})) {
      if (!this.resources[resId] || this.resources[resId].current < amount) {
        const resName = GameData.resources.find(r => r.id === resId)?.name || resId;
        return { success: false, message: `${resName}不足` };
      }
    }

    // Check facility requirements
    if (interactionId === "medical" && !this.facilities.some(f => f.type === "medical_room")) {
      return { success: false, message: "需要先建造医疗室" };
    }
    if (interactionId === "play" && !this.facilities.some(f => f.type === "play_area")) {
      return { success: false, message: "需要先建造活动区" };
    }
    if (interactionId === "photo_shoot" && !this.facilities.some(f => f.type === "photo_studio")) {
      return { success: false, message: "需要先建造摄影角" };
    }

    // Deduct resources
    for (const [resId, amount] of Object.entries(interactionDef.cost || {})) {
      this.resources[resId].current -= amount;
    }

    // Calculate success rate
    let successRate = interactionDef.success_rate_base || 0.5;
    if (interactionDef.success_rate_formula) {
      // Simple formula evaluation
      successRate = interactionDef.success_rate_base
        + (entityState.trust / 100) * 0.3
        - (entityState.stress / 100) * 0.2;
    }

    // Entity-specific modifiers
    const entityDef = GameData.entities.find(e => e.id === entityId);
    if (entityDef) {
      // Trauma-based modifiers
      if (entityDef.trauma_tags.includes("fear_of_touch") && interactionId === "gentle_touch") {
        successRate *= 0.4;
      }
      if (entityDef.trauma_tags.includes("confinement") && interactionId === "gentle_touch") {
        successRate *= 0.7;
      }
      // Special trait: feeding bonus for timid animals
      if (entityDef.special_trait?.includes("喂食") && interactionId === "feed") {
        successRate = Math.min(1, successRate * 1.5);
      }
    }

    successRate = Math.max(0.05, Math.min(0.95, successRate));
    const succeeded = Math.random() < successRate;

    // Apply effects
    const entityName = entityDef?.name || entityId;
    let message;

    if (succeeded) {
      const effects = interactionDef.effects_on_entity || {};
      for (const [stat, delta] of Object.entries(effects)) {
        if (entityState[stat] !== undefined) {
          entityState[stat] = Math.max(0, Math.min(100, entityState[stat] + delta));
        }
      }
      message = (interactionDef.success_message || "互动成功！").replace("{name}", entityName);
      this.stats.successfulInteractions++;
    } else {
      // Apply failure effects if defined
      const failEffects = interactionDef.failure_effects || {};
      for (const [stat, delta] of Object.entries(failEffects)) {
        if (entityState[stat] !== undefined) {
          entityState[stat] = Math.max(0, Math.min(100, entityState[stat] + delta));
        }
      }
      message = (interactionDef.failure_message || "互动失败...").replace("{name}", entityName);
    }

    // Set cooldown
    if (interactionDef.cooldown_turns > 0) {
      this.cooldowns[cooldownKey] = interactionDef.cooldown_turns;
    }

    // Record interaction
    entityState.interaction_history.push({
      turn: this.turn,
      interaction: interactionId,
      succeeded,
    });

    // Recalculate adoptability
    entityState.adoptability = this._calculateAdoptability(entityState);

    this.stats.interactionsPerformed++;

    return {
      success: true,
      interactionSucceeded: succeeded,
      message,
      entityState: { ...entityState },
    };
  }

  // ── Adoptability Calculation ──

  _calculateAdoptability(entityState) {
    // Adoptability is a composite score based on trust, stress, health
    const trustScore = entityState.trust * 0.4;
    const stressScore = (100 - entityState.stress) * 0.3;
    const healthScore = entityState.health * 0.3;
    return Math.round(Math.max(0, Math.min(100, trustScore + stressScore + healthScore)));
  }

  // ── Matching Algorithm ──

  calculateMatchScore(entityId, familyId) {
    const entityState = this.entityStates[entityId];
    const entityDef = GameData.entities.find(e => e.id === entityId);
    const familyDef = GameData.adopter_families.find(f => f.id === familyId);

    if (!entityState || !entityDef || !familyDef) return 0;

    let score = 50; // Base score

    // Species preference
    if (familyDef.preferences[entityDef.species]) {
      score += familyDef.preferences[entityDef.species] * 5;
    }

    // Trust threshold
    if (familyDef.match_bonus?.trust && entityState.trust >= familyDef.match_bonus.trust) {
      score += 15;
    }

    // Stress threshold (lower is better)
    if (familyDef.match_bonus?.stress_max && entityState.stress <= familyDef.match_bonus.stress_max) {
      score += 10;
    }

    // Health threshold
    if (familyDef.match_bonus?.health && entityState.health >= familyDef.match_bonus.health) {
      score += 10;
    }

    // Experience level bonus for difficult animals
    if (entityState.stress > 60 && familyDef.experience_level === "expert") {
      score += 10;
    }

    // Patience bonus
    score += (familyDef.patience / 100) * 10;

    return Math.round(Math.max(0, Math.min(100, score)));
  }

  // ── Adoption Processing ──

  processAdoption(entityId, familyId) {
    const entityState = this.entityStates[entityId];
    const entityDef = GameData.entities.find(e => e.id === entityId);
    const familyDef = GameData.adopter_families.find(f => f.id === familyId);

    if (!entityState || !entityDef || !familyDef) {
      return { success: false, message: "无效的领养请求" };
    }

    if (entityState.adoptability < 50) {
      return { success: false, message: `${entityDef.name}还没有准备好被领养` };
    }

    const matchScore = this.calculateMatchScore(entityId, familyId);

    // Complete adoption
    entityState.status = "adopted";
    entityState.matched_family = familyId;
    entityState.adopted_turn = this.turn;

    // Record in history
    this.adoptionHistory.push({
      entityId,
      familyId,
      matchScore,
      adoptedTurn: this.turn,
      entityName: entityDef.name,
      familyName: familyDef.name,
    });

    // Schedule revisit
    const revisitTemplate = GameData.revisit_templates[0];
    if (revisitTemplate) {
      this.pendingRevisits.push({
        entityId,
        familyId,
        revisitTurn: this.turn + (revisitTemplate.delay_turns || 3),
        template: revisitTemplate,
      });
    }

    // Update stats
    this.stats.adoptionsCompleted++;
    this.stats.totalMatchScore += matchScore;

    // Reputation boost
    if (this.resources.reputation) {
      this.resources.reputation.current = Math.min(
        this.resources.reputation.max,
        this.resources.reputation.current + 5
      );
    }

    return {
      success: true,
      matchScore,
      message: `${entityDef.name}被${familyDef.name}领养了！匹配度：${matchScore}%`,
      farewell: this._generateFarewell(entityDef, familyDef, entityState),
    };
  }

  _generateFarewell(entityDef, familyDef, entityState) {
    // Find matching farewell template
    let template = GameData.farewell_templates.find(t => t.condition === "default");
    if (entityState.trust >= 80) {
      template = GameData.farewell_templates.find(t => t.condition.includes("trust >= 80")) || template;
    } else if (entityState.attachment >= 70) {
      template = GameData.farewell_templates.find(t => t.condition.includes("attachment >= 70")) || template;
    }

    const pronoun = entityDef.species === "cat" ? "它" : "它";
    return {
      narrative: (template?.narrative || "")
        .replace("{name}", entityDef.name)
        .replace("{family}", familyDef.name)
        .replace(/{pronoun}/g, pronoun),
      photo_description: (template?.photo_description || "")
        .replace("{name}", entityDef.name)
        .replace(/{pronoun}/g, pronoun),
      emotion_type: template?.emotion_type || "gentle",
    };
  }

  // ── Facility Building ──

  buildFacility(facilityId) {
    const facilityDef = GameData.facilities.find(f => f.id === facilityId);
    if (!facilityDef) return { success: false, message: "设施不存在" };

    // Check if already built
    if (this.facilities.some(f => f.type === facilityId)) {
      return { success: false, message: `${facilityDef.name}已经建造过了` };
    }

    // Check resources
    for (const [resId, amount] of Object.entries(facilityDef.cost || {})) {
      if (!this.resources[resId] || this.resources[resId].current < amount) {
        return { success: false, message: "资源不足" };
      }
    }

    // Deduct resources
    for (const [resId, amount] of Object.entries(facilityDef.cost || {})) {
      this.resources[resId].current -= amount;
    }

    this.facilities.push({
      type: facilityId,
      builtAt: this.turn,
    });

    return { success: true, message: `成功建造${facilityDef.name}！` };
  }

  // ── End Condition Checking ──

  checkEndCondition() {
    // Check defeat conditions
    for (const condition of (GameData.defeatConditions || [])) {
      if (condition.check(this)) {
        return { ended: true, victory: false, message: condition.message };
      }
    }

    // Check resource-based defeat
    for (const res of GameData.resources) {
      if (res.failIfZero && this.resources[res.id]?.current <= 0) {
        return { ended: true, victory: false, message: `${res.name}耗尽！` };
      }
    }

    // Check victory
    if (GameData.victoryCondition && GameData.victoryCondition(this)) {
      return {
        ended: true,
        victory: true,
        message: `恭喜！你成功帮助${this.stats.adoptionsCompleted}只动物找到了新家！`,
      };
    }

    // Turn limit
    if (this.turn >= (GameData.maxTurns || 30)) {
      const adoptions = this.stats.adoptionsCompleted;
      if (adoptions >= 2) {
        return { ended: true, victory: true, message: `在${this.turn}天里，你帮助了${adoptions}只动物找到了家！` };
      }
      return { ended: true, victory: false, message: "时间到了，但还有动物在等待一个家..." };
    }

    return { ended: false };
  }

  // ── Event Effect Application ──

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

    if (effect.entity_effects) {
      // Apply to a specific entity (context-dependent)
      // The caller should set effect._targetEntityId
      const targetId = effect._targetEntityId;
      if (targetId && this.entityStates[targetId]) {
        for (const [stat, delta] of Object.entries(effect.entity_effects)) {
          const state = this.entityStates[targetId];
          if (state[stat] !== undefined) {
            state[stat] = Math.max(0, Math.min(100, state[stat] + delta));
          }
        }
      }
    }

    if (effect.all_entity_effects) {
      for (const state of Object.values(this.entityStates)) {
        if (state.status !== "in_shelter") continue;
        for (const [stat, delta] of Object.entries(effect.all_entity_effects)) {
          if (state[stat] !== undefined) {
            state[stat] = Math.max(0, Math.min(100, state[stat] + delta));
          }
        }
      }
    }

    this.stats.eventsTriggered = (this.stats.eventsTriggered || 0) + 1;
  }

  // ── Stats ──

  getStats() {
    return {
      "总天数": this.stats.totalTurns,
      "互动次数": this.stats.interactionsPerformed,
      "成功互动": this.stats.successfulInteractions,
      "成功领养": this.stats.adoptionsCompleted,
      "平均匹配度": this.stats.adoptionsCompleted > 0
        ? Math.round(this.stats.totalMatchScore / this.stats.adoptionsCompleted) + "%"
        : "N/A",
      "设施数量": this.facilities.length,
    };
  }
}
'''

# ═══════════════════════════════════════════════════
# Resource Management Gold References
# (e.g., restaurant, factory, city builder)
# ═══════════════════════════════════════════════════

RESOURCE_MANAGEMENT_DATA_JS = r'''
/**
 * Gold Reference: Resource Management - data.js
 * Theme: Hot Pot Restaurant
 */
const GameData = {
  name: "火锅传奇",
  description: "经营一家火锅店，从街边小摊做到连锁品牌",
  maxTurns: 50,
  initialPopulation: 0,

  resources: [
    { id: "cash", name: "现金", icon: "💰", initial: 8000, max: 999999, perTurn: 0, warningThreshold: 1000, failIfZero: true },
    { id: "ingredients", name: "食材", icon: "🥬", initial: 50, max: 200, perTurn: 0, warningThreshold: 10 },
    { id: "reputation", name: "口碑", icon: "⭐", initial: 20, max: 100, perTurn: 0, warningThreshold: 10 },
    { id: "customers", name: "客流", icon: "👥", initial: 10, max: 200, perTurn: 0 },
  ],

  buildings: [
    {
      id: "kitchen_upgrade",
      name: "厨房升级",
      icon: "🔥",
      description: "升级厨房设备，提高出餐效率",
      cost: { cash: 2000, ingredients: 10 },
      produces: { cash: 300, customers: 2 },
      consumes: { ingredients: 5 },
    },
    {
      id: "ingredient_supply",
      name: "食材供应链",
      icon: "🚛",
      description: "建立稳定的食材供应渠道",
      cost: { cash: 1500 },
      produces: { ingredients: 8 },
    },
    {
      id: "dining_expansion",
      name: "扩建餐厅",
      icon: "🏪",
      description: "增加座位数，容纳更多客人",
      cost: { cash: 3000, ingredients: 5 },
      produces: { cash: 500, customers: 5 },
      consumes: { ingredients: 8 },
    },
    {
      id: "marketing",
      name: "营销推广",
      icon: "📢",
      description: "线上线下推广，提升知名度",
      cost: { cash: 1000 },
      produces: { reputation: 3, customers: 3 },
    },
    {
      id: "secret_recipe",
      name: "秘制锅底研发",
      icon: "🧪",
      description: "研发独家秘制锅底，提升口碑",
      cost: { cash: 2500, ingredients: 20 },
      produces: { reputation: 5, cash: 200 },
    },
  ],

  events: [
    {
      id: "food_critic",
      title: "美食博主来访",
      description: "一位知名美食博主悄悄来到了你的火锅店！",
      icon: "📸",
      weight: 2,
      choices: [
        {
          text: "全力招待，赠送特色菜品",
          effect: { resources: { cash: -500, ingredients: -10, reputation: 8 }, message: "博主发了好评！口碑大涨！", messageType: "success" },
        },
        {
          text: "正常服务，保持水准",
          effect: { resources: { reputation: 3 }, message: "博主给了中规中矩的评价", messageType: "info" },
        },
      ],
    },
    {
      id: "supply_shortage",
      title: "食材涨价",
      description: "受季节影响，主要食材价格大幅上涨！",
      icon: "📈",
      weight: 2,
      minTurn: 3,
      choices: [
        {
          text: "提前囤货",
          effect: { resources: { cash: -1500, ingredients: 30 }, message: "虽然花了不少钱，但食材储备充足", messageType: "info" },
        },
        {
          text: "寻找替代食材",
          effect: { resources: { ingredients: -10, reputation: -2 }, message: "替代食材口感略有下降", messageType: "warning" },
        },
      ],
    },
  ],

  victoryCondition: (state) => {
    return state.resources.cash.current >= 50000 && state.resources.reputation.current >= 80;
  },
};
'''

# ═══════════════════════════════════════════════════
# Reference Registry
# ═══════════════════════════════════════════════════

GOLD_REFERENCES = {
    "entity_lifecycle": {
        "data.js": ENTITY_LIFECYCLE_DATA_JS,
        "game-state.js": ENTITY_LIFECYCLE_GAME_STATE_JS,
    },
    "resource_management": {
        "data.js": RESOURCE_MANAGEMENT_DATA_JS,
    },
}


def get_gold_reference(scaffolding_type: str, module_name: str) -> str:
    """
    Get the gold standard reference code for a given scaffolding type and module.

    Args:
        scaffolding_type: e.g., "entity_lifecycle", "resource_management"
        module_name: e.g., "data.js", "game-state.js"

    Returns:
        Reference code string, or empty string if no reference exists.
    """
    refs = GOLD_REFERENCES.get(scaffolding_type, {})
    return refs.get(module_name, "")


def get_available_references(scaffolding_type: str) -> list:
    """
    Get list of available reference modules for a scaffolding type.

    Returns:
        List of module names that have gold references.
    """
    return list(GOLD_REFERENCES.get(scaffolding_type, {}).keys())
