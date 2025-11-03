"""
湿度传感器实现
支持DHT22、DHT11等湿度传感器的模拟和真实连接
"""

import random
import time
from datetime import datetime
import os
import json

class HumiditySensor:
    """湿度传感器"""
    
    def __init__(self, sensor_id, location, sensor_model="DHT22", mode='simulation'):
        """
        初始化湿度传感器
        
        Args:
            sensor_id: 传感器ID
            location: 安装位置
            sensor_model: 传感器型号 (DHT22, DHT11, SHT31等)
            mode: 运行模式 ('real'=真实传感器, 'simulation'=模拟模式)
        """
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = "humidity"
        self.sensor_model = sensor_model
        self.mode = mode
        self.unit = "%"
        
        # 校准参数
        self.calibration_offset = 0.0
        self.humidity_scale = 1.0
        
        # 模拟参数
        self.base_humidity = 55.0
        self.humidity_trend = 0.0
        self.last_update_time = None
        self.reading_count = 0
        
        # 传感器特性
        if sensor_model == "DHT22":
            self.accuracy = 2.0  # ±2%
            self.range = (0, 100)
        elif sensor_model == "DHT11":
            self.accuracy = 5.0  # ±5%
            self.range = (20, 90)  # DHT11有测量范围限制
        else:  # SHT31等高端传感器
            self.accuracy = 1.5  # ±1.5%
            self.range = (0, 100)
        
        # 环境参数
        self.room_type = "laboratory"  # laboratory, office, outdoor, bathroom
        self.has_humidifier = False
        self.has_dehumidifier = False
        self.ventilation_level = 0.5  # 0-1, 通风程度
        self.occupancy_effect = 0.3  # 人员对湿度的影响
        
        print(f"💧 初始化湿度传感器 {sensor_id} ({sensor_model}) - 模式: {mode}")
    
    def _read_real_sensor(self):
        """从真实传感器读取湿度"""
        # 这里预留真实传感器的读取逻辑
        # 当连接真实DHT22等传感器时实现
        
        try:
            if self.sensor_model == "DHT22":
                # 实际实现示例：
                # import Adafruit_DHT
                # humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)
                # return humidity
                pass
                
            elif self.sensor_model == "DHT11":
                # import Adafruit_DHT
                # humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin)
                # return humidity
                pass
                
            elif self.sensor_model == "SHT31":
                # import board
                # import adafruit_sht31d
                # i2c = board.I2C()
                # sensor = adafruit_sht31d.SHT31D(i2c)
                # return sensor.relative_humidity
                pass
                
        except Exception as e:
            print(f"❌ 读取真实传感器失败: {e}")
            return None
        
        # 如果没有真实传感器，返回None触发模拟模式
        return None
    
    def _simulate_humidity(self):
        """模拟湿度读数"""
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        month = current_time.month
        day_of_year = current_time.timetuple().tm_yday
        
        # 基础湿度（基于季节和天气）
        seasonal_base = self._get_seasonal_base(month)
        
        # 日内湿度变化
        daily_variation = self._get_daily_variation(hour, minute)
        
        # 随机波动
        random_noise = random.uniform(-2.0, 2.0)
        
        # 趋势变化
        trend_change = self._update_humidity_trend()
        
        # 环境影响因素
        room_effect = self._get_room_type_effect()
        equipment_effect = self._get_equipment_effect()
        ventilation_effect = self._get_ventilation_effect()
        occupancy_effect = self._get_occupancy_effect(hour)
        
        # 天气影响（简化模拟）
        weather_effect = self._get_weather_effect()
        
        # 计算最终湿度
        humidity = (
            seasonal_base +
            daily_variation +
            random_noise +
            trend_change +
            room_effect +
            equipment_effect +
            ventilation_effect +
            occupancy_effect +
            weather_effect +
            self.calibration_offset
        )
        
        # 确保在合理范围内
        humidity = max(self.range[0], min(self.range[1], humidity))
        
        self.reading_count += 1
        self.last_update_time = current_time
        
        return round(humidity, 1)
    
    def _get_seasonal_base(self, month):
        """获取季节性基础湿度"""
        # 基于月份的季节性调整
        if month in [12, 1, 2]:  # 冬季 - 干燥
            return 40.0
        elif month in [6, 7, 8]:  # 夏季 - 潮湿
            return 65.0
        else:  # 春秋季
            return 55.0
    
    def _get_daily_variation(self, hour, minute):
        """获取日内湿度变化"""
        time_of_day = hour + minute / 60.0
        
        # 湿度在凌晨最高，下午最低
        if 4 <= hour <= 6:  # 凌晨露水
            return 8.0
        elif 14 <= hour <= 16:  # 下午最干燥
            return -5.0
        elif 20 <= hour <= 22:  # 晚上湿度回升
            return 3.0
        else:
            return 0.0
    
    def _update_humidity_trend(self):
        """更新湿度趋势"""
        # 湿度趋势缓慢变化
        if random.random() < 0.08:  # 8%的概率改变趋势
            self.humidity_trend += random.uniform(-0.1, 0.1)
            # 限制趋势范围
            self.humidity_trend = max(-3.0, min(3.0, self.humidity_trend))
        
        return self.humidity_trend
    
    def _get_room_type_effect(self):
        """获取房间类型影响"""
        effects = {
            "bathroom": 15.0,      # 浴室湿度高
            "laboratory": 0.0,     # 实验室相对稳定
            "office": -5.0,        # 办公室较干燥
            "outdoor": 10.0,       # 室外受天气影响
            "greenhouse": 25.0,    # 温室湿度很高
            "basement": 20.0       # 地下室潮湿
        }
        return effects.get(self.room_type, 0.0)
    
    def _get_equipment_effect(self):
        """获取设备影响"""
        effect = 0.0
        if self.has_humidifier:
            effect += random.uniform(5.0, 15.0)
        if self.has_dehumidifier:
            effect -= random.uniform(8.0, 20.0)
        return effect
    
    def _get_ventilation_effect(self):
        """获取通风影响"""
        # 通风越好，湿度越接近室外
        return -self.ventilation_level * 10.0
    
    def _get_occupancy_effect(self, hour):
        """获取人员影响"""
        # 人员在室内会增加湿度（呼吸、出汗）
        if 8 <= hour <= 18:  # 工作时间
            return self.occupancy_effect * 8.0
        else:
            return self.occupancy_effect * 2.0
    
    def _get_weather_effect(self):
        """获取天气影响"""
        # 模拟不同的天气状况
        weather_conditions = {
            "sunny": -8.0,
            "cloudy": 0.0,
            "rainy": 15.0,
            "foggy": 20.0,
            "snowy": 5.0
        }
        
        # 随机选择天气（但考虑季节性）
        current_month = datetime.now().month
        if current_month in [6, 7, 8]:  # 夏季多雨
            weights = [0.3, 0.3, 0.3, 0.05, 0.05]  # 雨天概率高
        elif current_month in [12, 1, 2]:  # 冬季
            weights = [0.4, 0.3, 0.1, 0.1, 0.1]  # 晴天概率高，可能下雪
        else:
            weights = [0.4, 0.4, 0.15, 0.05, 0.0]  # 春秋季
        
        weather = random.choices(
            ["sunny", "cloudy", "rainy", "foggy", "snowy"],
            weights=weights
        )[0]
        
        return weather_conditions[weather]
    
    def read_humidity(self):
        """读取湿度"""
        try:
            if self.mode == 'real':
                # 尝试读取真实传感器
                humidity = self._read_real_sensor()
                if humidity is not None:
                    return humidity
                else:
                    # 真实传感器读取失败，切换到模拟模式
                    self.mode = 'simulation'
                    print(f"⚠️ 传感器 {self.sensor_id} 切换到模拟模式")
            
            # 模拟模式
            return self._simulate_humidity()
            
        except Exception as e:
            print(f"❌ 读取湿度失败: {e}")
            return None
    
    def read_humidity_with_metadata(self):
        """读取湿度并返回元数据"""
        humidity = self.read_humidity()
        
        if humidity is None:
            return None
        
        return {
            'value': humidity,
            'unit': self.unit,
            'timestamp': datetime.now().isoformat(),
            'accuracy': f"±{self.accuracy}{self.unit}",
            'sensor_model': self.sensor_model,
            'reading_count': self.reading_count,
            'status': self.check_humidity_status(humidity)
        }
    
    def calibrate(self, reference_humidity):
        """校准传感器"""
        current_humidity = self.read_humidity()
        if current_humidity is None:
            return False
        
        self.calibration_offset = reference_humidity - current_humidity
        print(f"✅ 传感器 {self.sensor_id} 已校准，偏移量: {self.calibration_offset:.1f}{self.unit}")
        return True
    
    def set_environment(self, room_type="laboratory", has_humidifier=False, 
                       has_dehumidifier=False, ventilation_level=0.5, occupancy_effect=0.3):
        """设置环境参数"""
        self.room_type = room_type
        self.has_humidifier = has_humidifier
        self.has_dehumidifier = has_dehumidifier
        self.ventilation_level = max(0.0, min(1.0, ventilation_level))
        self.occupancy_effect = max(0.0, min(1.0, occupancy_effect))
        
        print(f"🔄 传感器 {self.sensor_id} 环境设置更新:")
        print(f"  房间类型: {room_type}")
        print(f"  加湿器: {'有' if has_humidifier else '无'}")
        print(f"  除湿器: {'有' if has_dehumidifier else '无'}")
        print(f"  通风程度: {ventilation_level:.1%}")
        print(f"  人员影响: {occupancy_effect:.1%}")
    
    def check_humidity_status(self, humidity=None):
        """检查湿度状态"""
        if humidity is None:
            humidity = self.read_humidity()
        
        if humidity is None:
            return 'unknown'
        
        # 根据湿度水平返回状态
        if humidity < 20:
            return 'too_dry'
        elif humidity < 30:
            return 'dry'
        elif humidity <= 60:
            return 'comfortable'
        elif humidity <= 70:
            return 'humid'
        else:
            return 'too_humid'
    
    def get_comfort_index(self, temperature=22.0, humidity=None):
        """计算舒适度指数"""
        if humidity is None:
            humidity = self.read_humidity()
        
        if humidity is None or temperature is None:
            return None
        
        # 简化的舒适度计算
        # 理想湿度: 40%-60%，理想温度: 18-26°C
        humidity_score = 1.0 - abs(humidity - 50.0) / 50.0  # 距离50%的偏差
        temperature_score = 1.0 - abs(temperature - 22.0) / 10.0  # 距离22°C的偏差
        
        comfort_index = (humidity_score + temperature_score) / 2.0
        
        return max(0.0, min(1.0, comfort_index))
    
    def get_humidity_history(self, hours=24, simulated=True):
        """获取湿度历史数据（模拟）"""
        if not simulated:
            # 这里可以从数据库获取真实历史数据
            return []
        
        # 生成模拟历史数据
        history = []
        current_time = datetime.now()
        
        for i in range(hours):
            timestamp = current_time.replace(hour=(current_time.hour - i) % 24)
            
            # 简化的历史湿度计算
            base_humidity = self._get_seasonal_base(timestamp.month)
            hour_variation = self._get_daily_variation(timestamp.hour, timestamp.minute)
            
            humidity = base_humidity + hour_variation + random.uniform(-3, 3)
            humidity = max(20, min(90, humidity))  # 合理范围
            
            history.append({
                'timestamp': timestamp.isoformat(),
                'humidity': round(humidity, 1),
                'unit': self.unit
            })
        
        return list(reversed(history))  # 按时间顺序返回
    
    def get_humidity_stats(self, hours=24):
        """获取湿度统计信息"""
        history = self.get_humidity_history(hours)
        
        if not history:
            return None
        
        humidities = [item['humidity'] for item in history]
        
        return {
            'period_hours': hours,
            'average': round(sum(humidities) / len(humidities), 1),
            'min': round(min(humidities), 1),
            'max': round(max(humidities), 1),
            'current': self.read_humidity(),
            'data_points': len(humidities),
            'comfort_level': self.check_humidity_status()
        }
    
    def get_sensor_info(self):
        """获取传感器信息"""
        current_humidity = self.read_humidity()
        
        return {
            'id': self.sensor_id,
            'name': f'湿度传感器-{self.sensor_id.split("_")[-1]}',
            'type': self.sensor_type,
            'model': self.sensor_model,
            'location': self.location,
            'mode': self.mode,
            'unit': self.unit,
            'current_humidity': current_humidity,
            'status': self.check_humidity_status(current_humidity),
            'accuracy': f"±{self.accuracy}{self.unit}",
            'measurement_range': f"{self.range[0]}-{self.range[1]}{self.unit}",
            'calibration_offset': round(self.calibration_offset, 1),
            'reading_count': self.reading_count,
            'room_type': self.room_type,
            'last_reading': self.last_update_time.isoformat() if self.last_update_time else '无'
        }

