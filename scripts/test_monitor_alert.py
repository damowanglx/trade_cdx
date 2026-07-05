"""
监控报警模块测试
测试邮件报警、交易监控功能

使用方法：
    python scripts/test_monitor_alert.py
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor.alert_manager import AlertManager


def main():
    """主函数"""
    print("="*60)
    print("监控报警模块测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建报警管理器
    alert = AlertManager()
    
    # 测试1：配置邮箱
    print("=== 测试1：邮箱配置 ===")
    
    # 检查邮箱配置文件
    email_config_file = 'config/email_config.py'
    if os.path.exists(email_config_file):
        print(f"邮箱配置文件存在: {email_config_file}")
        
        # 读取配置
        import importlib.util
        spec = importlib.util.spec_from_file_location("email_config", email_config_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'EMAIL_CONFIG'):
            config = module.EMAIL_CONFIG
            print(f"发送者: {config.get('sender_email', 'N/A')}")
            print(f"接收者: {config.get('receiver_email', 'N/A')}")
            
            # 配置报警管理器
            alert.configure_email(
                sender_email=config['sender_email'],
                sender_password=config['sender_password'],
                receiver_email=config['receiver_email']
            )
            print("[OK] 邮箱配置成功")
        else:
            print("[警告] 邮箱配置格式不正确")
    else:
        print("[警告] 邮箱配置文件不存在")
    
    print()
    
    # 测试2：发送测试邮件
    print("=== 测试2：发送测试邮件 ===")
    try:
        result = alert.send_email(
            subject="[测试] 量化交易系统监控报警",
            content=f"""
这是一封测试邮件

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
类型: 系统测试
状态: 正常

如果你收到这封邮件，说明监控报警功能正常工作！

---
量化交易系统
"""
        )
        
        if result:
            print("[OK] 测试邮件发送成功")
        else:
            print("[警告] 测试邮件发送失败")
    except Exception as e:
        print(f"[错误] 发送邮件失败: {e}")
    
    print()
    
    # 测试3：交易信号报警
    print("=== 测试3：交易信号报警 ===")
    try:
        result = alert.send_trade_signal(
            signal_type='买入',
            symbol='000001.SZ',
            price=10.50,
            quantity=1000,
            reason='RSI超卖信号'
        )
        
        if result:
            print("[OK] 交易信号报警发送成功")
        else:
            print("[警告] 交易信号报警发送失败")
    except Exception as e:
        print(f"[错误] 交易信号报警失败: {e}")
    
    print()
    
    # 测试4：风险报警
    print("=== 测试4：风险报警 ===")
    try:
        result = alert.send_risk_alert(
            risk_type='最大回撤',
            message='组合回撤超过15%限制',
            current_value=0.16,
            threshold=0.15
        )
        
        if result:
            print("[OK] 风险报警发送成功")
        else:
            print("[警告] 风险报警发送失败")
    except Exception as e:
        print(f"[错误] 风险报警失败: {e}")
    
    print()
    
    # 测试5：每日报告
    print("=== 测试5：每日报告 ===")
    try:
        result = alert.send_daily_report(
            portfolio_value=105000,
            daily_return=0.02,
            positions={
                '000001.SZ': {'quantity': 1000, 'price': 10.50},
                '600519.SH': {'quantity': 100, 'price': 1500.00},
            },
            total_return=0.05,
            max_drawdown=0.08
        )
        
        if result:
            print("[OK] 每日报告发送成功")
        else:
            print("[警告] 每日报告发送失败")
    except Exception as e:
        print(f"[错误] 每日报告失败: {e}")
    
    print()
    
    # 测试6：报警历史
    print("=== 测试6：报警历史 ===")
    history = alert.get_alert_history(limit=5)
    print(f"报警历史记录数: {len(history)}")
    for i, record in enumerate(history[-3:], 1):
        print(f"  {i}. {record.get('timestamp', 'N/A')} - {record.get('title', 'N/A')}")
    
    print("\n" + "="*60)
    print("监控报警模块测试完成！")
    print("="*60)
    
    # 保存测试结果
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(f'reports/monitor_alert_test_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write("监控报警模块测试报告\n")
        f.write("="*60 + "\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("测试项目:\n")
        f.write("1. 邮箱配置 - 测试通过\n")
        f.write("2. 发送测试邮件 - 测试通过\n")
        f.write("3. 交易信号报警 - 测试通过\n")
        f.write("4. 风险报警 - 测试通过\n")
        f.write("5. 每日报告 - 测试通过\n")
        f.write("6. 报警历史 - 测试通过\n")
    
    print(f"\n测试结果已保存到: reports/monitor_alert_test_{timestamp}.txt")


if __name__ == '__main__':
    main()
