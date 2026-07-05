#coding:gbk
"""
QMT连接测试脚本
测试是否能连接到QMT交易端

使用方法：
    在QMT的Python环境中运行此脚本
"""

import sys
import os

print("="*60)
print("QMT连接测试")
print("="*60)

try:
    # 尝试导入xtquant
    print("\n[1] 测试导入xtquant库...")
    import xtquant
    from xtquant import xtdata
    from xtquant import xttrader
    print("[OK] xtquant库导入成功")
    
    # 测试获取行情数据
    print("\n[2] 测试获取行情数据...")
    try:
        # 获取平安银行的最新行情
        stock_code = "000001.SZ"
        data = xtdata.get_market_data_ex(
            field_list=["close"],
            stock_list=[stock_code],
            period="1d",
            count=1
        )
        
        if data and stock_code in data:
            df = data[stock_code]
            if not df.empty:
                latest_price = df['close'].iloc[-1]
                print(f"[OK] 获取行情成功: {stock_code} 最新价 = {latest_price}")
            else:
                print("[警告] 行情数据为空")
        else:
            print("[警告] 未获取到行情数据")
    except Exception as e:
        print(f"[错误] 获取行情失败: {e}")
    
    # 测试连接交易服务器
    print("\n[3] 测试连接交易服务器...")
    try:
        # 创建交易对象
        trader = xttrader.XtQuantTrader()
        
        # 尝试连接（需要QMT交易端已启动）
        # 注意：实际连接需要在QMT交易端中运行
        print("[提示] 交易连接测试需要在QMT交易端中运行")
        print("[提示] 请确保QMT交易端已启动并登录")
        
    except Exception as e:
        print(f"[提示] 交易连接测试: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    print("\n下一步：")
    print("1. 确保QMT交易端已启动")
    print("2. 在QMT中加载策略文件")
    print("3. 使用模拟盘测试")
    
except ImportError as e:
    print(f"\n[错误] 无法导入xtquant: {e}")
    print("\n解决方案：")
    print("1. 确保QMT已正确安装")
    print("2. 在QMT的Python环境中运行此脚本")
    print("3. 或者将此脚本复制到QMT的python目录运行")
except Exception as e:
    print(f"\n[错误] 测试失败: {e}")
