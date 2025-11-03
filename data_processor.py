"""
数据处理器
提供数据清洗、分析和转换功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class DataProcessor:
    """数据处理器"""
    
    @staticmethod
    def clean_sensor_data(data_points, method='interpolate'):
        """
        清洗传感器数据
        method: 'interpolate' 插值, 'remove' 删除, 'average' 平均
        """
        if not data_points:
            return []
        
        df = pd.DataFrame(data_points)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # 处理缺失值
        if method == 'interpolate':
            df['value'] = df['value'].interpolate()
        elif method == 'remove':
            df = df.dropna()
        elif method == 'average':
            df['value'] = df['value'].fillna(df['value'].mean())
        
        # 处理异常值（使用IQR方法）
        Q1 = df['value'].quantile(0.25)
        Q3 = df['value'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df['value'] = np.where(
            (df['value'] < lower_bound) | (df['value'] > upper_bound),
            df['value'].median(),
            df['value']
        )
        
        return df.reset_index().to_dict('records')
    
    @staticmethod
    def calculate_statistics(data_points):
        """计算数据统计信息"""
        if not data_points:
            return {}
        
        values = [point['value'] for point in data_points if point['value'] is not None]
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'mean': round(np.mean(values), 2),
            'median': round(np.median(values), 2),
            'std': round(np.std(values), 2),
            'min': round(np.min(values), 2),
            'max': round(np.max(values), 2),
            'q1': round(np.percentile(values, 25), 2),
            'q3': round(np.percentile(values, 75), 2)
        }
    
    @staticmethod
    def detect_anomalies(data_points, window_size=10, threshold=2):
        """检测数据异常点"""
        if len(data_points) < window_size:
            return []
        
        values = [point['value'] for point in data_points if point['value'] is not None]
        
        anomalies = []
        for i in range(window_size, len(values)):
            window = values[i-window_size:i]
            mean = np.mean(window)
            std = np.std(window)
            
            if std == 0:  # 避免除零
                continue
                
            z_score = abs(values[i] - mean) / std
            if z_score > threshold:
                anomalies.append({
                    'index': i,
                    'value': values[i],
                    'z_score': round(z_score, 2),
                    'timestamp': data_points[i]['timestamp']
                })
        
        return anomalies
    
    @staticmethod
    def resample_data(data_points, interval_minutes=5):
        """重采样数据到固定间隔"""
        if not data_points:
            return []
        
        df = pd.DataFrame(data_points)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # 重采样
        resampled = df['value'].resample(f'{interval_minutes}T').mean()
        resampled = resampled.interpolate()
        
        return [{
            'timestamp': ts.isoformat(),
            'value': round(val, 2)
        } for ts, val in resampled.items()]

class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_daily_report(sensor_data, date=None):
        """生成日报"""
        if date is None:
            date = datetime.now().date()
        
        report = {
            'report_date': date.isoformat(),
            'generated_at': datetime.now().isoformat(),
            'sensor_summary': {},
            'alerts': [],
            'statistics': {}
        }
        
        for sensor_id, data_points in sensor_data.items():
            stats = DataProcessor.calculate_statistics(data_points)
            anomalies = DataProcessor.detect_anomalies(data_points)
            
            report['sensor_summary'][sensor_id] = {
                'data_points': len(data_points),
                'statistics': stats,
                'anomalies_count': len(anomalies)
            }
            
            if anomalies:
                report['alerts'].append(f"传感器 {sensor_id} 发现 {len(anomalies)} 个异常点")
        
        return report
    
    @staticmethod
    def save_report(report, filename=None):
        """保存报告到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ass/backups/report_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filename