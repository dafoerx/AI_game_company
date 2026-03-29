"""
完整游戏代码模板生成器。
提供预设的高质量游戏代码模板，确保生成的代码完整可运行。
"""

# HTML 基础模板
HTML_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{game_title}</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/animations.css">
</head>
<body>
    <div id="app">
        <!-- 加载屏幕 -->
        <div id="loading-screen" class="screen active">
            <div class="loading-content">
                <h1 class="game-title">{game_title}</h1>
                <p class="game-subtitle">{game_subtitle}</p>
                <div class="loading-bar">
                    <div class="loading-progress"></div>
                </div>
                <p class="loading-text">正在加载游戏资源...</p>
            </div>
        </div>

        <!-- 主菜单 -->
        <div id="main-menu" class="screen">
            <div class="menu-content">
                <h1 class="menu-title">{game_title}</h1>
                <div class="menu-buttons">
                    <button class="menu-btn" onclick="Game.startNewGame()">
                        <span class="btn-icon">🎮</span>
                        <span class="btn-text">开始游戏</span>
                    </button>
                    <button class="menu-btn" onclick="Game.showSettings()">
                        <span class="btn-icon">⚙️</span>
                        <span class="btn-text">游戏设置</span>
                    </button>
                    <button class="menu-btn" onclick="Game.showHelp()">
                        <span class="btn-icon">❓</span>
                        <span class="btn-text">游戏帮助</span>
                    </button>
                </div>
            </div>
            <div class="menu-particles" id="menu-particles"></div>
        </div>

        <!-- 游戏主界面 -->
        <div id="game-screen" class="screen">
            <!-- 顶部状态栏 -->
            <header class="game-header">
                <div class="header-left">
                    <span class="game-time" id="game-time">回合 1</span>
                </div>
                <div class="header-center">
                    <h2 class="current-phase" id="current-phase">准备阶段</h2>
                </div>
                <div class="header-right">
                    <button class="icon-btn" onclick="Game.togglePause()">
                        <span id="pause-icon">⏸️</span>
                    </button>
                    <button class="icon-btn" onclick="Game.openMenu()">☰</button>
                </div>
            </header>

            <!-- 资源面板 -->
            <div class="resource-panel" id="resource-panel">
                <!-- 资源条目将由 JS 动态生成 -->
            </div>

            <!-- 主游戏区域 -->
            <main class="game-main">
                <!-- 左侧面板 -->
                <aside class="side-panel left-panel">
                    <div class="panel-section">
                        <h3 class="section-title">📊 状态总览</h3>
                        <div id="status-overview"></div>
                    </div>
                    <div class="panel-section">
                        <h3 class="section-title">📋 任务列表</h3>
                        <div id="task-list"></div>
                    </div>
                </aside>

                <!-- 中央游戏区 -->
                <div class="center-area">
                    <div class="game-viewport" id="game-viewport">
                        <!-- 游戏主视图 -->
                    </div>
                    
                    <!-- 操作按钮区 -->
                    <div class="action-bar">
                        <button class="action-btn primary" onclick="Game.nextTurn()">
                            <span class="btn-icon">⏭️</span>
                            <span>下一回合</span>
                        </button>
                    </div>
                </div>

                <!-- 右侧面板 -->
                <aside class="side-panel right-panel">
                    <div class="panel-section">
                        <h3 class="section-title">🏗️ 建造</h3>
                        <div id="build-menu"></div>
                    </div>
                    <div class="panel-section">
                        <h3 class="section-title">📜 日志</h3>
                        <div id="game-log" class="log-container"></div>
                    </div>
                </aside>
            </main>

            <!-- 底部信息栏 -->
            <footer class="game-footer">
                <div class="footer-tips" id="footer-tips">
                    提示：点击建筑进行交互，右键查看详情
                </div>
            </footer>
        </div>

        <!-- 事件弹窗 -->
        <div id="event-modal" class="modal">
            <div class="modal-content event-content">
                <div class="event-icon" id="event-icon">⚠️</div>
                <h2 class="event-title" id="event-title">事件标题</h2>
                <p class="event-description" id="event-description">事件描述内容</p>
                <div class="event-choices" id="event-choices">
                    <!-- 选项按钮将由 JS 生成 -->
                </div>
            </div>
        </div>

        <!-- 设置弹窗 -->
        <div id="settings-modal" class="modal">
            <div class="modal-content settings-content">
                <h2>⚙️ 游戏设置</h2>
                <div class="settings-group">
                    <label>游戏速度</label>
                    <input type="range" min="1" max="3" value="2" id="game-speed">
                </div>
                <div class="settings-group">
                    <label>音效</label>
                    <input type="checkbox" id="sound-enabled" checked>
                </div>
                <div class="settings-group">
                    <label>动画效果</label>
                    <input type="checkbox" id="animations-enabled" checked>
                </div>
                <button class="btn-close" onclick="Game.closeModal('settings-modal')">关闭</button>
            </div>
        </div>

        <!-- 帮助弹窗 -->
        <div id="help-modal" class="modal">
            <div class="modal-content help-content">
                <h2>❓ 游戏帮助</h2>
                <div class="help-text">
                    <h3>基本操作</h3>
                    <ul>
                        <li>点击建筑可以查看详情和进行操作</li>
                        <li>使用"下一回合"按钮推进游戏时间</li>
                        <li>注意管理资源，避免资源耗尽</li>
                    </ul>
                    <h3>游戏目标</h3>
                    <p>{game_objective}</p>
                </div>
                <button class="btn-close" onclick="Game.closeModal('help-modal')">关闭</button>
            </div>
        </div>

        <!-- 游戏结束屏幕 -->
        <div id="game-over" class="screen">
            <div class="game-over-content">
                <h1 id="game-over-title">游戏结束</h1>
                <p id="game-over-message">你的成绩</p>
                <div class="game-over-stats" id="game-over-stats"></div>
                <button class="menu-btn" onclick="Game.restart()">重新开始</button>
                <button class="menu-btn secondary" onclick="Game.backToMenu()">返回主菜单</button>
            </div>
        </div>
    </div>

    <script src="js/utils.js"></script>
    <script src="js/data.js"></script>
    <script src="js/game-state.js"></script>
    <script src="js/ui.js"></script>
    <script src="js/events.js"></script>
    <script src="js/main.js"></script>
</body>
</html>
'''

# 主样式 CSS
STYLE_CSS_TEMPLATE = '''\
/* ═══════════════════════════════════════
   {game_title} - 主样式表
   视觉风格: {visual_style}
   ═══════════════════════════════════════ */

/* CSS 变量 - 配色方案 */
:root {{
    /* 主色调 */
    --primary-color: {primary_color};
    --primary-light: {primary_light};
    --primary-dark: {primary_dark};
    
    /* 辅助色 */
    --secondary-color: {secondary_color};
    --accent-color: {accent_color};
    
    /* 背景色 */
    --bg-dark: {bg_dark};
    --bg-medium: {bg_medium};
    --bg-light: {bg_light};
    
    /* 文字色 */
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --text-muted: {text_muted};
    
    /* 状态色 */
    --success-color: #2ecc71;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
    --info-color: #3498db;
    
    /* 边框和阴影 */
    --border-color: rgba(255, 255, 255, 0.1);
    --shadow-color: rgba(0, 0, 0, 0.3);
    --glow-color: {glow_color};
    
    /* 尺寸 */
    --header-height: 60px;
    --footer-height: 40px;
    --panel-width: 280px;
    --border-radius: 12px;
    --border-radius-sm: 8px;
    
    /* 字体 */
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}}

/* 基础重置 */
*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

html, body {{
    width: 100%;
    height: 100%;
    overflow: hidden;
}}

body {{
    font-family: var(--font-family);
    background: var(--bg-dark);
    color: var(--text-primary);
    line-height: 1.5;
}}

#app {{
    width: 100%;
    height: 100%;
    position: relative;
}}

/* ═══════════════════════════════════════
   屏幕/场景
   ═══════════════════════════════════════ */
