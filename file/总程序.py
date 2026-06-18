# p.py
import subprocess
import os
import sys

class FileBrowser:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.current_path = self.current_dir
        self.history = []  # 用于返回上一级
        
    def get_items(self, path):
        """获取当前路径下的所有项目和文件夹"""
        items = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                # 排除当前脚本文件
                if item_path == os.path.join(self.current_dir, 'p.py'):
                    continue
                    
                if os.path.isdir(item_path):
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'folder'
                    })
                elif item.endswith('.py'):
                    # 如果在根目录，不显示Python文件
                    if path == self.current_dir:
                        continue
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'file'
                    })
        except PermissionError:
            print(f"无法访问: {path}")
        
        # 排序：文件夹在前，文件在后
        items.sort(key=lambda x: (x['type'] != 'folder', x['name']))
        return items
    
    def display_browser(self, items):
        """显示文件浏览器界面"""
        print("\n" + "="*60)
        print("Python文件浏览器")
        print("="*60)
        
        # 显示当前路径
        rel_path = os.path.relpath(self.current_path, self.current_dir)
        if rel_path == '.':
            display_path = '根目录'
        else:
            display_path = rel_path
        print(f"📁 当前位置: {display_path}")
        print("-"*60)
        
        # 显示内容
        if not items:
            print("  (空目录)")
        else:
            for idx, item in enumerate(items, 1):
                if item['type'] == 'folder':
                    print(f"{idx:2}. 📂 {item['name']}/")
                else:
                    print(f"{idx:2}. 📄 {item['name']}")
        
        print("-"*60)
        
        # 菜单选项
        print("操作选项:")
        print("  [数字] - 进入文件夹或选择文件")
        if self.history:
            print("  b      - 返回上一级")
        else:
            print("  b      - (已在根目录)")
        print("  q      - 退出程序")
        print("="*60)
    
    def view_code(self, file_path):
        """查看文件代码"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print("\n" + "="*60)
            print(f"📄 文件: {os.path.basename(file_path)}")
            print(f"📁 路径: {os.path.relpath(file_path, self.current_dir)}")
            print("="*60)
            
            # 显示带行号的代码
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                print(f"{i:4} | {line}")
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
    
    def run_file(self, file_path):
        """运行Python文件"""
        print("\n" + "="*60)
        print(f"▶ 正在运行: {os.path.basename(file_path)}")
        print("="*60)
        
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                print("📤 输出:")
                print(result.stdout)
            
            if result.stderr:
                print("⚠️  错误:")
                print(result.stderr)
            
            if result.returncode == 0:
                print(f"\n✅ 运行成功！")
            else:
                print(f"\n❌ 运行失败，退出码: {result.returncode}")
            
        except subprocess.TimeoutExpired:
            print("❌ 运行超时（30秒）")
        except Exception as e:
            print(f"❌ 运行出错: {e}")
    
    def show_file_info(self, file_path):
        """显示文件信息"""
        try:
            stat = os.stat(file_path)
            print("\n" + "="*60)
            print("📋 文件信息")
            print("="*60)
            print(f"文件名: {os.path.basename(file_path)}")
            print(f"路径: {os.path.relpath(file_path, self.current_dir)}")
            print(f"大小: {stat.st_size/1024:.2f} KB")
            print(f"修改时间: {os.path.getmtime(file_path)}")
            print("="*60)
        except Exception as e:
            print(f"❌ 获取信息失败: {e}")
    
    def copy_path(self, file_path):
        """复制文件路径到剪贴板（如果可用）"""
        try:
            import pyperclip # type: ignore
            pyperclip.copy(file_path)
            print(f"✅ 路径已复制到剪贴板")
        except ImportError:
            # 如果没有pyperclip，直接显示路径
            print(f"📋 文件路径: {file_path}")
            print("💡 提示: 安装 pyperclip (pip install pyperclip) 可支持自动复制")
    
    def handle_file_selection(self, file_path):
        """处理选中文件后的操作"""
        while True:
            print("\n" + "-"*60)
            print(f"📄 文件: {os.path.basename(file_path)}")
            print("操作选项:")
            print("  1. 查看代码")
            print("  2. 运行文件")
            print("  3. 查看文件信息")
            print("  4. 复制文件路径")
            print("  5. 返回")
            print("-"*60)
            
            action = input("👉 请选择操作: ").strip()
            
            if action == '1':
                self.view_code(file_path)
                input("\n按Enter键继续...")
            elif action == '2':
                self.run_file(file_path)
                input("\n按Enter键继续...")
            elif action == '3':
                self.show_file_info(file_path)
                input("\n按Enter键继续...")
            elif action == '4':
                self.copy_path(file_path)
                input("\n按Enter键继续...")
            elif action == '5':
                break
            else:
                print("❌ 无效选择，请重新输入")
    
    def run(self):
        """主程序"""
        while True:
            # 获取当前目录内容
            items = self.get_items(self.current_path)
            
            # 显示浏览器
            self.display_browser(items)
            
            # 获取用户输入
            try:
                choice = input("\n👉 请输入选项: ").strip().lower()
                
                if not choice:
                    continue
                
                # 处理特殊命令
                if choice == 'q':
                    print("\n👋 再见！")
                    break
                
                if choice == 'b':
                    if self.history:
                        self.current_path = self.history.pop()
                        continue
                    else:
                        print("⚠️  已在根目录")
                        input("按Enter键继续...")
                        continue
                
                # 尝试转换为数字
                try:
                    choice_num = int(choice)
                except ValueError:
                    print("❌ 无效输入，请输入数字或命令 (b/q)")
                    input("按Enter键继续...")
                    continue
                
                # 检查选择是否有效
                if 1 <= choice_num <= len(items):
                    selected = items[choice_num - 1]
                    
                    if selected['type'] == 'folder':
                        # 进入文件夹
                        self.history.append(self.current_path)
                        self.current_path = selected['path']
                    else:
                        # 处理文件
                        self.handle_file_selection(selected['path'])
                else:
                    print("❌ 无效选择，请重新输入")
                    input("按Enter键继续...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                input("按Enter键继续...")

def main():
    browser = FileBrowser()
    browser.run()

main()