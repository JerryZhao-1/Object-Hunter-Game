import cv2
import os
import random

# Game basic settings
GAME_TITLE = "Object Hunter"
VERSION = "1.0.0"
DEFAULT_DIFFICULTY = "normal"
DEFAULT_PLAYER_NAME = "Player"
MAX_ROUNDS = 10
TIME_LIMITS = {
    "easy": 40,
    "normal": 30,
    "hard": 20
}

# Window settings
WINDOW_NAME = "Object Hunter"
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Game time settings
GAME_TIME_SECONDS = 120  # Game duration 2 minutes

# Difficulty settings
DIFFICULTY_LEVELS = {
    "Easy": 0.4,    # Minimum confidence for easy difficulty
    "Normal": 0.5,  # Minimum confidence for normal difficulty
    "Hard": 0.65    # Minimum confidence for hard difficulty
}

# Font settings
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = {
    "title": 2.0,
    "large": 1.2,
    "normal": 0.9,
    "small": 0.7
}
FONT_THICKNESS = {
    "title": 3,
    "normal": 2,
    "small": 1
}

# Font paths
FONT_PATHS = {
    "default": None,  # 使用默认字体
    "chinese": os.path.join("assets", "fonts", "simhei.ttf")  # 中文字体路径
}

# Color settings (BGR format)
COLORS = {
    "white": (255, 255, 255),
    "gray": (200, 200, 200),
    "yellow": (0, 230, 255),  # 调整为更明亮的黄色
    "red": (60, 76, 231),     # 改为更柔和的红色
    "green": (97, 222, 42),   # 调整为更生动的绿色
    "blue": (235, 151, 0),    # 调整为更温暖的蓝色
    "black": (0, 0, 0),
    
    # 更新背景颜色为渐变友好的颜色
    "bg_dark": (45, 45, 65),
    "bg_gradient_top": (65, 60, 100),  # 更鲜明的顶部渐变
    "bg_gradient_bottom": (30, 30, 50),  # 更深的底部渐变
    
    # 更现代化的面板颜色
    "panel": (60, 60, 95, 180),
    "panel_dark": (40, 40, 70, 200),
    
    # 更生动的按钮颜色
    "button_normal": (0, 195, 255),  # 更明亮的橙色
    "button_hover": (80, 220, 255),  # 更亮的高亮橙色
    "button_click": (50, 170, 240),  # 更深的点击橙色
    "button_disabled": (80, 80, 100),  # 禁用按钮
    "text_glow": (80, 220, 255),  # 文字发光效果
    "text_shadow": (0, 0, 0),     # 文字阴影
    "menu_bg": (20, 20, 35, 200),  # 菜单背景(半透明)
    "menu_highlight": (60, 60, 120, 230),  # 菜单高亮
    
    # 添加更多强调色
    "accent_1": (255, 120, 50),    # 热情的橙色
    "accent_2": (50, 200, 255),    # 清新的蓝色
    "accent_3": (130, 60, 240),    # 神秘的紫色
    "accent_4": (40, 210, 150),    # 薄荷绿
    
    # 添加主题色
    "theme_primary": (0, 180, 240),    # 主题主色
    "theme_secondary": (240, 100, 0),  # 主题辅色
    "theme_tertiary": (100, 220, 130), # 主题第三色
    
    # 已有颜色
    "bg_dark_gradient_top": (30, 30, 50),  # 深色渐变顶部
    "bg_dark_gradient_bottom": (15, 15, 25),  # 深色渐变底部
    "transparent_black": (0, 0, 0, 150),  # 半透明黑色
    "success": (0, 255, 127),     # 成功绿色
    "warning": (0, 165, 255),     # 警告橙色
    "danger": (0, 0, 255),        # 危险红色
    "error": (0, 0, 255),         # 错误红色
    "info": (255, 215, 0),        # 信息蓝色
    "progress_bg": (40, 40, 60),  # 进度条背景
    "progress_fill": (0, 180, 255)  # 进度条填充
}

# Object detection settings
DETECTION = {
    "confidence_threshold": 0.4,
    "cooldown": 0.5,
    "history_size": 3,
    "required_consecutive": 2
}

# Target objects
TARGET_OBJECTS = [
    'cup', 'bottle', 'book', 'cell phone', 'keyboard', 
    'mouse', 'chair', 'laptop', 'remote', 'backpack',
    'person', 'tv', 'scissors', 'clock'
]

# Object categories
OBJECTS = {
    "easy": [
        'book', 'cell phone', 'keyboard'
    ],
    "normal": [
        'cup', 'bottle', 'book', 'cell phone', 'chair', 
        'laptop', 'mouse', 'keyboard', 'remote', 'backpack'
    ],
    "hard": [
        'person', 'backpack', 'bottle', 'cup', 'keyboard', 
        'chair', 'tv', 'laptop', 'mouse', 'remote', 'cell phone', 
        'scissors', 'book', 'clock'
    ]
}

# File paths
PATHS = {
    "sounds": os.path.join("sounds", ""),
    "leaderboard": "leaderboard.json",
    "model": "yolo11x.pt",
    "assets": os.path.join("assets", "")
}

# Ensure file paths exist
for path in PATHS.values():
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception:
            pass

# Game states
STATES = [
    "menu",
    "game",
    "game_over"
]