# 测试函数
def test_humidity_sensor():
    """测试湿度传感器"""
    print("=" * 50)
    print("💧 湿度传感器测试")
    print("=" * 50)
    
    # 创建传感器实例
    sensor = HumiditySensor("humidity_001", "实验室A区", sensor_model="DHT22", mode='simulation')
    
    # 设置环境参数
    sensor.set_environment(
        room_type="laboratory",
        has_humidifier=False,
        has_dehumidifier=True,
        ventilation_level=0.3,
        occupancy_effect=0.6
    )
    
    # 获取传感器信息
    info = sensor.get_sensor_info()
    print("传感器信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n湿度读数:")
    # 读取多次湿度
    for i in range(5):
        humidity_data = sensor.read_humidity_with_metadata()
        if humidity_data:
            comfort_index = sensor.get_comfort_index(temperature=22.0, humidity=humidity_data['value'])
            comfort_level = "舒适" if comfort_index and comfort_index > 0.7 else "不舒适"
            print(f"  读数 {i+1}: {humidity_data['value']}{humidity_data['unit']} - {humidity_data['status']} - {comfort_level}")
        time.sleep(1)
    
    # 获取统计信息
    stats = sensor.get_humidity_stats(hours=6)
    if stats:
        print(f"\n6小时统计:")
        print(f"  平均湿度: {stats['average']}%")
        print(f"  湿度范围: {stats['min']}% - {stats['max']}%")
        print(f"  当前湿度: {stats['current']}%")
        print(f"  舒适等级: {stats['comfort_level']}")
    
    # 测试舒适度指数
    print(f"\n舒适度测试:")
    test_conditions = [
        (20, 45),  # 稍冷，湿度舒适
        (25, 55),  # 温暖，湿度舒适  
        (28, 75),  # 热，潮湿
        (18, 25),  # 凉，干燥
    ]
    
    for temp, hum in test_conditions:
        comfort = sensor.get_comfort_index(temperature=temp, humidity=hum)
        comfort_desc = "非常舒适" if comfort > 0.8 else "舒适" if comfort > 0.6 else "不舒适"
        print(f"  温度{temp}°C, 湿度{hum}% → 舒适度: {comfort:.2f} ({comfort_desc})")

if __name__ == "__main__":
    test_humidity_sensor()