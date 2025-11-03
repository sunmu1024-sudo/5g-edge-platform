#!/usr/bin/env python3
"""
自动备份脚本
定时备份数据库和配置文件
"""

import os
import shutil
import schedule
import time
from datetime import datetime
import sqlite3
import json

class AutoBackup:
    """自动备份管理器"""
    
    def __init__(self, backup_dir="ass/backups", retention_days=7):
        self.backup_dir = backup_dir
        self.retention_days = retention_days
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """确保备份目录存在"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"✅ 创建备份目录: {self.backup_dir}")
    
    def backup_database(self):
        """备份数据库文件"""
        try:
            if not os.path.exists('sensor_data.db'):
                print("❌ 数据库文件不存在")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f'sensor_db_{timestamp}.db')
            
            # 使用SQLite备份命令
            source_conn = sqlite3.connect('sensor_data.db')
            backup_conn = sqlite3.connect(backup_file)
            
            source_conn.backup(backup_conn)
            backup_conn.close()
            source_conn.close()
            
            print(f"✅ 数据库备份完成: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ 数据库备份失败: {e}")
            return False
    
    def backup_config_files(self):
        """备份配置文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_backup_dir = os.path.join(self.backup_dir, f'config_{timestamp}')
            
            if not os.path.exists(config_backup_dir):
                os.makedirs(config_backup_dir)
            
            # 备份配置文件
            config_files = [
                'ass/config/platform_config.py',
                'ass/config/sensor_config.py'
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, config_backup_dir)
                    print(f"✅ 备份配置文件: {config_file}")
            
            # 备份当前传感器状态
            self._backup_sensor_status(config_backup_dir)
            
            return True
            
        except Exception as e:
            print(f"❌ 配置文件备份失败: {e}")
            return False
    
    def _backup_sensor_status(self, backup_dir):
        """备份传感器状态"""
        try:
            # 这里可以添加从数据库读取传感器状态的逻辑
            sensor_status = {
                'backup_time': datetime.now().isoformat(),
                'sensors': []  # 可以从数据库获取实际数据
            }
            
            status_file = os.path.join(backup_dir, 'sensor_status.json')
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(sensor_status, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ 传感器状态备份失败: {e}")
    
    def cleanup_old_backups(self):
        """清理旧备份文件"""
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.backup_dir):
                filepath = os.path.join(self.backup_dir, filename)
                
                if os.path.isfile(filepath):
                    # 检查文件时间
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    days_old = (current_time - file_time).days
                    
                    if days_old > self.retention_days:
                        os.remove(filepath)
                        print(f"🗑️ 删除旧备份: {filename}")
                        
        except Exception as e:
            print(f"❌ 清理旧备份失败: {e}")
    
    def run_full_backup(self):
        """执行完整备份"""
        print("🔄 开始完整备份...")
        
        success_count = 0
        if self.backup_database():
            success_count += 1
        if self.backup_config_files():
            success_count += 1
        
        self.cleanup_old_backups()
        
        if success_count > 0:
            print(f"✅ 备份完成，成功项目: {success_count}/2")
        else:
            print("❌ 备份失败")
    
    def start_scheduled_backup(self, interval_hours=24):
        """启动定时备份"""
        print(f"⏰ 启动定时备份，每 {interval_hours} 小时执行一次")
        
        schedule.every(interval_hours).hours.do(self.run_full_backup)
        
        # 立即执行一次
        self.run_full_backup()
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # 每小时检查一次

if __name__ == "__main__":
    backup_manager = AutoBackup()
    
    # 手动执行备份
    backup_manager.run_full_backup()
    
    # 或者启动定时备份（取消注释使用）
    # backup_manager.start_scheduled_backup(24)