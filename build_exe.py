# build_exe.py
import PyInstaller.__main__
import os
import sys
def build_exe():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # PyInstaller参数
    args = [
        'frontend_launcher.py',  # 主入口文件
        '--name=文件浏览器',      # 生成的exe名称
        '--onefile',             # 打包成单个exe文件
        '--windowed',            # 不显示控制台窗口（GUI应用）
        '--clean',               # 清理临时文件
        '--noconfirm',           # 不询问确认
        '--add-data', f'file{os.pathsep}file',  # 包含file文件夹
        '--hidden-import=queue',
        '--hidden-import=threading',
        '--hidden-import=re',
        '--hidden-import=time',
    ]
    
    # 如果你的Python版本较新，可能需要添加
    if sys.platform == 'win32':
        args.append('--uac-admin')  # 请求管理员权限（可选）
    
    # 执行打包
    PyInstaller.__main__.run(args)
    
    print("\n✅ 打包完成！")
    print(f"📁 可执行文件位置: {os.path.join(current_dir, 'dist', '文件浏览器.exe')}")

if __name__ == '__main__':
    build_exe()