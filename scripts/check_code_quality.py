"""
代码质量检查脚本
检查类型提示、docstring、注释、错误处理

使用方法：
    python scripts/check_code_quality.py
"""

import ast
import os
import sys


class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self):
        self.issues = []
    
    def check_file(self, filepath):
        """检查单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 检查类型提示
            self.check_type_hints(tree, filepath)
            
            # 检查docstring
            self.check_docstrings(tree, filepath)
            
            # 检查错误处理
            self.check_error_handling(tree, filepath)
            
        except Exception as e:
            self.issues.append(f"{filepath}: 解析错误 - {e}")
    
    def check_type_hints(self, tree, filepath):
        """检查类型提示"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数参数是否有类型提示
                for arg in node.args.args:
                    if arg.annotation is None:
                        self.issues.append(f"{filepath}:{node.lineno} 函数 {node.name} 参数 {arg.arg} 缺少类型提示")
                
                # 检查返回值是否有类型提示
                if node.returns is None:
                    self.issues.append(f"{filepath}:{node.lineno} 函数 {node.name} 缺少返回值类型提示")
    
    def check_docstrings(self, tree, filepath):
        """检查docstring"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # 检查是否有docstring
                if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str)):
                    self.issues.append(f"{filepath}:{node.lineno} {node.name} 缺少docstring")
    
    def check_error_handling(self, tree, filepath):
        """检查错误处理"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # 检查是否有except子句
                if not node.handlers:
                    self.issues.append(f"{filepath}:{node.lineno} try块缺少except子句")
    
    def check_directory(self, directory):
        """检查目录中的所有Python文件"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    filepath = os.path.join(root, file)
                    self.check_file(filepath)
    
    def print_report(self):
        """打印检查报告"""
        print("="*60)
        print("代码质量检查报告")
        print("="*60)
        
        if not self.issues:
            print("✓ 未发现代码质量问题")
        else:
            print(f"发现 {len(self.issues)} 个问题：")
            for issue in self.issues[:20]:  # 只显示前20个
                print(f"  - {issue}")
            
            if len(self.issues) > 20:
                print(f"  ... 还有 {len(self.issues) - 20} 个问题")
        
        print("="*60)


def main():
    """主函数"""
    checker = CodeQualityChecker()
    
    # 检查项目目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checker.check_directory(project_dir)
    
    # 打印报告
    checker.print_report()


if __name__ == '__main__':
    main()
