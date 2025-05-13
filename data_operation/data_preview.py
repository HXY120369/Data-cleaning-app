import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os # 用于获取文件名

class DataPreviewApp:
    def __init__(self, master, initial_filepath=None):
        self.master = master
        self.root = master
        self.initial_filepath = initial_filepath
        master.title("数据预览 (Excel/CSV)")

        # 设置窗口居中
        window_width = 800
        window_height = 600
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.df = None
        self.current_filepath = None # 用于存储当前操作的文件路径
        self.preview_visible = True

        style = ttk.Style()
        style.theme_use('clam')

        # --- 最顶部：文件名、路径显示区 与 重新选择按钮 ---
        file_controls_frame = ttk.Frame(master, padding="5 10 5 10") # 上 右 下 左
        file_controls_frame.pack(fill='x', side='top')

        self.filename_display_var = tk.StringVar(value="文件名: N/A")
        filename_label = ttk.Label(file_controls_frame, textvariable=self.filename_display_var, anchor='w')
        filename_label.pack(side='left', padx=(10,10))

        self.filepath_display_var = tk.StringVar(value="文件路径: N/A")
        filepath_label = ttk.Label(file_controls_frame, textvariable=self.filepath_display_var, anchor='w')
        # 让路径标签占据更多空间
        filepath_label.pack(side='left', padx=(20,20), fill='x', expand=True)

        self.reselect_button = ttk.Button(file_controls_frame, text="重新选择文件", command=self.select_and_load_new_file)
        self.reselect_button.pack(side='left', padx=(10,15))


        # --- 中部数据预览区 (使用 Treeview) ---
        self.preview_frame = ttk.LabelFrame(master, text="数据预览 (最多显示前200行)", padding="10")
        self.preview_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(self.preview_frame, show="headings")
        vsb = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # --- 底部信息展示与控制区 ---
        self.info_frame = ttk.Frame(master, padding="10")
        self.info_frame.pack(fill='x', side='bottom')

        self.rows_var = tk.StringVar(value="数据条数 (行): N/A")
        rows_label = ttk.Label(self.info_frame, textvariable=self.rows_var)
        rows_label.pack(side='left', padx=(10, 20))

        self.cols_var = tk.StringVar(value="属性个数 (列): N/A")
        cols_label = ttk.Label(self.info_frame, textvariable=self.cols_var)
        cols_label.pack(side='left', padx=(20, 20))

        self.exit_button = ttk.Button(self.info_frame, text="退出预览", command=self.master.destroy)
        self.exit_button.pack(side='right', padx=(10,10))

        self.clear_data_button = ttk.Button(self.info_frame, text="清除数据", command=self.clear_all_data)
        self.clear_data_button.pack(side='right', padx=(10, 10))

        # 如果初始时提供了文件路径，则加载它
        if initial_filepath:
            self.load_data_from_filepath(initial_filepath)
        else:
            self.clear_all_data() # 确保标签是 N/A 状态


    def select_and_load_new_file(self):
        """
        通过文件对话框让用户选择新文件并加载。
        """
        filepath = filedialog.askopenfilename(
            title="选择 Excel 或 CSV 文件",
            filetypes=(("Excel 文件", "*.xlsx *.xls"),
                       ("CSV 文件", "*.csv"),
                       ("所有文件", "*.*"))
        )
        if filepath: # 如果用户选择了文件
            self.load_data_from_filepath(filepath)


    def load_data_from_filepath(self, filepath_to_load):
        """
        从给定的文件路径加载数据并更新UI。
        """
        try:
            if filepath_to_load.lower().endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(filepath_to_load)
            elif filepath_to_load.lower().endswith('.csv'):
                try:
                    self.df = pd.read_csv(filepath_to_load, encoding='utf-8')
                except UnicodeDecodeError:
                    self.df = pd.read_csv(filepath_to_load, encoding='gbk')
            else:
                messagebox.showerror("文件类型错误", "请选择 .xlsx, .xls 或 .csv 文件。")
                # 如果初始文件类型错误，也应该清除显示
                if self.current_filepath == filepath_to_load: # 判断是否是初始加载失败
                     self.clear_all_data()
                return

            self.current_filepath = filepath_to_load
            filename = os.path.basename(self.current_filepath) # 使用 os.path.basename 获取文件名

            self.filename_display_var.set(f"文件名: {filename}")
            self.filepath_display_var.set(f"文件路径: {self.current_filepath}")

            self.populate_treeview()
            self.update_summary_info()

        except Exception as e:
            messagebox.showerror("读取文件错误", f"无法加载文件 '{os.path.basename(filepath_to_load)}':\n{e}")
            self.clear_all_data() # 加载失败时清除所有数据和显示


    def populate_treeview(self):
        if self.df is None:
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree["columns"] = ()
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"
        for col in self.df.columns:
            self.tree.heading(col, text=col, anchor='center')
            try:
                max_len = max(self.df[col].astype(str).map(len).max(skipna=True), len(col))
                width = max(70, min(max_len * 8 + 10, 300)) # 略微增加宽度，限制最大宽度
            except:
                width = 100
            self.tree.column(col, anchor="w", width=width, stretch=tk.NO)
        df_preview = self.df.head(200)
        for index, row in df_preview.iterrows():
            values = [str(v) if pd.notna(v) else "" for v in row]
            self.tree.insert("", "end", values=values)


    def update_summary_info(self):
        if self.df is not None:
            num_rows = len(self.df)
            num_cols = len(self.df.columns)
            self.rows_var.set(f"数据条数 (行): {num_rows}")
            self.cols_var.set(f"属性个数 (列): {num_cols}")
        else:
            self.rows_var.set("数据条数 (行): N/A")
            self.cols_var.set("属性个数 (列): N/A")


    def clear_all_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree["columns"] = ()
        self.df = None
        self.current_filepath = None
        self.filename_display_var.set("文件名: N/A")
        self.filepath_display_var.set("文件路径: N/A")
        self.update_summary_info()
        if not self.preview_visible: # 如果预览是隐藏的，清除数据后也让按钮恢复到"隐藏预览"状态
            self.preview_frame.pack(fill='both', expand=True, padx=10, pady=5, before=self.info_frame)
            self.preview_visible = True


# --- 如何使用这个类 ---
if __name__ == "__main__":
    root = tk.Tk()
    initial_file_to_load = None

    # 检查文件是否存在，如果不存在，则传递 None (可选步骤，或者让 load_data_from_filepath 处理)
    if initial_file_to_load and not os.path.exists(initial_file_to_load):
        print(f"警告: 初始文件 '{initial_file_to_load}' 不存在。")
        initial_file_to_load = None

    app = DataPreviewApp(root, initial_filepath=initial_file_to_load)
    root.mainloop()