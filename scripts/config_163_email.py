"""
163邮箱配置脚本
配置163邮箱报警

使用方法：
    python scripts/config_163_email.py
"""

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def show_163_guide():
    """显示163邮箱配置指南"""
    print("="*60)
    print("163邮箱配置指南")
    print("="*60)
    print()
    print("步骤1：开启SMTP服务")
    print("-"*40)
    print("1. 登录163邮箱：https://mail.163.com")
    print("2. 点击 设置 -> POP3/SMTP/IMAP")
    print("3. 开启 'SMTP服务'")
    print("4. 按提示发送短信验证")
    print("5. 获取授权码（不是邮箱密码！）")
    print()
    print("步骤2：获取授权码")
    print("-"*40)
    print("开启SMTP服务后，会显示授权码")
    print("授权码格式类似：ABCDEFGHIJKLmnop")
    print("注意：授权码不是邮箱密码！")
    print()


def test_163_email(sender_email, sender_password, receiver_email):
    """测试163邮箱连接"""
    print("\n测试163邮箱连接...")
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "[测试] 量化交易系统邮箱配置"
        
        content = f"""
这是一封测试邮件

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
发送者: {sender_email}
接收者: {receiver_email}

如果你收到这封邮件，说明邮箱配置成功！

---
量化交易系统
        """
        
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 连接163 SMTP服务器
        print("连接SMTP服务器...")
        server = smtplib.SMTP_SSL('smtp.163.com', 465)
        
        # 登录
        print("登录邮箱...")
        server.login(sender_email, sender_password)
        
        # 发送邮件
        print("发送邮件...")
        server.sendmail(sender_email, receiver_email, msg.as_string())
        
        # 关闭连接
        server.quit()
        
        print("\n✓ 邮箱配置成功！")
        print("请检查你的收件箱")
        return True
        
    except Exception as e:
        print(f"\n✗ 邮箱配置失败: {e}")
        print("\n可能原因：")
        print("1. 授权码错误（不是邮箱密码）")
        print("2. SMTP服务未开启")
        print("3. 网络连接问题")
        return False


def create_email_config(sender_email, sender_password, receiver_email):
    """创建邮箱配置文件"""
    config_content = f'''"""
163邮箱配置
"""

EMAIL_CONFIG = {{
    'smtp_server': 'smtp.163.com',
    'smtp_port': 465,
    'sender_email': '{sender_email}',
    'sender_password': '{sender_password}',
    'receiver_email': '{receiver_email}',
}}
'''
    
    with open('config/email_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n邮箱配置已保存到: config/email_config.py")


def main():
    """主函数"""
    show_163_guide()
    
    print("="*60)
    print("请填写邮箱信息")
    print("="*60)
    
    # 用户信息
    sender_email = "damowang123lx@163.com"
    
    print(f"\n发送者邮箱: {sender_email}")
    
    # 获取授权码
    sender_password = input("\n请输入163邮箱授权码: ").strip()
    
    # 接收邮箱
    receiver_email = input("请输入接收报警的邮箱: ").strip()
    
    if not sender_password:
        print("\n错误：授权码不能为空")
        return
    
    if not receiver_email:
        receiver_email = sender_email
        print(f"接收邮箱默认为: {receiver_email}")
    
    # 测试连接
    success = test_163_email(sender_email, sender_password, receiver_email)
    
    if success:
        # 保存配置
        create_email_config(sender_email, sender_password, receiver_email)
        
        print("\n" + "="*60)
        print("邮箱配置完成！")
        print("="*60)
        print(f"发送者: {sender_email}")
        print(f"接收者: {receiver_email}")
        print("\n现在可以接收交易信号和风险报警了！")
    else:
        print("\n请检查授权码是否正确，然后重试")


if __name__ == '__main__':
    main()
