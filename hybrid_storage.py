"""
混合存储管理器
- SQLite: 主要存储（安全）
- JSON: 备份和调试（便利）  
- 内存: 实时缓存（性能）
"""

import sqlite3
import json
import os
import threading
from datetime import datetime, timedelta
import logging
import shutil

class HybridStorageManager:
    """
    混合存储管理器
    - SQLite: 主要存储（安全）
    - JSON: 备份和调试（便利）  
    - 内存: 实时缓存（性能）
    """
    
    def __init__(self, db_path='sensor_data.db', json_dir='data_backup'):
        self.db_path = db_path
        self.json_dir = json_dir
        self.memory_cache = {}
        self.lock = threading.RLock()
        self.sync_thread = None
        self.running = True
        
        # 初始化所有存储
        self._init_sqlite()
        self._init_json_backup()
        self._start_sync_thread()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('HybridStorage')
    
    def _init_sqlite(self):
        """初始化SQLite数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 启用WAL模式（写时复制，提高并发性）
            cursor.execute('PRAGMA journal_mode=WAL')
            
            # 传感器表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    location TEXT,
                    unit TEXT,
                    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP
                )
            ''')
            
            # 传感器数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT NOT NULL,
                    value REAL,
                    status TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_quality INTEGER DEFAULT 1,
                    FOREIGN KEY (sensor_id) REFERENCES sensors (id)
                )
            ''')
            
            # 系统事件表（审计日志）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    severity TEXT DEFAULT 'info',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_sensor_data_composite 
                ON sensor_data(sensor_id, timestamp DESC)
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("✅ SQLite数据库初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ SQLite初始化失败: {e}")
            raise
    
    def _init_json_backup(self):
        """初始化JSON备份目录"""
        try:
            if not os.path.exists(self.json_dir):
                os.makedirs(self.json_dir)
                self.logger.info(f"✅ JSON备份目录创建: {self.json_dir}")
        except Exception as e:
            self.logger.error(f"❌ JSON备份目录创建失败: {e}")
    
    def save_sensor_reading(self, sensor_id, value, status='online', metadata=None):
        """
        保存传感器读数 - 三级存储
        1. 内存缓存（立即）
        2. SQLite数据库（立即）  
        3. JSON备份（异步）
        """
        timestamp = datetime.now()
        
        try:
            with self.lock:
                # 1. 更新内存缓存
                self._update_memory_cache(sensor_id, value, status, timestamp)
                
                # 2. 保存到SQLite（带事务）
                self._save_to_sqlite(sensor_id, value, status, timestamp, metadata)
                
                # 3. 异步JSON备份（不阻塞主线程）
                threading.Thread(
                    target=self._async_json_backup,
                    args=(sensor_id, value, status, timestamp),
                    daemon=True
                ).start()
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 保存传感器数据失败 {sensor_id}: {e}")
            self._log_system_event('storage_error', f'Sensor {sensor_id} save failed: {e}', 'error')
            return False
    
    def _update_memory_cache(self, sensor_id, value, status, timestamp):
        """更新内存缓存"""
        cache_key = f"{sensor_id}_latest"
        self.memory_cache[cache_key] = {
            'value': value,
            'status': status,
            'timestamp': timestamp.isoformat(),
            'cached_at': datetime.now().isoformat()
        }
        
        # 限制缓存大小
        if len(self.memory_cache) > 1000:
            # 移除最旧的缓存项
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
    
    def _save_to_sqlite(self, sensor_id, value, status, timestamp, metadata):
        """保存到SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 开始事务
            cursor.execute('BEGIN TRANSACTION')
            
            # 插入传感器数据
            cursor.execute('''
                INSERT INTO sensor_data (sensor_id, value, status, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (sensor_id, value, status, timestamp))
            
            # 更新传感器最后活跃时间
            cursor.execute('''
                INSERT OR REPLACE INTO sensors (id, name, type, location, unit, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                sensor_id,
                metadata.get('name', 'Unknown') if metadata else 'Unknown',
                metadata.get('type', 'unknown') if metadata else 'unknown', 
                metadata.get('location', 'Unknown') if metadata else 'Unknown',
                metadata.get('unit', '') if metadata else '',
                timestamp
            ))
            
            # 提交事务
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _async_json_backup(self, sensor_id, value, status, timestamp):
        """异步JSON备份"""
        try:
            backup_file = os.path.join(self.json_dir, f'{sensor_id}_backup.json')
            backup_data = {
                'sensor_id': sensor_id,
                'value': value,
                'status': status,
                'timestamp': timestamp.isoformat(),
                'backup_time': datetime.now().isoformat()
            }
            
            # 读取现有备份数据
            existing_data = []
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []
            
            # 添加新数据（限制大小）
            existing_data.append(backup_data)
            if len(existing_data) > 1000:  # 最多1000条备份
                existing_data = existing_data[-1000:]
            
            # 写入备份文件
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.warning(f"⚠️ JSON备份失败 {sensor_id}: {e}")
    
    def get_latest_readings(self, use_cache=True):
        """获取最新读数 - 优先使用缓存"""
        if use_cache and self.memory_cache:
            # 从内存缓存构建结果
            result = {}
            for key, data in self.memory_cache.items():
                if key.endswith('_latest'):
                    sensor_id = key.replace('_latest', '')
                    result[sensor_id] = data
            return result
        
        # 缓存不可用，从数据库查询
        return self._get_latest_from_sqlite()
    
    def _get_latest_from_sqlite(self):
        """从SQLite获取最新数据"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.id, s.name, s.type, s.location, s.unit,
                       sd.value, sd.status, sd.timestamp
                FROM sensors s
                JOIN sensor_data sd ON s.id = sd.sensor_id
                WHERE sd.timestamp = (
                    SELECT MAX(timestamp) 
                    FROM sensor_data 
                    WHERE sensor_id = s.id
                )
            ''')
            
            results = {}
            for row in cursor.fetchall():
                results[row[0]] = {
                    'name': row[1],
                    'type': row[2],
                    'location': row[3],
                    'unit': row[4],
                    'value': row[5],
                    'status': row[6],
                    'timestamp': row[7]
                }
            
            return results
            
        finally:
            conn.close()
    
    def get_sensor_history(self, sensor_id, hours=24, source='auto'):
        """获取传感器历史数据"""
        if source == 'auto':
            # 自动选择：最近数据用缓存，历史数据用数据库
            if hours <= 1:  # 1小时内数据尝试从缓存获取
                cached = self._get_recent_from_cache(sensor_id, hours)
                if cached:
                    return cached
            
        # 从数据库获取
        return self._get_history_from_sqlite(sensor_id, hours)
    
    def _get_recent_from_cache(self, sensor_id, hours):
        """从缓存获取近期数据"""
        cache_key = f"{sensor_id}_latest"
        if cache_key in self.memory_cache:
            data = self.memory_cache[cache_key]
            # 检查数据是否在时间范围内
            data_time = datetime.fromisoformat(data['timestamp'])
            if (datetime.now() - data_time).total_seconds() <= hours * 3600:
                return [data]
        return []
    
    def _get_history_from_sqlite(self, sensor_id, hours):
        """从SQLite获取历史数据"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, value, status 
                FROM sensor_data 
                WHERE sensor_id = ? AND timestamp >= datetime('now', ?)
                ORDER BY timestamp DESC
                LIMIT 1000
            ''', (sensor_id, f'-{hours} hours'))
            
            return [
                {
                    'timestamp': row[0],
                    'value': row[1], 
                    'status': row[2]
                }
                for row in cursor.fetchall()
            ]
            
        finally:
            conn.close()
    
    def _log_system_event(self, event_type, event_data, severity='info'):
        """记录系统事件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_events (event_type, event_data, severity)
                VALUES (?, ?, ?)
            ''', (event_type, json.dumps(event_data), severity))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ 记录系统事件失败: {e}")
    
    def _start_sync_thread(self):
        """启动数据同步线程"""
        def sync_worker():
            while self.running:
                try:
                    self._sync_json_to_sqlite()
                    threading.Event().wait(30)  # 每30秒同步一次
                except Exception as e:
                    self.logger.error(f"❌ 数据同步失败: {e}")
                    threading.Event().wait(60)  # 出错时等待更久
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
    
    def _sync_json_to_sqlite(self):
        """将JSON备份数据同步到SQLite"""
        # 实现JSON到SQLite的数据恢复同步
        # 用于灾难恢复场景
        pass
    
    def backup_database(self, backup_dir='backups'):
        """备份数据库"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_file = os.path.join(
                backup_dir, 
                f'sensor_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            )
            
            # SQLite备份
            conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_file)
            
            conn.backup(backup_conn)
            backup_conn.close()
            conn.close()
            
            self.logger.info(f"✅ 数据库备份完成: {backup_file}")
            return backup_file
            
        except Exception as e:
            self.logger.error(f"❌ 数据库备份失败: {e}")
            return None
    
    def get_system_stats(self, days=7):
        """获取系统统计信息"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # 传感器数量统计
            cursor.execute('SELECT COUNT(*) FROM sensors')
            total_sensors = cursor.fetchone()[0]
            
            # 在线传感器数量（最近5分钟有数据的）
            cursor.execute('''
                SELECT COUNT(DISTINCT sensor_id) 
                FROM sensor_data 
                WHERE timestamp >= datetime('now', '-5 minutes')
            ''')
            online_sensors = cursor.fetchone()[0]
            
            # 数据点总数
            cursor.execute('SELECT COUNT(*) FROM sensor_data')
            total_readings = cursor.fetchone()[0]
            
            # 今日数据量
            cursor.execute('''
                SELECT COUNT(*) 
                FROM sensor_data 
                WHERE date(timestamp) = date('now')
            ''')
            today_readings = cursor.fetchone()[0]
            
            return {
                'total_sensors': total_sensors,
                'online_sensors': online_sensors,
                'total_readings': total_readings,
                'today_readings': today_readings,
                'storage_size_mb': round(os.path.getsize(self.db_path) / (1024*1024), 2)
            }
            
        finally:
            conn.close()
    
    def close(self):
        """关闭存储管理器"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        
        # 执行最终备份
        self.backup_database()
        self.logger.info("🔒 混合存储管理器已关闭")

# 测试函数
def test_hybrid_storage():
    """测试混合存储"""
    print("🧪 测试混合存储管理器...")
    
    storage = HybridStorageManager()
    
    # 测试保存数据
    test_data = [
        ('temp_001', 22.5, 'online', {'name': '温度传感器1', 'type': 'temperature', 'location': 'A区', 'unit': '°C'}),
        ('humidity_001', 55.0, 'online', {'name': '湿度传感器1', 'type': 'humidity', 'location': 'A区', 'unit': '%'}),
        ('light_001', 450, 'online', {'name': '光照传感器1', 'type': 'light', 'location': 'B区', 'unit': 'lux'})
    ]
    
    for sensor_id, value, status, metadata in test_data:
        success = storage.save_sensor_reading(sensor_id, value, status, metadata)
        print(f"保存 {sensor_id}: {'✅' if success else '❌'}")
    
    # 测试读取数据
    latest = storage.get_latest_readings()
    print(f"最新读数: {len(latest)} 个传感器")
    
    stats = storage.get_system_stats()
    print(f"系统统计: {stats}")
    
    storage.close()
    print("✅ 混合存储测试完成")

if __name__ == "__main__":
    test_hybrid_storage()