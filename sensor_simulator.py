import time
import random
from datetime import datetime
import serial
import threading

class SensorSimulator:
    """传感器模拟器 - 生成真实的物理数据流"""
    
    def __init__(self):
        self.simulated_ports = {}
        self.data_streams = {}
        self.running = False
        
    def start_simulation(self):
        """启动传感器模拟"""
        print("🎮 启动传感器模拟器...")
        self.running = True
        
        # 创建模拟的串口数据流
        self.create_simulated_sensors()
        
        # 启动数据生成线程
        self.simulation_thread = threading.Thread(target=self._generate_sensor_data, daemon=True)
        self.simulation_thread.start()
        
        print("✅ 传感器模拟器运行中 - 生成真实物理数据流")
    
    def create_simulated_sensors(self):
        """创建模拟传感器"""
        # 模拟温度传感器 (DS18B20风格)
        self.data_streams['temp_sensor'] = {
            'type': 'temperature',
            'base_value': 22.0,
            'variation': 2.0,
            'trend': 0.1,
            'unit': '°C'
        }
        
        # 模拟湿度传感器 (DHT22风格)
        self.data_streams['humidity_sensor'] = {
            'type': 'humidity', 
            'base_value': 55.0,
            'variation': 10.0,
            'trend': 0.05,
            'unit': '%'
        }
        
        # 模拟光照传感器 (BH1750风格)
        self.data_streams['light_sensor'] = {
            'type': 'light',
            'base_value': 500,
            'variation': 200,
            'trend': 10,
            'unit': 'lux'
        }
        
        # 模拟压力传感器 (BMP280风格)
        self.data_streams['pressure_sensor'] = {
            'type': 'pressure',
            'base_value': 1013.25,
            'variation': 5.0,
            'trend': 0.1,
            'unit': 'hPa'
        }
    
    def _generate_sensor_data(self):
        """生成模拟传感器数据"""
        while self.running:
            try:
                # 模拟真实的物理过程
                current_time = datetime.now()
                hour = current_time.hour
                
                # 温度 - 模拟日夜变化
                temp_base = 22.0
                if 6 <= hour <= 18:  # 白天升温
                    temp_base += (hour - 6) * 0.5
                else:  # 夜晚降温
                    temp_base -= min((hour - 18) % 24, 6) * 0.3
                
                temp_variation = random.uniform(-0.5, 0.5)
                temperature = round(temp_base + temp_variation, 1)
                
                # 湿度 - 与温度负相关
                humidity_base = 60.0 - (temperature - 22.0) * 2
                humidity_variation = random.uniform(-3, 3)
                humidity = max(20, min(90, round(humidity_base + humidity_variation, 1)))
                
                # 光照 - 模拟太阳位置
                if 6 <= hour <= 18:
                    # 正弦曲线模拟太阳光照
                    progress = (hour - 6) / 12.0
                    light_intensity = int(800 * abs((progress - 0.5) * 2) + 200)
                else:
                    light_intensity = random.randint(50, 150)  # 夜晚基础光照
                
                light_variation = random.randint(-50, 50)
                light = max(0, light_intensity + light_variation)
                
                # 压力 - 缓慢变化
                pressure_base = 1013.25 + random.uniform(-2, 2)
                pressure = round(pressure_base, 1)
                
                # 更新数据流
                self.data_streams['temp_sensor']['current_value'] = temperature
                self.data_streams['humidity_sensor']['current_value'] = humidity
                self.data_streams['light_sensor']['current_value'] = light
                self.data_streams['pressure_sensor']['current_value'] = pressure
                
                # 模拟真实传感器的数据延迟
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 传感器模拟错误: {e}")
                time.sleep(5)
    
    def read_temperature(self):
        """读取模拟温度数据"""
        if 'temp_sensor' in self.data_streams:
            return self.data_streams['temp_sensor']['current_value']
        return None
    
    def read_humidity(self):
        """读取模拟湿度数据"""
        if 'humidity_sensor' in self.data_streams:
            return self.data_streams['humidity_sensor']['current_value']
        return None
    
    def read_light(self):
        """读取模拟光照数据"""
        if 'light_sensor' in self.data_streams:
            return self.data_streams['light_sensor']['current_value']
        return None
    
    def read_pressure(self):
        """读取模拟压力数据"""
        if 'pressure_sensor' in self.data_streams:
            return self.data_streams['pressure_sensor']['current_value']
        return None
    
    def stop_simulation(self):
        """停止模拟"""
        self.running = False
        print("🛑 传感器模拟器已停止")