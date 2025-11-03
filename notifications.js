/**
 * 通知管理系统
 */
class NotificationManager {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.style.cssText = 
            'position: fixed; top: 20px; right: 20px; z-index: 10000; max-width: 400px;';
        document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        const colors = {
            'success': '#10b981',
            'error': '#ef4444', 
            'warning': '#f59e0b',
            'info': '#3b82f6'
        };
        
        notification.style.cssText = 
            'background: var(--bg-primary); border: 1px solid var(--border-light); ' +
            'border-left: 4px solid ' + (colors[type] || '#3b82f6') + '; ' +
            'border-radius: 8px; padding: 16px; margin-bottom: 10px; ' +
            'box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); ' +
            'animation: slideInRight 0.3s ease;';
        
        notification.innerHTML = 
            '<div style=\"font-weight: 600; margin-bottom: 4px; color: var(--text-primary);\">' +
            this.getTitle(type) + '</div>' +
            '<div style=\"color: var(--text-secondary); font-size: 0.9rem;\">' + message + '</div>';
        
        this.container.appendChild(notification);
        
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        }
        
        return notification;
    }
    
    getTitle(type) {
        const titles = {
            'success': '成功',
            'error': '错误', 
            'warning': '警告',
            'info': '信息'
        };
        return titles[type] || '通知';
    }
    
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }
    
    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = 
    '@keyframes slideInRight { ' +
    'from { transform: translateX(100%); opacity: 0; } ' +
    'to { transform: translateX(0); opacity: 1; } ' +
    '}';
document.head.appendChild(style);

window.NotificationManager = NotificationManager;