.screen {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: none;
    opacity: 0;
    transition: opacity 0.5s ease;
}}

.screen.active {{
    display: flex;
    flex-direction: column;
    opacity: 1;
}}

/* ═══════════════════════════════════════
   加载屏幕
   ═══════════════════════════════════════ */
#loading-screen {{
    background: linear-gradient(135deg, var(--bg-dark), var(--bg-medium));
    justify-content: center;
    align-items: center;
}}

.loading-content {{
    text-align: center;
}}

.game-title {{
    font-size: 48px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
    animation: titleGlow 2s ease-in-out infinite;
}}

.game-subtitle {{
    font-size: 18px;
    color: var(--text-secondary);
    margin-bottom: 40px;
}}

.loading-bar {{
    width: 300px;
    height: 6px;
    background: var(--bg-light);
    border-radius: 3px;
    overflow: hidden;
    margin: 0 auto 20px;
}}

.loading-progress {{
    width: 0%;
    height: 100%;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    border-radius: 3px;
    animation: loadingProgress 2s ease-out forwards;
}}

.loading-text {{
    color: var(--text-muted);
    font-size: 14px;
}}

/* ═══════════════════════════════════════
   主菜单
   ═══════════════════════════════════════ */
#main-menu {{
    background: linear-gradient(135deg, var(--bg-dark), var(--bg-medium));
    justify-content: center;
    align-items: center;
    position: relative;
}}

.menu-content {{
    text-align: center;
    z-index: 10;
}}

.menu-title {{
    font-size: 56px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 50px;
    text-shadow: 0 0 40px var(--glow-color);
}}

.menu-buttons {{
    display: flex;
    flex-direction: column;
    gap: 16px;
    align-items: center;
}}

.menu-btn {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 40px;
    min-width: 250px;
    background: linear-gradient(135deg, var(--bg-light), var(--bg-medium));
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}

.menu-btn::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: left 0.5s ease;
}}

.menu-btn:hover {{
    transform: translateY(-3px);
    border-color: var(--primary-color);
    box-shadow: 0 10px 30px var(--shadow-color), 0 0 20px var(--glow-color);
}}

.menu-btn:hover::before {{
    left: 100%;
}}

.menu-btn:active {{
    transform: translateY(-1px);
}}

.menu-btn.secondary {{
    background: transparent;
    border-color: var(--text-muted);
}}

.btn-icon {{
    font-size: 24px;
}}

/* 菜单粒子效果 */
.menu-particles {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    overflow: hidden;
}}

/* ═══════════════════════════════════════
   游戏主界面
   ═══════════════════════════════════════ */
#game-screen {{
    background: var(--bg-dark);
}}

/* 顶部栏 */
.game-header {{
    height: var(--header-height);
    background: linear-gradient(180deg, var(--bg-medium), transparent);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    border-bottom: 1px solid var(--border-color);
}}

.game-time {{
    font-size: 16px;
    font-weight: 600;
    color: var(--primary-color);
}}

.current-phase {{
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
}}

.icon-btn {{
    width: 40px;
    height: 40px;
    background: var(--bg-light);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    font-size: 18px;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.icon-btn:hover {{
    background: var(--primary-dark);
    border-color: var(--primary-color);
}}

/* 资源面板 */
.resource-panel {{
    display: flex;
    justify-content: center;
    gap: 20px;
    padding: 12px 20px;
    background: var(--bg-medium);
    border-bottom: 1px solid var(--border-color);
    flex-wrap: wrap;
}}

.resource-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    background: var(--bg-light);
    border-radius: var(--border-radius-sm);
    border: 1px solid var(--border-color);
    min-width: 120px;
}}

.resource-icon {{
    font-size: 24px;
}}

.resource-info {{
    display: flex;
    flex-direction: column;
}}

.resource-name {{
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.resource-value {{
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    font-family: var(--font-mono);
}}

.resource-value.low {{
    color: var(--danger-color);
    animation: pulse 1s ease-in-out infinite;
}}

.resource-change {{
    font-size: 12px;
    font-weight: 600;
}}

.resource-change.positive {{
    color: var(--success-color);
}}

.resource-change.negative {{
    color: var(--danger-color);
}}

/* 主游戏区 */
.game-main {{
    flex: 1;
    display: flex;
    overflow: hidden;
}}

/* 侧边面板 */
.side-panel {{
    width: var(--panel-width);
    background: var(--bg-medium);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}}

.right-panel {{
    border-right: none;
    border-left: 1px solid var(--border-color);
}}

.panel-section {{
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
}}

.section-title {{
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 12px;
}}

/* 中央区域 */
.center-area {{
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px;
}}

.game-viewport {{
    flex: 1;
    background: var(--bg-light);
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
    overflow: hidden;
    position: relative;
}}

/* 操作按钮区 */
.action-bar {{
    display: flex;
    justify-content: center;
    gap: 12px;
    padding: 16px;
}}

.action-btn {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: var(--bg-light);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.action-btn:hover {{
    transform: translateY(-2px);
    border-color: var(--primary-color);
    box-shadow: 0 4px 12px var(--shadow-color);
}}

.action-btn.primary {{
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    border-color: var(--primary-color);
}}

.action-btn.primary:hover {{
    box-shadow: 0 4px 20px var(--glow-color);
}}

/* 底部栏 */
.game-footer {{
    height: var(--footer-height);
    background: var(--bg-medium);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 20px;
    border-top: 1px solid var(--border-color);
}}

.footer-tips {{
    font-size: 13px;
    color: var(--text-muted);
}}

/* 日志 */
.log-container {{
    max-height: 200px;
    overflow-y: auto;
    font-size: 12px;
}}

.log-entry {{
    padding: 6px 0;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    gap: 8px;
}}

.log-time {{
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 10px;
}}

.log-message {{
    color: var(--text-secondary);
}}

.log-message.warning {{
    color: var(--warning-color);
}}

.log-message.danger {{
    color: var(--danger-color);
}}

.log-message.success {{
    color: var(--success-color);
}}

/* ═══════════════════════════════════════
   模态框/弹窗
   ═══════════════════════════════════════ */
.modal {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s ease;
}}

.modal.active {{
    display: flex;
    opacity: 1;
}}

.modal-content {{
    background: var(--bg-medium);
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
    padding: 30px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    animation: modalSlideIn 0.3s ease;
}}

/* 事件弹窗 */
.event-content {{
    text-align: center;
}}

.event-icon {{
    font-size: 64px;
    margin-bottom: 20px;
    animation: eventIconPulse 1s ease-in-out infinite;
}}

.event-title {{
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--text-primary);
}}

.event-description {{
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 24px;
    line-height: 1.6;
}}

.event-choices {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.event-choice {{
    padding: 14px 20px;
    background: var(--bg-light);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
}}

.event-choice:hover {{
    border-color: var(--primary-color);
    background: var(--primary-dark);
}}

.event-choice .choice-effect {{
    display: block;
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
}}

/* 设置/帮助 */
.settings-group {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-color);
}}

.help-text h3 {{
    font-size: 16px;
    color: var(--primary-color);
    margin: 16px 0 8px;
}}

.help-text ul {{
    padding-left: 20px;
    color: var(--text-secondary);
}}

.help-text li {{
    margin-bottom: 6px;
}}

.btn-close {{
    width: 100%;
    padding: 12px;
    margin-top: 20px;
    background: var(--bg-light);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.btn-close:hover {{
    background: var(--primary-dark);
    border-color: var(--primary-color);
}}

/* ═══════════════════════════════════════
   游戏结束屏幕
   ═══════════════════════════════════════ */
#game-over {{
    background: linear-gradient(135deg, var(--bg-dark), var(--bg-medium));
    justify-content: center;
    align-items: center;
}}

.game-over-content {{
    text-align: center;
}}

#game-over-title {{
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 20px;
}}

#game-over-title.victory {{
    color: var(--success-color);
}}

#game-over-title.defeat {{
    color: var(--danger-color);
}}

#game-over-message {{
    font-size: 18px;
    color: var(--text-secondary);
    margin-bottom: 30px;
}}

