"""
QMT模拟盘测试脚本
测试QMT连接和模拟交易

使用方法：
    python scripts/test_qmt_simulation.py
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_qmt_connection():
    """测试QMT连接"""
    print("=== 测试QMT连接 ===")
    
    try:
        # 尝试导入QMT模块
        qmt_path = r'D:\国金QMT\国金证券QMT交易端\python'
        if os.path.exists(qmt_path):
            sys.path.insert(0, qmt_path)
            print(f"[OK] QMT路径: {qmt_path}")
        else:
            print(f"[警告] QMT路径不存在: {qmt_path}")
            return False
        
        # 尝试导入xtquant
        import xtquant
        print("[OK] xtquant导入成功")
        
        from xtquant import xtdata
        print("[OK] xtdata导入成功")
        
        return True
        
    except ImportError as e:
        print(f"[错误] 导入失败: {e}")
        print("[提示] 请确保QMT交易端已启动")
        return False


def test_data_fetch():
    """测试数据获取"""
    print("\n=== 测试数据获取 ===")
    
    try:
        from xtquant import xtdata
        
        # 获取平安银行数据
        stock_code = "000001.SZ"
        print(f"获取 {stock_code} 数据...")
        
        data = xtdata.get_market_data_ex(
            field_list=["close"],
            stock_list=[stock_code],
            period="1d",
            count=5
        )
        
        if data and stock_code in data:
            df = data[stock_code]
            if not df.empty:
                print(f"[OK] 获取数据成功")
                print(f"最新价格: {df['close'].iloc[-1]:.2f}")
                return True
        
        print("[警告] 未获取到数据")
        return False
        
    except Exception as e:
        print(f"[错误] 数据获取失败: {e}")
        return False


def create_simulation_config():
    """创建模拟盘配置"""
    print("\n=== 创建模拟盘配置 ===")
    
    config = {
        'stocks': [
            '000001.SZ',  # 平安银行
            '600036.SH',  # 招商银行
            '600519.SH',  # 贵州茅台
            '000858.SZ',  # 五粮液
            '300750.SZ',  # 宁德时代
        ],
        'strategy': 'RSI',
        'params': {
            'rsi_period': 21,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'stop_loss': 0.10,
            'take_profit': 0.30,
        },
        'capital': 100000,
        'max_position': 0.30,
        'created_at': datetime.now().isoformat()
    }
    
    # 保存配置
    os.makedirs('config', exist_ok=True)
    import json
    with open('config/simulation_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("[OK] 模拟盘配置已创建: config/simulation_config.json")
    print(f"股票列表: {config['stocks']}")
    print(f"策略: {config['strategy']}")
    print(f"参数: {config['params']}")
    print(f"资金: {config['capital']:,}")
    
    return config


def main():
    """主函数"""
    print("="*60)
    print("QMT模拟盘测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试QMT连接
    connection_ok = test_qmt_connection()
    
    if connection_ok:
        # 测试数据获取
        data_ok = test_data_fetch()
        
        if data_ok:
            # 创建模拟盘配置
            config = create_simulation_config()
            
            print("\n" + "="*60)
            print("QMT模拟盘测试完成！")
            print("="*60)
            print("\n下一步：")
            print("1. 在QMT交易端中加载RSI策略")
            print("2. 配置交易股票列表")
            print("3. 开启模拟交易")
            print("4. 监控策略运行")
        else:
            print("\n[警告] 数据获取失败，请检查QMT连接")
    else:
        print("\n[提示] QMT连接失败，请确保：")
        print("1. QMT交易端已启动")
        print("2. 已登录国金证券账户")
        print("3. QMT路径正确")


if __name__ == '__main__':
    main()
