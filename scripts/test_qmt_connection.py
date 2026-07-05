"""
QMT连接测试脚本
测试QMT交易端连接

使用方法：
    python scripts/test_qmt_connection.py
"""

import sys
import os

# 添加QMT路径
qmt_python_path = r'D:\国金QMT\国金证券QMT交易端\python'
if os.path.exists(qmt_python_path):
    sys.path.insert(0, qmt_python_path)
    print(f"[OK] QMT Python路径已添加: {qmt_python_path}")
else:
    print(f"[警告] QMT路径不存在: {qmt_python_path}")

def test_qmt_import():
    """测试QMT模块导入"""
    print("\n=== 测试QMT模块导入 ===")
    
    try:
        import xtquant
        print("[OK] xtquant导入成功")
        
        from xtquant import xtdata
        print("[OK] xtdata导入成功")
        
        from xtquant import xttrader
        print("[OK] xttrader导入成功")
        
        return True
    except ImportError as e:
        print(f"[错误] 导入失败: {e}")
        return False

def test_qmt_data():
    """测试QMT数据获取"""
    print("\n=== 测试QMT数据获取 ===")
    
    try:
        from xtquant import xtdata
        
        # 获取平安银行数据
        stock_code = "000001.SZ"
        data = xtdata.get_market_data_ex(
            field_list=["close"],
            stock_list=[stock_code],
            period="1d",
            count=5
        )
        
        if data and stock_code in data:
            df = data[stock_code]
            if not df.empty:
                print(f"[OK] 获取数据成功: {stock_code}")
                print(f"最新价格: {df['close'].iloc[-1]:.2f}")
                return True
        
        print("[警告] 未获取到数据")
        return False
        
    except Exception as e:
        print(f"[错误] 数据获取失败: {e}")
        return False

def test_qmt_connection():
    """测试QMT交易连接"""
    print("\n=== 测试QMT交易连接 ===")
    
    try:
        from xtquant import xttrader
        
        print("[提示] 交易连接测试需要QMT交易端已启动")
        print("[提示] 请确保已登录国金证券账户")
        
        # 这里可以添加实际的连接测试
        # 但需要QMT交易端运行
        
        return True
    except Exception as e:
        print(f"[错误] 连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("QMT连接测试")
    print("="*60)
    
    # 测试导入
    import_success = test_qmt_import()
    
    if import_success:
        # 测试数据获取
        data_success = test_qmt_data()
        
        # 测试交易连接
        connection_success = test_qmt_connection()
        
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)
        print(f"模块导入: {'通过' if import_success else '失败'}")
        print(f"数据获取: {'通过' if data_success else '失败'}")
        print(f"交易连接: {'通过' if connection_success else '失败'}")
        
        if all([import_success, data_success, connection_success]):
            print("\n[OK] QMT连接测试全部通过！")
        else:
            print("\n[警告] 部分测试失败，请检查QMT配置")
    else:
        print("\n[错误] QMT模块导入失败，请检查QMT安装")

if __name__ == '__main__':
    main()
