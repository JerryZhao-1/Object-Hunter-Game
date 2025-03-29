"""
DirectShow摄像头接口 - 提供更稳定的摄像头访问
"""
import cv2
import os
import time
import numpy as np

class DirectCamera:
    """DirectShow摄像头包装类"""
    
    def __init__(self, camera_index=0, width=1280, height=720, fallback=True):
        """初始化摄像头接口
        
        参数:
            camera_index: 摄像头索引（默认0）
            width: 期望的宽度
            height: 期望的高度
            fallback: 是否在DirectShow失败时尝试其他方法
        """
        self.camera = None
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fallback = fallback
        self.last_frame = None
        self.frame_count = 0
        self.retry_count = 0
        self.max_retries = 5
        self.initialized = False
        
        # 尝试设置环境变量优化摄像头访问
        os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "1"  # 优先MSMF
        os.environ["OPENCV_VIDEOIO_PRIORITY_DSHOW"] = "2"  # 次优先DirectShow
        
        # 尝试初始化摄像头
        self.initialize()
    
    def initialize(self):
        """初始化摄像头连接"""
        try:
            # 关闭任何现有连接
            self.release()
            
            # 先尝试使用DirectShow
            if os.name == 'nt':
                print(f"尝试使用DirectShow打开摄像头 #{self.camera_index}...")
                self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                
                # 设置分辨率
                if self.camera.isOpened():
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减小缓冲区大小，降低延迟
                    print(f"成功使用DirectShow打开摄像头 #{self.camera_index}")
                    self.initialized = True
                    return True
                else:
                    print(f"使用DirectShow打开摄像头 #{self.camera_index} 失败")
            
            # 如果DirectShow失败或不是Windows，尝试默认方法
            if self.fallback and (not self.camera or not self.camera.isOpened()):
                print(f"尝试使用默认方法打开摄像头 #{self.camera_index}...")
                self.camera = cv2.VideoCapture(self.camera_index)
                
                # 设置分辨率
                if self.camera.isOpened():
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    print(f"成功使用默认方法打开摄像头 #{self.camera_index}")
                    self.initialized = True
                    return True
                else:
                    print(f"使用默认方法打开摄像头 #{self.camera_index} 失败")
            
            # 尝试其他索引
            if self.fallback and (not self.camera or not self.camera.isOpened()):
                for idx in range(3):
                    if idx == self.camera_index:
                        continue
                        
                    print(f"尝试打开摄像头 #{idx}...")
                    self.camera = cv2.VideoCapture(idx)
                    
                    if self.camera.isOpened():
                        print(f"成功打开摄像头 #{idx}")
                        self.camera_index = idx
                        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                        self.initialized = True
                        return True
            
            # 所有方法都失败
            if not self.camera or not self.camera.isOpened():
                print("无法打开任何摄像头")
                self.initialized = False
                return False
            
            return self.camera.isOpened()
            
        except Exception as e:
            print(f"初始化摄像头时出错: {e}")
            self.initialized = False
            return False
    
    def read(self):
        """读取一帧
        
        返回:
            成功: (True, frame)
            失败: (False, black_frame)
        """
        # 检查摄像头是否初始化
        if not self.initialized or not self.camera or not self.camera.isOpened():
            self.retry_count += 1
            if self.retry_count <= self.max_retries:
                print(f"摄像头未初始化，重试 ({self.retry_count}/{self.max_retries})...")
                self.initialize()
            
            # 返回黑帧
            black_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(black_frame, "摄像头未连接", (self.width//2-100, self.height//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return False, black_frame
        
        # 重置重试计数
        self.retry_count = 0
        
        try:
            # 读取帧
            ret, frame = self.camera.read()
            
            # 增加帧计数
            self.frame_count += 1
            
            if ret and frame is not None and frame.size > 0:
                # 保存最后一帧
                self.last_frame = frame
                return True, frame
            else:
                print(f"读取帧失败 (帧 #{self.frame_count})")
                
                # 如果有最后一帧，返回它
                if self.last_frame is not None:
                    return False, self.last_frame
                
                # 否则返回黑帧
                black_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                cv2.putText(black_frame, "摄像头未连接", (self.width//2-100, self.height//2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                return False, black_frame
                
        except Exception as e:
            print(f"读取帧时出错: {e}")
            
            # 尝试重新初始化摄像头
            print("尝试重新初始化摄像头...")
            self.initialize()
            
            # 返回黑帧
            black_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(black_frame, f"摄像头错误: {str(e)[:30]}", (self.width//2-150, self.height//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return False, black_frame
    
    def release(self):
        """释放摄像头资源"""
        if self.camera is not None:
            try:
                self.camera.release()
                print("摄像头资源已释放")
            except Exception as e:
                print(f"释放摄像头资源时出错: {e}")
        
        self.camera = None
        self.initialized = False
    
    def __del__(self):
        """析构函数，确保释放资源"""
        self.release()
    
    def is_opened(self):
        """检查摄像头是否打开"""
        return self.initialized and self.camera is not None and self.camera.isOpened()
    
    def get_resolution(self):
        """获取当前摄像头分辨率"""
        if not self.is_opened():
            return self.width, self.height
            
        try:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        except:
            return self.width, self.height 