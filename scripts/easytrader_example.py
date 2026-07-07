"""
easytrader使用示例
零门槛量化交易

使用方法：
    python scripts/easytrader_example.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import easytrader
    print("easytrader导入成功")
except ImportError:
    print("请先安装easytrader: pip install easytrader pywinauto")
    sys.exit(1)


def main():
    """主函数"""
    print("="*60)
    print("easytrader量化交易示例")
    print("="*60)
    
    # 1. 连接券商客户端
    print("\n[步骤1] 连接国金证券客户端...")
    
    # 方式1：自动查找客户端
    # user = easytrader.use('gj')  # 国金证券
    
    # 方式2：指定客户端路径
    user = easytrader.use('gj')
    
    try:
        # 连接客户端（需要客户端已启动并登录）
        user.connect(r'D:\国金QMT\国金证券QMT交易端\bin.x64\XtMiniQmt.exe')
        print("[OK] 连接成功")
    except Exception as e:
        print(f"[错误] 连接失败: {e}")
        print("\n请确保：")
        print("1. 国金证券客户端已启动")
        print("2. 已登录账户")
        print("3. 客户端路径正确")
        return
    
    # 2. 获取账户信息
    print("\n[步骤2] 获取账户信息...")
    try:
        balance = user.balance
        print(f"总资产: {balance.get('总资产', 'N/A')}")
        print(f"可用资金: {balance.get('可用资金', 'N/A')}")
        print(f"持仓市值: {balance.get('证券市值', 'N/A')}")
    except Exception as e:
        print(f"获取账户信息失败: {e}")
    
    # 3. 获取持仓
    print("\n[步骤3] 获取持仓...")
    try:
        position = user.position
        if position:
            print("当前持仓:")
            for stock in position:
                print(f"  {stock.get('证券代码')}: {stock.get('股票余额')}股")
        else:
            print("当前无持仓")
    except Exception as e:
        print(f"获取持仓失败: {e}")
    
    # 4. 获取实时行情
    print("\n[步骤4] 获取实时行情...")
    try:
        # 获取平安银行行情
        quote = user.get_quote('000001')
        print(f"平安银行(000001):")
        print(f"  最新价: {quote.get('最新价', 'N/A')}")
        print(f"  涨跌幅: {quote.get('涨跌幅', 'N/A')}%")
    except Exception as e:
        print(f"获取行情失败: {e}")
    
    print("\n" + "="*60)
    print("easytrader连接测试完成！")
    print("="*60)
    print("\n下一步：")
    print("1. 修改配置文件中的账号密码")
    print("2. 运行RSI策略进行模拟交易")
    print("3. 监控交易结果")


if __name__ == '__main__':
    main()
