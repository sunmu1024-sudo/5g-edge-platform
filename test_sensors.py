#!/usr/bin/env python3
"""
传感器测试脚本
测试所有传感器功能
"""

import time
from datetime import datetime
from temperature_sensor import TemperatureSensor
from humidity_sensor import HumiditySensor
from pressure_sensor import PressureSensor
from light_sensor import LightSensor
from air_quality_sensor import AirQualitySensor
from motion_sensor import MotionSensor

def test_temperature_sensor():
    """测试温度传感器"""
    print("🌡️ 测试温度传感器...")
    sensor = TemperatureSensor("test_temp", "测试位置")
    
    for i in range(5):
        temp = sensor.read_temperature()
        info = sensor.get_sensor_info()
        print(f"  读数 {i+1}: {temp}°C - {info}")
        time.sleep(1)

def test_humidity_sensor():
    """测试湿度传感器"""
    print("💧 测试湿度传感器...")
    sensor = HumiditySensor("test_humidity", "测试位置")
    
    for i in range(5):
        humidity = sensor.read_humidity()
        info = sensor.get_sensor_info()
        print(f"  读数 {i+1}: {humidity}% - {info}")
        time.sleep(1)

def test_pressure_sensor():
    """测试压力传感器"""
    print("📊 测试压力传感器...")
    sensor = PressureSensor("test_pressure", "测试位置")
    
    for i in range(5):
        pressure = sensor.read_pressure()
        info = sensor.get_sensor_info()
        print(f"  读数 {i+1}: {pressure} hPa - {info}")
        time.sleep(1)

def test_light_sensor():
    """测试光照传感器"""
    print("💡 测试光照传感器...")
    sensor = LightSensor("test_light", "测试位置")
    
    for i in range(5):
        light = sensor.read_light_intensity()
        info = sensor.get_sensor_info()
        print(f"  读数 {i+1}: {light} lux - {info}")
        time.sleep(1)

def test_air_quality_sensor():
    """测试空气质量传感器"""
    print("🌫️ 测试空气质量传感器...")
    sensor = AirQualitySensor("test_air", "测试位置")
    
    for i in range(5):
        aqi = sensor.read_air_quality()
        pollutants = sensor.read_pollutant_levels()
        info = sensor.get_sensor_info()
        print(f"  读数 {i+1}: AQI {aqi}")
        print(f"    污染物: {pollutants}")
        time.sleep(1)

def test_motion_sensor():
    """测试运动传感器"""
    print("🚶 测试运动传感器...")
    sensor = MotionSensor("test_motion", "测试位置")
    
    for i in range(10):
        motion_data = sensor.get_motion_data()
        info = sensor.get_sensor_info()
        status = "检测到运动" if motion_data['motion_detected'] else "无运动"
        print(f"  检测 {i+1}: {status} - 计数: {motion_data['motion_count_today']}")
        time.sleep(2)

def test_sensor_factory():
    """测试传感器工厂"""
    print("🏭 测试传感器工厂...")
    from sensors import SensorFactory
    
    # 测试创建各种传感器
    sensor_types = ['temperature', 'humidity', 'light', 'pressure']
    
    for sensor_type in sensor_types:
        try:
            sensor = SensorFactory.create_sensor(sensor_type, f"factory_{sensor_type}", "工厂测试位置")
            info = sensor.get_sensor_info()
            print(f"  ✅ 创建 {sensor_type}: {info['name']}")
        except Exception as e:
            print(f"  ❌ 创建 {sensor_type} 失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 传感器测试套件")
    print("=" * 50)
    
    # 运行所有测试
    test_temperature_sensor()
    test_humidity_sensor() 
    test_pressure_sensor()
    test_light_sensor()
    test_air_quality_sensor()
    test_motion_sensor()
    test_sensor_factory()
    
    print("=" * 50)
    print("✅ 所有测试完成!")
    print("=" * 50)