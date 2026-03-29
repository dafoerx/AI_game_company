"""
Design Specification Module

Responsibilities:
1. Theme-Mechanic Mapping Library: maps game themes to appropriate mechanics
2. Design Spec Generator: produces structured JSON Schema specs from consensus
3. Design Verification Role: validates spec completeness before code generation
4. Scaffolding System: provides different code scaffolds per game type
"""

import json
import re
from .llm import LLMClient

# ═══════════════════════════════════════════════════
# 1. Theme-Mechanic Mapping Library
# ═══════════════════════════════════════════════════

THEME_MECHANIC_LIBRARY = {
    # ── Animal / Pet / Rescue themes ──
    "animal_rescue": {
        "keywords": ["动物", "救助", "流浪", "领养", "宠物", "猫", "狗", "中转", "收容"],
        "label": "动物救助/养成",
        "core_mechanics": {
            "entity_system": {
                "description": "Individual entity profiles with unique backstories, traits, and state machines",
                "required_models": ["EntityProfile", "EntityState", "TraitSystem"],
                "data_schema": {
                    "entities": [
                        {
                            "id": "string",
                            "name": "string",
                            "species": "string",
                            "backstory": "string",
                            "trauma_tags": ["string"],
                            "personality": "string",
                            "initial_state": {
                                "trust": "number (0-100)",
                                "stress": "number (0-100)",
                                "attachment": "number (0-100)",
                                "health": "number (0-100)",
                                "adoptability": "number (0-100, computed)"
                            },
                            "unlock_conditions": "string (when this entity appears)",
                            "portrait_emoji": "string"
                        }
                    ]
                }
            },
            "interaction_system": {
                "description": "Player-entity interactions that affect entity state",
                "required_models": ["InteractionType", "InteractionOutcome"],
                "data_schema": {
                    "interactions": [
                        {
                            "id": "string",
                            "name": "string",
                            "icon": "string",
                            "description": "string",
                            "cost": {"resource_id": "number"},
                            "effects_on_entity": {
                                "trust": "number delta",
                                "stress": "number delta",
                                "attachment": "number delta",
                                "health": "number delta"
                            },
                            "success_rate_formula": "string (e.g. 'base + trust * 0.5 - stress * 0.3')",
                            "success_message": "string",
                            "failure_message": "string",
                            "cooldown_turns": "number"
                        }
                    ]
                }
            },
            "matching_system": {
                "description": "Match entities with adopter families based on compatibility",
                "required_models": ["AdopterProfile", "MatchScore"],
                "data_schema": {
                    "adopter_families": [
                        {
                            "id": "string",
                            "name": "string",
                            "description": "string",
                            "preferences": {"trait": "weight"},
                            "environment": "string",
                            "experience_level": "string",
                            "portrait_emoji": "string"
                        }
                    ]
                }
            },
            "farewell_system": {
                "description": "Emotional farewell and post-adoption revisit events",
                "required_models": ["FarewellEvent", "RevisitEvent"],
                "data_schema": {
                    "farewell_templates": [
                        {
                            "condition": "string",
                            "narrative": "string",
                            "photo_description": "string",
                            "emotion_type": "string"
                        }
                    ],
                    "revisit_templates": [
                        {
                            "delay_turns": "number",
                            "narrative": "string",
                            "photo_description": "string",
                            "mood": "string"
                        }
                    ]
                }
            }
        },
        "victory_conditions": [
            "successful_adoptions >= threshold",
            "average_trust_at_adoption >= threshold",
            "revisit_happiness_rate >= threshold"
        ],
        "anti_patterns": [
            "DO NOT reduce entities to global resource numbers",
            "DO NOT make adoption automatic - player must decide when entity is ready",
            "DO NOT skip farewell/revisit emotional moments",
            "DO NOT use generic building-produces-resource as the only mechanic"
        ],
        "scaffolding_type": "entity_lifecycle"
    },

    # ── Restaurant / Food Business themes ──
    "restaurant": {
        "keywords": ["餐厅", "火锅", "烧烤", "美食", "厨房", "料理", "饭店", "小吃"],
        "label": "餐饮经营",
        "core_mechanics": {
            "menu_system": {
                "description": "Menu items with recipes, ingredients, and customer preferences",
                "required_models": ["MenuItem", "Recipe", "Ingredient"],
                "data_schema": {
                    "menu_items": [
                        {
                            "id": "string",
                            "name": "string",
                            "icon": "string",
                            "recipe": {"ingredient_id": "quantity"},
                            "prep_time": "number",
                            "sell_price": "number",
                            "popularity": "number",
                            "unlock_level": "number"
                        }
                    ]
                }
            },
            "customer_system": {
                "description": "Customer types with preferences, patience, and satisfaction",
                "required_models": ["CustomerType", "Order", "Satisfaction"],
                "data_schema": {
                    "customer_types": [
                        {
                            "id": "string",
                            "name": "string",
                            "icon": "string",
                            "preferences": ["menu_item_id"],
                            "patience": "number",
                            "tip_multiplier": "number"
                        }
                    ]
                }
            },
            "upgrade_system": {
                "description": "Kitchen equipment and restaurant upgrades",
                "required_models": ["Equipment", "Upgrade"],
                "data_schema": {
                    "upgrades": [
                        {
                            "id": "string",
                            "name": "string",
                            "icon": "string",
                            "cost": {"resource_id": "number"},
                            "effect": "string",
                            "effect_value": "number"
                        }
                    ]
                }
            }
        },
        "victory_conditions": [
            "reputation >= threshold",
            "total_revenue >= threshold",
            "menu_items_unlocked >= threshold"
        ],
        "anti_patterns": [
            "DO NOT ignore customer satisfaction feedback loop",
            "DO NOT make all menu items available from start"
        ],
        "scaffolding_type": "resource_management"
    },

    # ── Space / Sci-fi themes ──
    "space": {
        "keywords": ["太空", "星际", "宇宙", "外星", "银河", "飞船", "殖民", "探索"],
        "label": "太空探索/经营",
        "core_mechanics": {
            "exploration_system": {
                "description": "Procedural sector exploration with discoveries and hazards",
                "required_models": ["Sector", "Discovery", "Hazard"],
                "data_schema": {
                    "sectors": [
                        {
                            "id": "string",
                            "name": "string",
                            "type": "string",
                            "discoveries": ["discovery_id"],
                            "hazards": ["hazard_id"],
                            "resources": {"resource_id": "amount"}
                        }
                    ]
                }
            },
            "crew_system": {
                "description": "Crew members with skills, morale, and assignments",
                "required_models": ["CrewMember", "Skill", "Assignment"],
                "data_schema": {
                    "crew_roles": [
                        {
                            "id": "string",
                            "name": "string",
                            "skills": ["string"],
                            "morale_factors": {"factor": "weight"}
                        }
                    ]
                }
            }
        },
        "victory_conditions": [
            "sectors_explored >= threshold",
            "crew_survival_rate >= threshold"
        ],
        "anti_patterns": [
            "DO NOT make exploration purely random without player agency",
            "DO NOT ignore crew morale and interpersonal dynamics"
        ],
        "scaffolding_type": "exploration_management"
    },

    # ── Default / Generic management ──
    "generic_management": {
        "keywords": [],
        "label": "通用经营模拟",
        "core_mechanics": {
            "resource_system": {
                "description": "Standard resource production and consumption",
                "required_models": ["Resource", "Building", "Event"],
                "data_schema": {
                    "resources": [{"id": "string", "name": "string", "initial": "number"}],
                    "buildings": [{"id": "string", "name": "string", "cost": {}, "produces": {}}],
                    "events": [{"id": "string", "title": "string", "choices": []}]
                }
            }
        },
        "victory_conditions": ["resources >= threshold"],
        "anti_patterns": [],
        "scaffolding_type": "resource_management"
    }
}


