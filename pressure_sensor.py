"""
压力传感器实现
模拟BMP280等压力传感器
"""

import random
from datetime import datetime

class PressureSensor:
    """压力传感器"""
    
    def __init__(self, sensor_id, location, sensor_model="BMP280"):
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = "pressure"
        self.sensor_model = sensor_model
        self.unit = "hPa"
        self.calibration_offset = random.uniform(-2, 2)
    
    def read_pressure(self):
        """读取压力数据"""
        # 模拟真实压力传感器读数
        base_pressure = 1013.25  # 标准大气压
        
        # 模拟天气变化影响
        hour = datetime.now().hour
        day_of_year = datetime.now().timetuple().tm_yday
        
        # 季节性变化（简化模型）
        seasonal_variation = 0
        if 80 <= day_of_year <= 170:  # 春季
            seasonal_variation = -5
        elif 171 <= day_of_year <= 265:  # 夏季
            seasonal_variation = -8
        elif 266 <= day_of_year <= 355:  # 秋季
            seasonal_variation = -3
        else:  # 冬季
            seasonal_variation = 2
        
        # 日内波动
        daily_variation = 0
        if 2 <= hour <= 6:  # 凌晨最低
            daily_variation = -1
        elif 14 <= hour <= 16:  # 下午最高
            daily_variation = 1
        
        # 随机波动和校准偏移
        random_variation = random.uniform(-0.5, 0.5)
        
        pressure = base_pressure + seasonal_variation + daily_variation + random_variation + self.calibration_offset
        
        return round(pressure, 2)
    
    def get_sensor_info(self):
        """获取传感器信息"""
        return {
            'id': self.sensor_id,
            'name': f'压力传感器-{self.sensor_id.split("_")[-1]}',
            'type': self.sensor_type,
            'model': self.sensor_model,
            'location': self.location,
            'unit': self.unit,
            'calibration_offset': round(self.calibration_offset, 2),
            'status': 'online'
        }
    
    def calibrate(self, reference_pressure):
        """校准传感器"""
        current_reading = self.read_pressure()
        self.calibration_offset = reference_pressure - current_reading
        return self.calibration_offset