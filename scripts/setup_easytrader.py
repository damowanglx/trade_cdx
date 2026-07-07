"""
easytrader配置脚本
零门槛量化交易方案

使用方法：
    python scripts/setup_easytrader.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_easytrader():
    """检查easytrader是否安装"""
    print("=== 检查easytrader安装 ===")
    
    try:
        import easytrader
        print("[OK] easytrader已安装")
        print(f"版本: {easytrader.__version__}")
        return True
    except ImportError:
        print("[错误] easytrader未安装")
        print("请运行: pip install easytrader pywinauto")
        return False


def check_pywinauto():
    """检查pywinauto是否安装"""
    print("\n=== 检查pywinauto安装 ===")
    
    try:
        import pywinauto
        print("[OK] pywinauto已安装")
        return True
    except ImportError:
        print("[错误] pywinauto未安装")
        print("请运行: pip install pywinauto")
        return False


def find_broker_client():
    """查找券商客户端"""
    print("\n=== 查找券商客户端 ===")
    
    # 常见券商客户端路径
    common_paths = [
        r'C:\国金证券',
        r'C:\国金QMT',
        r'D:\国金证券',
        r'D:\国金QMT',
        r'C:\Program Files\国金证券',
        r'C:\Program Files (x86)\国金证券',
    ]
    
    found_paths = []
    for path in common_paths:
        if os.path.exists(path):
            found_paths.append(path)
            print(f"[找到] {path}")
    
    if not found_paths:
        print("[提示] 未找到默认安装路径")
        print("请手动指定客户端路径")
    
    return found_paths


def create_easytrader_config():
    """创建easytrader配置"""
    print("\n=== 创建easytrader配置 ===")
    
    config = {
        'broker': 'gj',  # 国金证券
        'client_path': r'D:\国金QMT\国金证券QMT交易端\bin.x64\XtMiniQmt.exe',
        'account': '你的资金账号',
        'password': '你的密码',
    }
    
    # 保存配置
    os.makedirs('config', exist_ok=True)
    
    with open('config/easytrader_config.py', 'w', encoding='utf-8') as f:
        f.write('"""easytrader配置"""\n\n')
        f.write('EASYTRADER_CONFIG = {\n')
        for key, value in config.items():
            f.write(f"    '{key}': '{value}',\n")
        f.write('}\n')
    
    print("[OK] 配置已创建: config/easytrader_config.py")
    print("\n请修改配置文件：")
    print("1. 填写你的资金账号")
    print("2. 填写你的密码")
    print("3. 确认客户端路径正确")
    
    return config


def create_easytrader_example():
    """创建easytrader使用示例"""
    print("\n=== 创建easytrader使用示例 ===")
    
    example_code = '''"""
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
    print("\\n[步骤1] 连接国金证券客户端...")
    
    # 方式1：自动查找客户端
    # user = easytrader.use('gj')  # 国金证券
    
    # 方式2：指定客户端路径
    user = easytrader.use('gj')
    
    try:
        # 连接客户端（需要客户端已启动并登录）
        user.connect(r'D:\\国金QMT\\国金证券QMT交易端\\bin.x64\\XtMiniQmt.exe')
        print("[OK] 连接成功")
    except Exception as e:
        print(f"[错误] 连接失败: {e}")
        print("\\n请确保：")
        print("1. 国金证券客户端已启动")
        print("2. 已登录账户")
        print("3. 客户端路径正确")
        return
    
    # 2. 获取账户信息
    print("\\n[步骤2] 获取账户信息...")
    try:
        balance = user.balance
        print(f"总资产: {balance.get('总资产', 'N/A')}")
        print(f"可用资金: {balance.get('可用资金', 'N/A')}")
        print(f"持仓市值: {balance.get('证券市值', 'N/A')}")
    except Exception as e:
        print(f"获取账户信息失败: {e}")
    
    # 3. 获取持仓
    print("\\n[步骤3] 获取持仓...")
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
    print("\\n[步骤4] 获取实时行情...")
    try:
        # 获取平安银行行情
        quote = user.get_quote('000001')
        print(f"平安银行(000001):")
        print(f"  最新价: {quote.get('最新价', 'N/A')}")
        print(f"  涨跌幅: {quote.get('涨跌幅', 'N/A')}%")
    except Exception as e:
        print(f"获取行情失败: {e}")
    
    print("\\n" + "="*60)
    print("easytrader连接测试完成！")
    print("="*60)
    print("\\n下一步：")
    print("1. 修改配置文件中的账号密码")
    print("2. 运行RSI策略进行模拟交易")
    print("3. 监控交易结果")


if __name__ == '__main__':
    main()
'''
    
    with open('scripts/easytrader_example.py', 'w', encoding='utf-8') as f:
        f.write(example_code)
    
    print("[OK] 示例脚本已创建: scripts/easytrader_example.py")


def main():
    """主函数"""
    print("="*60)
    print("easytrader零门槛量化交易配置")
    print("="*60)
    print("\n无需开通QMT，用现有国金证券账户即可！")
    
    # 检查安装
    if not check_easytrader():
        print("\n请先安装easytrader:")
        print("pip install easytrader pywinauto")
        return
    
    if not check_pywinauto():
        print("\n请先安装pywinauto:")
        print("pip install pywinauto")
        return
    
    # 查找客户端
    find_broker_client()
    
    # 创建配置
    create_easytrader_config()
    
    # 创建示例
    create_easytrader_example()
    
    print("\n" + "="*60)
    print("配置完成！")
    print("="*60)
    print("\n下一步：")
    print("1. 启动国金证券客户端并登录")
    print("2. 修改 config/easytrader_config.py 中的账号密码")
    print("3. 运行 python scripts/easytrader_example.py 测试连接")


if __name__ == '__main__':
    main()
