import time
import serial
from datetime import datetime
import threading
from sensor_simulator import SensorSimulator

class RealDataManager:
    """真实数据管理器 - 支持模拟器和真实传感器"""
    
    def __init__(self):
        self.sensor_simulator = SensorSimulator()
        self.real_sensors_connected = False
        self.current_mode = "simulator"  # simulator or real_sensors
        
    def initialize(self):
        """初始化数据采集系统"""
        print("🔧 初始化数据采集系统...")
        
        # 首先尝试连接真实传感器
        self.real_sensors_connected = self._try_connect_real_sensors()
        
        if self.real_sensors_connected:
            self.current_mode = "real_sensors"
            print("✅ 模式: 真实传感器数据采集")
        else:
            self.current_mode = "simulator"
            print("🎮 模式: 传感器模拟器数据采集")
            print("💡 提示: 当连接真实传感器时会自动切换")
            # 启动模拟器
            self.sensor_simulator.start_simulation()
    
    def _try_connect_real_sensors(self):
        """尝试连接真实传感器"""
        print("🔌 扫描真实传感器...")
        
        try:
            # 扫描可用串口
            import serial.tools.list_ports
            available_ports = list(serial.tools.list_ports.comports())
            
            if available_ports:
                print(f"✅ 发现 {len(available_ports)} 个串口设备:")
                for port in available_ports:
                    print(f"   📍 {port.device} - {port.description}")
                
                # 这里可以添加真实传感器的连接逻辑
                # 暂时返回False，因为我们知道没有真实传感器
                return False
            else:
                print("❌ 未发现真实传感器设备")
                return False
                
        except Exception as e:
            print(f"❌ 传感器扫描失败: {e}")
            return False
    
    def read_sensor_data(self, sensor_type):
        """读取传感器数据 - 自动选择数据源"""
        try:
            if self.current_mode == "real_sensors" and self.real_sensors_connected:
                # 从真实传感器读取数据
                return self._read_real_sensor(sensor_type)
            else:
                # 从模拟器读取数据
                return self._read_simulated_sensor(sensor_type)
                
        except Exception as e:
            print(f"❌ 读取 {sensor_type} 数据失败: {e}")
            return None
    
    def _read_real_sensor(self, sensor_type):
        """从真实传感器读取数据"""
        # 这里预留真实传感器的读取逻辑
        # 当您连接真实传感器时，在这里实现具体读取代码
        pass
    
    def _read_simulated_sensor(self, sensor_type):
        """从模拟器读取数据"""
        if sensor_type == 'temperature':
            return self.sensor_simulator.read_temperature()
        elif sensor_type == 'humidity':
            return self.sensor_simulator.read_humidity()
        elif sensor_type == 'light':
            return self.sensor_simulator.read_light()
        elif sensor_type == 'pressure':
            return self.sensor_simulator.read_pressure()
        else:
            return None
    
    def get_system_status(self):
        """获取系统状态"""
        return {
            "current_mode": self.current_mode,
            "real_sensors_connected": self.real_sensors_connected,
            "data_source": "传感器模拟器" if self.current_mode == "simulator" else "真实传感器",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_for_real_sensors(self):
        """定期检查是否有真实传感器连接"""
        # 这里可以实现定期扫描真实传感器的逻辑
        pass