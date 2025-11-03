"""
运动传感器实现
模拟PIR运动检测传感器
"""

import random
from datetime import datetime, timedelta

class MotionSensor:
    """运动传感器"""
    
    def __init__(self, sensor_id, location, sensor_model="HC-SR501"):
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = "motion"
        self.sensor_model = sensor_model
        self.unit = "detection"
        self.last_motion_time = None
        self.motion_count = 0
        
    def detect_motion(self):
        """检测运动"""
        current_time = datetime.now()
        hour = current_time.hour
        
        # 运动概率基于时间（白天活动多，夜晚活动少）
        base_probability = 0.1  # 基础概率
        
        if 8 <= hour <= 12:  # 上午活跃
            base_probability = 0.3
        elif 14 <= hour <= 18:  # 下午活跃
            base_probability = 0.4
        elif 19 <= hour <= 22:  # 晚上较活跃
            base_probability = 0.2
        else:  # 深夜
            base_probability = 0.05
        
        # 随机决定是否检测到运动
        motion_detected = random.random() < base_probability
        
        if motion_detected:
            self.last_motion_time = current_time
            self.motion_count += 1
            
            # 模拟持续运动（一旦检测到，短时间内可能持续）
            if random.random() < 0.7:  # 70%概率持续运动
                self.last_motion_time = current_time + timedelta(seconds=random.randint(5, 30))
        
        return motion_detected
    
    def get_motion_status(self):
        """获取运动状态"""
        current_time = datetime.now()
        
        # 检查是否有近期运动
        if self.last_motion_time:
            time_since_last_motion = (current_time - self.last_motion_time).total_seconds()
            
            # 如果最近30秒内有运动，认为仍在运动
            if time_since_last_motion <= 30:
                return True
        
        # 随机检测当前运动
        return self.detect_motion()
    
    def get_motion_data(self):
        """获取运动数据"""
        motion_detected = self.get_motion_status()
        
        return {
            'motion_detected': motion_detected,
            'last_motion_time': self.last_motion_time.isoformat() if self.last_motion_time else None,
            'motion_count_today': self.motion_count,
            'sensitivity': 'medium'  # 可以调整的灵敏度
        }
    
    def reset_counter(self):
        """重置计数器"""
        self.motion_count = 0
    
    def get_sensor_info(self):
        """获取传感器信息"""
        return {
            'id': self.sensor_id,
            'name': f'运动传感器-{self.sensor_id.split("_")[-1]}',
            'type': self.sensor_type,
            'model': self.sensor_model,
            'location': self.location,
            'unit': self.unit,
            'motion_count_today': self.motion_count,
            'last_motion': self.last_motion_time.isoformat() if self.last_motion_time else '无',
            'status': 'online'
        }