"""
Object Finder Game Main Module
"""
import cv2
import numpy as np
import random
import time
import os
import pygame
import math
from object_detector import ObjectDetector
from config import (
    WINDOW_NAME, CAMERA_WIDTH, CAMERA_HEIGHT, 
    TARGET_OBJECTS, GAME_TIME_SECONDS, DIFFICULTY_LEVELS,
    get_random_prompt, MENU, UI, COLORS,
    ANIMATION, SOUNDS, OBJECTS
)
from direct_camera import DirectCamera
from pygame_window import PygameWindow

class Game:
    """Game main class"""
    
    def __init__(self):
        """Initialize game"""
        # Initialize components
        self.detector = ObjectDetector()
        self.window = PygameWindow(WINDOW_NAME, CAMERA_WIDTH, CAMERA_HEIGHT)
        self.camera = None
        self.running = False
        
        # 初始化所有游戏变量
        self._initialize_game_variables()
        
        # Sound effects
        self.sounds = {}
        self._initialize_audio()
        self._load_sounds()
        
        print("Game object initialized")
    
    def _initialize_game_variables(self):
        """初始化所有游戏相关变量，确保它们都被正确设置"""
        # Game state
        self.difficulty = "normal"  # 默认难度
        self.difficulty_time = 45   # 默认时间(秒)
        self.score = 0
        self.current_target = None
        self.game_start_time = 0
        self.time_remaining = 0
        self.last_found_time = 0
        self.target_found = False
        self.target_found_time = 0
        self.game_started = False
        self.game_over = False
        self.game_end_time = 0
        self.auto_next_target_time = 0  # 自动切换目标的时间
        self.next_clicks_remaining = 3  # Hard模式下可用的Next点击次数
        self.found_targets = set()      # 记录已找到的目标，防止重复加分
        
        # 双击检测相关变量
        self.last_click_time = 0
        self.last_click_position = None
        self.last_click_element = None
        
        # Menu state
        self.current_menu = "main"  # main, difficulty, game
        self.selected_option = 0
        self.last_click = None
        self.transition_active = False
        self.transition_target = None
        self.transition_start_time = 0
        
        # Animation states
        self.button_hover = None
        self.button_click_animation = {}
        self.celebration_particles = []
        self.particle_lifetime = ANIMATION["particle_lifetime"]
        self.title_animation = 0.5   # 标题动画状态
        self.float_offset = 0      # 浮动偏移
        
        # 初始化按钮
        self.buttons = {
            "start": {
                "text": "Start",
                "coords": (CAMERA_WIDTH - 240, CAMERA_HEIGHT - 80, 
                          CAMERA_WIDTH - 20, CAMERA_HEIGHT - 20),
                "color": COLORS["button_normal"],
                "hover_color": COLORS["button_hover"],
                "active": True
            },
            "quit": {
                "text": "Quit",
                "coords": (20, CAMERA_HEIGHT - 80, 
                          240, CAMERA_HEIGHT - 20),
                "color": COLORS["button_normal"],
                "hover_color": COLORS["button_hover"],
                "active": True
            },
            "next": {
                "text": "Next",
                "coords": (CAMERA_WIDTH - 240, CAMERA_HEIGHT - 80, 
                          CAMERA_WIDTH - 20, CAMERA_HEIGHT - 20),
                "color": COLORS["button_normal"],
                "hover_color": COLORS["button_hover"],
                "active": True
            },
            "restart": {
                "text": "Restart",
                "coords": (CAMERA_WIDTH - 240, CAMERA_HEIGHT - 80, 
                          CAMERA_WIDTH - 20, CAMERA_HEIGHT - 20),
                "color": COLORS["button_normal"],
                "hover_color": COLORS["button_hover"],
                "active": True
            },
            "menu": {
                "text": "Menu",
                "coords": (20, CAMERA_HEIGHT - 80, 
                          240, CAMERA_HEIGHT - 20),
                "color": COLORS["button_normal"],
                "hover_color": COLORS["button_hover"],
                "active": True
            },
            "confirm_difficulty": {
                "text": "Confirm & Return",
                "coords": (CAMERA_WIDTH - 240, CAMERA_HEIGHT - 80, 
                          CAMERA_WIDTH - 20, CAMERA_HEIGHT - 20),
                "color": COLORS["button_normal"],
                "hover_color": COLORS["button_hover"],
                "active": True
            },
            "exit_game": {
                "text": "Exit Game",
                "coords": (CAMERA_WIDTH - 240, CAMERA_HEIGHT - 80, 
                          CAMERA_WIDTH - 20, CAMERA_HEIGHT - 20),
                "color": COLORS["button_normal"],
                "hover_color": COLORS["button_hover"],
                "active": True
            }
        }
    
    def _initialize_audio(self):
        """Initialize audio system"""
        try:
            # 确保pygame mixer已初始化
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 2048)
                print("Pygame mixer initialized")
            else:
                print("Pygame mixer already initialized")
        except Exception as e:
            print(f"Failed to initialize audio system: {e}")
    
    def _load_sounds(self):
        """Load all sound effects"""
        try:
            # 先检查声音目录是否存在
            sound_dir = "sounds"
            if not os.path.exists(sound_dir):
                os.makedirs(sound_dir, exist_ok=True)
                print(f"Created sounds directory: {sound_dir}")
            
            # 显示所有可用的声音文件
            print(f"Available sound files in {sound_dir}:")
            if os.path.exists(sound_dir):
                for file in os.listdir(sound_dir):
                    if file.endswith(".wav"):
                        print(f"  - {file}")
            
            # 加载声音文件
            for sound_name, sound_file in SOUNDS.items():
                if sound_name == "volume":  # 跳过音量设置
                    continue
                    
                if isinstance(sound_file, str):
                    sound_path = os.path.join("sounds", sound_file)
                    if os.path.exists(sound_path):
                        try:
                            self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                            self.sounds[sound_name].set_volume(SOUNDS["volume"])
                            print(f"Loaded sound: {sound_name} from {sound_path}")
                        except Exception as e:
                            print(f"Error loading sound {sound_name}: {e}")
                    else:
                        print(f"Warning: Sound file not found: {sound_path}")
            print("Sound effects loaded successfully")
        except Exception as e:
            print(f"Failed to load sound effects: {e}")
    
    def _play_sound(self, sound_name):
        """Play a sound effect with better error handling"""
        if sound_name in self.sounds:
            try:
                # 确保混音器已初始化
                if not pygame.mixer.get_init():
                    self._initialize_audio()
                
                # 播放声音
                self.sounds[sound_name].play()
                print(f"Playing sound: {sound_name}")
                
            except Exception as e:
                print(f"Failed to play sound {sound_name}: {e}")
        else:
            print(f"Warning: Sound not found: {sound_name}")
    
    def create_particle(self, x, y, color):
        """创建更高级的粒子效果"""
        # 随机选择粒子类型
        particle_type = random.choice(["circle", "star", "sparkle", "triangle"])
        
        # 根据粒子类型设置不同参数
        if particle_type == "circle":
            size = random.uniform(3, 8)
            velocity = (random.uniform(-3, 3), random.uniform(-5, -1))
            acceleration = (0, 0.1)  # 向下的重力
            decay_rate = random.uniform(0.95, 0.99)  # 速度衰减率
        elif particle_type == "star":
            size = random.uniform(4, 10)
            velocity = (random.uniform(-2, 2), random.uniform(-4, -0.5))
            acceleration = (0, 0.05)
            decay_rate = random.uniform(0.97, 0.99)
        elif particle_type == "sparkle":
            size = random.uniform(1, 3)
            velocity = (random.uniform(-4, 4), random.uniform(-4, 4))
            acceleration = (0, 0.02)
            decay_rate = random.uniform(0.9, 0.95)
        else:  # triangle
            size = random.uniform(4, 8)
            velocity = (random.uniform(-3, 3), random.uniform(-3, -0.5))
            acceleration = (0, 0.07)
            decay_rate = random.uniform(0.96, 0.98)
            
        # 随机调整颜色亮度
        brightness = random.uniform(0.7, 1.3)
        bright_color = tuple(min(255, int(c * brightness)) for c in color)
        
        return {
            "x": x,
            "y": y,
            "color": bright_color,
            "velocity": velocity,
            "acceleration": acceleration,
            "size": size,
            "type": particle_type,
            "lifetime": self.particle_lifetime,
            "created_time": time.time(),
            "alpha": 255,  # 初始透明度
            "decay_rate": decay_rate,
            "rotation": random.uniform(0, 360),  # 初始旋转角度
            "rotation_speed": random.uniform(-5, 5)  # 旋转速度
        }
    
    def update_particles(self):
        """更新粒子位置、速度和生命周期"""
        current_time = time.time()
        
        # 过滤掉生命周期结束的粒子
        self.celebration_particles = [
            particle for particle in self.celebration_particles
            if current_time - particle["created_time"] < particle["lifetime"]
        ]
        
        for particle in self.celebration_particles:
            # 更新位置
            particle["x"] += particle["velocity"][0]
            particle["y"] += particle["velocity"][1]
            
            # 应用加速度
            particle["velocity"] = (
                particle["velocity"][0] + particle["acceleration"][0],
                particle["velocity"][1] + particle["acceleration"][1]
            )
            
            # 应用速度衰减
            particle["velocity"] = (
                particle["velocity"][0] * particle["decay_rate"],
                particle["velocity"][1] * particle["decay_rate"]
            )
            
            # 更新透明度
            age_ratio = (current_time - particle["created_time"]) / particle["lifetime"]
            particle["alpha"] = int(255 * (1 - age_ratio))
            
            # 更新旋转角度
            particle["rotation"] += particle["rotation_speed"]
            
            # 根据粒子类型缩小尺寸
            if particle["type"] == "sparkle":
                # 闪烁效果
                particle["size"] *= 0.98
            else:
                # 缓慢缩小效果
                particle["size"] *= 0.995
    
    def draw_particles(self, frame):
        """绘制更高级的粒子效果"""
        for particle in self.celebration_particles:
            # 获取粒子信息
            x, y = int(particle["x"]), int(particle["y"])
            size = int(particle["size"])
            particle_type = particle["type"]
            color = particle["color"]
            alpha = particle["alpha"]
            rotation = particle["rotation"]
            
            # 调整颜色，添加alpha通道
            color_with_alpha = (*color, alpha)
            
            # 确保粒子在画面内
            if x < 0 or y < 0 or x >= frame.shape[1] or y >= frame.shape[0]:
                continue
            
            # 根据粒子类型绘制不同形状
            if particle_type == "circle":
                # 绘制圆形粒子
                cv2.circle(frame, (x, y), size, color, -1, cv2.LINE_AA)
                
                # 添加光晕效果
                for i in range(1, 4):
                    glow_alpha = alpha // (i * 2)
                    glow_size = size + i * 2
                    glow_color = (*color[:3], glow_alpha)
                    cv2.circle(frame, (x, y), glow_size, glow_color, 1, cv2.LINE_AA)
                    
            elif particle_type == "star":
                # 绘制星形粒子
                points = 5
                outer_radius = size
                inner_radius = size // 2
                
                # 计算星形点
                star_points = []
                for i in range(points * 2):
                    # 交替使用内外半径
                    radius = outer_radius if i % 2 == 0 else inner_radius
                    angle = math.pi * i / points + math.radians(rotation)
                    px = x + int(radius * math.cos(angle))
                    py = y + int(radius * math.sin(angle))
                    star_points.append([px, py])
                
                # 绘制填充星形
                cv2.fillPoly(frame, [np.array(star_points)], color, cv2.LINE_AA)
                
            elif particle_type == "sparkle":
                # 闪烁效果
                brightness = random.uniform(0.7, 1.0)
                sparkle_color = tuple(min(255, int(c * brightness)) for c in color)
                
                # 绘制中心点
                cv2.circle(frame, (x, y), size, sparkle_color, -1, cv2.LINE_AA)
                
                # 绘制射线
                for i in range(4):
                    angle = math.pi * i / 2 + math.radians(rotation)
                    ray_length = int(size * 3)
                    end_x = x + int(ray_length * math.cos(angle))
                    end_y = y + int(ray_length * math.sin(angle))
                    cv2.line(frame, (x, y), (end_x, end_y), sparkle_color, 1, cv2.LINE_AA)
                    
            elif particle_type == "triangle":
                # 绘制三角形
                side = size * 2
                height = int(side * math.sqrt(3) / 2)
                
                # 计算三角形三个顶点
                angle = math.radians(rotation)
                points = []
                for i in range(3):
                    point_angle = angle + math.pi * 2 * i / 3
                    px = x + int(side * math.cos(point_angle))
                    py = y + int(side * math.sin(point_angle))
                    points.append([px, py])
                
                # 绘制填充三角形
                cv2.fillPoly(frame, [np.array(points)], color, cv2.LINE_AA)
    
    def draw_button(self, frame, button_name, button):
        """Draw a button with hover and click effects"""
        x1, y1, x2, y2 = button["coords"]
        
        # Calculate button color based on state
        if button_name == self.button_hover:
            color = button["hover_color"]
        else:
            color = button["color"]
        
        # Apply click animation
        if button_name in self.button_click_animation:
            click_time = self.button_click_animation[button_name]
            if time.time() - click_time < 0.1:  # 100ms animation
                scale = 0.95
            else:
                del self.button_click_animation[button_name]
                scale = 1.0
        else:
            scale = 1.0
        
        # Calculate scaled coordinates
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = (x2 - x1) * scale
        height = (y2 - y1) * scale
        
        x1 = int(center_x - width / 2)
        y1 = int(center_y - height / 2)
        x2 = int(center_x + width / 2)
        y2 = int(center_y + height / 2)
        
        # Draw button background
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        
        # Draw button border
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        
        # Draw button text
        text_size = cv2.getTextSize(button["text"], cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = x1 + (x2 - x1 - text_size[0]) // 2
        text_y = y1 + (y2 - y1 + text_size[1]) // 2
        cv2.putText(frame, button["text"], (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    def draw_game(self, frame):
        """Draw modern style game interface"""
        h, w = frame.shape[:2]
        center_x = w // 2
        center_y = h // 2
        
        # 不添加背景渐变，保持原始画面亮度
        # 注释掉可能引用不存在颜色的代码
        # self.create_gradient(frame, (0, 0, w, h), 
        #                    COLORS["bg_gradient_top"], 
        #                    COLORS["bg_gradient_bottom"], 
        #                    vertical=True)
        
        # 绘制顶部和底部状态栏
        topbar_height = UI["topbar_height"]
        bottombar_height = UI["bottombar_height"]
        
        # 绘制半透明顶部状态栏
        topbar_rect = (0, 0, w, topbar_height)
        # 使用更透明的背景，确保视觉清晰
        self.create_glass_effect(frame, topbar_rect, 
                               COLORS["panel"], 
                               alpha=0.6,  # 降低不透明度
                               blur=UI["blur_amount"], 
                               border_radius=0)
        
        # 绘制半透明底部状态栏
        bottombar_rect = (0, h - bottombar_height, w, h)
        # 使用更透明的背景，确保视觉清晰
        self.create_glass_effect(frame, bottombar_rect, 
                               COLORS["panel"], 
                               alpha=0.6,  # 降低不透明度
                               blur=UI["blur_amount"], 
                               border_radius=0)
        
        # 计算时间进度条
        time_progress = max(0.0, min(1.0, self.time_remaining / self.difficulty_time))
        progress_width = int(w * time_progress)
        progress_height = 4
        
        # 根据剩余时间使用不同颜色
        if time_progress > 0.6:
            progress_color = COLORS["success"]
        elif time_progress > 0.3:
            progress_color = COLORS["warning"]
        else:
            progress_color = COLORS["danger"]
        
        # 绘制时间进度条
        cv2.rectangle(frame, 
                    (0, topbar_height), 
                    (progress_width, topbar_height + progress_height),
                    progress_color, -1)
        
        # 绘制游戏信息 - 目标、分数和时间
        padding = 20
        
        # 目标对象
        if self.current_target:
            target_text = f"Find: {self.current_target}"
            cv2.putText(frame, target_text, 
                      (padding, int(topbar_height // 2 + 10)),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS["white"], 2, cv2.LINE_AA)
        
        # 分数和时间放到右侧
        score_text = f"Score: {self.score}"
        score_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        score_x = w - score_size[0] - padding
        cv2.putText(frame, score_text, 
                  (score_x, int(topbar_height // 2 + 10)),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS["white"], 2, cv2.LINE_AA)
        
        # 时间格式化为分:秒
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        time_text = f"Time: {minutes:01d}:{seconds:02d}"
        time_size = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        time_x = score_x - time_size[0] - padding
        cv2.putText(frame, time_text, 
                  (time_x, int(topbar_height // 2 + 10)),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS["white"], 2, cv2.LINE_AA)
        
        # 控制按钮放在底部状态栏
        # 计算按钮位置
        next_text = "Next"
        next_size = cv2.getTextSize(next_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        next_width = next_size[0] + 40
        next_height = next_size[1] + 20
        next_x = w - next_width - padding
        next_y = h - bottombar_height + (bottombar_height - next_height) // 2
        
        quit_text = "Quit"
        quit_size = cv2.getTextSize(quit_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        quit_width = quit_size[0] + 40
        quit_height = quit_size[1] + 20
        quit_x = next_x - quit_width - padding
        quit_y = next_y
        
        # 更新按钮位置到self.buttons中
        next_button_rect = (
            int(next_x), 
            int(next_y), 
            int(next_x + next_width), 
            int(next_y + next_height)
        )
        
        quit_button_rect = (
            int(quit_x), 
            int(quit_y), 
            int(quit_x + quit_width), 
            int(quit_y + quit_height)
        )
        
        # 存储按钮位置以供点击检测
        self.buttons["next"] = next_button_rect
        self.buttons["quit"] = quit_button_rect
        
        # 绘制按钮
        self.draw_modern_button(frame, "next", {
            "text": "Next", 
            "coords": self.buttons["next"],
            "color": COLORS["button_normal"],
            "hover_color": COLORS["button_hover"],
            "active": True
        })
        
        self.draw_modern_button(frame, "quit", {
            "text": "Quit", 
            "coords": self.buttons["quit"],
            "color": COLORS["button_normal"],
            "hover_color": COLORS["button_hover"],
            "active": True
        })
        
        # 在Hard模式下显示剩余Next点击次数
        if self.difficulty == "hard" and not self.game_over:
            next_text = f"Next clicks: {self.next_clicks_remaining}"
            next_size = cv2.getTextSize(next_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            next_x = int(next_x - next_size[0] - 20)
            next_y = int(next_y - next_height - 15)
            
            # 为文本背景添加半透明背景
            next_bg_rect = (next_x - 10, next_y - next_size[1] - 5, 
                           next_x + next_size[0] + 10, next_y + 5)
            
            # 根据剩余次数设置不同颜色
            if self.next_clicks_remaining <= 0:
                next_color = COLORS["danger"]
            elif self.next_clicks_remaining == 1:
                next_color = COLORS["warning"]
            else:
                next_color = COLORS["success"]
                
            # 创建半透明背景
            self.create_glass_effect(frame, next_bg_rect, next_color, 
                                   alpha=0.7, blur=UI["blur_amount"]//2, 
                                   border_radius=UI["corner_radius"]//2)
            
            # 绘制文本
            cv2.putText(frame, next_text, (next_x, next_y), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS["white"], 2, cv2.LINE_AA)
        
        # Update and draw particle effects
        self.update_particles()
        self.draw_particles(frame)
        
        # 在游戏结束时处理
        if self.game_over:
            # 计算淡入效果的进度
            progress = min(1.0, (time.time() - self.game_end_time) / ANIMATION["result_fade_duration"])
            
            # 使用透明黑色叠加创建暗淡效果
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (CAMERA_WIDTH, CAMERA_HEIGHT), 
                        (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7 * progress, frame, 1 - 0.7 * progress, 0, frame)
            
            # 绘制结果面板
            panel_width = CAMERA_WIDTH * 0.7
            panel_height = CAMERA_HEIGHT * 0.6
            panel_x1 = (CAMERA_WIDTH - panel_width) // 2
            panel_y1 = (CAMERA_HEIGHT - panel_height) // 2
            
            # 创建面板玻璃效果
            panel_rect = (int(panel_x1), int(panel_y1), 
                        int(panel_x1 + panel_width), int(panel_y1 + panel_height))
            
            # 创建面板
            self.create_glass_effect(frame, panel_rect, COLORS["panel"], 
                                   alpha=0.9 * progress, 
                                   blur=UI["blur_amount"], 
                                   border_radius=UI["corner_radius"])
            
            # 绘制标题
            title = "Game Over"
            title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 3)[0]
            cv2.putText(frame, title,
                      (int(CAMERA_WIDTH//2 - title_size[0]//2), int(panel_y1 + 80)),
                      cv2.FONT_HERSHEY_SIMPLEX, 2.0, 
                      (*COLORS["accent_2"], int(255 * progress)), 3, cv2.LINE_AA)
            
            # 绘制分数
            score_text = f"Final Score: {self.score}"
            score_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
            cv2.putText(frame, score_text,
                      (int(CAMERA_WIDTH//2 - score_size[0]//2), int(panel_y1 + 150)),
                      cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                      (*COLORS["white"], int(255 * progress)), 2, cv2.LINE_AA)
            
            # 在一定进度后显示"Play Again"按钮
            if progress > 0.6:
                button_progress = min(1.0, (progress - 0.6) / 0.4)
                
                # 创建"Play Again"按钮
                restart_text = "Play Again"
                restart_size = cv2.getTextSize(restart_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                restart_button_w = restart_size[0] + 40
                restart_button_h = restart_size[1] + 20
                restart_button_x = int(CAMERA_WIDTH//2 - restart_button_w - 20)
                restart_button_y = int(panel_y1 + panel_height - 80)
                
                restart_button_rect = (
                    restart_button_x, 
                    restart_button_y, 
                    restart_button_x + restart_button_w, 
                    restart_button_y + restart_button_h
                )
                
                # 创建按钮效果
                self.create_glass_effect(
                    frame, 
                    restart_button_rect, 
                    (*COLORS["success"], int(200 * button_progress)), 
                    alpha=0.9 * button_progress, 
                    blur=UI["blur_amount"] // 2, 
                    border_radius=UI["corner_radius"]
                )
                
                # 绘制按钮文本
                cv2.putText(
                    frame, 
                    restart_text,
                    (int(restart_button_x + (restart_button_w - restart_size[0])//2), 
                     int(restart_button_y + (restart_button_h + restart_size[1])//2 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.0, 
                    (*COLORS["white"], int(255 * button_progress)), 
                    2, 
                    cv2.LINE_AA
                )
                
                # 存储按钮位置用于点击检测 - 添加中文注释
                self.buttons["restart"] = restart_button_rect
                
            # 在一定进度后显示"Main Menu"按钮
            if progress > 0.7:
                button_progress = min(1.0, (progress - 0.7) / 0.3)
                
                # 创建"Main Menu"按钮
                menu_text = "Main Menu"
                menu_size = cv2.getTextSize(menu_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                menu_button_w = menu_size[0] + 40
                menu_button_h = menu_size[1] + 20
                menu_button_x = int(CAMERA_WIDTH//2 + 20)
                menu_button_y = int(panel_y1 + panel_height - 80)
                
                menu_button_rect = (
                    menu_button_x, 
                    menu_button_y, 
                    menu_button_x + menu_button_w, 
                    menu_button_y + menu_button_h
                )
                
                # 创建按钮效果
                self.create_glass_effect(
                    frame, 
                    menu_button_rect, 
                    (*COLORS["info"], int(200 * button_progress)), 
                    alpha=0.9 * button_progress, 
                    blur=UI["blur_amount"] // 2, 
                    border_radius=UI["corner_radius"]
                )
                
                # 绘制按钮文本
                cv2.putText(
                    frame, 
                    menu_text,
                    (int(menu_button_x + (menu_button_w - menu_size[0])//2), 
                     int(menu_button_y + (menu_button_h + menu_size[1])//2 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1.0, 
                    (*COLORS["white"], int(255 * button_progress)), 
                    2, 
                    cv2.LINE_AA
                )
                
                # 存储按钮位置用于点击检测 - 添加中文注释
                self.buttons["menu"] = menu_button_rect
                
            # 检查游戏结束后是否有按钮点击，处理"Play Again"和"Main Menu"按钮的点击
            # 注意：实际点击处理在handle_mouse_click中，此处只存储按钮坐标
    
    def draw_modern_button(self, frame, button_name, button):
        """Draw modern style button"""
        # 按钮坐标可能是字典中的coords字段，也可能直接是坐标元组
        if isinstance(button, dict) and "coords" in button:
            x1, y1, x2, y2 = button["coords"]
            color = button.get("color", COLORS["button_normal"])
            hover_color = button.get("hover_color", COLORS["button_hover"])
            text = button.get("text", button_name)
        else:  # 按钮是元组坐标
            x1, y1, x2, y2 = button
            color = COLORS["button_normal"]
            hover_color = COLORS["button_hover"]
            text = button_name
        
        # Calculate button color based on state
        if button_name == self.button_hover:
            color = hover_color
        
        # Apply click animation
        if button_name in self.button_click_animation:
            click_time = self.button_click_animation[button_name]
            if time.time() - click_time < ANIMATION["button_click_duration"]:
                scale = 0.95
            else:
                del self.button_click_animation[button_name]
                scale = 1.0
        else:
            scale = 1.0
        
        # Calculate scaled coordinates
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = (x2 - x1) * scale
        height = (y2 - y1) * scale
        
        x1 = int(center_x - width / 2)
        y1 = int(center_y - height / 2)
        x2 = int(center_x + width / 2)
        y2 = int(center_y + height / 2)
        
        # Create button area
        button_rect = (x1, y1, x2, y2)
        
        # Use glass morphism effect to draw button
        self.create_glass_effect(frame, button_rect, (*color, 220), 
                               alpha=0.9, blur=UI["blur_amount"]//2, 
                               border_radius=UI["corner_radius"])
        
        # Draw button text
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        text_x = int(x1 + (x2 - x1 - text_size[0]) // 2)
        text_y = int(y1 + (y2 - y1 + text_size[1]) // 2)
        
        # Draw text shadow
        shadow_offset = 2
        cv2.putText(frame, text, 
                  (int(text_x + shadow_offset), int(text_y + shadow_offset)), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Draw main text
        cv2.putText(frame, text, 
                  (text_x, text_y), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS["white"], 2, cv2.LINE_AA)
    
    def draw_menu(self, frame):
        """Draw modern main menu interface"""
        # Get window size
        h, w = frame.shape[:2]
        center_x = w // 2
        center_y = h // 2
        
        # Add background gradient
        self.create_gradient(frame, (0, 0, w, h), 
                            COLORS["bg_gradient_top"], 
                            COLORS["bg_gradient_bottom"], 
                            vertical=True)
        
        # Calculate time-based animations
        current_time = time.time()
        self.title_animation = 0.5 + 0.5 * np.sin(current_time * ANIMATION["pulse_speed"] * 0.5)
        self.float_offset = ANIMATION["float_amount"] * np.sin(current_time * 1.5)
        
        # Create semi-transparent center panel
        panel_width = w * 0.7
        panel_height = h * 0.75
        panel_x1 = center_x - panel_width // 2
        panel_y1 = center_y - panel_height // 2
        panel_rect = (int(panel_x1), int(panel_y1), 
                      int(panel_x1 + panel_width), int(panel_y1 + panel_height))
        
        # Create glass effect panel
        self.create_glass_effect(frame, panel_rect, COLORS["panel"], 
                               alpha=0.7, blur=UI["blur_amount"], 
                               border_radius=UI["corner_radius"])
        
        # Draw title (with floating animation effect)
        title = MENU["title"]
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 4)[0]
        # 更高的位置，确保不与下面元素重叠
        title_y = int(center_y - 200 + int(self.float_offset))
        
        # Draw glow effect
        glow_size = int(UI["glow_radius"] * self.title_animation)
        for i in range(glow_size, 0, -1):
            alpha = int(255 * (1 - i / glow_size) * 0.7)
            color = (
                int(COLORS["text_glow"][0] * self.title_animation),
                int(COLORS["text_glow"][1] * self.title_animation),
                int(COLORS["text_glow"][2] * self.title_animation)
            )
            
            # Draw outer glow
            cv2.putText(frame, title,
                      (int(center_x - title_size[0]//2 + i), title_y),
                      cv2.FONT_HERSHEY_SIMPLEX, 2.0, color, 4, cv2.LINE_AA)
            cv2.putText(frame, title,
                      (int(center_x - title_size[0]//2 - i), title_y),
                      cv2.FONT_HERSHEY_SIMPLEX, 2.0, color, 4, cv2.LINE_AA)
        
        # Draw title
        cv2.putText(frame, title,
                  (int(center_x - title_size[0]//2), title_y),
                  cv2.FONT_HERSHEY_SIMPLEX, 2.0, COLORS["white"], 4, cv2.LINE_AA)
        
        # Draw version number
        version = MENU["version"]
        version_size = cv2.getTextSize(version, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        cv2.putText(frame, version,
                  (int(center_x + title_size[0]//2 - version_size[0]), title_y - title_size[1] + version_size[1]),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS["gray"], 1, cv2.LINE_AA)
        
        # Draw subtitle
        subtitle = "Modern Object Recognition Game"
        subtitle_size = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        cv2.putText(frame, subtitle,
                  (int(center_x - subtitle_size[0]//2), int(title_y + 50)),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS["gray"], 2, cv2.LINE_AA)
        
        # Draw separator line
        line_y = int(title_y + 80)
        line_width = int(panel_width * 0.6)
        cv2.line(frame, 
                (int(center_x - line_width//2), line_y),
                (int(center_x + line_width//2), line_y),
                COLORS["accent_2"], 2, cv2.LINE_AA)
        
        # 过滤菜单选项，删除"Exit Game"
        filtered_options = [option for option in MENU["main_options"] if option["action"] != "quit"]
        
        # Draw menu options - 增加起始位置，距标题更远
        start_y = int(center_y - 20)  # 更低的起始位置，避免与标题重叠
        spacing = UI["menu_spacing"]  # Use defined spacing value
        
        for i, option in enumerate(filtered_options):
            text = option["text"]
            y_pos = int(start_y + i * spacing)
            
            # Calculate option size
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.1, 2)[0]
            option_width = text_size[0] + UI["menu_padding"] * 2
            option_height = text_size[1] + UI["menu_padding"]
            
            # Calculate option position
            rect_x1 = int(center_x - option_width // 2)
            rect_y1 = int(y_pos - option_height // 2)
            rect_x2 = int(center_x + option_width // 2)
            rect_y2 = int(y_pos + option_height // 2)
            
            option_rect = (rect_x1, rect_y1, rect_x2, rect_y2)
            
            # Current selected option has a different style
            if i == self.selected_option:
                # Draw selected button with glass effect
                self.create_glass_effect(frame, option_rect, COLORS["accent_2"], 
                                       alpha=0.8, blur=UI["blur_amount"] // 2, 
                                       border_radius=UI["corner_radius"])
                
                # Add highlight indicator
                cv2.line(frame, 
                       (rect_x1 + 5, rect_y1 + 5), 
                       (rect_x1 + 5, rect_y2 - 5), 
                       COLORS["white"], 3, cv2.LINE_AA)
                
                text_color = COLORS["white"]
            else:
                # Draw normal button with glass effect
                self.create_glass_effect(frame, option_rect, 
                                       (*COLORS["transparent_black"][:3], 150), 
                                       alpha=0.6, blur=UI["blur_amount"] // 2, 
                                       border_radius=UI["corner_radius"])
                
                text_color = COLORS["white"]
            
            # Draw option text
            cv2.putText(frame, text,
                      (int(center_x - text_size[0]//2), int(y_pos + text_size[1]//2)),
                      cv2.FONT_HERSHEY_SIMPLEX, 1.1, text_color, 2, cv2.LINE_AA)
        
        # 添加Exit Game按钮（替换Close按钮）
        exit_text = "Exit Game"
        exit_size = cv2.getTextSize(exit_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        exit_button_w = exit_size[0] + 40
        exit_button_h = exit_size[1] + 20
        exit_button_x = int(panel_x1 + panel_width - exit_button_w - 20)
        exit_button_y = int(panel_y1 + panel_height - exit_button_h - 20)
        
        exit_button_rect = (
            exit_button_x, 
            exit_button_y, 
            exit_button_x + exit_button_w, 
            exit_button_y + exit_button_h
        )
        
        # 创建Exit Game按钮效果
        self.create_glass_effect(
            frame, 
            exit_button_rect, 
            COLORS["danger"], 
            alpha=0.8, 
            blur=UI["blur_amount"] // 2, 
            border_radius=UI["corner_radius"]
        )
        
        # 绘制按钮文本
        cv2.putText(
            frame, 
            exit_text,
            (int(exit_button_x + (exit_button_w - exit_size[0])//2), 
             int(exit_button_y + (exit_button_h + exit_size[1])//2 - 2)),
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.9, 
            COLORS["white"], 
            2, 
            cv2.LINE_AA
        )
        
        # 存储Exit Game按钮位置供点击检测
        self.buttons["exit_game"] = exit_button_rect
        
        # Draw bottom instruction
        instruction = "Click on an option to select"
        instruction_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
        
        instruction_y = int(panel_y1 + panel_height - 30)
        
        cv2.putText(frame, instruction,
                  (int(center_x - instruction_size[0]//2), instruction_y),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS["gray"], 1, cv2.LINE_AA)
                  
        # Add bottom decoration
        decoration_y = int(instruction_y + 15)
        decoration_width = 50
        decoration_x1 = int(center_x - decoration_width - 10)
        decoration_x2 = int(center_x + decoration_width + 10)
        
        cv2.line(frame, 
               (int(center_x - decoration_width), decoration_y), 
               (int(center_x + decoration_width), decoration_y), 
               COLORS["accent_1"], 2)
    
    def draw_difficulty_menu(self, frame):
        """Draw modern difficulty selection menu"""
        # Get window size
        h, w = frame.shape[:2]
        center_x = w // 2
        center_y = h // 2
        
        # Add background gradient effect
        self.create_gradient(frame, (0, 0, w, h), 
                            COLORS["bg_gradient_top"], 
                            COLORS["bg_gradient_bottom"], 
                            vertical=True)
        
        # Calculate animation effects
        current_time = time.time()
        pulse = 0.5 + 0.5 * np.sin(current_time * ANIMATION["pulse_speed"] * 0.3)
        float_offset = ANIMATION["float_amount"] * 0.5 * np.sin(current_time * 1.2)
        
        # Draw center panel - 增加panel高度确保所有内容都能显示
        panel_width = w * 0.7
        panel_height = h * 0.8  # 增加面板高度
        panel_x1 = center_x - panel_width // 2
        panel_y1 = center_y - panel_height // 2
        panel_rect = (int(panel_x1), int(panel_y1), 
                      int(panel_x1 + panel_width), int(panel_y1 + panel_height))
        
        # Create glass effect panel
        self.create_glass_effect(frame, panel_rect, COLORS["panel"], 
                               alpha=0.7, blur=UI["blur_amount"], 
                               border_radius=UI["corner_radius"])
        
        # Draw back button (top left)
        back_text = "< Back"
        back_size = cv2.getTextSize(back_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        back_rect = (20, 20, 20 + back_size[0] + 20, 20 + back_size[1] + 10)
        
        # Create back button glass effect
        self.create_glass_effect(frame, back_rect, 
                               (*COLORS["transparent_black"][:3], 120), 
                               alpha=0.6, blur=3, border_radius=5)
        
        # Draw back button text
        cv2.putText(frame, back_text,
                  (30, 20 + back_size[1]),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS["gray"], 2, cv2.LINE_AA)
        
        # Draw title - 调整标题位置避免与选项重叠
        title = "Select Difficulty"
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 4)[0]
        title_y = int(panel_y1 + 80 + int(float_offset))  # 将标题上移
        
        # Draw title glow effect
        glow_color = (
            int(COLORS["text_glow"][0] * pulse),
            int(COLORS["text_glow"][1] * pulse),
            int(COLORS["text_glow"][2] * pulse)
        )
        
        for i in range(UI["glow_radius"]):
            offset = UI["glow_radius"] - i
            cv2.putText(frame, title,
                      (int(center_x - title_size[0]//2 + offset), title_y),
                      cv2.FONT_HERSHEY_SIMPLEX, 2.0, glow_color, 4, cv2.LINE_AA)
            cv2.putText(frame, title,
                      (int(center_x - title_size[0]//2 - offset), title_y),
                      cv2.FONT_HERSHEY_SIMPLEX, 2.0, glow_color, 4, cv2.LINE_AA)
        
        # Draw main title text
        cv2.putText(frame, title,
                  (int(center_x - title_size[0]//2), title_y),
                  cv2.FONT_HERSHEY_SIMPLEX, 2.0, COLORS["accent_2"], 4, cv2.LINE_AA)
        
        # Draw description text
        description = "Double-click to select a difficulty level"
        desc_size = cv2.getTextSize(description, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 1)[0]
        cv2.putText(frame, description,
                  (int(center_x - desc_size[0]//2), int(title_y + 50)),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS["gray"], 1, cv2.LINE_AA)
        
        # Draw separator line
        line_y = int(title_y + 80)
        line_width = int(panel_width * 0.6)
        cv2.line(frame, 
                (int(center_x - line_width//2), line_y),
                (int(center_x + line_width//2), line_y),
                COLORS["accent_1"], 2, cv2.LINE_AA)
        
        # Calculate difficulty options layout - 从线条下方开始布局选项
        diff_start_y = line_y + 70  # 从分隔线下方开始
        diff_spacing = 120  # 增加间距，确保不重叠
        
        # 设置统一的卡片大小，确保所有难度选项卡片保持一致
        card_width = int(panel_width * 0.7)
        card_height = 90  # 略微减小卡片高度
        
        # 更加简化的难度描述
        difficulty_descriptions = {
            "easy": "Lower Recognition Requirements",
            "normal": "Balanced Challenge",
            "hard": "Higher Recognition Requirements"
        }
        
        # Draw all difficulty options
        for i, diff in enumerate(MENU["difficulties"]):
            text = diff["text"]
            value = diff["value"]
            
            # Calculate position
            y_pos = int(diff_start_y + i * diff_spacing)
            
            # 获取对应的简化描述
            desc = difficulty_descriptions[value]
            
            # 设置颜色
            if value == "easy":
                color = COLORS["info"]  # Blue
            elif value == "normal":
                color = COLORS["success"]  # Green
            else:
                color = COLORS["warning"]  # Orange
            
            # Calculate text sizes - 稍微减小文字大小
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            desc_size = cv2.getTextSize(desc, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            
            # 使用统一大小的卡片
            card_x1 = int(center_x - card_width // 2)
            card_y1 = int(y_pos - card_height // 2)
            card_x2 = int(center_x + card_width // 2)
            card_y2 = int(y_pos + card_height // 2)
            
            card_rect = (card_x1, card_y1, card_x2, card_y2)
            
            # 添加到按钮列表，用于鼠标检测
            self.buttons[f"difficulty_{value}"] = card_rect
            
            # Current selected option has special style
            if i == self.selected_option:
                # Create selected item glass effect
                self.create_glass_effect(frame, card_rect, (*color, 180), 
                                       0.8, UI["blur_amount"], UI["corner_radius"])
                
                # Draw small icon (difficulty indicator)
                icon_size = 12
                icon_x = card_x1 + 20
                icon_y = card_y1 + card_height//2
                
                # Draw difficulty level indicators
                for j in range(3):
                    if j < {"easy": 1, "normal": 2, "hard": 3}[value]:
                        dot_color = color  # Active color
                    else:
                        dot_color = COLORS["button_disabled"]  # Inactive color
                    
                    cv2.circle(frame, (int(icon_x + j*18), int(icon_y)), 
                            icon_size//2, dot_color, -1, cv2.LINE_AA)
                
                # Draw difficulty name (large text) - 位置调整避免重叠
                cv2.putText(frame, text,
                          (int(card_x1 + 80), int(card_y1 + 35)),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLORS["white"], 2, cv2.LINE_AA)
                
                # Draw difficulty description (small text) - 位置调整避免重叠
                cv2.putText(frame, desc,
                          (int(card_x1 + 80), int(card_y1 + 65)),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS["white"], 1, cv2.LINE_AA)
                
            else:
                # Create normal item transparent effect
                self.draw_rounded_rect(frame, card_rect, (*COLORS["transparent_black"][:3], 120), 
                                     UI["corner_radius"], -1)
                
                # Draw thin border
                self.draw_rounded_rect(frame, card_rect, (*color, 150), 
                                     UI["corner_radius"], 1)
                
                # Draw difficulty name - 位置调整避免重叠
                cv2.putText(frame, text,
                          (int(card_x1 + 80), int(card_y1 + 35)),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)
                
                # Draw difficulty description - 位置调整避免重叠
                cv2.putText(frame, desc,
                          (int(card_x1 + 80), int(card_y1 + 65)),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS["gray"], 1, cv2.LINE_AA)
        
        # 在底部添加提示文本 - 调整位置确保在面板内
        hint_text = "Double-click on an option to select and return to main menu"
        hint_size = cv2.getTextSize(hint_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
        hint_y = int(panel_y1 + panel_height - 20)
        
        cv2.putText(frame, hint_text,
                  (int(center_x - hint_size[0]//2), hint_y),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS["accent_2"], 1, cv2.LINE_AA)
    
    def handle_menu_input(self, event, x, y, flags=None, param=None):
        """Handle menu input interactions with animations"""
        # Only process left mouse button clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            self.last_click = (x, y)
            
            # Handle main menu options
            if self.current_menu == "main":
                # 检查Exit Game按钮
                if "exit_game" in self.buttons:
                    exit_button = self.buttons["exit_game"]
                    if (exit_button[0] <= x <= exit_button[2] and 
                        exit_button[1] <= y <= exit_button[3]):
                        print("Exit Game button clicked, exiting game...")
                        
                        # Play click sound
                        self._play_sound("click")
                        
                        # Create particles
                        for _ in range(10):
                            self.celebration_particles.append(
                                self.create_particle(x, y, COLORS["danger"])
                            )
                        
                        # Exit game
                        self.running = False
                        return True
                
                # 过滤掉quit按钮
                filtered_options = [option for option in MENU["main_options"] if option["action"] != "quit"]
                
                for i, option in enumerate(filtered_options):
                    # Calculate button position from draw_menu
                    start_y = int(self.get_center_y() - 10)
                    spacing = UI["menu_spacing"]
                    option_y = start_y + i * spacing
                    
                    # Check if click is within button area
                    if abs(y - option_y) < UI["button_height"] // 2:
                        # Play click sound
                        self._play_sound("click")
                        
                        # Create particles at click point
                        for _ in range(10):
                            self.celebration_particles.append(
                                self.create_particle(x, y, COLORS["accent_2"])
                            )
                        
                        # Handle option action
                        action = option["action"]
                        if action == "start":
                            print("Starting game from main menu...")
                            self.transition_to_game()
                        elif action == "settings":
                            self.transition_to("main", "settings")
                        elif action == "difficulty":
                            self.transition_to("main", "difficulty")
            
            # Handle difficulty menu options
            elif self.current_menu == "difficulty":
                # Check back button
                if y < 50 and x < 120:  # Approximate back button area
                    self.transition_to("difficulty", "main")
                    self._play_sound("click")
                    return
                
                # Check difficulty options - 使用self.buttons来检查而不是计算位置
                for button_name, button_coords in self.buttons.items():
                    if button_name.startswith("difficulty_"):
                        if (button_coords[0] <= x <= button_coords[2] and 
                            button_coords[1] <= y <= button_coords[3]):
                            difficulty_value = button_name.split("_")[1]
                            
                            # 设置选中的选项索引
                            for i, diff in enumerate(MENU["difficulties"]):
                                if diff["value"] == difficulty_value:
                                    self.selected_option = i
                                    break
                                    
                            # 设置难度和对应的时间
                            self.difficulty = difficulty_value
                            if difficulty_value == "easy":
                                self.difficulty_time = 60  # 60秒
                            elif difficulty_value == "normal":
                                self.difficulty_time = 45  # 45秒
                            else:
                                self.difficulty_time = 30  # 30秒
                                
                            # 设置颜色
                            if difficulty_value == "easy":
                                color = COLORS["info"]
                            elif difficulty_value == "normal":
                                color = COLORS["success"]
                            else:
                                color = COLORS["warning"]
                            
                            # 播放点击音效
                            self._play_sound("difficulty_change")
                            
                            # 创建粒子效果
                            for _ in range(15):
                                self.celebration_particles.append(
                                    self.create_particle(x, y, color)
                                )
                            
                            # 添加视觉反馈，提示选择已生效
                            print(f"Difficulty selected: {difficulty_value}")
                            return True
    
    def transition_to_game(self):
        """Perform smooth transition to game from menu"""
        print("Transitioning to game...")
        
        # Play start sound
        self._play_sound("game_start")
        
        # Create particle effect at mouse position
        if self.last_click:
            x, y = self.last_click
            # 创建多个粒子效果
            for _ in range(15):
                self.celebration_particles.append(
                    self.create_particle(x, y, COLORS["success"])
                )
        
        # 重要：直接设置游戏状态，而不仅仅是设置transition参数
        self.current_menu = "game"
        
        # 仍然保留过渡动画效果
        self.transition_active = True
        self.transition_target = "game"
        self.transition_start_time = time.time()
        
        # 选择随机目标
        self.select_random_target()
        
        # Reset game variables
        self.score = 0
        self.time_remaining = self.difficulty_time
        self.game_started = True
        self.game_start_time = time.time()
        self.target_found = False
        self.target_found_time = 0
        
        print(f"Game started with difficulty: {self.difficulty}")
        print(f"Current target: {self.current_target}")
    
    def transition_to(self, from_menu, to_menu):
        """Smooth transition to new menu interface"""
        # Record start time
        start_time = time.time()
        duration = UI["transition_time"]  # Transition duration
        
        # Set transition animation frame rate
        fps = 60
        frame_time = 1.0 / fps
        
        # Transition animation loop
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Calculate progress (0.0 to 1.0)
            progress = min(1.0, elapsed / duration)
            
            # Get camera frame
            ret, frame = self.camera.read()
            if not ret:
                continue
                
            # Flip image horizontally
            frame = cv2.flip(frame, 1)
            
            # Draw fade-out effect
            if from_menu == "main":
                self.draw_menu(frame)
            elif from_menu == "difficulty":
                self.draw_difficulty_menu(frame)
            elif from_menu == "game":
                self.draw_game(frame)
                
            # Create transition mask
            overlay = frame.copy()
            alpha = progress  # Alpha from 0 to 1
            
            # Different transition effects
            if to_menu == "game":
                # Circular mask expanding from center
                center_x, center_y = frame.shape[1]//2, frame.shape[0]//2
                max_radius = int(np.sqrt(center_x**2 + center_y**2))
                radius = int((1.0 - progress) * max_radius)
                
                # Draw black background
                cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
                
                # Draw circular mask
                cv2.circle(overlay, (center_x, center_y), radius, (255, 255, 255), -1)
                
                # Blend images
                alpha = 0.9
                mask = np.zeros_like(frame)
                cv2.circle(mask, (center_x, center_y), radius, (255, 255, 255), -1)
                
                # Create area inside mask
                masked_frame = cv2.bitwise_and(frame, mask)
                
                # Create area outside mask
                inverse_mask = cv2.bitwise_not(mask)
                masked_background = cv2.bitwise_and(overlay, inverse_mask)
                
                # Combine results
                frame = cv2.add(masked_frame, masked_background)
                
                # If transition is complete, draw game interface
                if progress >= 0.95:
                    self.draw_game(frame)
            else:
                # Fade in/out effect
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                
                # Draw target menu
                if progress >= 0.5:  # Start drawing target menu at midpoint
                    if to_menu == "main":
                        self.draw_menu(frame)
                    elif to_menu == "difficulty":
                        self.draw_difficulty_menu(frame)
                    elif to_menu == "game":
                        self.draw_game(frame)
            
            # Display frame
            self.window.show(frame)
            
            # Check keys
            key = self.window.wait_key(int(frame_time * 1000))
            if key == 27:  # ESC
                self.running = False
                break
            
            # Check if transition is complete
            if progress >= 1.0:
                break
        
        # Update current menu state
        self.current_menu = to_menu
    
    def initialize_camera(self):
        """Initialize camera"""
        try:
            self.camera = DirectCamera(0, CAMERA_WIDTH, CAMERA_HEIGHT, True)
            return self.camera.is_opened()
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            return False
    
    def run(self):
        """Run game loop"""
        if not self.window.create():
            print("Unable to create window, game exiting")
            return
            
        if not self.initialize_camera():
            print("Unable to initialize camera, game may not function properly")
        
        # 再次初始化音频系统
        self._initialize_audio()
        
        # Set mouse callbacks
        self.window.set_mouse_callback(self.handle_mouse_click)
        self.window.set_mouse_move_callback(self.handle_mouse_move)
        
        # Set game reference in window
        self.window.game = self
        
        self.running = True
        
        while self.running:
            ret, frame = self.camera.read()
            
            if not ret:
                print("Unable to get camera frame, attempting to reconnect...")
                if not self.initialize_camera():
                    print("Failed to reconnect camera, will use black background")
                    # 创建一个黑色背景
                    frame = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
            
            # Horizontally flip image (mirror)
            if frame is not None:
                frame = cv2.flip(frame, 1)
            
            # 如果在游戏界面，更新游戏状态
            if self.current_menu == "game":
                self._update_game_state(frame)
            
            # Draw current menu or game state
            if self.current_menu == "main":
                self.draw_menu(frame)
            elif self.current_menu == "difficulty":
                self.draw_difficulty_menu(frame)
            elif self.current_menu == "game":
                self.draw_game(frame)
            
            self.window.show(frame)
            
            if self.window.wait_key(1) == 27:  # ESC key to exit
                self.running = False
        
        self._cleanup()
    
    def _update_game_state(self, frame):
        """Update game state"""
        # 游戏时间和状态更新
        current_time = time.time()
        
        # 仅当游戏正在进行且未结束时更新
        if self.game_started and not self.game_over:
            elapsed = current_time - self.game_start_time
            self.time_remaining = max(0, self.difficulty_time - elapsed)
            
            # 检查游戏是否结束
            if self.time_remaining <= 0:
                self.game_over = True
                self.game_end_time = current_time
                
                # 播放游戏结束音效
                self._play_sound("game_over")
            
            # 检查是否需要自动切换目标
            if self.target_found and current_time >= self.auto_next_target_time and self.auto_next_target_time > 0:
                self.target_found = False
                self.select_random_target()
                self.auto_next_target_time = 0  # 重置定时器
        
        # 运行对象检测
        detections = self.detector.detect_objects(frame)
        frame = self.detector.draw_detection_boxes(frame, detections)
        
        # 检查是否找到目标对象
        self.check_target_found(detections)
    
    def _cleanup(self):
        """Clean up resources"""
        if self.camera is not None:
            self.camera.release()
        self.window.destroy()
    
    def start_game(self):
        """Start new game"""
        self.score = 0
        self.game_start_time = time.time()
        self.time_remaining = self.difficulty_time
        self.game_started = True
        self.game_over = False
        self.target_found = False
        self.target_found_time = 0
        self.auto_next_target_time = 0
        self.next_clicks_remaining = 3  # 重置Hard模式下的Next点击次数
        self.found_targets = set()      # 清空已找到的目标记录
        self.select_random_target()
        
        # Play game start sound
        self._play_sound("game_start")
        
        print(f"Game started! Current difficulty: {self.difficulty}")
        print(f"Target object: {self.current_target}")
        if self.difficulty == "hard":
            print(f"Hard mode: {self.next_clicks_remaining} Next clicks available")
    
    def select_random_target(self):
        """Randomly select target object"""
        # 根据当前难度级别选择可用目标
        available_targets = list(OBJECTS[self.difficulty])
        
        # 确保新目标不会出现在已找到的目标列表中
        if self.found_targets and len(available_targets) > len(self.found_targets):
            available_targets = [t for t in available_targets if t not in self.found_targets]
        # 如果所有目标都找到了，清空记录重新开始
        elif len(self.found_targets) >= len(available_targets):
            self.found_targets = set()
            available_targets = list(OBJECTS[self.difficulty])
        
        # 避免选择当前目标（如果还有其他选择）
        if self.current_target in available_targets and len(available_targets) > 1:
            available_targets.remove(self.current_target)
        
        self.current_target = random.choice(available_targets)
        print(f"New target object: {self.current_target}")
    
    def check_target_found(self, detections):
        """Check if target object is found"""
        if not self.current_target or self.time_remaining <= 0 or self.game_over:
            return
        
        # 防止对同一目标重复加分
        if self.current_target in self.found_targets:
            return
            
        required_confidence = DIFFICULTY_LEVELS.get(self.difficulty, 0.5)
        
        for detection in detections:
            detected_class, confidence = detection[:2]
            if detected_class == self.current_target and confidence >= required_confidence:
                print(f"Found target object {self.current_target}! Score +1")
                self.score += 1
                self.target_found = True
                self.target_found_time = time.time()
                
                # 将当前目标添加到已找到集合中，防止重复加分
                self.found_targets.add(self.current_target)
                
                # Play correct sound - 修复音效播放方式
                self._play_sound("correct")
                
                # 创建庆祝粒子效果
                center_x, center_y = self.get_center_x(), self.get_center_y()
                for _ in range(20):
                    x = random.randint(center_x - 100, center_x + 100)
                    y = random.randint(center_y - 100, center_y + 100)
                    self.celebration_particles.append(
                        self.create_particle(x, y, COLORS["success"])
                    )
                
                # 自动选择新目标，不需要手动点击Next
                # 设置延迟定时器，在庆祝动画结束后选择新目标
                self.auto_next_target_time = time.time() + ANIMATION["celebration_duration"]
                
                break
    
    def handle_mouse_click(self, event, x, y, flags, param):
        """Handle mouse click events"""
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Mouse clicked at: ({x}, {y})")  # 调试信息
            
            # 记录当前点击时间和位置
            current_time = time.time()
            click_element = None
            
            # 在菜单状态下处理菜单点击 (main或difficulty)
            if self.current_menu in ["main", "difficulty"]:
                # 如果在难度选择界面，检查是否点击了难度选项
                if self.current_menu == "difficulty":
                    for button_name, button_coords in self.buttons.items():
                        if button_name.startswith("difficulty_"):
                            if (button_coords[0] <= x <= button_coords[2] and 
                                button_coords[1] <= y <= button_coords[3]):
                                click_element = button_name
                                # 记录选中的难度
                                difficulty_value = button_name.split("_")[1]
                                self.difficulty = difficulty_value
                                
                                # 设置难度对应的时间
                                if difficulty_value == "easy":
                                    self.difficulty_time = 60  # 60秒
                                    self.selected_option = 0
                                elif difficulty_value == "normal":
                                    self.difficulty_time = 45  # 45秒
                                    self.selected_option = 1
                                else:
                                    self.difficulty_time = 30  # 30秒
                                    self.selected_option = 2
                                
                                # 播放点击音效
                                self._play_sound("click")
                                
                                # 检查是否是双击
                                if (self.last_click_time and 
                                    current_time - self.last_click_time < 0.4 and 
                                    self.last_click_element == click_element):
                                    
                                    print(f"Double-click detected on {difficulty_value}")
                                    # 播放确认音效
                                    self._play_sound("difficulty_change")
                                    
                                    # 创建粒子效果
                                    color = COLORS["success"] if difficulty_value == "normal" else (
                                        COLORS["info"] if difficulty_value == "easy" else COLORS["warning"])
                                    for _ in range(15):
                                        self.celebration_particles.append(
                                            self.create_particle(x, y, color)
                                        )
                                    
                                    # 修改：选择难度后返回主菜单，而不是直接开始游戏
                                    self.transition_to("difficulty", "main")
                                    return True
                                break
                    
                    # 处理返回按钮
                    if x < 100 and y < 50:  # Back按钮区域
                        self._play_sound("click")
                        self.transition_to("difficulty", "main")
                        return True
                
                # 使用常规菜单输入处理其他情况
                if not click_element:  # 如果没有点击特定的难度选项
                    self.handle_menu_input(event, x, y)
                    return True
            
            # 处理游戏界面的点击
            elif self.current_menu == "game":
                # 游戏结束时的按钮处理
                if self.game_over:
                    # 检查所有按钮
                    for name, button in self.buttons.items():
                        if isinstance(button, tuple) and len(button) == 4:  # 确保是坐标元组
                            coords = button
                            # 检查点击是否在按钮范围内
                            if (coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]):
                                print(f"Game over button {name} clicked!")
                                # 播放按钮点击音效
                                self._play_sound("click")
                                # 设置按钮点击动画
                                self.button_click_animation[name] = time.time()
                                
                                # 处理不同按钮的操作
                                if name == "restart":
                                    # 重新开始游戏
                                    self.start_game()
                                    return True
                                elif name == "menu":
                                    # 返回主菜单
                                    self.transition_to("game", "main")
                                    return True
                    return True  # 即使没有点击任何按钮，也表示已处理此点击
                
                # 游戏进行中的按钮处理
                for name, button in self.buttons.items():
                    if isinstance(button, tuple) and len(button) == 4:  # 确保是坐标元组
                        coords = button
                        # 检查点击是否在按钮范围内
                        if (coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]):
                            print(f"Button {name} clicked!")
                            # 播放按钮点击音效
                            self._play_sound("click")
                            # 设置按钮点击动画
                            self.button_click_animation[name] = time.time()
                            
                            # 处理不同按钮的操作
                            if name == "quit":
                                # 修改为返回主菜单而不是退出游戏
                                self.transition_to("game", "main")
                                return True
                            elif name == "start" or name == "restart":
                                self.start_game()
                                return True
                            elif name == "next":
                                # 在Hard模式下检查点击限制
                                if self.difficulty == "hard" and self.next_clicks_remaining <= 0:
                                    # 播放错误音效提示玩家限制已用完
                                    self._play_sound("error")
                                    # 创建红色粒子提示玩家限制已用完
                                    for _ in range(10):
                                        self.celebration_particles.append(
                                            self.create_particle(x, y, COLORS["danger"])
                                        )
                                    print("Hard mode: No more Next clicks allowed!")
                                    return True
                                
                                # 如果是Hard模式且还有点击次数，减少计数
                                if self.difficulty == "hard":
                                    self.next_clicks_remaining -= 1
                                    print(f"Hard mode: {self.next_clicks_remaining} Next clicks remaining")
                                
                                # 选择新目标，继续游戏
                                self.target_found = False
                                self.select_random_target()
                                return True
                            elif name == "menu":
                                # 返回主菜单
                                self.transition_to("game", "main")
                                return True
            
            # 更新上次点击的状态
            self.last_click_time = current_time
            self.last_click_position = (x, y)
            self.last_click_element = click_element
            
            return False  # 表示此点击没有被处理
    
    def handle_mouse_move(self, event, x, y, flags, param):
        """Handle mouse movement events"""
        if event == cv2.EVENT_MOUSEMOVE:
            # Update button hover state
            self.button_hover = None
            for button_name, button in self.buttons.items():
                if not button["active"]:
                    continue
                if button["coords"][0] <= x <= button["coords"][2] and \
                   button["coords"][1] <= y <= button["coords"][3]:
                    self.button_hover = button_name
                    break
                    
    # 添加实用绘图函数
    def draw_rounded_rect(self, img, rect, color, radius=10, thickness=-1, line_type=cv2.LINE_AA):
        """绘制圆角矩形
        
        参数:
            img: 目标图像
            rect: 矩形坐标 (x1, y1, x2, y2)
            color: 颜色
            radius: 圆角半径
            thickness: 线宽，-1表示填充
            line_type: 线型
        """
        x1, y1, x2, y2 = rect
        
        # 确保最小尺寸
        if x2 - x1 < radius * 2 or y2 - y1 < radius * 2:
            radius = min((x2 - x1) // 2 - 1, (y2 - y1) // 2 - 1, radius)
        
        # 绘制填充矩形(排除圆角部分)
        if thickness < 0:
            # 中心部分
            cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1, line_type)
            cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1, line_type)
        else:
            # 只绘制边框
            cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness, line_type)
            cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness, line_type)
            cv2.line(img, (x1 + radius, y1 + radius), (x1, y2 - radius), color, thickness, line_type)
            cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness, line_type)
        
        # 绘制四个圆角
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness, line_type)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness, line_type)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness, line_type)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness, line_type)
        
        return img
    
    def create_glass_effect(self, frame, rect, color, alpha=0.7, blur=5, border_radius=10):
        """创建玻璃拟态效果
        
        参数:
            frame: 原始图像
            rect: 矩形区域 (x1, y1, x2, y2)
            color: 基础颜色 (B,G,R) 或 (B,G,R,A)
            alpha: 透明度
            blur: 模糊程度
            border_radius: 边框圆角
            
        返回:
            处理后的图像
        """
        x1, y1, x2, y2 = rect
        h, w = frame.shape[:2]
        
        # 确保坐标在图像范围内
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return frame
        
        # 提取区域并模糊
        roi = frame[y1:y2, x1:x2].copy()
        
        # 确保blur是正奇数
        if blur <= 0:
            blur = 5  # 默认值
        if blur % 2 == 0:
            blur += 1  # 如果是偶数，加1使其变为奇数
            
        blurred = cv2.GaussianBlur(roi, (blur, blur), 0)
        
        # 创建遮罩
        mask = np.zeros((y2-y1, x2-x1, 3), dtype=np.uint8)
        mask = self.draw_rounded_rect(mask, (0, 0, x2-x1, y2-y1), (255, 255, 255), border_radius)
        
        # 将颜色与模糊图像混合
        overlay = mask.copy()
        if len(color) == 3:
            overlay = self.draw_rounded_rect(overlay, (0, 0, x2-x1, y2-y1), color, border_radius)
            cv2.addWeighted(overlay, alpha, blurred, 1-alpha, 0, blurred)
        else:
            # 如果颜色包含alpha通道
            overlay = self.draw_rounded_rect(overlay, (0, 0, x2-x1, y2-y1), color[:3], border_radius)
            cv2.addWeighted(overlay, color[3]/255, blurred, 1-color[3]/255, 0, blurred)
        
        # 创建带圆角的遮罩
        mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        
        # 将处理后的ROI放回原图
        roi_result = frame[y1:y2, x1:x2]
        np.copyto(roi_result, blurred, where=mask>0)
        
        # 添加边框效果
        border_color = (255, 255, 255)
        self.draw_rounded_rect(frame, (x1, y1, x2, y2), border_color, border_radius, 1)
        
        return frame
    
    def create_gradient(self, frame, rect, color1, color2, vertical=True):
        """创建渐变效果
        
        参数:
            frame: 目标图像
            rect: 矩形区域 (x1, y1, x2, y2)
            color1: 起始颜色 (B,G,R)
            color2: 结束颜色 (B,G,R)
            vertical: 是否垂直渐变
            
        返回:
            带有渐变的图像
        """
        x1, y1, x2, y2 = rect
        h, w = frame.shape[:2]
        
        # 确保坐标在图像范围内
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return frame
        
        # 创建渐变蒙版
        gradient = np.zeros((y2-y1, x2-x1, 3), dtype=np.uint8)
        
        if vertical:
            # 垂直渐变
            for y in range(y2-y1):
                alpha = y / (y2-y1-1)
                g_color = [
                    int(color1[0] * (1 - alpha) + color2[0] * alpha),
                    int(color1[1] * (1 - alpha) + color2[1] * alpha),
                    int(color1[2] * (1 - alpha) + color2[2] * alpha)
                ]
                gradient[y, :] = g_color
        else:
            # 水平渐变
            for x in range(x2-x1):
                alpha = x / (x2-x1-1)
                g_color = [
                    int(color1[0] * (1 - alpha) + color2[0] * alpha),
                    int(color1[1] * (1 - alpha) + color2[1] * alpha),
                    int(color1[2] * (1 - alpha) + color2[2] * alpha)
                ]
                gradient[:, x] = g_color
        
        # 提取原区域
        roi = frame[y1:y2, x1:x2]
        
        # 将渐变和原图合并
        result = cv2.addWeighted(gradient, 0.7, roi, 0.3, 0)
        
        # 放回原图
        frame[y1:y2, x1:x2] = result
        
        return frame
                    
    def get_center_x(self):
        """获取窗口水平中心坐标"""
        if hasattr(self, 'window'):
            return self.window.width // 2
        return CAMERA_WIDTH // 2

    def get_center_y(self):
        """获取窗口垂直中心坐标"""
        if hasattr(self, 'window'):
            return self.window.height // 2
        return CAMERA_HEIGHT // 2
    
    def handle_button_hover(self, mouse_x, mouse_y):
        """Handle button hover state"""
        hover = None
        for button_name, button in self.buttons.items():
            if isinstance(button, dict) and "coords" in button:
                x1, y1, x2, y2 = button["coords"]
            else:
                x1, y1, x2, y2 = button

            if x1 <= mouse_x <= x2 and y1 <= mouse_y <= y2:
                hover = button_name
                break
                
        if hover != self.button_hover:
            self.button_hover = hover
            if hover is not None:
                self.play_sound('hover')
                    
    def play_sound(self, sound_name):
        """别名，用于向后兼容"""
        self._play_sound(sound_name)

if __name__ == "__main__":
    try:
        print("Starting Object Finder Game...")
        game = Game()
        game.run()
        print("Game exited normally")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
