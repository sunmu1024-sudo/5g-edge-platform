/**
 * 工具函数库
 */
class PlatformUtils {
    static formatTime(date) {
        if (!date) return '从未更新';
        const now = new Date();
        const target = new Date(date);
        const diff = now - target;
        
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
        if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
        return Math.floor(diff / 86400000) + '天前';
    }
    
    static formatValue(value, unit = '') {
        if (value === null || value === undefined) return '--';
        return value + ' ' + unit;
    }
    
    static getSensorIcon(sensorType) {
        const icons = {
            'temperature': 'fa-thermometer-half',
            'humidity': 'fa-tint',
            'light': 'fa-sun',
            'pressure': 'fa-tachometer-alt',
            'camera': 'fa-camera'
        };
        return icons[sensorType] || 'fa-microchip';
    }
    
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// 本地存储工具
class StorageManager {
    static set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('存储失败:', error);
            return false;
        }
    }
    
    static get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('读取失败:', error);
            return defaultValue;
        }
    }
}

window.PlatformUtils = PlatformUtils;
window.StorageManager = StorageManager;