def detect_theme(direction: str, theme: str = "", core_loop: str = "") -> dict:
    """
    Detect the game theme from user direction and return the matching
    theme-mechanic mapping entry.
    """
    combined = (direction + " " + theme + " " + core_loop).lower()

    best_match = None
    best_score = 0

    for theme_id, mapping in THEME_MECHANIC_LIBRARY.items():
        if theme_id == "generic_management":
            continue
        score = sum(1 for kw in mapping["keywords"] if kw in combined)
        if score > best_score:
            best_score = score
            best_match = theme_id

    if best_match and best_score > 0:
        result = THEME_MECHANIC_LIBRARY[best_match].copy()
        result["theme_id"] = best_match
        return result

    result = THEME_MECHANIC_LIBRARY["generic_management"].copy()
    result["theme_id"] = "generic_management"
    return result


# ═══════════════════════════════════════════════════
# 2. Design Spec Generator
# ═══════════════════════════════════════════════════

DESIGN_SPEC_SYSTEM_PROMPT = """\
你是一位资深的游戏系统设计师，擅长将多角色讨论的共识转化为精确的、可被代码生成引擎直接消费的结构化设计规格。

你的输出必须是严格的 JSON 格式（不要用 markdown 代码块包裹），包含以下结构：

{
  "game_type": "游戏类型标识",
  "entity_definitions": [
    {
      "id": "实体唯一ID",
      "name": "实体名称",
      "species": "物种/类型",
      "backstory": "背景故事（2-3句话）",
      "trauma_tags": ["创伤标签1", "创伤标签2"],
      "personality": "性格描述",
      "portrait_emoji": "表情符号",
      "initial_state": {
        "trust": 0,
        "stress": 0,
        "attachment": 0,
        "health": 0
      }
    }
  ],
  "interaction_definitions": [
    {
      "id": "互动ID",
      "name": "互动名称",
      "icon": "图标",
      "description": "描述",
      "cost": {},
      "effects_on_entity": {},
      "success_rate_base": 0.5,
      "success_message": "",
      "failure_message": "",
      "cooldown_turns": 0
    }
  ],
  "state_machine": {
    "states": ["state1", "state2"],
    "transitions": [
      {
        "from": "state1",
        "to": "state2",
        "condition": "条件描述",
        "trigger": "触发方式"
      }
    ]
  },
  "adopter_families": [
    {
      "id": "家庭ID",
      "name": "家庭名称",
      "description": "描述",
      "preferences": {},
      "environment": "环境描述",
      "portrait_emoji": "表情符号"
    }
  ],
  "resource_definitions": [
    {
      "id": "资源ID",
      "name": "资源名称",
      "icon": "图标",
      "initial": 0,
      "max": 999,
      "per_turn": 0,
      "warning_threshold": 0,
      "fail_if_zero": false
    }
  ],
  "facility_definitions": [
    {
      "id": "设施ID",
      "name": "设施名称",
      "icon": "图标",
      "description": "描述",
      "cost": {},
      "produces": {},
      "consumes": {},
      "unlocks_interactions": ["互动ID"]
    }
  ],
  "event_definitions": [
    {
      "id": "事件ID",
      "title": "事件标题",
      "description": "事件描述",
      "icon": "图标",
      "trigger_condition": "触发条件",
      "choices": [
        {
          "text": "选项文本",
          "effects": {},
          "entity_effects": {},
          "message": "结果描述",
          "message_type": "success/warning/danger/info"
        }
      ]
    }
  ],
  "victory_conditions": [
    {
      "type": "条件类型",
      "description": "条件描述",
      "formula": "计算公式"
    }
  ],
  "ui_flow": {
    "main_screens": ["screen1", "screen2"],
    "core_interaction_flow": "核心交互流程描述",
    "key_ui_components": ["组件1", "组件2"]
  }
}

要求：
1. entity_definitions 至少 6 个实体，每个有独特的背景和状态
2. interaction_definitions 至少 5 种互动方式
3. state_machine 必须定义完整的状态流转
4. event_definitions 至少 8 个事件
5. 所有数值必须经过平衡性考虑
6. victory_conditions 必须与游戏主题紧密相关
"""


