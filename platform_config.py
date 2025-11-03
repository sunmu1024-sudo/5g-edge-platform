"""
平台配置文件
集中管理所有配置参数
"""

class PlatformConfig:
    """平台核心配置"""
    
    # 系统信息
    PLATFORM_NAME = "5G边缘计算平台"
    VERSION = "2.0.0"
    DEVELOPER = "蚌埠学院物联网工程实验室"
    
    # 网络配置
    BACKEND_HOST = "0.0.0.0"
    BACKEND_PORT = 5000
    FRONTEND_PORT = 8000
    API_PREFIX = "/api"
    
    # 数据存储配置
    STORAGE_TYPE = "hybrid"  # hybrid, sqlite, json
    DATA_RETENTION_DAYS = 30
    BACKUP_INTERVAL_HOURS = 24
    
    # 传感器配置
    SENSOR_UPDATE_INTERVAL = 3  # 秒
    MAX_SENSOR_HISTORY = 1000
    SENSOR_TIMEOUT = 10  # 秒
    
    # WiFi传感器配置
    WIFI_SCAN_RANGE = "192.168.1"
    WIFI_PORTS = [8080, 8888, 8000, 5000]
    WIFI_TIMEOUT = 3
    
    # 串口配置
    SERIAL_PORTS = ["COM3", "COM4", "COM5", "/dev/ttyUSB0", "/dev/ttyACM0"]
    SERIAL_BAUDRATE = 9600
    
    # 阈值配置
    THRESHOLDS = {
        'temperature': {
            'min': 10,
            'max': 35,
            'warning_high': 30,
            'warning_low': 15,
            'critical_high': 40,
            'critical_low': 5
        },
        'humidity': {
            'min': 20,
            'max': 80,
            'warning_high': 70,
            'warning_low': 30,
            'critical_high': 90,
            'critical_low': 15
        },
        'light': {
            'min': 0,
            'max': 2000,
            'warning_high': 1500,
            'warning_low': 50,
            'critical_high': 2500,
            'critical_low': 10
        }
    }
    
    # 告警配置
    ALERT_ENABLED = True
    ALERT_EMAIL = "admin@bbu.edu.cn"
    ALERT_PHONE = ""  # 短信告警手机号
    
    @classmethod
    def get_sensor_thresholds(cls, sensor_type):
        """获取传感器阈值"""
        return cls.THRESHOLDS.get(sensor_type, {})
    
    @classmethod
    def check_value_status(cls, sensor_type, value):
        """检查数值状态"""
        thresholds = cls.get_sensor_thresholds(sensor_type)
        if not thresholds or value is None:
            return 'unknown'
        
        if value >= thresholds.get('critical_high', 100) or value <= thresholds.get('critical_low', 0):
            return 'critical'
        elif value >= thresholds.get('warning_high', 80) or value <= thresholds.get('warning_low', 20):
            return 'warning'
        else:
            return 'normal'