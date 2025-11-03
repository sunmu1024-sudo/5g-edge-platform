from datetime import datetime
import json

class Sensor:
    def __init__(self, sensor_id, name, sensor_type, location, api_endpoint=None):
        self.id = sensor_id
        self.name = name
        self.type = sensor_type
        self.location = location
        self.api_endpoint = api_endpoint
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
            'pressure': 'hPa',
            'air_quality': 'AQI',
            'camera': 'image'
        }
        return units.get(self.type, '')
    
    def update_value(self, value, timestamp=None):
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