def generate_design_spec(llm: LLMClient, plan: dict, theme_mapping: dict,
                         consensus_texts: list) -> dict:
    """
    Generate a structured design specification from the project plan,
    theme mapping, and consensus discussion texts.

    Returns a dict that can be directly consumed by the code generator.
    """
    consensus_summary = "\n\n---\n\n".join(consensus_texts[-6:]) if consensus_texts else "(No consensus discussions yet)"

    mechanics_desc = json.dumps(theme_mapping.get("core_mechanics", {}),
                                ensure_ascii=False, indent=2)
    anti_patterns = "\n".join(f"- {ap}" for ap in theme_mapping.get("anti_patterns", []))

    user_prompt = f"""
## Project Information
- Name: {plan.get('project_name', 'Unknown')}
- Theme: {plan.get('theme', '')}
- Core Loop: {plan.get('core_loop', '')}
- Visual Style: {plan.get('visual_style', '')}
- Platform: {plan.get('platform', 'Web')}

## Detected Game Type: {theme_mapping.get('label', 'Generic')}

## Required Core Mechanics (from theme-mechanic library)
{mechanics_desc}

## Anti-Patterns to Avoid
{anti_patterns}

## Multi-Role Consensus Discussions
{consensus_summary}

## MVP Scope
Must Have: {json.dumps(plan.get('mvp_scope', {}).get('must_have', []), ensure_ascii=False)}
Nice to Have: {json.dumps(plan.get('mvp_scope', {}).get('nice_to_have', []), ensure_ascii=False)}
Not Doing: {json.dumps(plan.get('mvp_scope', {}).get('not_doing', []), ensure_ascii=False)}

Please generate a complete, structured design specification in JSON format.
All text content should be in Chinese. Ensure every entity has unique traits and backstory.
"""

    raw = llm.complete(DESIGN_SPEC_SYSTEM_PROMPT, user_prompt)

    # Extract JSON from response
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(1)

    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        raw = raw[start:end + 1]

    try:
        spec = json.loads(raw)
    except json.JSONDecodeError:
        spec = {
            "error": "Failed to parse design spec",
            "_raw": raw[:2000],
            "entity_definitions": [],
            "interaction_definitions": [],
            "state_machine": {"states": [], "transitions": []},
            "resource_definitions": [],
            "facility_definitions": [],
            "event_definitions": [],
            "victory_conditions": [],
            "ui_flow": {}
        }

    return spec


