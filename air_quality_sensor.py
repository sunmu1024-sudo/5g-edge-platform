"""
空气质量传感器实现
模拟PM2.5、CO2等空气质量传感器
"""

import random
from datetime import datetime

class AirQualitySensor:
    """空气质量传感器"""
    
    def __init__(self, sensor_id, location, sensor_model="PMS5003"):
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = "air_quality"
        self.sensor_model = sensor_model
        self.unit = "AQI"
        self.pollutants = ['PM2.5', 'PM10', 'CO2', 'VOC']
    
    def read_air_quality(self):
        """读取空气质量数据"""
        current_time = datetime.now()
        hour = current_time.hour
        weekday = current_time.weekday()
        
        # 基础空气质量（基于时间和星期）
        base_aqi = 50  # 良好空气质量
        
        # 交通高峰时段空气质量较差
        if (7 <= hour <= 9) or (17 <= hour <= 19):  # 早晚高峰
            base_aqi += random.randint(20, 40)
        
        # 工作日空气质量较差
        if weekday < 5:  # 周一到周五
            base_aqi += random.randint(10, 20)
        
        # 随机事件影响
        event_effect = random.choice([
            0,    # 无事件
            30,   # 轻度污染
            60,   # 中度污染
            -20   # 空气质量改善（如降雨后）
        ])
        
        aqi = base_aqi + event_effect + random.randint(-5, 5)
        
        # 确保在合理范围内
        aqi = max(0, min(500, aqi))
        
        return int(aqi)
    
    def read_pollutant_levels(self):
        """读取各污染物浓度"""
        aqi = self.read_air_quality()
        
        # 基于AQI计算各污染物浓度
        pollutants = {}
        for pollutant in self.pollutants:
            if pollutant == 'PM2.5':
                # AQI到PM2.5的近似转换
                concentration = round(aqi * 0.5 + random.uniform(-5, 5), 1)
            elif pollutant == 'PM10':
                concentration = round(aqi * 0.8 + random.uniform(-8, 8), 1)
            elif pollutant == 'CO2':
                concentration = 400 + aqi * 2 + random.randint(-20, 20)
            elif pollutant == 'VOC':
                concentration = round(aqi * 0.1 + random.uniform(-0.5, 0.5), 2)
            
            pollutants[pollutant] = max(0, concentration)
        
        return pollutants
    
    def get_air_quality_level(self, aqi):
        """根据AQI获取空气质量等级"""
        if aqi <= 50:
            return '优', 'green'
        elif aqi <= 100:
            return '良', 'blue'
        elif aqi <= 150:
            return '轻度污染', 'yellow'
        elif aqi <= 200:
            return '中度污染', 'orange'
        elif aqi <= 300:
            return '重度污染', 'red'
        else:
            return '严重污染', 'purple'
    
    def get_sensor_info(self):
        """获取传感器信息"""
        current_aqi = self.read_air_quality()
        level, color = self.get_air_quality_level(current_aqi)
        
        return {
            'id': self.sensor_id,
            'name': f'空气质量传感器-{self.sensor_id.split("_")[-1]}',
            'type': self.sensor_type,
            'model': self.sensor_model,
            'location': self.location,
            'unit': self.unit,
            'current_aqi': current_aqi,
            'air_quality_level': level,
            'pollutants_monitored': self.pollutants,
            'status': 'online'
        }