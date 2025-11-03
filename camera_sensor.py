"""
摄像头传感器实现
支持真实摄像头和模拟图像生成
"""

import cv2
import numpy as np
from datetime import datetime
import os
import json
import random
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class CameraSensor:
    """摄像头传感器"""
    
    def __init__(self, sensor_id, location, camera_index=0, mode='simulation'):
        """
        初始化摄像头传感器
        
        Args:
            sensor_id: 传感器ID
            location: 安装位置
            camera_index: 摄像头索引（0=默认摄像头）
            mode: 运行模式 ('real'=真实摄像头, 'simulation'=模拟模式)
        """
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = "camera"
        self.unit = "image"
        self.camera_index = camera_index
        self.mode = mode
        self.cap = None
        self.frame_count = 0
        self.last_capture_time = None
        
        # 模拟数据参数
        self.simulation_scenes = ['office', 'laboratory', 'outdoor', 'night']
        self.current_scene = 'laboratory'
        
        # 初始化摄像头
        if mode == 'real':
            self._initialize_real_camera()
        else:
            print(f"🎮 摄像头 {sensor_id} 运行在模拟模式")
    
    def _initialize_real_camera(self):
        """初始化真实摄像头"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"❌ 无法打开摄像头 {self.camera_index}，切换到模拟模式")
                self.mode = 'simulation'
                self.cap = None
            else:
                # 设置摄像头参数
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                print(f"✅ 摄像头 {self.camera_index} 初始化成功")
                
        except Exception as e:
            print(f"❌ 摄像头初始化失败: {e}")
            self.mode = 'simulation'
            self.cap = None
    
    def _generate_simulation_frame(self, width=640, height=480):
        """生成模拟摄像头帧"""
        # 创建空白图像
        if self.current_scene == 'office':
            # 办公室场景 - 偏亮的背景
            background_color = (240, 240, 245)  # 浅灰色
            text_color = (50, 50, 50)  # 深灰色
        elif self.current_scene == 'laboratory':
            # 实验室场景 - 偏冷的背景
            background_color = (220, 240, 255)  # 浅蓝色
            text_color = (30, 80, 120)  # 深蓝色
        elif self.current_scene == 'outdoor':
            # 户外场景 - 偏暖的背景
            background_color = (255, 245, 235)  # 浅黄色
            text_color = (100, 70, 30)  # 棕色
        else:  # night
            # 夜晚场景 - 暗色背景
            background_color = (50, 50, 70)  # 深蓝色
            text_color = (200, 200, 220)  # 浅灰色
        
        # 创建PIL图像
        pil_image = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(pil_image)
        
        # 添加一些随机元素模拟真实场景
        self._add_simulation_elements(draw, width, height)
        
        # 添加时间戳和信息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info_text = f"摄像头: {self.sensor_id} | 位置: {self.location} | 场景: {self.current_scene}"
        
        # 添加文字（简化版，不使用字体文件）
        draw.rectangle([10, 10, width-10, 50], fill=(0, 0, 0, 128))
        draw.text((15, 15), timestamp, fill=(255, 255, 255))
        draw.text((15, 35), info_text, fill=(200, 200, 255))
        
        # 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return cv_image
    
    def _add_simulation_elements(self, draw, width, height):
        """添加模拟场景元素"""
        # 随机添加一些矩形模拟物体
        for _ in range(random.randint(3, 8)):
            x1 = random.randint(0, width-100)
            y1 = random.randint(0, height-100)
            x2 = x1 + random.randint(50, 150)
            y2 = y1 + random.randint(50, 150)
            
            color = (
                random.randint(50, 200),
                random.randint(50, 200), 
                random.randint(50, 200)
            )
            
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=(0, 0, 0), width=2)
        
        # 添加一些线条模拟边缘
        for _ in range(random.randint(2, 5)):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            
            draw.line([x1, y1, x2, y2], fill=(100, 100, 100), width=2)
    
    def capture_frame(self, save_to_file=False, save_path="captures"):
        """捕获一帧图像"""
        try:
            if self.mode == 'real' and self.cap and self.cap.isOpened():
                # 从真实摄像头捕获
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ 无法从摄像头读取帧")
                    return None
            else:
                # 生成模拟帧
                frame = self._generate_simulation_frame()
            
            self.frame_count += 1
            self.last_capture_time = datetime.now()
            
            # 如果需要保存到文件
            if save_to_file:
                self._save_frame_to_file(frame, save_path)
            
            return frame
            
        except Exception as e:
            print(f"❌ 捕获图像失败: {e}")
            return None
    
    def _save_frame_to_file(self, frame, save_path):
        """保存帧到文件"""
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.sensor_id}_{timestamp}.jpg"
            filepath = os.path.join(save_path, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"✅ 图像已保存: {filepath}")
            
        except Exception as e:
            print(f"❌ 保存图像失败: {e}")
    
    def capture_image(self, return_base64=False, analyze_image=True):
        """捕获图像（兼容性方法）"""
        frame = self.capture_frame()
        if frame is None:
            return None
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'frame_info': self.get_frame_info(frame),
            'sensor_id': self.sensor_id,
            'location': self.location
        }
        
        if analyze_image:
            result['analysis'] = self.analyze_frame(frame)
        
        if return_base64:
            result['image_base64'] = self.frame_to_base64(frame)
        
        return result
    
    def get_frame_info(self, frame):
        """获取帧信息"""
        if frame is None:
            return None
            
        height, width, channels = frame.shape
        
        # 计算一些基本图像统计
        avg_brightness = np.mean(frame)
        contrast = np.std(frame)
        
        # 转换为HSV计算饱和度
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        avg_saturation = np.mean(hsv_frame[:, :, 1])
        
        return {
            'resolution': f"{width}x{height}",
            'channels': channels,
            'file_size_estimate': width * height * channels,  # 字节估算
            'brightness': round(avg_brightness, 2),
            'contrast': round(contrast, 2),
            'saturation': round(avg_saturation, 2),
            'frame_count': self.frame_count
        }
    
    def analyze_frame(self, frame):
        """分析图像帧"""
        if frame is None:
            return None
        
        try:
            analysis = {}
            
            # 转换为灰度图
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 运动检测（简单版 - 与上一帧比较）
            if hasattr(self, 'previous_frame'):
                # 计算帧差异
                frame_diff = cv2.absdiff(self.previous_frame, gray_frame)
                motion_level = np.mean(frame_diff)
                analysis['motion_detected'] = motion_level > 10  # 阈值
                analysis['motion_level'] = round(motion_level, 2)
            else:
                analysis['motion_detected'] = False
                analysis['motion_level'] = 0
            
            self.previous_frame = gray_frame
            
            # 边缘检测
            edges = cv2.Canny(gray_frame, 50, 150)
            analysis['edge_density'] = round(np.sum(edges > 0) / edges.size, 4)
            
            # 亮度分析
            brightness = np.mean(gray_frame)
            analysis['brightness_category'] = self._categorize_brightness(brightness)
            
            # 场景识别（简化版）
            analysis['scene_guess'] = self._guess_scene(frame)
            
            return analysis
            
        except Exception as e:
            print(f"❌ 图像分析失败: {e}")
            return None
    
    def _categorize_brightness(self, brightness):
        """分类亮度水平"""
        if brightness < 50:
            return "dark"
        elif brightness < 100:
            return "dim" 
        elif brightness < 150:
            return "normal"
        elif brightness < 200:
            return "bright"
        else:
            return "very_bright"
    
    def _guess_scene(self, frame):
        """猜测场景类型（简化版）"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 分析颜色分布
        avg_saturation = np.mean(hsv[:, :, 1])
        avg_value = np.mean(hsv[:, :, 2])
        
        if avg_value < 50:
            return "night"
        elif avg_saturation < 50:
            return "office"
        elif avg_value > 180:
            return "outdoor"
        else:
            return "laboratory"
    
    def frame_to_base64(self, frame):
        """将帧转换为base64字符串"""
        try:
            # 调整图像大小以减少数据量
            small_frame = cv2.resize(frame, (320, 240))
            
            # 编码为JPEG
            retval, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            
            if retval:
                # 转换为base64
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                return f"data:image/jpeg;base64,{jpg_as_text}"
            else:
                return None
                
        except Exception as e:
            print(f"❌ 图像编码失败: {e}")
            return None
    
    def change_scene(self, scene_name):
        """更改模拟场景"""
        if scene_name in self.simulation_scenes:
            self.current_scene = scene_name
            print(f"🔄 摄像头 {self.sensor_id} 场景更改为: {scene_name}")
            return True
        else:
            print(f"❌ 未知场景: {scene_name}")
            return False
    
    def get_sensor_info(self):
        """获取传感器信息"""
        status = 'online'
        if self.mode == 'real':
            status = 'online' if self.cap and self.cap.isOpened() else 'offline'
        
        return {
            'id': self.sensor_id,
            'name': f'摄像头-{self.sensor_id.split("_")[-1]}',
            'type': self.sensor_type,
            'location': self.location,
            'mode': self.mode,
            'status': status,
            'unit': self.unit,
            'frame_count': self.frame_count,
            'last_capture': self.last_capture_time.isoformat() if self.last_capture_time else '从未捕获',
            'available_scenes': self.simulation_scenes,
            'current_scene': self.current_scene
        }
    
    def start_continuous_capture(self, interval=5, duration=60):
        """开始连续捕获（用于监控）"""
        print(f"📹 开始连续捕获，间隔: {interval}秒，时长: {duration}秒")
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < duration:
            result = self.capture_image(analyze_image=True)
            if result:
                print(f"📸 捕获成功 - 运动: {result['analysis']['motion_detected']}")
            
            time.sleep(interval)
        
        print("🛑 连续捕获结束")
    
    def release(self):
        """释放摄像头资源"""
        if self.cap:
            self.cap.release()
            self.cap = None
            print(f"🔒 摄像头 {self.sensor_id} 资源已释放")

# 测试函数
def test_camera_sensor():
    """测试摄像头传感器"""
    print("测试摄像头传感器...")
    
    # 测试模拟模式
    camera = CameraSensor("camera_001", "实验室入口", mode='simulation')
    
    # 获取传感器信息
    info = camera.get_sensor_info()
    print("传感器信息:", json.dumps(info, indent=2, ensure_ascii=False))
    
    # 捕获测试图像
    for i in range(3):
        result = camera.capture_image(analyze_image=True)
        if result:
            print(f"捕获 #{i+1}:")
            print(f"  分辨率: {result['frame_info']['resolution']}")
            print(f"  亮度: {result['frame_info']['brightness']}")
            print(f"  运动检测: {result['analysis']['motion_detected']}")
        
        # 切换场景
        if i == 1:
            camera.change_scene('night')
    
    camera.release()

if __name__ == "__main__":
    test_camera_sensor()