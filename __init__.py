"""
传感器模块入口
提供统一的传感器接口
"""

from .temperature_sensor import TemperatureSensor
from .humidity_sensor import HumiditySensor
from .camera_sensor import CameraSensor
from .pressure_sensor import PressureSensor
from .light_sensor import LightSensor
from .air_quality_sensor import AirQualitySensor
from .motion_sensor import MotionSensor

# 传感器工厂类
class SensorFactory:
    """传感器工厂"""
    
    @staticmethod
    def create_sensor(sensor_type, sensor_id, location, **kwargs):
        """创建传感器实例"""
        sensor_classes = {
            'temperature': TemperatureSensor,
            'humidity': HumiditySensor,
            'camera': CameraSensor,
            'pressure': PressureSensor,
            'light': LightSensor,
            'air_quality': AirQualitySensor,
            'motion': MotionSensor
        }
        
        sensor_class = sensor_classes.get(sensor_type)
        if sensor_class:
            return sensor_class(sensor_id, location, **kwargs)
        else:
            raise ValueError(f"不支持的传感器类型: {sensor_type}")
    
    @staticmethod
    def get_available_sensor_types():
        """获取可用的传感器类型"""
        return {
            'temperature': '温度传感器',
            'humidity': '湿度传感器',
            'camera': '摄像头',
            'pressure': '压力传感器', 
            'light': '光照传感器',
            'air_quality': '空气质量传感器',
            'motion': '运动传感器'
        }

# 导出主要类
__all__ = [
    'TemperatureSensor',
    'HumiditySensor', 
    'CameraSensor',
    'PressureSensor',
    'LightSensor',
    'AirQualitySensor',
    'MotionSensor',
    'SensorFactory'
]