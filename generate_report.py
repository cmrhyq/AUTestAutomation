#!/usr/bin/env python3
"""
Allure 报告生成脚本

该脚本提供便捷的命令来生成和查看 Allure 测试报告。

使用方式:
    python generate_report.py serve          # 生成并在浏览器中打开报告
    python generate_report.py generate       # 生成静态报告
    python generate_report.py open           # 打开已生成的报告
    python generate_report.py clean          # 清理报告文件

"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class AllureReportGenerator:
    """Allure 报告生成器"""
    
    def __init__(self):
        self.results_dir = "report/allure-results"
        self.report_dir = "report/allure-report"
    
    def check_allure_installed(self) -> bool:
        """检查 Allure 命令行工具是否已安装"""
        try:
            result = subprocess.run(
                ["allure", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"✓ Allure 已安装: {result.stdout.strip()}")
                return True
            else:
                print("✗ Allure 未安装或无法访问")
                return False
        except FileNotFoundError:
            print("✗ Allure 未安装")
            return False
    
    def print_installation_instructions(self):
        """打印 Allure 安装说明"""
        print("\n请安装 Allure 命令行工具:")
        print("\nmacOS (使用 Homebrew):")
        print("  brew install allure")
        print("\nWindows (使用 Scoop):")
        print("  scoop install allure")
        print("\nLinux:")
        print("  从 https://github.com/allure-framework/allure2/releases 下载")
        print("  解压并添加到 PATH\n")
    
    def serve(self):
        """生成并在浏览器中打开报告"""
        print(f"正在生成并打开 Allure 报告...")
        print(f"结果目录: {self.results_dir}")
        
        if not Path(self.results_dir).exists():
            print(f"✗ 错误: 结果目录 '{self.results_dir}' 不存在")
            print("请先运行测试: pytest --alluredir=report/allure-results")
            return False
        
        try:
            subprocess.run(
                ["allure", "serve", self.results_dir],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 生成报告失败: {e}")
            return False
        except KeyboardInterrupt:
            print("\n报告服务已停止")
            return True
    
    def generate(self):
        """生成静态报告"""
        print(f"正在生成静态 Allure 报告...")
        print(f"结果目录: {self.results_dir}")
        print(f"报告目录: {self.report_dir}")
        
        if not Path(self.results_dir).exists():
            print(f"✗ 错误: 结果目录 '{self.results_dir}' 不存在")
            print("请先运行测试: pytest --alluredir=allure-results")
            return False
        
        try:
            subprocess.run(
                ["allure", "generate", self.results_dir, "-o", self.report_dir, "--clean"],
                check=True
            )
            print(f"✓ 报告已生成到: {self.report_dir}")
            print(f"使用以下命令打开报告:")
            print(f"  allure open {self.report_dir}")
            print(f"  或")
            print(f"  python generate_report.py open")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 生成报告失败: {e}")
            return False
    
    def open_report(self):
        """打开已生成的报告"""
        print(f"正在打开 Allure 报告...")
        print(f"报告目录: {self.report_dir}")
        
        if not Path(self.report_dir).exists():
            print(f"✗ 错误: 报告目录 '{self.report_dir}' 不存在")
            print("请先生成报告: python generate_report.py generate")
            return False
        
        try:
            subprocess.run(
                ["allure", "open", self.report_dir],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 打开报告失败: {e}")
            return False
        except KeyboardInterrupt:
            print("\n报告服务已停止")
            return True
    
    def clean(self):
        """清理报告文件"""
        print("正在清理报告文件...")
        
        cleaned = False
        
        if Path(self.results_dir).exists():
            shutil.rmtree(self.results_dir)
            print(f"✓ 已删除: {self.results_dir}")
            cleaned = True
        
        if Path(self.report_dir).exists():
            shutil.rmtree(self.report_dir)
            print(f"✓ 已删除: {self.report_dir}")
            cleaned = True
        
        if not cleaned:
            print("没有需要清理的文件")
        
        return True
    
    def print_usage(self):
        """打印使用说明"""
        print("Allure 报告生成脚本")
        print("\n使用方式:")
        print("  python generate_report.py serve      # 生成并在浏览器中打开报告")
        print("  python generate_report.py generate   # 生成静态报告")
        print("  python generate_report.py open       # 打开已生成的报告")
        print("  python generate_report.py clean      # 清理报告文件")
        print("\n示例:")
        print("  1. 运行测试:")
        print("     pytest --alluredir=allure-results")
        print("\n  2. 查看报告:")
        print("     python generate_report.py serve")


def main():
    """主函数"""
    generator = AllureReportGenerator()
    
    # 检查 Allure 是否已安装
    if not generator.check_allure_installed():
        generator.print_installation_instructions()
        sys.exit(1)
    
    # 解析命令行参数
    if len(sys.argv) < 2:
        generator.print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'serve': generator.serve,
        'generate': generator.generate,
        'open': generator.open_report,
        'clean': generator.clean,
        'help': generator.print_usage,
    }
    
    if command in commands:
        success = commands[command]()
        sys.exit(0 if success else 1)
    else:
        print(f"✗ 未知命令: {command}")
        generator.print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
