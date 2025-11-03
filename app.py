from flask import Flask, jsonify, request
from flask_cors import CORS
from sensor_manager import RealSensorManager
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# 初始化传感器管理器
sensor_manager = RealSensorManager()

# 全局数据存储
current_sensor_data = {}
current_node_data = {}
update_count = 0

@app.route('/')
def index():
    system_info = sensor_manager.get_system_info()
    return jsonify({
        "message": "5G边缘计算平台 - 真实数据采集系统",
        "version": "1.0.0",
        "status": "running",
        "mode": system_info['current_mode'],
        "data_source": system_info['data_source'],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    online_sensors = len([s for s in sensor_manager.sensors.values() if s.status == 'online'])
    total_sensors = len(sensor_manager.sensors)
    online_nodes = len([n for n in sensor_manager.nodes.values() if n.status == 'online'])
    total_nodes = len(sensor_manager.nodes)
    
    system_info = sensor_manager.get_system_info()
    
    return jsonify({
        "system_status": "running",
        "mode": system_info['current_mode'],
        "data_source": system_info['data_source'],
        "online_sensors": online_sensors,
        "total_sensors": total_sensors,
        "online_nodes": online_nodes,
        "total_nodes": total_nodes,
        "last_update": datetime.now().isoformat(),
        "update_count": update_count
    })

@app.route('/api/sensors')
def get_all_sensors():
    """获取所有传感器数据"""
    return jsonify(current_sensor_data)

@app.route('/api/sensors/<sensor_id>')
def get_sensor(sensor_id):
    """获取特定传感器数据"""
    if sensor_id in current_sensor_data:
        return jsonify(current_sensor_data[sensor_id])
    return jsonify({"error": "Sensor not found"}), 404

@app.route('/api/system/info')
def system_info():
    """获取系统详细信息"""
    system_info = sensor_manager.get_system_info()
    sensor_info = {}
    
    for sensor_id, sensor in sensor_manager.sensors.items():
        sensor_info[sensor_id] = {
            "name": sensor.name,
            "type": sensor.type,
            "location": sensor.location,
            "status": sensor.status,
            "current_value": sensor.current_value
        }
    
    return jsonify({
        "platform": "5G边缘计算平台",
        "version": "1.0.0",
        "system_mode": system_info,
        "sensors": sensor_info,
        "last_start": datetime.now().isoformat()
    })

@app.route('/api/control/update')
def manual_update():
    """手动更新传感器数据"""
    online_count = sensor_manager.update_all_sensors()
    update_global_data()
    return jsonify({
        "message": "传感器数据更新完成",
        "online_sensors": online_count,
        "timestamp": datetime.now().isoformat()
    })

def update_global_data():
    """更新全局数据"""
    global current_sensor_data, current_node_data, update_count
    current_sensor_data = sensor_manager.get_sensor_data()
    current_node_data = sensor_manager.get_node_data()
    update_count += 1

def background_data_update():
    """后台数据更新线程"""
    print("🔄 启动数据采集线程...")
    
    while True:
        try:
            # 更新传感器数据
            online_count = sensor_manager.update_all_sensors()
            
            # 更新全局数据
            update_global_data()
            
            # 显示更新状态
            total_count = len(current_sensor_data)
            system_info = sensor_manager.get_system_info()
            
            if update_count % 10 == 0:  # 每10次更新显示一次
                print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] {system_info['data_source']}: {online_count}/{total_count} 传感器在线")
            
        except Exception as e:
            print(f"❌ 数据采集错误: {e}")
        
        # 每3秒更新一次
        time.sleep(3)

if __name__ == '__main__':
    # 初始化系统
    print("🚀 启动5G边缘计算平台...")
    sensor_manager.initialize_sensors()
    
    # 初始数据更新
    update_global_data()
    
    # 启动后台更新线程
    update_thread = threading.Thread(target=background_data_update, daemon=True)
    update_thread.start()
    
    system_info = sensor_manager.get_system_info()
    print("✅ 系统启动成功!")
    print(f"🌐 访问地址: http://localhost:5000")
    print(f"📊 运行模式: {system_info['data_source']}")
    print(f"🔄 数据每3秒自动更新")
    print("=" * 50)
    
    # 启动Flask服务器
    app.run(host='0.0.0.0', port=5000, debug=False)