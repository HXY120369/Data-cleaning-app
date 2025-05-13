import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
from datetime import datetime
import os

class LogDisplayApp:
    def __init__(self, master):
        self.master = master
        master.title("文件操作日志")

        # 设置窗口的初始大小和位置
        window_width = 700
        window_height = 500
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        master.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        master.minsize(400, 300) # 设置最小尺寸

        style = ttk.Style()
        style.theme_use('clam')

        # 主内容Frame
        main_frame = ttk.Frame(master, padding="10", relief="ridge", borderwidth=2)
        main_frame.pack(fill="both", expand=True)

        # --- 日志显示区域 ---
        log_frame = ttk.Frame(main_frame, relief="ridge", borderwidth=2)
        log_frame.pack(fill='both', expand=True)

        self.log_text_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=15, font=("Arial", 14))
        self.log_text_area.pack(fill='both', expand=True)

        # --- 按钮区域 ---
        button_frame = ttk.Frame(main_frame, padding="10", relief="ridge", borderwidth=2)
        button_frame.pack(fill='x', side='bottom')

        self.clear_button = ttk.Button(button_frame, text="清除日志", command=self.clear_log, width=12)
        self.clear_button.pack(side='left', padx=5, pady=5)

        self.save_button = ttk.Button(button_frame, text="保存日志", command=self.save_log, width=12)
        self.save_button.pack(side='left', padx=5, pady=5)

        self.back_button = ttk.Button(button_frame, text="返回", command=master.destroy, width=12) # 直接关闭窗口
        self.back_button.pack(side='right', padx=5, pady=5) # 靠右放置

        # 可以在这里添加一些示例日志
        self.add_log_entry("应用程序启动。")
        self.add_log_entry("用户 'admin' 登录系统。")

    def add_log_entry(self, message):
        """
        向日志区域添加一条新的日志条目。
        """
        self.log_text_area.config(state=tk.NORMAL) # 先设置为可编辑
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text_area.insert(tk.END, log_entry)
        self.log_text_area.see(tk.END) # 滚动到最新条目
        self.log_text_area.config(state=tk.DISABLED) # 再设置为只读

    def clear_log(self):
        """
        清除日志区域的所有内容。
        """
        confirmed = messagebox.askyesno("确认操作", "您确定要清除所有日志吗？此操作不可撤销。")
        if confirmed:
            self.log_text_area.config(state=tk.NORMAL)
            self.log_text_area.delete(1.0, tk.END)
            self.log_text_area.config(state=tk.DISABLED)
            self.add_log_entry("日志已清除。") # 记录清除操作本身
            messagebox.showinfo("操作完成", "日志已成功清除。")


    def save_log(self):
        """
        将日志区域的内容保存到TXT文件。
        """
        log_content = self.log_text_area.get(1.0, tk.END).strip() # 获取所有内容并移除末尾可能多余的换行
        if not log_content:
            messagebox.showwarning("日志为空", "没有可保存的日志内容。")
            return

        # 弹出文件保存对话框
        # 初始文件名可以包含时间戳
        default_filename = f"操作日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=os.getcwd(), # 默认从当前工作目录开始
            initialfile=default_filename,
            title="保存操作日志"
        )

        if filepath: # 如果用户选择了路径并没有取消
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(log_content + "\n") # 确保文件末尾有一个换行
                self.add_log_entry(f"日志已保存到: {os.path.basename(filepath)}")
                messagebox.showinfo("保存成功", f"日志已成功保存到:\n{filepath}")
            except Exception as e:
                self.add_log_entry(f"保存日志失败: {e}")
                messagebox.showerror("保存失败", f"无法保存日志文件到:\n{filepath}\n\n错误: {e}")
        else:
            self.add_log_entry("用户取消了保存日志操作。")


if __name__ == "__main__":
    root = tk.Tk()
    app = LogDisplayApp(root)

    # 模拟外部操作来添加日志（可选的演示）
    def simulate_file_operation():
        # 这个函数可以在您的主程序中被调用，当有实际操作发生时
        app.add_log_entry("用户对 'document_A.docx' 进行了编辑操作。")

    def simulate_another_operation():
        app.add_log_entry("系统检测到 'backup_script.sh' 执行完成。")

    # 添加一个按钮到主窗口外，用于模拟添加日志（仅为演示目的）
    # 在实际应用中，add_log_entry 会被你的程序逻辑在后台调用
    # demo_button = tk.Button(root, text="模拟文件操作日志", command=simulate_file_operation)
    # demo_button.pack(side=tk.BOTTOM, pady=5)
    # demo_button2 = tk.Button(root, text="模拟其他日志", command=simulate_another_operation)
    # demo_button2.pack(side=tk.BOTTOM, pady=5)

    root.mainloop()