.game-over-stats {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 40px;
}}

.stat-item {{
    padding: 16px;
    background: var(--bg-light);
    border-radius: var(--border-radius-sm);
    border: 1px solid var(--border-color);
}}

.stat-value {{
    font-size: 28px;
    font-weight: 700;
    color: var(--primary-color);
}}

.stat-label {{
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
}}

/* ═══════════════════════════════════════
   滚动条
   ═══════════════════════════════════════ */
::-webkit-scrollbar {{
    width: 6px;
}}

::-webkit-scrollbar-track {{
    background: var(--bg-dark);
}}

::-webkit-scrollbar-thumb {{
    background: var(--bg-light);
    border-radius: 3px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--primary-dark);
}}
'''

# 动画 CSS
ANIMATIONS_CSS_TEMPLATE = '''\
/* ═══════════════════════════════════════
   {game_title} - 动画效果
   ═══════════════════════════════════════ */

/* 标题发光动画 */
@keyframes titleGlow {{
    0%, 100% {{
        text-shadow: 0 0 20px var(--glow-color);
    }}
    50% {{
        text-shadow: 0 0 40px var(--glow-color), 0 0 60px var(--glow-color);
    }}
}}

/* 加载进度条动画 */
@keyframes loadingProgress {{
    0% {{ width: 0%; }}
    100% {{ width: 100%; }}
}}

/* 脉冲动画 */
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.7; transform: scale(1.02); }}
}}

/* 模态框滑入 */
@keyframes modalSlideIn {{
    from {{
        opacity: 0;
        transform: translateY(-30px) scale(0.95);
    }}
    to {{
        opacity: 1;
        transform: translateY(0) scale(1);
    }}
}}

/* 事件图标脉冲 */
@keyframes eventIconPulse {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.1); }}
}}

/* 淡入动画 */
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}

