"""
温度传感器实现
支持DS18B20等温度传感器的模拟和真实连接
"""

import random
import time
from datetime import datetime
import os
import json

class TemperatureSensor:
    """温度传感器"""
    
    def __init__(self, sensor_id, location, sensor_model="DS18B20", mode='simulation'):
        """
        初始化温度传感器
        
        Args:
            sensor_id: 传感器ID
            location: 安装位置
            sensor_model: 传感器型号
            mode: 运行模式 ('real'=真实传感器, 'simulation'=模拟模式)
        """
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = "temperature"
        self.sensor_model = sensor_model
        self.mode = mode
        self.unit = "°C"
        
        # 校准参数
        self.calibration_offset = 0.0
        self.temperature_scale = 1.0  # 比例因子
        
        # 模拟参数
        self.base_temperature = 22.0
        self.temperature_trend = 0.0  # 温度趋势
        self.last_update_time = None
        self.reading_count = 0
        
        # 传感器特性
        self.accuracy = 0.5  # 精度 ±0.5°C
        self.resolution = 0.0625  # 分辨率
        
        # 环境参数
        self.room_size = "medium"  # small, medium, large
        self.has_heating = False
        self.has_cooling = False
        self.occupancy_level = 0.5  # 0-1, 人员密度
        
        print(f"🌡️ 初始化温度传感器 {sensor_id} - 模式: {mode}")
    
    def _read_real_sensor(self):
        """从真实传感器读取温度"""
        # 这里预留真实传感器的读取逻辑
        # 当连接真实DS18B20等传感器时实现
        
        try:
            # 示例：读取DS18B20的伪代码
            if self.sensor_model == "DS18B20":
                # 实际实现会读取 /sys/bus/w1/devices/28-*/w1_slave
                # temperature = read_ds18b20()
                # return temperature
                pass
                
            elif self.sensor_model == "DHT22":
                # 实际实现会使用Adafruit_DHT库
                # humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)
                # return temperature
                pass
                
        except Exception as e:
            print(f"❌ 读取真实传感器失败: {e}")
            return None
        
        # 如果没有真实传感器，返回None触发模拟模式
        return None
    
    def _simulate_temperature(self):
        """模拟温度读数"""
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        month = current_time.month
        day_of_year = current_time.timetuple().tm_yday
        
        # 基础温度（基于季节）
        seasonal_base = self._get_seasonal_base(month)
        
        # 日内温度变化（正弦曲线）
        daily_variation = self._get_daily_variation(hour, minute)
        
        # 随机波动（模拟环境噪声）
        random_noise = random.uniform(-0.3, 0.3)
        
        # 趋势变化（缓慢的温度变化）
        trend_change = self._update_temperature_trend()
        
        # 人员影响（人员越多温度越高）
        occupancy_effect = self.occupancy_level * 1.5
        
        # 设备影响
        equipment_effect = 0.0
        if self.has_heating:
            equipment_effect += random.uniform(0.5, 2.0)
        if self.has_cooling:
            equipment_effect -= random.uniform(0.5, 1.5)
        
        # 房间大小影响
        room_size_effect = self._get_room_size_effect()
        
        # 计算最终温度
        temperature = (
            seasonal_base +
            daily_variation +
            random_noise +
            trend_change +
            occupancy_effect +
            equipment_effect +
            room_size_effect +
            self.calibration_offset
        )
        
        # 应用传感器精度
        temperature = round(temperature / self.resolution) * self.resolution
        
        self.reading_count += 1
        self.last_update_time = current_time
        
        return round(temperature, 2)
    
    def _get_seasonal_base(self, month):
        """获取季节性基础温度"""
        # 基于月份的季节性调整
        if month in [12, 1, 2]:  # 冬季
            return 18.0
        elif month in [3, 4, 5]:  # 春季
            return 20.0
        elif month in [6, 7, 8]:  # 夏季
            return 26.0
        else:  # 秋季
            return 22.0
    
    def _get_daily_variation(self, hour, minute):
        """获取日内温度变化"""
        # 使用正弦曲线模拟一天中的温度变化
        time_of_day = hour + minute / 60.0
        
        # 温度在下午2点达到峰值，凌晨4点达到谷值
        peak_hour = 14  # 下午2点
        trough_hour = 4  # 凌晨4点
        
        # 计算与峰值小时的时间差
        hour_diff = min(
            abs(time_of_day - peak_hour),
            abs(time_of_day + 24 - peak_hour),
            abs(time_of_day - 24 - peak_hour)
        )
        
        # 正弦曲线变化，振幅为3°C
        amplitude = 3.0
        variation = amplitude * (1 - (hour_diff / 12.0))
        
        return variation
    
    def _update_temperature_trend(self):
        """更新温度趋势"""
        # 温度趋势缓慢变化
        if random.random() < 0.1:  # 10%的概率改变趋势
            self.temperature_trend += random.uniform(-0.05, 0.05)
            # 限制趋势范围
            self.temperature_trend = max(-1.0, min(1.0, self.temperature_trend))
        
        return self.temperature_trend
    
    def _get_room_size_effect(self):
        """获取房间大小影响"""
        if self.room_size == "small":
            return 2.0  # 小房间温度更容易升高
        elif self.room_size == "large":
            return -1.0  # 大房间温度更稳定
        else:  # medium
            return 0.0
    
    def read_temperature(self):
        """读取温度"""
        try:
            if self.mode == 'real':
                # 尝试读取真实传感器
                temperature = self._read_real_sensor()
                if temperature is not None:
                    return temperature
                else:
                    # 真实传感器读取失败，切换到模拟模式
                    self.mode = 'simulation'
                    print(f"⚠️ 传感器 {self.sensor_id} 切换到模拟模式")
            
            # 模拟模式
            return self._simulate_temperature()
            
        except Exception as e:
            print(f"❌ 读取温度失败: {e}")
            return None
    
    def read_temperature_with_metadata(self):
        """读取温度并返回元数据"""
        temperature = self.read_temperature()
        
        if temperature is None:
            return None
        
        return {
            'value': temperature,
            'unit': self.unit,
            'timestamp': datetime.now().isoformat(),
            'accuracy': f"±{self.accuracy}{self.unit}",
            'sensor_model': self.sensor_model,
            'reading_count': self.reading_count
        }
    
    def calibrate(self, reference_temperature):
        """校准传感器"""
        current_temperature = self.read_temperature()
        if current_temperature is None:
            return False
        
        self.calibration_offset = reference_temperature - current_temperature
        print(f"✅ 传感器 {self.sensor_id} 已校准，偏移量: {self.calibration_offset:.2f}{self.unit}")
        return True
    
    def set_environment(self, room_size="medium", has_heating=False, has_cooling=False, occupancy_level=0.5):
        """设置环境参数"""
        self.room_size = room_size
        self.has_heating = has_heating
        self.has_cooling = has_cooling
        self.occupancy_level = max(0.0, min(1.0, occupancy_level))
        
        print(f"🔄 传感器 {self.sensor_id} 环境设置更新:")
        print(f"  房间大小: {room_size}")
        print(f"  供暖: {'有' if has_heating else '无'}")
        print(f"  空调: {'有' if has_cooling else '无'}")
        print(f"  人员密度: {occupancy_level:.1%}")
    
    def get_temperature_history(self, hours=24, simulated=True):
        """获取温度历史数据（模拟）"""
        if not simulated:
            # 这里可以从数据库获取真实历史数据
            return []
        
        # 生成模拟历史数据
        history = []
        current_time = datetime.now()
        
        for i in range(hours):
            timestamp = current_time.replace(hour=(current_time.hour - i) % 24)
            
            # 简化的历史温度计算
            base_temp = self._get_seasonal_base(timestamp.month)
            hour_variation = self._get_daily_variation(timestamp.hour, timestamp.minute)
            
            temperature = base_temp + hour_variation + random.uniform(-1, 1)
            
            history.append({
                'timestamp': timestamp.isoformat(),
                'temperature': round(temperature, 2),
                'unit': self.unit
            })
        
        return list(reversed(history))  # 按时间顺序返回
    
    def get_temperature_stats(self, hours=24):
        """获取温度统计信息"""
        history = self.get_temperature_history(hours)
        
        if not history:
            return None
        
        temperatures = [item['temperature'] for item in history]
        
        return {
            'period_hours': hours,
            'average': round(sum(temperatures) / len(temperatures), 2),
            'min': round(min(temperatures), 2),
            'max': round(max(temperatures), 2),
            'current': self.read_temperature(),
            'data_points': len(temperatures)
        }
    
    def check_temperature_status(self, temperature=None):
        """检查温度状态"""
        if temperature is None:
            temperature = self.read_temperature()
        
        if temperature is None:
            return 'unknown'
        
        # 简单的状态判断
        if temperature < 10:
            return 'too_cold'
        elif temperature < 18:
            return 'cold'
        elif temperature <= 26:
            return 'comfortable'
        elif temperature <= 30:
            return 'warm'
        else:
            return 'too_hot'
    
    def get_sensor_info(self):
        """获取传感器信息"""
        current_temp = self.read_temperature()
        
        return {
            'id': self.sensor_id,
            'name': f'温度传感器-{self.sensor_id.split("_")[-1]}',
            'type': self.sensor_type,
            'model': self.sensor_model,
            'location': self.location,
            'mode': self.mode,
            'unit': self.unit,
            'current_temperature': current_temp,
            'status': self.check_temperature_status(current_temp),
            'accuracy': f"±{self.accuracy}{self.unit}",
            'calibration_offset': round(self.calibration_offset, 2),
            'reading_count': self.reading_count,
            'last_reading': self.last_update_time.isoformat() if self.last_update_time else '无'
        }

# 测试函数
def test_temperature_sensor():
    """测试温度传感器"""
    print("测试温度传感器...")
    
    # 创建传感器实例
    sensor = TemperatureSensor("temp_001", "实验室A区", mode='simulation')
    
    # 设置环境参数
    sensor.set_environment(
        room_size="medium",
        has_heating=True,
        has_cooling=False,
        occupancy_level=0.7
    )
    
    # 获取传感器信息
    info = sensor.get_sensor_info()
    print("传感器信息:", json.dumps(info, indent=2, ensure_ascii=False))
    
    # 读取多次温度
    print("温度读数:")
    for i in range(5):
        temp_data = sensor.read_temperature_with_metadata()
        if temp_data:
            status = sensor.check_temperature_status(temp_data['value'])
            print(f"  读数 {i+1}: {temp_data['value']}{temp_data['unit']} - {status}")
        time.sleep(1)
    
    # 获取统计信息
    stats = sensor.get_temperature_stats(hours=6)
    if stats:
        print("6小时统计:")
        print(f"  平均: {stats['average']}°C")
        print(f"  范围: {stats['min']}°C - {stats['max']}°C")
        print(f"  当前: {stats['current']}°C")

if __name__ == "__main__":
    test_temperature_sensor()