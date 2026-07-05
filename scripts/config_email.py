"""
邮箱配置脚本
帮助配置QQ邮箱报警

使用方法：
    python scripts/config_email.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def show_email_guide():
    """显示邮箱配置指南"""
    print("="*60)
    print("QQ邮箱配置指南")
    print("="*60)
    print()
    print("步骤1：开启SMTP服务")
    print("-"*40)
    print("1. 登录QQ邮箱：https://mail.qq.com")
    print("2. 点击 设置 -> 账户")
    print("3. 找到 'POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务'")
    print("4. 开启 'POP3/SMTP服务'")
    print("5. 按提示发送短信验证")
    print("6. 获取授权码（16位字母）")
    print()
    print("步骤2：获取授权码")
    print("-"*40)
    print("开启SMTP服务后，会显示授权码")
    print("授权码格式类似：abcdefghijklmnop")
    print("注意：授权码不是QQ密码！")
    print()
    print("步骤3：配置信息")
    print("-"*40)
    print("需要填写：")
    print("  - 发送者邮箱：你的QQ邮箱")
    print("  - 授权码：步骤2获取的授权码")
    print("  - 接收者邮箱：接收报警的邮箱")
    print()


def create_email_config(sender_email, sender_password, receiver_email):
    """创建邮箱配置"""
    config_content = f'''"""
邮箱配置
"""

EMAIL_CONFIG = {{
    'smtp_server': 'smtp.qq.com',
    'smtp_port': 587,
    'sender_email': '{sender_email}',
    'sender_password': '{sender_password}',
    'receiver_email': '{receiver_email}',
}}
'''
    
    with open('config/email_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n邮箱配置已保存到: config/email_config.py")
    print(f"发送者: {sender_email}")
    print(f"接收者: {receiver_email}")


def test_email_config():
    """测试邮箱配置"""
    print("\n测试邮箱连接...")
    
    try:
        from monitor.alert_manager import AlertManager
        
        alert = AlertManager()
        
        # 读取配置
        from config.email_config import EMAIL_CONFIG
        
        alert.configure_email(
            sender_email=EMAIL_CONFIG['sender_email'],
            sender_password=EMAIL_CONFIG['sender_password'],
            receiver_email=EMAIL_CONFIG['receiver_email']
        )
        
        # 发送测试邮件
        result = alert.send_email(
            subject="[测试] 量化交易系统邮箱配置",
            content="这是一封测试邮件，如果你收到这封邮件，说明邮箱配置成功！"
        )
        
        if result:
            print("\n✓ 邮箱配置成功！")
            print("请检查你的收件箱")
        else:
            print("\n✗ 邮箱配置失败，请检查配置")
        
        return result
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        return False


def main():
    """主函数"""
    show_email_guide()
    
    print("="*60)
    print("请填写邮箱信息")
    print("="*60)
    
    # 获取用户输入
    sender_email = input("\n请输入你的QQ邮箱: ").strip()
    sender_password = input("请输入授权码: ").strip()
    receiver_email = input("请输入接收报警的邮箱: ").strip()
    
    # 验证输入
    if not sender_email or not sender_password or not receiver_email:
        print("\n错误：邮箱信息不能为空")
        return
    
    # 保存配置
    create_email_config(sender_email, sender_password, receiver_email)
    
    # 测试配置
    test_email_config()


if __name__ == '__main__':
    main()