/* 从下滑入 */
@keyframes slideInUp {{
    from {{
        opacity: 0;
        transform: translateY(20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* 从上滑入 */
@keyframes slideInDown {{
    from {{
        opacity: 0;
        transform: translateY(-20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* 从左滑入 */
@keyframes slideInLeft {{
    from {{
        opacity: 0;
        transform: translateX(-20px);
    }}
    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

/* 从右滑入 */
@keyframes slideInRight {{
    from {{
        opacity: 0;
        transform: translateX(20px);
    }}
    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

/* 缩放弹出 */
@keyframes scaleIn {{
    from {{
        opacity: 0;
        transform: scale(0.8);
    }}
    to {{
        opacity: 1;
        transform: scale(1);
    }}
}}

/* 抖动效果 */
@keyframes shake {{
    0%, 100% {{ transform: translateX(0); }}
    10%, 30%, 50%, 70%, 90% {{ transform: translateX(-5px); }}
    20%, 40%, 60%, 80% {{ transform: translateX(5px); }}
}}

/* 闪烁效果 */
@keyframes blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

/* 旋转效果 */
@keyframes spin {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}

/* 浮动效果 */
@keyframes float {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-10px); }}
}}

/* 心跳效果 */
@keyframes heartbeat {{
    0%, 100% {{ transform: scale(1); }}
    14% {{ transform: scale(1.1); }}
    28% {{ transform: scale(1); }}
    42% {{ transform: scale(1.1); }}
    70% {{ transform: scale(1); }}
}}

/* 波纹效果 */
@keyframes ripple {{
    0% {{
        transform: scale(0);
        opacity: 1;
    }}
    100% {{
        transform: scale(2);
        opacity: 0;
    }}
}}

/* 数值变化动画 */
@keyframes numberChange {{
    0% {{
        transform: scale(1.2);
        color: var(--accent-color);
    }}
    100% {{
        transform: scale(1);
        color: inherit;
    }}
}}

/* 进度条填充 */
@keyframes progressFill {{
    from {{ width: 0%; }}
    to {{ width: var(--progress-value); }}
}}

/* 警告脉冲 */
@keyframes warningPulse {{
    0%, 100% {{
        box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4);
    }}
    50% {{
        box-shadow: 0 0 0 10px rgba(231, 76, 60, 0);
    }}
}}

/* 成功闪烁 */
@keyframes successFlash {{
    0% {{ background-color: rgba(46, 204, 113, 0.3); }}
    100% {{ background-color: transparent; }}
}}

/* 粒子漂浮 */
@keyframes particleFloat {{
    0% {{
        transform: translateY(100vh) rotate(0deg);
        opacity: 0;
    }}
    10% {{
        opacity: 1;
    }}
    90% {{
        opacity: 1;
    }}
    100% {{
        transform: translateY(-10vh) rotate(720deg);
        opacity: 0;
    }}
}}

/* 光晕效果 */
@keyframes glow {{
    0%, 100% {{
        box-shadow: 0 0 5px var(--glow-color), 0 0 10px var(--glow-color);
    }}
    50% {{
        box-shadow: 0 0 20px var(--glow-color), 0 0 30px var(--glow-color);
    }}
}}

/* 打字机效果 */
@keyframes typing {{
    from {{ width: 0; }}
    to {{ width: 100%; }}
}}

/* 光标闪烁 */
@keyframes cursorBlink {{
    0%, 100% {{ border-color: transparent; }}
    50% {{ border-color: var(--text-primary); }}
}}

/* ═══════════════════════════════════════
   动画工具类
   ═══════════════════════════════════════ */

.animate-fade-in {{
    animation: fadeIn 0.5s ease forwards;
}}

.animate-slide-up {{
    animation: slideInUp 0.5s ease forwards;
}}

.animate-slide-down {{
    animation: slideInDown 0.5s ease forwards;
}}

.animate-slide-left {{
    animation: slideInLeft 0.5s ease forwards;
}}

.animate-slide-right {{
    animation: slideInRight 0.5s ease forwards;
}}

.animate-scale-in {{
    animation: scaleIn 0.3s ease forwards;
}}

.animate-shake {{
    animation: shake 0.5s ease;
}}

.animate-blink {{
    animation: blink 1s ease-in-out infinite;
}}

.animate-spin {{
    animation: spin 1s linear infinite;
}}

.animate-float {{
    animation: float 3s ease-in-out infinite;
}}

.animate-heartbeat {{
    animation: heartbeat 1.5s ease-in-out infinite;
}}

.animate-glow {{
    animation: glow 2s ease-in-out infinite;
}}

.animate-pulse {{
    animation: pulse 2s ease-in-out infinite;
}}

/* 延迟类 */
.delay-100 {{ animation-delay: 0.1s; }}
.delay-200 {{ animation-delay: 0.2s; }}
.delay-300 {{ animation-delay: 0.3s; }}
.delay-400 {{ animation-delay: 0.4s; }}
.delay-500 {{ animation-delay: 0.5s; }}

/* 时长类 */
.duration-fast {{ animation-duration: 0.2s; }}
.duration-normal {{ animation-duration: 0.5s; }}
.duration-slow {{ animation-duration: 1s; }}

/* 悬停效果 */
.hover-lift {{
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.hover-lift:hover {{
    transform: translateY(-4px);
    box-shadow: 0 10px 20px var(--shadow-color);
}}

.hover-glow {{
    transition: box-shadow 0.3s ease;
}}

.hover-glow:hover {{
    box-shadow: 0 0 20px var(--glow-color);
}}

.hover-scale {{
    transition: transform 0.2s ease;
}}

.hover-scale:hover {{
    transform: scale(1.05);
}}

/* 按钮点击波纹效果 */
.btn-ripple {{
    position: relative;
    overflow: hidden;
}}

.btn-ripple::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.3s ease, height 0.3s ease;
}}

.btn-ripple:active::after {{
    width: 200%;
    height: 200%;
}}

/* 数值变化效果 */
.value-changed {{
    animation: numberChange 0.3s ease;
}}

.value-increased {{
    color: var(--success-color) !important;
}}

.value-decreased {{
    color: var(--danger-color) !important;
}}

/* 粒子效果容器 */
.particles-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    overflow: hidden;
}}

.particle {{
    position: absolute;
    width: 10px;
    height: 10px;
    background: var(--primary-color);
    border-radius: 50%;
    animation: particleFloat 10s linear infinite;
}}
'''

# 主 JS 模板
MAIN_JS_TEMPLATE = '''\
/**
 * {game_title} - 主入口
 * ═══════════════════════════════════════
 */

// 游戏主对象
const Game = {{
    // 游戏状态
    state: null,
    
    // 是否暂停
    isPaused: false,
    
    // 当前屏幕
    currentScreen: 'loading-screen',
    
    /**
     * 初始化游戏
     */
    init() {{
        console.log('🎮 {game_title} 初始化中...');
        
        // 初始化游戏状态
        this.state = new GameState();
        
        // 初始化 UI
        UI.init();
        
        // 初始化事件系统
        Events.init();
        
        // 模拟加载过程
        this.simulateLoading();
    }},
    
    /**
     * 模拟加载过程
     */
    simulateLoading() {{
        const loadingBar = document.querySelector('.loading-progress');
        const loadingText = document.querySelector('.loading-text');
        
        const steps = [
            {{ progress: 20, text: '加载游戏资源...' }},
            {{ progress: 40, text: '初始化游戏系统...' }},
            {{ progress: 60, text: '准备游戏数据...' }},
            {{ progress: 80, text: '加载界面组件...' }},
            {{ progress: 100, text: '准备就绪！' }},
        ];
        
        let stepIndex = 0;
        
        const loadStep = () => {{
            if (stepIndex >= steps.length) {{
                setTimeout(() => this.showScreen('main-menu'), 500);
                return;
            }}
            
            const step = steps[stepIndex];
            loadingBar.style.width = step.progress + '%';
            loadingText.textContent = step.text;
            stepIndex++;
            
            setTimeout(loadStep, 400);
        }};
        
        setTimeout(loadStep, 500);
    }},
    
    /**
     * 切换屏幕
     */
    showScreen(screenId) {{
        // 隐藏当前屏幕
        const currentEl = document.getElementById(this.currentScreen);
        if (currentEl) {{
            currentEl.classList.remove('active');
        }}
        
        // 显示新屏幕
        const newEl = document.getElementById(screenId);
        if (newEl) {{
            setTimeout(() => {{
                newEl.classList.add('active');
            }}, 100);
        }}
        
        this.currentScreen = screenId;
        
        // 如果是主菜单，初始化粒子效果
        if (screenId === 'main-menu') {{
            UI.initMenuParticles();
        }}
    }},
    
    /**
     * 开始新游戏
     */
    startNewGame() {{
        console.log('🎮 开始新游戏');
        
        // 重置游戏状态
        this.state.reset();
        this.isPaused = false;
        
        // 切换到游戏屏幕
        this.showScreen('game-screen');
        
        // 初始化游戏 UI
        UI.updateAll();
        
        // 添加开局日志
        UI.addLog('游戏开始！欢迎来到 {game_title}', 'success');
        UI.addLog('提示：合理分配资源，保持稳定发展');
    }},
    
    /**
     * 下一回合
     */
    nextTurn() {{
        if (this.isPaused) return;
        
        console.log('⏭️ 执行回合 ' + this.state.turn);
        
        // 执行回合逻辑
        const result = this.state.processTurn();
        
        // 更新 UI
        UI.updateAll();
        
        // 触发随机事件
        if (Math.random() < 0.3) {{
            Events.triggerRandomEvent();
        }}
        
        // 检查游戏结束条件
        this.checkGameOver();
    }},
    
    /**
     * 检查游戏结束
     */
    checkGameOver() {{
        const result = this.state.checkEndCondition();
        
        if (result.ended) {{
            this.endGame(result.victory, result.message);
        }}
    }},
    
    /**
     * 结束游戏
     */
    endGame(victory, message) {{
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
                <div class="stat-value">${{value}}</div>
                <div class="stat-label">${{key}}</div>
            </div>
        `).join('');
        
        this.showScreen('game-over');
    }},
    
    /**
     * 重新开始
     */
    restart() {{
        this.startNewGame();
    }},
    
    /**
     * 返回主菜单
     */
    backToMenu() {{
        this.showScreen('main-menu');
    }},
    
    /**
     * 切换暂停
     */
    togglePause() {{
        this.isPaused = !this.isPaused;
        const icon = document.getElementById('pause-icon');
        icon.textContent = this.isPaused ? '▶️' : '⏸️';
        
        UI.addLog(this.isPaused ? '游戏已暂停' : '游戏继续', 'info');
    }},
    
    /**
     * 打开菜单
     */
    openMenu() {{
        // 暂停游戏并显示菜单选项
        this.isPaused = true;
        this.showSettings();
    }},
    
    /**
     * 显示设置
     */
    showSettings() {{
        this.showModal('settings-modal');
    }},
    
    /**
     * 显示帮助
     */
    showHelp() {{
        this.showModal('help-modal');
    }},
    
    /**
     * 显示模态框
     */
    showModal(modalId) {{
        const modal = document.getElementById(modalId);
        if (modal) {{
            modal.classList.add('active');
        }}
    }},
    
    /**
     * 关闭模态框
     */
    closeModal(modalId) {{
        const modal = document.getElementById(modalId);
        if (modal) {{
            modal.classList.remove('active');
        }}
    }},
}};

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', () => {{
    Game.init();
}});
'''

# 游戏状态 JS
GAME_STATE_JS_TEMPLATE = '''\
/**
 * {game_title} - 游戏状态管理
 * ═══════════════════════════════════════
 */

class GameState {{
    constructor() {{
        this.reset();
    }}
    
    /**
     * 重置游戏状态
     */
    reset() {{
        // 回合数
        this.turn = 1;
        
        // 资源
        this.resources = {{}};
        for (const res of GameData.resources) {{
            this.resources[res.id] = {{
                current: res.initial,
                max: res.max || Infinity,
                perTurn: res.perTurn || 0,
            }};
        }}
        
        // 建筑
        this.buildings = [];
        
        // 人口/单位
        this.population = {{
            total: GameData.initialPopulation || 10,
            available: GameData.initialPopulation || 10,
            assigned: {{}},
        }};
        
        // 已触发的事件
        this.triggeredEvents = [];
        
        // 成就/里程碑
        this.achievements = [];
        
        // 游戏统计
        this.stats = {{
            totalTurns: 0,
            resourcesGained: {{}},
            resourcesSpent: {{}},
            eventsTriggered: 0,
            buildingsBuilt: 0,
        }};
    }}
    
    /**
     * 处理一个回合
     */
    processTurn() {{
        const results = {{
            resourceChanges: {{}},
            events: [],
            messages: [],
        }};
        
        // 1. 计算资源产出
        for (const [resId, res] of Object.entries(this.resources)) {{
            const change = this.calculateResourceChange(resId);
            results.resourceChanges[resId] = change;
            
            const newValue = Math.max(0, Math.min(res.max, res.current + change));
            res.current = newValue;
            
            // 记录统计
            if (change > 0) {{
                this.stats.resourcesGained[resId] = (this.stats.resourcesGained[resId] || 0) + change;
            }} else if (change < 0) {{
                this.stats.resourcesSpent[resId] = (this.stats.resourcesSpent[resId] || 0) + Math.abs(change);
            }}
        }}
        
        // 2. 处理建筑效果
        for (const building of this.buildings) {{
            this.processBuildingEffect(building, results);
        }}
        
        // 3. 更新人口
        this.updatePopulation();
        
        // 4. 增加回合数
        this.turn++;
        this.stats.totalTurns++;
        
        return results;
    }}
    
    /**
     * 计算资源变化
     */
    calculateResourceChange(resourceId) {{
        let change = this.resources[resourceId].perTurn || 0;
        
        // 建筑产出
        for (const building of this.buildings) {{
            const buildingData = GameData.buildings.find(b => b.id === building.type);
            if (buildingData && buildingData.produces && buildingData.produces[resourceId]) {{
                change += buildingData.produces[resourceId] * (building.level || 1);
            }}
            if (buildingData && buildingData.consumes && buildingData.consumes[resourceId]) {{
                change -= buildingData.consumes[resourceId] * (building.level || 1);
            }}
        }}
        
        // 人口消耗
        const resData = GameData.resources.find(r => r.id === resourceId);
        if (resData && resData.consumedPerPopulation) {{
            change -= resData.consumedPerPopulation * this.population.total;
        }}
        
        return change;
    }}
    
    /**
     * 处理建筑效果
     */
    processBuildingEffect(building, results) {{
        // 可以在这里添加建筑特殊效果
    }}
    
    /**
     * 更新人口
     */
    updatePopulation() {{
        // 简单的人口增长逻辑
        // 可以根据游戏设计调整
    }}
    
    /**
     * 建造建筑
     */
    build(buildingId) {{
        const buildingData = GameData.buildings.find(b => b.id === buildingId);
        if (!buildingData) return {{ success: false, message: '建筑不存在' }};
        
        // 检查资源
        for (const [resId, amount] of Object.entries(buildingData.cost || {{}})) {{
            if (!this.resources[resId] || this.resources[resId].current < amount) {{
                return {{ success: false, message: '资源不足' }};
            }}
        }}
        
        // 扣除资源
        for (const [resId, amount] of Object.entries(buildingData.cost || {{}})) {{
            this.resources[resId].current -= amount;
        }}
        
        // 添加建筑
        this.buildings.push({{
            type: buildingId,
            level: 1,
            builtAt: this.turn,
        }});
        
        this.stats.buildingsBuilt++;
        
        return {{ success: true, message: `成功建造 ${{buildingData.name}}` }};
    }}
    
    /**
     * 检查游戏结束条件
     */
    checkEndCondition() {{
        // 检查失败条件
        for (const res of GameData.resources) {{
            if (res.failIfZero && this.resources[res.id].current <= 0) {{
                return {{
                    ended: true,
                    victory: false,
                    message: `${{res.name}}耗尽，游戏失败！`,
                }};
            }}
        }}
        
        // 检查胜利条件
        if (GameData.victoryCondition) {{
            const victory = GameData.victoryCondition(this);
            if (victory) {{
                return {{
                    ended: true,
                    victory: true,
                    message: '恭喜达成目标！',
                }};
            }}
        }}
        
        // 默认回合数胜利
        if (this.turn >= (GameData.maxTurns || 100)) {{
            return {{
                ended: true,
                victory: true,
                message: `成功存活了 ${{this.turn}} 回合！`,
            }};
        }}
        
        return {{ ended: false }};
    }}
    
    /**
     * 获取统计数据
     */
    getStats() {{
        return {{
            '总回合数': this.stats.totalTurns,
            '建筑数量': this.buildings.length,
            '触发事件': this.stats.eventsTriggered,
        }};
    }}
    
    /**
     * 应用事件效果
     */
    applyEventEffect(effect) {{
        if (effect.resources) {{
            for (const [resId, amount] of Object.entries(effect.resources)) {{
                if (this.resources[resId]) {{
                    this.resources[resId].current = Math.max(0, 
                        Math.min(this.resources[resId].max, this.resources[resId].current + amount)
                    );
                }}
            }}
        }}
        
        if (effect.population) {{
            this.population.total = Math.max(0, this.population.total + effect.population);
            this.population.available = Math.max(0, this.population.available + effect.population);
        }}
        
        this.stats.eventsTriggered++;
    }}
}}
'''

# UI JS 模板
UI_JS_TEMPLATE = '''\
/**
 * {game_title} - UI 管理
 * ═══════════════════════════════════════
 */

const UI = {{
    /**
     * 初始化 UI
     */
    init() {{
        this.initResourcePanel();
        this.initBuildMenu();
    }},
    
    /**
     * 初始化资源面板
     */
    initResourcePanel() {{
        const panel = document.getElementById('resource-panel');
        panel.innerHTML = GameData.resources.map(res => `
            <div class="resource-item" id="resource-${{res.id}}">
                <span class="resource-icon">${{res.icon}}</span>
                <div class="resource-info">
                    <span class="resource-name">${{res.name}}</span>
                    <span class="resource-value" id="res-value-${{res.id}}">0</span>
                    <span class="resource-change" id="res-change-${{res.id}}"></span>
                </div>
            </div>
        `).join('');
    }},
    
    /**
     * 初始化建造菜单
     */
    initBuildMenu() {{
        const menu = document.getElementById('build-menu');
        menu.innerHTML = GameData.buildings.map(building => `
            <div class="build-item hover-lift" onclick="UI.showBuildingInfo('${{building.id}}')">
                <span class="build-icon">${{building.icon}}</span>
                <div class="build-info">
                    <span class="build-name">${{building.name}}</span>
                    <span class="build-cost">${{this.formatCost(building.cost)}}</span>
                </div>
                <button class="build-btn btn-ripple" onclick="event.stopPropagation(); UI.build('${{building.id}}')">建造</button>
            </div>
        `).join('');
    }},
    
    /**
     * 更新所有 UI
     */
    updateAll() {{
        this.updateResources();
        this.updateTurn();
        this.updateStatusOverview();
        this.updateGameViewport();
    }},
    
    /**
     * 更新资源显示
     */
    updateResources() {{
        const state = Game.state;
        
        for (const res of GameData.resources) {{
            const valueEl = document.getElementById(`res-value-${{res.id}}`);
            const changeEl = document.getElementById(`res-change-${{res.id}}`);
            const itemEl = document.getElementById(`resource-${{res.id}}`);
            
            if (!valueEl) continue;
            
            const current = Math.floor(state.resources[res.id].current);
            const change = state.calculateResourceChange(res.id);
            
            // 更新数值（带动画）
            const oldValue = parseInt(valueEl.textContent) || 0;
            if (current !== oldValue) {{
                valueEl.classList.add('value-changed');
                if (current > oldValue) {{
                    valueEl.classList.add('value-increased');
                }} else {{
                    valueEl.classList.add('value-decreased');
                }}
                setTimeout(() => {{
                    valueEl.classList.remove('value-changed', 'value-increased', 'value-decreased');
                }}, 300);
            }}
            
            valueEl.textContent = current;
            
            // 更新变化
            if (change !== 0) {{
                changeEl.textContent = (change > 0 ? '+' : '') + change + '/回合';
                changeEl.className = 'resource-change ' + (change > 0 ? 'positive' : 'negative');
            }} else {{
                changeEl.textContent = '';
            }}
            
            // 低资源警告
            if (res.warningThreshold && current <= res.warningThreshold) {{
                valueEl.classList.add('low');
            }} else {{
                valueEl.classList.remove('low');
            }}
        }}
    }},
    
    /**
     * 更新回合显示
     */
    updateTurn() {{
        document.getElementById('game-time').textContent = `回合 ${{Game.state.turn}}`;
    }},
    
    /**
     * 更新状态总览
     */
    updateStatusOverview() {{
        const state = Game.state;
        const overview = document.getElementById('status-overview');
        
        overview.innerHTML = `
            <div class="status-item">
                <span>👥 人口</span>
                <span>${{state.population.total}}</span>
            </div>
            <div class="status-item">
                <span>🏠 建筑</span>
                <span>${{state.buildings.length}}</span>
            </div>
        `;
    }},
    
    /**
     * 更新游戏主视图
     */
    updateGameViewport() {{
        const viewport = document.getElementById('game-viewport');
        const state = Game.state;
        
        // 显示建筑
        let buildingsHtml = state.buildings.map((b, i) => {{
            const data = GameData.buildings.find(bd => bd.id === b.type);
            return `
                <div class="building-card animate-scale-in" style="animation-delay: ${{i * 0.1}}s">
                    <span class="building-icon">${{data?.icon || '🏢'}}</span>
                    <span class="building-name">${{data?.name || b.type}}</span>
                    <span class="building-level">Lv.${{b.level}}</span>
                </div>
            `;
        }}).join('');
        
        if (!buildingsHtml) {{
            buildingsHtml = '<div class="empty-state">暂无建筑，从右侧菜单开始建造</div>';
        }}
        
        viewport.innerHTML = `<div class="buildings-grid">${{buildingsHtml}}</div>`;
    }},
    
    /**
     * 建造建筑
     */
    build(buildingId) {{
        const result = Game.state.build(buildingId);
        
        if (result.success) {{
            this.addLog(result.message, 'success');
            this.updateAll();
        }} else {{
            this.addLog(result.message, 'warning');
            // 添加抖动效果
            const menu = document.getElementById('build-menu');
            menu.classList.add('animate-shake');
            setTimeout(() => menu.classList.remove('animate-shake'), 500);
        }}
    }},
    
    /**
     * 显示建筑信息
     */
    showBuildingInfo(buildingId) {{
        const building = GameData.buildings.find(b => b.id === buildingId);
        if (!building) return;
        
        this.addLog(`${{building.name}}: ${{building.description || '暂无描述'}}`, 'info');
    }},
    
    /**
     * 格式化花费
     */
    formatCost(cost) {{
        if (!cost) return '免费';
        return Object.entries(cost).map(([resId, amount]) => {{
            const res = GameData.resources.find(r => r.id === resId);
            return `${{res?.icon || '💰'}}${{amount}}`;
        }}).join(' ');
    }},
    
    /**
     * 添加日志
     */
    addLog(message, type = 'info') {{
        const logContainer = document.getElementById('game-log');
        const time = new Date().toLocaleTimeString('zh-CN', {{ hour: '2-digit', minute: '2-digit' }});
        
        const entry = document.createElement('div');
        entry.className = 'log-entry animate-slide-up';
        entry.innerHTML = `
            <span class="log-time">${{time}}</span>
            <span class="log-message ${{type}}">${{message}}</span>
        `;
        
        logContainer.insertBefore(entry, logContainer.firstChild);
        
        // 限制日志数量
        while (logContainer.children.length > 50) {{
            logContainer.removeChild(logContainer.lastChild);
        }}
    }},
    
    /**
     * 初始化菜单粒子效果
     */
    initMenuParticles() {{
        const container = document.getElementById('menu-particles');
        if (!container) return;
        
        container.innerHTML = '';
        
        for (let i = 0; i < 20; i++) {{
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (10 + Math.random() * 10) + 's';
            particle.style.opacity = 0.1 + Math.random() * 0.3;
            particle.style.width = (5 + Math.random() * 10) + 'px';
            particle.style.height = particle.style.width;
            container.appendChild(particle);
        }}
    }},
}};
'''

# 事件系统 JS
EVENTS_JS_TEMPLATE = '''\
/**
 * {game_title} - 事件系统
 * ═══════════════════════════════════════
 */

const Events = {{
    /**
     * 初始化事件系统
     */
    init() {{
        // 绑定模态框关闭事件
        document.querySelectorAll('.modal').forEach(modal => {{
            modal.addEventListener('click', (e) => {{
                if (e.target === modal) {{
                    modal.classList.remove('active');
                }}
            }});
        }});
    }},
    
    /**
     * 触发随机事件
     */
    triggerRandomEvent() {{
        const eligibleEvents = GameData.events.filter(event => {{
            // 检查触发条件
            if (event.minTurn && Game.state.turn < event.minTurn) return false;
            if (event.maxTurn && Game.state.turn > event.maxTurn) return false;
            if (event.condition && !event.condition(Game.state)) return false;
            
            // 检查是否已触发过（一次性事件）
            if (event.once && Game.state.triggeredEvents.includes(event.id)) return false;
            
            return true;
        }});
        
        if (eligibleEvents.length === 0) return;
        
        // 根据权重随机选择
        const totalWeight = eligibleEvents.reduce((sum, e) => sum + (e.weight || 1), 0);
        let random = Math.random() * totalWeight;
        
        let selectedEvent = eligibleEvents[0];
        for (const event of eligibleEvents) {{
            random -= (event.weight || 1);
            if (random <= 0) {{
                selectedEvent = event;
                break;
            }}
        }}
        
        this.showEvent(selectedEvent);
    }},
    
    /**
     * 显示事件
     */
    showEvent(event) {{
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
            <button class="event-choice btn-ripple" onclick="Events.selectChoice(${{index}}, '${{event.id}}')">
                ${{choice.text}}
                <span class="choice-effect">${{this.formatEffect(choice.effect)}}</span>
            </button>
        `).join('');
        
        modal.classList.add('active');
        
        // 记录已触发
        if (event.once) {{
            Game.state.triggeredEvents.push(event.id);
        }}
        
        UI.addLog(`📢 事件：${{event.title}}`, 'warning');
    }},
    
    /**
     * 选择事件选项
     */
    selectChoice(choiceIndex, eventId) {{
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
        UI.addLog(`选择了：${{choice.text}}`, 'info');
        
        if (choice.effect.message) {{
            UI.addLog(choice.effect.message, choice.effect.messageType || 'info');
        }}
    }},
    
    /**
     * 格式化效果显示
     */
    formatEffect(effect) {{
        const parts = [];
        
        if (effect.resources) {{
            for (const [resId, amount] of Object.entries(effect.resources)) {{
                const res = GameData.resources.find(r => r.id === resId);
                const prefix = amount > 0 ? '+' : '';
                parts.push(`${{res?.icon || '💰'}}${{prefix}}${{amount}}`);
            }}
        }}
        
        if (effect.population) {{
            const prefix = effect.population > 0 ? '+' : '';
            parts.push(`👥${{prefix}}${{effect.population}}`);
        }}
        
        return parts.join(' ') || '无直接效果';
    }},
}};
'''

# 工具函数 JS
UTILS_JS_TEMPLATE = '''\
/**
 * {game_title} - 工具函数
 * ═══════════════════════════════════════
 */

/**
 * 格式化数字
 */
function formatNumber(num) {{
    if (num >= 1000000) {{
        return (num / 1000000).toFixed(1) + 'M';
    }}
    if (num >= 1000) {{
        return (num / 1000).toFixed(1) + 'K';
    }}
    return Math.floor(num).toString();
}}

/**
 * 随机整数
 */
function randomInt(min, max) {{
    return Math.floor(Math.random() * (max - min + 1)) + min;
}}

/**
 * 随机选择
 */
function randomChoice(array) {{
    return array[Math.floor(Math.random() * array.length)];
}}

/**
 * 延迟执行
 */
function delay(ms) {{
    return new Promise(resolve => setTimeout(resolve, ms));
}}

/**
 * 深拷贝
 */
function deepClone(obj) {{
    return JSON.parse(JSON.stringify(obj));
}}

/**
 * 限制数值范围
 */
function clamp(value, min, max) {{
    return Math.min(Math.max(value, min), max);
}}

/**
 * 线性插值
 */
function lerp(start, end, t) {{
    return start + (end - start) * t;
}}
'''

# 游戏数据模板
DATA_JS_TEMPLATE = '''\
/**
 * {game_title} - 游戏数据定义
 * ═══════════════════════════════════════
 */

const GameData = {{
    // 游戏名称
    name: '{game_title}',
    
    // 游戏描述
    description: '{game_description}',
    
    // 最大回合数
    maxTurns: 100,
    
    // 初始人口
    initialPopulation: 10,
    
    // 资源定义
    resources: [
        {{
            id: 'energy',
            name: '能源',
            icon: '⚡',
            initial: 100,
            max: 500,
            perTurn: 5,
            warningThreshold: 20,
            failIfZero: true,
        }},
        {{
            id: 'materials',
            name: '材料',
            icon: '🔩',
            initial: 50,
            max: 300,
            perTurn: 2,
            warningThreshold: 10,
        }},
        {{
            id: 'food',
            name: '食物',
            icon: '🍞',
            initial: 80,
            max: 200,
            perTurn: 3,
            consumedPerPopulation: 0.5,
            warningThreshold: 20,
            failIfZero: true,
        }},
        {{
            id: 'credits',
            name: '资金',
            icon: '💰',
            initial: 200,
            max: 10000,
            perTurn: 10,
        }},
    ],
    
    // 建筑定义
    buildings: [
        {{
            id: 'generator',
            name: '发电站',
            icon: '🏭',
            description: '提供稳定的能源供应',
            cost: {{ materials: 30, credits: 50 }},
            produces: {{ energy: 10 }},
        }},
        {{
            id: 'mine',
            name: '采矿场',
            icon: '⛏️',
            description: '开采材料资源',
            cost: {{ energy: 20, credits: 40 }},
            produces: {{ materials: 5 }},
        }},
        {{
            id: 'farm',
            name: '农场',
            icon: '🌾',
            description: '生产食物',
            cost: {{ materials: 25, credits: 30 }},
            produces: {{ food: 8 }},
        }},
        {{
            id: 'housing',
            name: '居住区',
            icon: '🏠',
            description: '增加人口上限',
            cost: {{ materials: 50, energy: 30, credits: 100 }},
        }},
        {{
            id: 'market',
            name: '贸易站',
            icon: '🏪',
            description: '增加资金收入',
            cost: {{ materials: 40, energy: 20, credits: 80 }},
            produces: {{ credits: 15 }},
        }},
    ],
    
    // 事件定义
    events: [
        {{
            id: 'power_surge',
            title: '能源波动',
            description: '检测到能源网络不稳定，需要紧急处理。',
            icon: '⚡',
            weight: 2,
            choices: [
                {{
                    text: '紧急维修',
                    effect: {{
                        resources: {{ energy: -20, credits: -30 }},
                        message: '成功稳定了能源网络',
                        messageType: 'success',
                    }},
                }},
                {{
                    text: '暂时忽略',
                    effect: {{
                        resources: {{ energy: -50 }},
                        message: '能源损失严重！',
                        messageType: 'danger',
                    }},
                }},
            ],
        }},
        {{
            id: 'trade_opportunity',
            title: '贸易机会',
            description: '一支商队路过，愿意进行交易。',
            icon: '🤝',
            weight: 2,
            choices: [
                {{
                    text: '购买物资',
                    effect: {{
                        resources: {{ credits: -100, materials: 30, food: 20 }},
                        message: '获得了宝贵的物资',
                        messageType: 'success',
                    }},
                }},
                {{
                    text: '出售能源',
                    effect: {{
                        resources: {{ energy: -50, credits: 80 }},
                        message: '获得了一笔资金',
                        messageType: 'info',
                    }},
                }},
                {{
                    text: '礼貌拒绝',
                    effect: {{
                        message: '商队继续前行了',
                    }},
                }},
            ],
        }},
        {{
            id: 'natural_disaster',
            title: '自然灾害',
            description: '一场风暴正在逼近，可能造成破坏。',
            icon: '🌪️',
            weight: 1,
            minTurn: 5,
            choices: [
                {{
                    text: '加固防御',
                    effect: {{
                        resources: {{ materials: -40, energy: -20 }},
                        message: '成功抵御了风暴',
                        messageType: 'success',
                    }},
                }},
                {{
                    text: '冒险继续',
                    effect: {{
                        resources: {{ materials: -60, food: -30 }},
                        message: '风暴造成了较大损失',
                        messageType: 'danger',
                    }},
                }},
            ],
        }},
        {{
            id: 'discovery',
            title: '意外发现',
            description: '探索队在附近发现了一处资源矿脉！',
            icon: '🎉',
            weight: 1,
            minTurn: 10,
            once: true,
            choices: [
                {{
                    text: '立即开采',
                    effect: {{
                        resources: {{ materials: 100, energy: -30 }},
                        message: '获得了大量材料！',
                        messageType: 'success',
                    }},
                }},
                {{
                    text: '标记位置，稍后开采',
                    effect: {{
                        resources: {{ materials: 30 }},
                        message: '记录了矿脉位置',
                    }},
                }},
            ],
        }},
    ],
    
    // 胜利条件（可选）
    victoryCondition: (state) => {{
        // 例如：累计资金达到 5000
        return state.resources.credits.current >= 5000;
    }},
}};
'''

# 配色方案
COLOR_SCHEMES = {
    '赛博朋克': {
        'primary_color': '#00f0ff',
        'primary_light': '#4df7ff',
        'primary_dark': '#00a8b3',
        'secondary_color': '#ff00ff',
        'accent_color': '#ffff00',
        'bg_dark': '#0a0a0f',
        'bg_medium': '#12121a',
        'bg_light': '#1a1a2e',
        'text_primary': '#e0e0ff',
        'text_secondary': '#a0a0c0',
        'text_muted': '#606080',
        'glow_color': 'rgba(0, 240, 255, 0.4)',
    },
    '太空科幻': {
        'primary_color': '#4da6ff',
        'primary_light': '#80c1ff',
        'primary_dark': '#2979ff',
        'secondary_color': '#7c4dff',
        'accent_color': '#00e5ff',
        'bg_dark': '#050510',
        'bg_medium': '#0d1025',
        'bg_light': '#151a35',
        'text_primary': '#e8eaf6',
        'text_secondary': '#9fa8da',
        'text_muted': '#5c6bc0',
        'glow_color': 'rgba(77, 166, 255, 0.4)',
    },
    '复古像素': {
        'primary_color': '#4caf50',
        'primary_light': '#81c784',
        'primary_dark': '#388e3c',
        'secondary_color': '#ff9800',
        'accent_color': '#ffeb3b',
        'bg_dark': '#1a1a2e',
        'bg_medium': '#252545',
        'bg_light': '#2f2f5a',
        'text_primary': '#e8e8e8',
        'text_secondary': '#b8b8b8',
        'text_muted': '#888888',
        'glow_color': 'rgba(76, 175, 80, 0.4)',
    },
    '水墨中国风': {
        'primary_color': '#c9a06c',
        'primary_light': '#dbb896',
        'primary_dark': '#9a7b50',
        'secondary_color': '#8b4513',
        'accent_color': '#dc143c',
        'bg_dark': '#1a1810',
        'bg_medium': '#2a2820',
        'bg_light': '#3a3830',
        'text_primary': '#f5f5dc',
        'text_secondary': '#d4c4a8',
        'text_muted': '#a09080',
        'glow_color': 'rgba(201, 160, 108, 0.3)',
    },
    '现代简约': {
        'primary_color': '#2196f3',
        'primary_light': '#64b5f6',
        'primary_dark': '#1976d2',
        'secondary_color': '#00bcd4',
        'accent_color': '#ff4081',
        'bg_dark': '#121212',
        'bg_medium': '#1e1e1e',
        'bg_light': '#2d2d2d',
        'text_primary': '#ffffff',
        'text_secondary': '#b3b3b3',
        'text_muted': '#757575',
        'glow_color': 'rgba(33, 150, 243, 0.3)',
    },
}

def get_color_scheme(visual_style):
    """根据视觉风格获取配色方案"""
    visual_lower = visual_style.lower()
    
    if '赛博' in visual_lower or 'cyber' in visual_lower:
        return COLOR_SCHEMES['赛博朋克']
    elif '太空' in visual_lower or '科幻' in visual_lower or 'space' in visual_lower:
        return COLOR_SCHEMES['太空科幻']
    elif '像素' in visual_lower or 'pixel' in visual_lower or '复古' in visual_lower:
        return COLOR_SCHEMES['复古像素']
    elif '水墨' in visual_lower or '中国' in visual_lower or '国风' in visual_lower:
        return COLOR_SCHEMES['水墨中国风']
    else:
        return COLOR_SCHEMES['现代简约']


# ═══════════════════════════════════════════════════
# P2: Code Skeleton Library
# Provides structural skeletons for each scaffolding type.
# These ensure architectural correctness - the LLM fills in
# the implementation details while the skeleton guarantees
# the right methods and interfaces exist.
# ═══════════════════════════════════════════════════

SKELETON_LIBRARY = {
    "entity_lifecycle": {
        "game-state.js": '''\
/**
 * {game_title} - Game State Management
 * Scaffolding: Entity Lifecycle
 * ═══════════════════════════════════════
 */

class GameState {{
  constructor() {{
    this.reset();
  }}

  /**
   * Reset all game state to initial values
   */
  reset() {{
    this.turn = 1;

    // Global resources (from GameData.resources)
    this.resources = {{}};
    for (const res of GameData.resources) {{
      this.resources[res.id] = {{
        current: res.initial,
        max: res.max || Infinity,
        perTurn: res.perTurn || 0,
      }};
    }}

    // Per-entity state tracking (CORE of entity lifecycle)
    this.entityStates = {{}};
    for (const entity of (GameData.entities || [])) {{
      if (!entity.unlock_turn || entity.unlock_turn <= 1) {{
        this._initEntity(entity);
      }}
    }}
    this.unlockedEntities = Object.keys(this.entityStates);

    // Built facilities
    this.facilities = [];

    // Interaction cooldowns
    this.cooldowns = {{}};

    // Adoption tracking
    this.adoptionHistory = [];
    this.pendingRevisits = [];

    // Events
    this.triggeredEvents = [];

    // Stats
    this.stats = {{
      totalTurns: 0,
      interactionsPerformed: 0,
      successfulInteractions: 0,
      adoptionsCompleted: 0,
      totalMatchScore: 0,
    }};
  }}

  _initEntity(entityDef) {{
    // AI FILL: Initialize per-entity state from entityDef.initial_state
  }}

  /**
   * Process one game turn
   * @returns {{resourceChanges, entityUpdates, messages, newEntities, revisits}}
   */
  processTurn() {{
    // AI FILL: Resource settlement, entity state decay/recovery,
    // unlock new entities, process cooldowns, check revisits
  }}

  /**
   * Process player interaction with a specific entity
   * @param {{string}} entityId
   * @param {{string}} interactionId
   * @returns {{success, interactionSucceeded, message, entityState}}
   */
  interact(entityId, interactionId) {{
    // AI FILL: Check cooldown, check min_trust, check resource cost,
    // calculate success rate (considering trauma_tags), apply effects
  }}

  /**
   * Calculate adoptability score for an entity
   * @param {{object}} entityState
   * @returns {{number}} 0-100
   */
  _calculateAdoptability(entityState) {{
    // AI FILL: Composite score from trust, stress, health
  }}

  /**
   * Calculate match score between entity and adopter family
   * @param {{string}} entityId
   * @param {{string}} familyId
   * @returns {{number}} 0-100
   */
  calculateMatchScore(entityId, familyId) {{
    // AI FILL: Species preference, trust threshold, stress threshold,
    // experience level bonus, patience bonus
  }}

  /**
   * Process adoption of an entity by a family
   * @param {{string}} entityId
   * @param {{string}} familyId
   * @returns {{success, matchScore, message, farewell}}
   */
  processAdoption(entityId, familyId) {{
    // AI FILL: Check adoptability, calculate match, update state,
    // record history, schedule revisit, generate farewell narrative
  }}

  /**
   * Build a facility
   * @param {{string}} facilityId
   * @returns {{success, message}}
   */
  buildFacility(facilityId) {{
    // AI FILL: Check cost, deduct resources, add facility
  }}

  /**
   * Check game end conditions
   * @returns {{ended, victory, message}}
   */
  checkEndCondition() {{
    // AI FILL: Check defeat conditions, victory conditions, turn limit
  }}

  /**
   * Apply event effect to game state
   * @param {{object}} effect
   */
  applyEventEffect(effect) {{
    // AI FILL: Apply resource changes, entity effects, all-entity effects
  }}

  /**
   * Get game statistics
   * @returns {{object}}
   */
  getStats() {{
    // AI FILL: Return formatted stats
  }}
}}
''',
        "ui.js": '''\
/**
 * {game_title} - UI Management
 * Scaffolding: Entity Lifecycle
 * ═══════════════════════════════════════
 */

const UI = {{
  selectedEntityId: null,

  init() {{
    this.initResourcePanel();
    this.initEntityGallery();
    this.initFacilityMenu();
    this.initInteractionPanel();
  }},

  // ── Resource Panel ──
  initResourcePanel() {{
    // AI FILL: Render resource items from GameData.resources
  }},

  // ── Entity Gallery (CORE UI for entity lifecycle) ──
  initEntityGallery() {{
    // AI FILL: Render entity cards with portrait, name, status bars
  }},

  updateEntityGallery() {{
    // AI FILL: Update entity cards with current state
  }},

  selectEntity(entityId) {{
    // AI FILL: Show entity detail card, update interaction panel
  }},

  // ── Entity Detail Card ──
  renderEntityDetail(entityId) {{
    // AI FILL: Show backstory, state bars (trust/stress/health/attachment),
    // adoptability indicator, interaction history
  }},

  // ── Interaction Panel ──
  initInteractionPanel() {{
    // AI FILL: Render available interactions for selected entity
  }},

  updateInteractionPanel(entityId) {{
    // AI FILL: Update button states based on cooldowns, trust requirements
  }},

  performInteraction(entityId, interactionId) {{
    // AI FILL: Call Game.state.interact(), show result, update UI
  }},

  // ── Facility Menu ──
  initFacilityMenu() {{
    // AI FILL: Render facility build options from GameData.facilities
  }},

  buildFacility(facilityId) {{
    // AI FILL: Call Game.state.buildFacility(), update UI
  }},

  // ── Matching Interface ──
  showMatchingPanel(entityId) {{
    // AI FILL: Show available families with match scores
  }},

  // ── Farewell Scene ──
  showFarewellScene(farewell) {{
    // AI FILL: Render emotional farewell narrative and photo
  }},

  // ── Revisit Album ──
  showRevisitAlbum(revisit) {{
    // AI FILL: Render post-adoption revisit photos and narrative
  }},

  // ── Common UI Methods ──
  updateAll() {{
    // AI FILL: Update resources, entity gallery, turn display
  }},

  updateResources() {{
    // AI FILL: Update resource values with animations
  }},

  updateTurn() {{
    // AI FILL: Update turn counter
  }},

  addLog(message, type) {{
    // AI FILL: Add log entry with timestamp
  }},

  initMenuParticles() {{
    // AI FILL: Create particle effects for main menu
  }},
}};
''',
    },

    "resource_management": {
        "game-state.js": '''\
/**
 * {game_title} - Game State Management
 * Scaffolding: Resource Management
 * ═══════════════════════════════════════
 */

class GameState {{
  constructor() {{
    this.reset();
  }}

  reset() {{
    this.turn = 1;
    this.resources = {{}};
    for (const res of GameData.resources) {{
      this.resources[res.id] = {{
        current: res.initial,
        max: res.max || Infinity,
        perTurn: res.perTurn || 0,
      }};
    }}
    this.buildings = [];
    this.triggeredEvents = [];
    this.stats = {{ totalTurns: 0, buildingsBuilt: 0, eventsTriggered: 0 }};
  }}

  processTurn() {{
    // AI FILL: Calculate resource changes from buildings, apply perTurn
  }}

  calculateResourceChange(resourceId) {{
    // AI FILL: Sum perTurn + building produces - building consumes
  }}

  build(buildingId) {{
    // AI FILL: Check cost, deduct resources, add building
  }}

  checkEndCondition() {{
    // AI FILL: Check failIfZero resources, victory condition, turn limit
  }}

  applyEventEffect(effect) {{
    // AI FILL: Apply resource changes, population changes
  }}

  getStats() {{
    // AI FILL: Return formatted stats
  }}
}}
''',
    },
}


def get_skeleton(scaffolding_type: str, module_name: str) -> str:
    """
    Get the code skeleton for a given scaffolding type and module.

    Args:
        scaffolding_type: e.g., "entity_lifecycle", "resource_management"
        module_name: e.g., "game-state.js", "ui.js"

    Returns:
        Skeleton code string, or empty string if no skeleton exists.
    """
    skeletons = SKELETON_LIBRARY.get(scaffolding_type, {})
    return skeletons.get(module_name, "")
