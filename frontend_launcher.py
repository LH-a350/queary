# frontend_launcher.py（最终优化版）
import os
import sys
import subprocess
import tkinter as tk
from tkinter import font, scrolledtext
import threading
import queue
import re
import time

def resource_path(relative_path):
    """打包后也能正确找到文件"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))  # 改这一行
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class BackendManager:
    """管理后端进程，并解析输出"""
    def __init__(self):
        self.process = None
        self.running = False
        self.output_queue = queue.Queue()
        self.root = None  # 由外部传入，用于在主线程调度回调
        
    def start_backend(self, log_callback):
        if self.running:
            return
        
        # 使用 resource_path 获取后端路径
        backend_path = resource_path(os.path.join('file', '总程序.py'))
        
        if not os.path.exists(backend_path):
            log_callback(f"❌ 错误: 找不到后端文件 {backend_path}")
            return
        
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 获取后端所在目录作为工作目录
            backend_dir = os.path.dirname(backend_path)
            
            self.process = subprocess.Popen(
                [sys.executable, backend_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=1,
                cwd=backend_dir,  # 使用后端文件所在目录
                env=env
            )
            self.running = True
            log_callback(f"✅ 后端已启动 (PID: {self.process.pid})")
            
            def read_output():
                try:
                    for line in iter(self.process.stdout.readline, ''):
                        if line:
                            self.output_queue.put(line.rstrip())
                except Exception as e:
                    log_callback(f"⚠️ 读取输出时出错: {e}")
                finally:
                    self.running = False
                    log_callback("⚠️ 后端进程已结束")
                
            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            log_callback(f"❌ 启动失败: {e}")
            self.running = False
    
    def send_input(self, text):
        if self.running and self.process and self.process.stdin:
            try:
                self.process.stdin.write(text + '\n')
                self.process.stdin.flush()
                return True
            except (BrokenPipeError, OSError) as e:
                # 管道已关闭，说明后端已退出
                self.running = False
                return False
            except Exception:
                return False
        return False
    
    def stop_backend(self, log_callback, callback=None):
        """异步停止后端进程，完成后调用 callback（在主线程）"""
        if self.process and self.running:
            def stop_thread():
                try:
                    # 先尝试优雅终止
                    self.process.terminate()
                    # 等待最多 2 秒，若未退出则强制 kill
                    for _ in range(20):  # 0.1s * 20 = 2s
                        if self.process.poll() is not None:
                            break
                        time.sleep(0.1)
                    else:
                        # 超时，强制杀死
                        self.process.kill()
                        log_callback("⚠️ 后端进程被强制终止")
                    
                    self.running = False
                    log_callback("🛑 后端已停止")
                except Exception as e:
                    log_callback(f"❌ 停止失败: {e}")
                    self.running = False
                finally:
                    if callback and self.root:
                        self.root.after(0, callback)
            threading.Thread(target=stop_thread, daemon=True).start()
        else:
            log_callback("⚠️ 后端未运行")
            if callback:
                callback()

class FullscreenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文件浏览器前端")
        self.root.configure(bg='#FDF5E6')
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        title_font = font.Font(family='微软雅黑', size=20, weight='bold')
        btn_font = font.Font(family='微软雅黑', size=12)
        list_font = font.Font(family='微软雅黑', size=11)
        output_font = font.Font(family='Consolas', size=10)
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        top_frame = tk.Frame(self.root, bg='#FDF5E6', height=60)
        top_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=(10,5))
        top_frame.grid_propagate(False)
        title = tk.Label(top_frame, text="📁 图形化Python题目浏览器", 
                         font=title_font, bg='#FDF5E6', fg='#5D4037')
        title.pack(side='left')
        self.status_label = tk.Label(top_frame, text="⏹ 未启动", 
                                     font=btn_font, bg='#FDF5E6', fg='#C62828')
        self.status_label.pack(side='right')
        
        mid_frame = tk.Frame(self.root, bg='#FDF5E6')
        mid_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=5)
        mid_frame.grid_rowconfigure(0, weight=1)
        mid_frame.grid_columnconfigure(0, weight=1)
        mid_frame.grid_columnconfigure(1, weight=2)
        
        left_frame = tk.Frame(mid_frame, bg='#FDF5E6', relief='groove', bd=2)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0,10))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        self.path_label = tk.Label(left_frame, text="📂 根目录", 
                                   font=btn_font, bg='#FDF5E6', anchor='w')
        self.path_label.grid(row=0, column=0, sticky='ew', pady=(5,5))
        
        list_container = tk.Frame(left_frame, bg='#FFFFFF')
        list_container.grid(row=1, column=0, sticky='nsew')
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        self.listbox = tk.Listbox(list_container, font=list_font, 
                                  bg='#FFFFFF', fg='#333', 
                                  selectbackground='#BBDEFB',
                                  relief='flat', bd=0)
        self.listbox.grid(row=0, column=0, sticky='nsew')
        scrollbar = tk.Scrollbar(list_container, orient='vertical', 
                                 command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind('<Double-Button-1>', self.on_item_double_click)
        
        right_frame = tk.Frame(mid_frame, bg='#FDF5E6')
        right_frame.grid(row=0, column=1, sticky='nsew')
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(right_frame, 
                                                     font=output_font,
                                                     bg='#FFF8F0',
                                                     fg='#333',
                                                     relief='sunken',
                                                     bd=2,
                                                     wrap='word')
        self.output_text.grid(row=0, column=0, sticky='nsew')
        self.output_text.config(state='disabled')
        
        bottom_frame = tk.Frame(self.root, bg='#FDF5E6', height=50)
        bottom_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=(5,10))
        bottom_frame.grid_propagate(False)
        
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(bottom_frame, textvariable=self.input_var,
                              font=btn_font, bg='#FFFFFF', fg='#333',
                              relief='sunken', bd=2)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0,10))
        self.entry.bind('<Return>', self.send_command)
        self.entry.config(state='disabled')
        
        self.send_btn = tk.Button(bottom_frame, text="发送命令", 
                                  font=btn_font, bg='#42A5F5', fg='white',
                                  padx=15, pady=5, relief='flat',
                                  command=self.send_command)
        self.send_btn.pack(side='left', padx=(0,10))
        self.send_btn.config(state='disabled')
        
        self.start_btn = tk.Button(bottom_frame, text="▶ 启动后端", 
                                   font=btn_font, bg='#8BC34A', fg='white',
                                   padx=15, pady=5, relief='flat',
                                   command=self.start_backend)
        self.start_btn.pack(side='left', padx=(0,5))
        
        self.stop_btn = tk.Button(bottom_frame, text="⏹ 停止", 
                                  font=btn_font, bg='#EF5350', fg='white',
                                  padx=15, pady=5, relief='flat',
                                  command=self.stop_backend)
        self.stop_btn.pack(side='left', padx=(0,5))
        self.stop_btn.config(state='disabled')
        
        quit_btn = tk.Button(bottom_frame, text="✖ 退出", 
                             font=btn_font, bg='#BDBDBD', fg='#333',
                             padx=15, pady=5, relief='flat',
                             command=self.quit_app)
        quit_btn.pack(side='left')
        
        # 初始化后端管理器，并传入 root 引用
        self.backend = BackendManager()
        self.backend.root = self.root
        
        self.current_items = []
        self.poll_output()
    
    def toggle_fullscreen(self, event=None):
        is_full = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_full)
    
    def log_output(self, msg):
        self.output_text.config(state='normal')
        self.output_text.insert('end', msg + '\n')
        self.output_text.see('end')
        self.output_text.config(state='disabled')
    
    def update_status(self, running):
        if running:
            self.status_label.config(text="✅ 运行中", fg='#2E7D32')
            self.start_btn.config(state='disabled', bg='#9E9E9E')
            self.stop_btn.config(state='normal', bg='#EF5350')
            self.entry.config(state='normal')
            self.send_btn.config(state='normal')
        else:
            self.status_label.config(text="⏹ 已停止", fg='#C62828')
            self.start_btn.config(state='normal', bg='#8BC34A')
            self.stop_btn.config(state='disabled', bg='#9E9E9E')
            self.entry.config(state='disabled')
            self.send_btn.config(state='disabled')
    
    def parse_listing(self, line):
        pattern = r'^\s*(\d+)\.\s+([📂📄])\s+(.+?)(?:/)?\s*$'
        match = re.match(pattern, line)
        if match:
            idx = int(match.group(1))
            icon = match.group(2)
            name = match.group(3).strip()
            typ = 'folder' if icon == '📂' else 'file'
            return (idx, name, typ)
        return None
    
    def update_listbox(self, lines):
        items = []
        for line in lines:
            parsed = self.parse_listing(line)
            if parsed:
                items.append(parsed)
        if items:
            self.current_items = items
            self.listbox.delete(0, tk.END)
            for idx, name, typ in items:
                if typ == 'folder':
                    display = f"📂 {name}/"
                else:
                    display = f"📄 {name}"
                self.listbox.insert(tk.END, display)
    
    def on_item_double_click(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index < len(self.current_items):
            idx, name, typ = self.current_items[index]
            if typ == 'folder':
                self.backend.send_input(str(idx))
                self.listbox.delete(0, tk.END)
                self.current_items = []
                self.log_output(f"📂 进入文件夹: {name}")
            else:
                self.show_file_menu(idx, name)
    
    def show_file_menu(self, idx, name):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="查看代码", command=lambda: self.send_file_operation(idx, 1))
        menu.add_command(label="运行文件", command=lambda: self.send_file_operation(idx, 2))
        menu.add_command(label="查看信息", command=lambda: self.send_file_operation(idx, 3))
        menu.add_command(label="复制路径", command=lambda: self.send_file_operation(idx, 4))
        menu.add_separator()
        menu.add_command(label="取消", command=menu.destroy)
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()
    
    def send_file_operation(self, idx, op_num):
        self.backend.send_input(str(idx))
        self.root.after(300, lambda: self.backend.send_input(str(op_num)))
        self.log_output(f"📄 文件 {idx} 执行操作 {op_num}")
    
    def send_command(self, event=None):
        cmd = self.input_var.get().strip()
        if cmd:
            self.backend.send_input(cmd)
            self.input_var.set('')
            self.log_output(f"> {cmd}")
    
    def poll_output(self):
        lines = []
        while True:
            try:
                line = self.backend.output_queue.get_nowait()
                lines.append(line)
            except queue.Empty:
                break
        
        if lines:
            for line in lines:
                self.log_output(line)
            self.update_listbox(lines)
            for line in lines:
                if '当前位置:' in line:
                    path_part = line.split('当前位置:')[-1].strip()
                    self.path_label.config(text=f"📂 {path_part}")
                if "根目录" in line and "当前位置" in line:
                    self.path_label.config(text="📂 根目录")
        
        self.root.after(200, self.poll_output)
    
    def start_backend(self):
        self.log_output("⏳ 正在启动后端...")
        self.backend.start_backend(self.log_output)
        self.root.after(500, self.check_start)
    
    def check_start(self):
        if self.backend.running:
            self.update_status(True)
        else:
            self.update_status(False)
    
    def stop_backend(self):
        """点击停止按钮时调用"""
        self.log_output("⏳ 正在停止后端...")
        self.stop_btn.config(state='disabled')
        self.backend.stop_backend(self.log_output, self.on_stopped)
    
    def on_stopped(self):
        """后端停止后的清理回调（在主线程执行）"""
        self.update_status(False)
        self.listbox.delete(0, tk.END)
        self.current_items = []
        self.path_label.config(text="📂 根目录")
        self.log_output("✅ 后端已完全停止，界面已重置")
    
    def quit_app(self):
        """退出程序，如果后端在运行则先停止"""
        if self.backend.running:
            self.log_output("🔄 正在停止后端并退出...")
            self.backend.stop_backend(self.log_output, self.finish_quit)
        else:
            self.root.destroy()
    
    def finish_quit(self):
        """停止后端后，最终退出"""
        self.root.destroy()

if __name__ == "__main__":
    app = FullscreenApp()
    app.root.mainloop()