# ═══════════════════════════════════════════════════
# 3. Design Verification Role
# ═══════════════════════════════════════════════════

VERIFICATION_SYSTEM_PROMPT = """\
你是设计验证专家。你的职责是检查游戏设计规格是否完整到可以指导代码生成。

你需要检查以下维度：
1. 实体完整性：是否有足够的实体定义？每个实体是否有独特的状态和背景？
2. 交互完整性：是否有足够的互动方式？互动效果是否合理？
3. 状态机完整性：状态流转是否闭环？是否有死锁状态？
4. 数值平衡性：资源产出/消耗是否平衡？胜利条件是否可达？
5. 叙事完整性：事件是否覆盖了核心情感体验？
6. UI 可行性：交互流程是否清晰？关键界面是否定义？

输出格式（严格 JSON，不要 markdown 包裹）：
{
  "passed": true/false,
  "score": 0-100,
  "checks": [
    {
      "dimension": "检查维度",
      "passed": true/false,
      "score": 0-100,
      "issues": ["问题1", "问题2"],
      "suggestions": ["建议1", "建议2"]
    }
  ],
  "blocking_issues": ["必须修复的问题"],
  "overall_assessment": "总体评估（一段话）"
}
"""


def verify_design_spec(llm: LLMClient, spec: dict, theme_mapping: dict) -> dict:
    """
    Verify that a design spec is complete enough to guide code generation.

    Returns a verification report dict.
    """
    anti_patterns = "\n".join(f"- {ap}" for ap in theme_mapping.get("anti_patterns", []))

    user_prompt = f"""
## Design Specification to Verify
{json.dumps(spec, ensure_ascii=False, indent=2)[:8000]}

## Expected Game Type: {theme_mapping.get('label', 'Generic')}

## Anti-Patterns to Check Against
{anti_patterns}

## Required Core Mechanics
{json.dumps(list(theme_mapping.get('core_mechanics', {}).keys()), ensure_ascii=False)}

Please verify this design specification and output your assessment in JSON format.
"""

    raw = llm.complete(VERIFICATION_SYSTEM_PROMPT, user_prompt)

    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(1)

    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        raw = raw[start:end + 1]

    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        report = {
            "passed": False,
            "score": 0,
            "checks": [],
            "blocking_issues": ["Design verification response could not be parsed"],
            "overall_assessment": raw[:500]
        }

    return report


# ═══════════════════════════════════════════════════
# 4. Scaffolding System
# ═══════════════════════════════════════════════════

