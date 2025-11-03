import time
from datetime import datetime
from real_data_manager import RealDataManager

class Sensor:
    def __init__(self, sensor_id, name, sensor_type, location):
        self.id = sensor_id
        self.name = name
        self.type = sensor_type
        self.location = location
        self.current_value = None
        self.last_update = None
        self.status = 'offline'
        self.history = []
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'location': self.location,
            'current_value': self.current_value,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'status': self.status,
            'unit': self.get_unit(),
            'history_count': len(self.history)
        }
    
    def get_unit(self):
        units = {
            'temperature': '°C',
            'humidity': '%',
            'light': 'lux',
            'pressure': 'hPa'
        }
        return units.get(self.type, '')
    
    def update_value(self, value, timestamp=None):
        if value is not None:
            self.current_value = value
            self.last_update = timestamp or datetime.now()
            self.status = 'online'
            
            # 添加到历史记录
            self.history.append({
                'time': self.last_update.isoformat(),
                'value': value,
                'timestamp': self.last_update.timestamp()
            })
            
            # 保持最近100条记录
            if len(self.history) > 100:
                self.history = self.history[-100:]

class EdgeNode:
    def __init__(self, node_id, name, location, ip_address):
        self.id = node_id
        self.name = name
        self.location = location
        self.ip_address = ip_address
        self.status = 'offline'
        self.cpu_usage = 0
        self.memory_usage = 0
        self.connected_sensors = []
        self.last_active = None
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'ip_address': self.ip_address,
            'status': self.status,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'connected_sensors': len(self.connected_sensors),
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class RealSensorManager:
    def __init__(self):
        self.sensors = {}
        self.nodes = {}
        self.data_manager = RealDataManager()
        
    def initialize_sensors(self):
        """初始化传感器系统"""
        print("=" * 60)
        print("🚀 5G边缘计算平台 - 真实数据采集系统")
        print("=" * 60)
        
        # 初始化传感器配置
        self.add_sensor(Sensor(
            sensor_id="temp_001",
            name="温度传感器-01",
            sensor_type="temperature",
            location="实验室A区"
        ))
        
        self.add_sensor(Sensor(
            sensor_id="humidity_001",
            name="湿度传感器-01", 
            sensor_type="humidity",
            location="实验室A区"
        ))
        
        self.add_sensor(Sensor(
            sensor_id="light_001",
            name="光照传感器-01",
            sensor_type="light", 
            location="实验室B区"
        ))
        
        self.add_sensor(Sensor(
            sensor_id="pressure_001",
            name="压力传感器-01",
            sensor_type="pressure",
            location="实验室C区"
        ))
        
        # 初始化边缘节点
        self.add_node(EdgeNode(
            node_id="node_001",
            name="边缘节点-01",
            location="实验室中心",
            ip_address="192.168.1.100"
        ))
        
        # 初始化数据采集系统
        self.data_manager.initialize()
        
        system_status = self.data_manager.get_system_status()
        print(f"✅ 系统初始化完成")
        print(f"📊 运行模式: {system_status['data_source']}")
        print(f"🔧 已注册传感器: {len(self.sensors)} 个")
        print(f"🖥️  已注册节点: {len(self.nodes)} 个")
        print("=" * 60)
    
    def add_sensor(self, sensor):
        self.sensors[sensor.id] = sensor
    
    def add_node(self, node):
        self.nodes[node.id] = node
    
    def update_all_sensors(self):
        """从数据源更新所有传感器数据"""
        online_count = 0
        
        for sensor_id, sensor in self.sensors.items():
            try:
                # 从数据管理器读取数据（模拟器或真实传感器）
                value = self.data_manager.read_sensor_data(sensor.type)
                
                if value is not None:
                    sensor.update_value(value)
                    online_count += 1
                else:
                    sensor.status = 'offline'
                    
            except Exception as e:
                print(f"❌ 更新 {sensor.name} 时出错: {e}")
                sensor.status = 'offline'
        
        # 更新节点状态
        self.update_node_status(online_count)
        
        return online_count
    
    def update_node_status(self, online_sensor_count):
        """更新边缘节点状态"""
        for node_id, node in self.nodes.items():
            if online_sensor_count > 0:
                node.status = 'online'
                node.cpu_usage = min(80, online_sensor_count * 8 + 10)
                node.memory_usage = min(85, online_sensor_count * 12 + 20)
            else:
                node.status = 'offline'
                node.cpu_usage = 0
                node.memory_usage = 0
            
            node.last_active = datetime.now()
    
    def get_sensor_data(self):
        """获取所有传感器数据"""
        return {sensor_id: sensor.to_dict() for sensor_id, sensor in self.sensors.items()}
    
    def get_node_data(self):
        """获取所有节点数据"""
        return {node_id: node.to_dict() for node_id, node in self.nodes.items()}
    
    def get_sensor_history(self, sensor_id, hours=24):
        """获取传感器历史数据"""
        if sensor_id not in self.sensors:
            return []
        
        sensor = self.sensors[sensor_id]
        cutoff_time = datetime.now().timestamp() - hours * 3600
        
        return [entry for entry in sensor.history if entry['timestamp'] >= cutoff_time]
    
    def get_system_info(self):
        """获取系统信息"""
        return self.data_manager.get_system_status()