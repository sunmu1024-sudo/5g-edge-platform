#!/usr/bin/env python3
"""
系统监控脚本
监控平台运行状态和资源使用情况
"""

import psutil
import time
import json
from datetime import datetime
import requests

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, api_url="http://localhost:5000/api"):
        self.api_url = api_url
        self.monitor_data = []
    
    def get_system_metrics(self):
        """获取系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = round(memory.used / (1024**3), 2)
            memory_total_gb = round(memory.total / (1024**3), 2)
            
            # 磁盘使用
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = round(disk.used / (1024**3), 2)
            disk_total_gb = round(disk.total / (1024**3), 2)
            
            # 网络IO
            net_io = psutil.net_io_counters()
            bytes_sent_mb = round(net_io.bytes_sent / (1024**2), 2)
            bytes_recv_mb = round(net_io.bytes_recv / (1024**2), 2)
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_gb': memory_used_gb,
                'memory_total_gb': memory_total_gb,
                'disk_percent': disk_percent,
                'disk_used_gb': disk_used_gb,
                'disk_total_gb': disk_total_gb,
                'network_sent_mb': bytes_sent_mb,
                'network_recv_mb': bytes_recv_mb
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ 获取系统指标失败: {e}")
            return None
    
    def check_api_health(self):
        """检查API健康状态"""
        try:
            response = requests.get(f"{self.api_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'online_sensors': data.get('online_sensors', 0),
                    'total_sensors': data.get('total_sensors', 0),
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {'status': 'unhealthy', 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'status': 'unreachable', 'error': str(e)}
    
    def check_disk_space(self, threshold=80):
        """检查磁盘空间"""
        disk = psutil.disk_usage('/')
        if disk.percent >= threshold:
            return {
                'status': 'warning',
                'message': f'磁盘使用率过高: {disk.percent}%',
                'usage_percent': disk.percent
            }
        else:
            return {
                'status': 'normal',
                'message': f'磁盘使用率正常: {disk.percent}%',
                'usage_percent': disk.percent
            }
    
    def generate_report(self, hours=24):
        """生成监控报告"""
        try:
            current_metrics = self.get_system_metrics()
            api_health = self.check_api_health()
            disk_status = self.check_disk_space()
            
            report = {
                'report_time': datetime.now().isoformat(),
                'time_range_hours': hours,
                'system_metrics': current_metrics,
                'api_health': api_health,
                'disk_status': disk_status,
                'alerts': []
            }
            
            # 生成告警
            if current_metrics and current_metrics['cpu_percent'] > 80:
                report['alerts'].append('CPU使用率过高')
            
            if current_metrics and current_metrics['memory_percent'] > 85:
                report['alerts'].append('内存使用率过高')
            
            if disk_status['status'] == 'warning':
                report['alerts'].append(disk_status['message'])
            
            if api_health['status'] != 'healthy':
                report['alerts'].append(f'API服务异常: {api_health["status"]}')
            
            return report
            
        except Exception as e:
            print(f"❌ 生成监控报告失败: {e}")
            return None
    
    def save_monitor_data(self, data):
        """保存监控数据"""
        try:
            # 限制数据量，只保留最近1000条记录
            self.monitor_data.append(data)
            if len(self.monitor_data) > 1000:
                self.monitor_data = self.monitor_data[-1000:]
            
            # 保存到文件
            monitor_file = "ass/backups/system_monitor.json"
            os.makedirs(os.path.dirname(monitor_file), exist_ok=True)
            
            with open(monitor_file, 'w', encoding='utf-8') as f:
                json.dump(self.monitor_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ 保存监控数据失败: {e}")
    
    def start_monitoring(self, interval_seconds=60):
        """启动监控"""
        print(f"🔍 启动系统监控，间隔: {interval_seconds}秒")
        
        try:
            while True:
                report = self.generate_report()
                if report:
                    self.save_monitor_data(report)
                    print(f"📊 监控数据已记录 - CPU: {report['system_metrics']['cpu_percent']}%")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("🛑 监控已停止")

if __name__ == "__main__":
    monitor = SystemMonitor()
    
    # 生成一次报告
    report = monitor.generate_report()
    if report:
        print("📋 系统监控报告:")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    # 启动持续监控（取消注释使用）
    # monitor.start_monitoring(60)