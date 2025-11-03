"""
传感器配置文件
定义所有传感器类型和参数
"""

# 传感器类型定义
SENSOR_TYPES = {
    'temperature': {
        'name': '温度传感器',
        'unit': '°C',
        'icon': 'fa-thermometer-half',
        'color': '#e74c3c',
        'description': '测量环境温度'
    },
    'humidity': {
        'name': '湿度传感器', 
        'unit': '%',
        'icon': 'fa-tint',
        'color': '#3498db',
        'description': '测量环境湿度'
    },
    'light': {
        'name': '光照传感器',
        'unit': 'lux', 
        'icon': 'fa-sun',
        'color': '#f39c12',
        'description': '测量光照强度'
    },
    'pressure': {
        'name': '压力传感器',
        'unit': 'hPa',
        'icon': 'fa-tachometer-alt',
        'color': '#9b59b6',
        'description': '测量大气压力'
    },
    'camera': {
        'name': '摄像头',
        'unit': 'image',
        'icon': 'fa-camera',
        'color': '#2ecc71',
        'description': '视频监控和图像采集'
    },
    'air_quality': {
        'name': '空气质量传感器',
        'unit': 'AQI',
        'icon': 'fa-wind',
        'color': '#1abc9c',
        'description': '测量空气质量指数'
    }
}

# 预定义传感器列表
PREDEFINED_SENSORS = [
    {
        'id': 'temp_001',
        'name': '温度传感器-01',
        'type': 'temperature',
        'location': '实验室A区',
        'description': '主要温度监测点'
    },
    {
        'id': 'humidity_001',
        'name': '湿度传感器-01',
        'type': 'humidity', 
        'location': '实验室A区',
        'description': '主要湿度监测点'
    },
    {
        'id': 'light_001',
        'name': '光照传感器-01',
        'type': 'light',
        'location': '实验室B区', 
        'description': '光照强度监测'
    },
    {
        'id': 'pressure_001',
        'name': '压力传感器-01',
        'type': 'pressure',
        'location': '实验室C区',
        'description': '大气压力监测'
    }
]

def get_sensor_type_info(sensor_type):
    """获取传感器类型信息"""
    return SENSOR_TYPES.get(sensor_type, {
        'name': '未知传感器',
        'unit': '',
        'icon': 'fa-microchip',
        'color': '#95a5a6',
        'description': '未知传感器类型'
    })

def get_predefined_sensors():
    """获取预定义传感器列表"""
    return PREDEFINED_SENSORS.copy()