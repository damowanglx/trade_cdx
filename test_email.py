import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 邮箱配置
sender_email = 'damowang123lx@163.com'
sender_password = 'GXrpVgWngzGxpTkb'
receiver_email = 'damowang123lx@163.com'

print('Connecting to 163 SMTP server...')

try:
    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = '[Test] Quant Trading System Email Config Success'
    
    content = f"""
Congratulations! Email configuration successful

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sender: {sender_email}
Receiver: {receiver_email}

You can now receive the following notifications:
- Trading signals (buy/sell)
- Risk alerts (stop loss/take profit)
- Daily investment reports

---
Quant Trading System
"""
    
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    # Connect to SMTP server
    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    
    # Login
    print('Logging in...')
    server.login(sender_email, sender_password)
    
    # Send email
    print('Sending test email...')
    server.sendmail(sender_email, receiver_email, msg.as_string())
    
    # Close connection
    server.quit()
    
    print('')
    print('[OK] Email configuration successful!')
    print('Please check your 163 email inbox')
    
except Exception as e:
    print(f'[ERROR] Email configuration failed: {e}')
    print('')
    print('Possible reasons:')
    print('1. Authorization code error')
    print('2. SMTP service not enabled')
    print('3. Network connection issue')
