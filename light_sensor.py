"""
光照传感器实现
模拟BH1750等光照传感器
"""

import random
from datetime import datetime

class LightSensor:
    """光照传感器"""
    
    def __init__(self, sensor_id, location, sensor_model="BH1750"):
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = "light"
        self.sensor_model = sensor_model
        self.unit = "lux"
        self.measurement_range = (0, 65535)  # BH1750测量范围
    
    def read_light_intensity(self):
        """读取光照强度"""
        current_time = datetime.now()
        hour = current_time.hour
        month = current_time.month
        
        # 基础光照强度（基于时间和季节）
        if 6 <= hour <= 18:  # 白天
            # 正弦曲线模拟太阳位置
            progress = (hour - 6) / 12.0
            light_intensity = 800 * abs((progress - 0.5) * 2) + 200
            
            # 季节调整（夏季光照更强）
            if 5 <= month <= 8:  # 夏季
                light_intensity *= 1.3
            elif 11 <= month or month <= 2:  # 冬季
                light_intensity *= 0.7
        else:  # 夜晚
            # 基础环境光 + 月光/人造光
            light_intensity = random.randint(10, 50)
        
        # 天气影响（随机模拟）
        weather_effect = random.choice([
            1.0,   # 晴天
            0.6,   # 多云
            0.3,   # 阴天
            0.2    # 雨天
        ])
        
        light_intensity *= weather_effect
        
        # 随机波动
        light_intensity += random.randint(-30, 30)
        
        # 确保在合理范围内
        light_intensity = max(0, min(2000, light_intensity))
        
        return int(light_intensity)
    
    def read_light(self):
        """兼容性方法"""
        return self.read_light_intensity()
    
    def get_sensor_info(self):
        """获取传感器信息"""
        return {
            'id': self.sensor_id,
            'name': f'光照传感器-{self.sensor_id.split("_")[-1]}',
            'type': self.sensor_type,
            'model': self.sensor_model,
            'location': self.location,
            'unit': self.unit,
            'measurement_range': f"{self.measurement_range[0]}-{self.measurement_range[1]} {self.unit}",
            'status': 'online'
        }