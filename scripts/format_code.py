"""
代码格式化脚本
使用black和isort格式化代码

使用方法：
    python scripts/format_code.py
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """运行命令"""
    print(f"\n{description}...")
    print(f"命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ 成功")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"✗ 失败")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("代码格式化")
    print("="*60)
    
    # 检查是否安装了black和isort
    print("\n检查依赖...")
    
    try:
        import black
        print("✓ black已安装")
    except ImportError:
        print("✗ black未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "black"], capture_output=True)
    
    try:
        import isort
        print("✓ isort已安装")
    except ImportError:
        print("✗ isort未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "isort"], capture_output=True)
    
    # 格式化代码
    print("\n" + "="*60)
    print("开始格式化...")
    print("="*60)
    
    # 使用isort排序导入
    run_command(
        "isort . --profile black --line-length 127",
        "isort: 排序导入语句"
    )
    
    # 使用black格式化代码
    run_command(
        "black . --line-length 127",
        "black: 格式化代码"
    )
    
    # 检查格式化结果
    print("\n" + "="*60)
    print("检查格式化结果...")
    print("="*60)
    
    run_command(
        "black --check . --line-length 127",
        "black: 检查格式"
    )
    
    run_command(
        "isort --check-only . --profile black --line-length 127",
        "isort: 检查导入"
    )
    
    print("\n" + "="*60)
    print("格式化完成！")
    print("="*60)


if __name__ == '__main__':
    main()