SCAFFOLDING_TYPES = {
    "entity_lifecycle": {
        "description": "Entity-centric game with individual profiles, state machines, and lifecycle events",
        "js_modules": {
            "data.js": {
                "global_var": "GameData",
                "must_contain": [
                    "entities (array of entity profiles with individual states)",
                    "interactions (array of player-entity interaction types)",
                    "adopter_families or matching_targets (array of match targets)",
                    "resources (array of global resource definitions)",
                    "facilities (array of facility/building definitions)",
                    "events (array of narrative events)",
                    "farewell_templates (array of farewell narratives)",
                    "revisit_templates (array of revisit narratives)"
                ]
            },
            "game-state.js": {
                "global_var": "GameState",
                "must_contain": [
                    "Entity state tracking (per-entity trust/stress/attachment/health)",
                    "Interaction processing (apply interaction to specific entity)",
                    "Adoptability calculation (computed from entity state)",
                    "Matching algorithm (entity-family compatibility score)",
                    "Farewell/adoption processing",
                    "Revisit event scheduling",
                    "Global resource management",
                    "Turn processing with entity state decay/recovery"
                ]
            },
            "ui.js": {
                "global_var": "UI",
                "must_contain": [
                    "Entity gallery/list view",
                    "Entity detail card (showing state, backstory, portrait)",
                    "Interaction panel (available actions for selected entity)",
                    "Adoption readiness indicator",
                    "Matching interface",
                    "Farewell scene renderer",
                    "Revisit album/gallery",
                    "Resource panel",
                    "Game log"
                ]
            },
            "events.js": {
                "global_var": "Events",
                "must_contain": [
                    "Entity-specific events (triggered by entity state)",
                    "Global narrative events",
                    "Farewell events",
                    "Revisit events",
                    "Event modal with choices"
                ]
            },
            "main.js": {
                "global_var": "Game",
                "must_contain": [
                    "Game loop with entity state updates",
                    "Screen management",
                    "Turn processing",
                    "Victory/defeat checking based on adoption metrics"
                ]
            }
        },
        "html_sections": [
            "entity-gallery (grid of entity cards)",
            "entity-detail (selected entity info + interaction buttons)",
            "matching-panel (adoption matching interface)",
            "farewell-scene (farewell narrative display)",
            "revisit-album (post-adoption photo gallery)",
            "resource-panel",
            "game-log"
        ]
    },

    "resource_management": {
        "description": "Classic resource management with buildings, production chains, and events",
        "js_modules": {
            "data.js": {
                "global_var": "GameData",
                "must_contain": [
                    "resources (array of resource definitions)",
                    "buildings (array of building definitions with cost/produces/consumes)",
                    "events (array of random events with choices)"
                ]
            },
            "game-state.js": {
                "global_var": "GameState",
                "must_contain": [
                    "Resource tracking and turn settlement",
                    "Building construction and production",
                    "Event effect application",
                    "Victory/defeat condition checking"
                ]
            },
            "ui.js": {
                "global_var": "UI",
                "must_contain": [
                    "Resource panel",
                    "Building menu and viewport",
                    "Game log"
                ]
            },
            "events.js": {
                "global_var": "Events",
                "must_contain": [
                    "Random event triggering",
                    "Event modal with choices",
                    "Effect application"
                ]
            },
            "main.js": {
                "global_var": "Game",
                "must_contain": [
                    "Game loop",
                    "Screen management",
                    "Turn processing"
                ]
            }
        },
        "html_sections": [
            "resource-panel",
            "build-menu",
            "game-viewport",
            "game-log"
        ]
    },

    "exploration_management": {
        "description": "Exploration-based game with sectors, crew, and discoveries",
        "js_modules": {
            "data.js": {
                "global_var": "GameData",
                "must_contain": [
                    "sectors (explorable areas)",
                    "crew_roles (crew member types)",
                    "discoveries (things to find)",
                    "hazards (dangers)",
                    "resources",
                    "events"
                ]
            },
            "game-state.js": {
                "global_var": "GameState",
                "must_contain": [
                    "Sector exploration state",
                    "Crew management and morale",
                    "Discovery tracking",
                    "Resource management",
                    "Turn processing"
                ]
            },
            "ui.js": {
                "global_var": "UI",
                "must_contain": [
                    "Sector map view",
                    "Crew roster",
                    "Discovery log",
                    "Resource panel"
                ]
            },
            "events.js": {
                "global_var": "Events",
                "must_contain": [
                    "Exploration events",
                    "Crew events",
                    "Discovery events"
                ]
            },
            "main.js": {
                "global_var": "Game",
                "must_contain": [
                    "Game loop",
                    "Screen management",
                    "Exploration turn processing"
                ]
            }
        },
        "html_sections": [
            "sector-map",
            "crew-panel",
            "discovery-log",
            "resource-panel",
            "game-log"
        ]
    }
}


def get_scaffolding(scaffolding_type: str) -> dict:
    """Get the scaffolding definition for a given game type."""
    return SCAFFOLDING_TYPES.get(scaffolding_type,
                                  SCAFFOLDING_TYPES["resource_management"])


def build_scaffolding_prompt_section(scaffolding: dict, module_name: str) -> str:
    """
    Build a prompt section that describes what a specific module MUST contain
    based on the scaffolding type.
    """
    module_spec = scaffolding.get("js_modules", {}).get(module_name, {})
    if not module_spec:
        return ""

    lines = [
        f"\n## Scaffolding Requirements for {module_name}",
        f"Game Type: {scaffolding.get('description', 'Unknown')}",
        f"Global Variable: {module_spec.get('global_var', 'Unknown')}",
        "",
        "### This module MUST contain the following (non-negotiable):"
    ]

    for item in module_spec.get("must_contain", []):
        lines.append(f"- {item}")

    if module_name == "data.js":
        lines.append("")
        lines.append("### HTML sections that will reference this data:")
        for section in scaffolding.get("html_sections", []):
            lines.append(f"- {section}")

    return "\n".join(lines)
