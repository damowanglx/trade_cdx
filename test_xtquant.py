import sys

sys.path.insert(0, r"D:\国金QMT\国金证券QMT交易端\bin.x64")

try:
    from xtquant import xtdata
    print("[OK] xtquant导入成功")
    
    # 获取平安银行最新行情
    data = xtdata.get_market_data_ex(
        field_list=["close", "open", "high", "low", "volume"],
        stock_list=["000001.SZ"],
        period="1d",
        count=5
    )
    
    if data and "000001.SZ" in data:
        df = data["000001.SZ"]
        print(f"\n平安银行最近5日行情:")
        print(df)
    else:
        print("[提示] 未获取到数据，可能需要启动QMT交易端")
        
except ImportError as e:
    print(f"[错误] 导入失败: {e}")
    print("\n可能原因：")
    print("1. QMT未启动")
    print("2. xtquant库未正确安装")
    print("3. 需要在QMT的Python环境中运行")
except Exception as e:
    print(f"[错误] {e}")