# Menu settings
MENU = {
    "title": "Object Hunter",
    "version": "1.0.0",
    "options": [
        {
            "text": "Start Game",
            "action": "start",
            "position": (0, 0)  # Relative position
        },
        {
            "text": "Difficulty Settings",
            "action": "difficulty",
            "position": (0, 1)
        },
        {
            "text": "Exit Game",
            "action": "quit",
            "position": (0, 2)
        }
    ],
    "main_options": [
        {
            "text": "Start Game",
            "action": "start",
            "position": (0, 0)
        },
        {
            "text": "Difficulty Settings",
            "action": "difficulty",
            "position": (0, 1)
        },
        {
            "text": "Exit Game",
            "action": "quit",
            "position": (0, 2)
        }
    ],
    "difficulties": [
        {
            "text": "Easy",
            "value": "easy",
            "position": (0, 0)
        },
        {
            "text": "Normal",
            "value": "normal",
            "position": (0, 1)
        },
        {
            "text": "Hard",
            "value": "hard",
            "position": (0, 2)
        }
    ]
}

# Prompt templates (simplified to avoid encoding issues)
PROMPTS = {
    "basic": [
        "Find a {object} in {time} seconds!",
        "Show me a {object} quickly!",
        "Grab a {object} and point your camera at it!",
        "Hunt down a {object}, time is ticking!",
        "Can you find a {object}? Hurry up!"
    ],
    "fun": [
        "Scoop up a {object} before time runs out!",
        "Time to find a {object} now!",
        "Hunter, show me a {object} in {time} seconds!",
        "Quick, find a {object} now!",
        "Find and show me a {object}!"
    ],
    "dynamic": [
        "Almost there, tilt the camera to show the {object} clearly!",
        "I see something... is that a {object}? Keep it steady!",
        "Getting closer, make sure the {object} is in frame!",
        "Nice try, but that is not a {object}, keep hunting!",
        "Yes! You found it, {object} detected!"
    ],
    "themed": [
        "Search the room for a {object}!",
        "Use your camera to find a {object}!",
        "Scan the area for a {object}, explorer!",
        "Detective, uncover a {object} now!",
        "Time to hunt down a {object}!"
    ]
}

# Sound settings
SOUNDS = {
    "volume": 0.5,
    "button_click": "button_click.wav",
    "difficulty_change": "difficulty_change.wav",
    "game_start": "game_start.wav",
    "game_over": "game_over.wav",
    "correct": "correct.wav",
    "countdown": "countdown.wav",
    "level_up": "level_up.wav",         # 升级音效
    "achievement": "achievement.wav",   # 成就解锁音效
    "combo_increase": "combo_up.wav",   # 连击增加音效
    "combo_break": "combo_break.wav",   # 连击中断音效
    "challenge_complete": "challenge_complete.wav",  # 挑战完成音效
    "round_start": "round_start.wav",   # 回合开始音效
    "round_end": "round_end.wav",       # 回合结束音效
    "time_low": "time_low.wav",         # 时间不足警告
    "new_discovery": "discovery.wav"    # 新物品发现音效
}

# Animation settings
ANIMATION = {
    "button_click_duration": 0.2,          # 按钮点击动画持续时间
    "menu_transition_duration": 0.4,       # 菜单过渡动画持续时间
    "text_effect_duration": 0.7,           # 文本效果持续时间
    "particle_lifetime": 2.0,              # 粒子生命周期
    "loading_speed": 5,                    # 加载动画速度
    "pulse_speed": 2.5,                    # 脉动效果速度
    "celebration_duration": 2.0,           # 庆祝效果持续时间
    "bounce_height": 10,                   # 反弹高度
    "float_amount": 5,                     # 浮动量
    "shake_intensity": 3,                  # 抖动强度
    "fade_duration": 0.5,                  # 淡入淡出持续时间
    "expand_scale": 1.1,                   # 扩展比例
    "rotation_speed": 1,                   # 旋转速度
    "wave_amplitude": 10,                  # 波浪振幅
    "wave_frequency": 0.2,                 # 波浪频率
    "game_over_fade": 1.5,                 # 游戏结束淡出动画时间
    "result_fade_duration": 1.5,           # 结果淡入动画时间
    # 添加新动画效果
    "pop_scale": 1.15,                # 弹出动画缩放
    "pop_duration": 0.3,              # 弹出动画持续时间
    "wave_effect_speed": 0.8,         # 波浪效果速度
    "particle_count": 25,             # 粒子效果数量
    "particle_speed": 3.0,            # 粒子移动速度
    "particle_size_range": (3, 8),    # 粒子大小范围
    "transition_style": "fade",       # 过渡动画样式 (fade/slide/zoom)
    "confetti_on_success": True,      # 成功时显示彩色粒子
    "typing_effect_speed": 0.05       # 打字效果速度
}

# UI settings
UI = {
    "menu_spacing": 80,        # 增加菜单选项间距
    "button_width": 220,       # 按钮宽度
    "button_height": 60,       # 按钮高度
    "glow_radius": 7,          # 发光半径
    "shadow_offset": 3,        # 阴影偏移
    "corner_radius": 10,       # 圆角半径
    "menu_padding": 20,        # 菜单内边距
    "blur_amount": 21,         # 模糊效果强度
    "topbar_height": 70,       # 顶部栏高度
    "bottombar_height": 80,    # 底部栏高度
    "transition_time": 0.5,    # 过渡动画时间
}

def get_random_prompt(object_name, time_left, style="basic"):
    """Get a random prompt based on style"""
    if style not in PROMPTS:
        style = "basic"
    
    # Clean object name - ensure ASCII characters only
    clean_object = object_name.encode('ascii', 'replace').decode('ascii')
    
    # Get random template
    template = random.choice(PROMPTS[style])
    
    try:
        # Format with error handling
        return template.format(object=clean_object, time=int(time_left))
    except Exception as e:
        print(f"Error formatting prompt: {e}")
        return f"Find a {clean_object}!"  # Fallback prompt 