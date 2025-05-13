import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os

class DataCleaningApp:
    def __init__(self, master, initial_file_path=None):
        self.master = master
        self.root = master
        self.initial_file_path = initial_file_path
        master.title("数据清洗 (Excel/CSV)")

        # 设置窗口居中
        window_width = 800
        window_height = 800
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.original_df = None
        self.cleaned_df = None
        self.current_filepath = None

        style = ttk.Style()
        style.theme_use("clam")

        # 最顶部文件操作区域
        file_frame = ttk.LabelFrame(master, text="1. 文件操作")
        file_frame.pack(padx=10, pady=10, fill="x")

        self.filename_display_var = tk.StringVar(value="文件名: N/A")
        filename_label = ttk.Label(file_frame, textvariable=self.filename_display_var, anchor='w')
        filename_label.pack(side='left', padx=(10,10))

        self.filepath_display_var = tk.StringVar(value="文件路径: N/A")
        filepath_label = ttk.Label(file_frame, textvariable=self.filepath_display_var, anchor='w')
        filepath_label.pack(side='left', padx=(20,20), fill="x", expand=True)

        self.save_button = ttk.Button(file_frame, text="保存清洗后数据", command=self.save_file, state=tk.DISABLED)
        self.save_button.pack(side='right', padx=5, pady=5)

        self.load_button = ttk.Button(file_frame, text="重新选择文件", command=self.select_and_load_new_file)
        self.load_button.pack(side='right', padx=5, pady=5)

        # 中部文件清洗区域
        operations_frame = ttk.LabelFrame(master, text="2. 清洗操作")
        operations_frame.pack(padx=10, pady=5, fill="x")

        # Missing Values
        missing_values_frame = ttk.Frame(operations_frame)
        missing_values_frame.pack(pady=5, fill="x")
        ttk.Label(missing_values_frame, text="处理缺失值:").pack(side='left', padx=5)
        self.missing_strategy_var = tk.StringVar(value="drop")
        ttk.Radiobutton(missing_values_frame, text="删除行", variable=self.missing_strategy_var, value="drop").pack(side=tk.LEFT)
        ttk.Radiobutton(missing_values_frame, text="填充 (均值/众数)", variable=self.missing_strategy_var, value="fill").pack(side=tk.LEFT)
        self.apply_missing_button = ttk.Button(missing_values_frame, text="应用", command=self.handle_missing_values, state=tk.DISABLED)
        self.apply_missing_button.pack(side='left', padx=5)

        # Duplicates
        duplicates_frame = ttk.Frame(operations_frame)
        duplicates_frame.pack(pady=5, fill="x")
        ttk.Label(duplicates_frame, text="处理重复行:").pack(side='left', padx=5)
        self.remove_duplicates_button = ttk.Button(duplicates_frame, text="移除重复行", command=self.remove_duplicates, state=tk.DISABLED)
        self.remove_duplicates_button.pack(side='left', padx=5)

        # 底部清洗后数据预览区域
        display_frame = ttk.LabelFrame(master, text="3. 数据预览 (清洗后)")
        display_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(display_frame, show="headings")

        # Scrollbars for Treeview
        vsb = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(display_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # --- Log Frame ---
        log_frame = ttk.LabelFrame(master, text="4. 操作日志")
        log_frame.pack(padx=10, pady=10, fill="x")

        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill="x", expand=True, padx=5, pady=5)

        if initial_file_path:
            self.load_data_from_filepath(initial_file_path)

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{pd.Timestamp.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def select_and_load_new_file(self):
        filepath = filedialog.askopenfilename(
            title="选择 Excel 或 CSV 文件",
            filetypes=(("Excel 文件", "*.xlsx *.xls"), ("CSV 文件", "*.csv"), ("所有文件", "*.*"))
        )
        if not filepath:
            return
        if filepath:  # 如果用户选择了文件
            self.load_data_from_filepath(filepath)

    def load_data_from_filepath(self, filepath_to_load):
        """
        从给定的文件路径加载数据并更新UI。
        """
        if filepath_to_load is None:
            messagebox.showerror("文件路径错误", "未选择有效文件路径。")
            return
        try:
            if filepath_to_load.lower().endswith(('.xlsx', '.xls')):
                self.original_df = pd.read_excel(filepath_to_load)
            elif filepath_to_load.lower().endswith('.csv'):
                try:
                    self.original_df = pd.read_csv(filepath_to_load, encoding='utf-8')
                except UnicodeDecodeError:
                    self.original_df = pd.read_csv(filepath_to_load, encoding='gbk')
            else:
                messagebox.showerror("文件类型错误", "请选择 .xlsx, .xls 或 .csv 文件。")

            self.cleaned_df = self.original_df.copy()
            self.current_filepath = filepath_to_load
            filename = os.path.basename(self.current_filepath)  # 使用 os.path.basename 获取文件名
            self.filename_display_var.set(f"文件名: {filename}")
            self.filepath_display_var.set(f"文件路径: {self.current_filepath}")
            self.display_dataframe(self.cleaned_df)
            self.log_message(f"文件 '{self.current_filepath.split('/')[-1]}' 加载成功. 数据形状: {self.original_df.shape}")
            self._update_button_states(loaded=True)

        except Exception as e:
            messagebox.showerror("读取文件错误", f"无法加载文件 '{os.path.basename(filepath_to_load)}':\n{e}")
            self.current_filepath = None
            self.log_message(f"加载文件失败: {e}")
            self._update_button_states(loaded=False)


    def display_dataframe(self, df_to_display, max_rows=50):
        # Clear previous Treeview content
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree["columns"] = []

        if df_to_display is None or df_to_display.empty:
            self.log_message("数据为空，无法显示。")
            return

        # Limit rows for display performance
        display_df_subset = df_to_display.head(max_rows)

        self.tree["columns"] = list(display_df_subset.columns)
        self.tree["show"] = "headings"

        for col in display_df_subset.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='w') # Adjust width as needed

        for index, row in display_df_subset.iterrows():
            self.tree.insert("", "end", values=list(row))

        if len(df_to_display) > max_rows:
            self.log_message(f"数据预览显示前 {max_rows} 行 (共 {len(df_to_display)} 行)。")


    def _update_button_states(self, loaded=False):
        state = tk.NORMAL if loaded else tk.DISABLED
        self.apply_missing_button.config(state=state)
        self.remove_duplicates_button.config(state=state)
        self.save_button.config(state=state)


    def handle_missing_values(self):
        if self.cleaned_df is None:
            messagebox.showwarning("无数据", "请先加载数据。")
            return

        strategy = self.missing_strategy_var.get()
        rows_before = len(self.cleaned_df)
        missing_before = self.cleaned_df.isnull().sum().sum()

        try:
            if strategy == "drop":
                self.cleaned_df.dropna(inplace=True)
                action_taken = f"删除了包含缺失值的行。影响 {rows_before - len(self.cleaned_df)} 行。"
            elif strategy == "fill":
                filled_count = 0
                for col in self.cleaned_df.columns:
                    if self.cleaned_df[col].isnull().any():
                        if pd.api.types.is_numeric_dtype(self.cleaned_df[col]):
                            fill_value = self.cleaned_df[col].mean()
                            self.cleaned_df[col].fillna(fill_value, inplace=True)
                            filled_count += self.cleaned_df[col].isnull().sum() # Should be 0 after fill
                            self.log_message(f"列 '{col}' 中的缺失值已用均值 ({fill_value:.2f}) 填充。")
                        elif pd.api.types.is_object_dtype(self.cleaned_df[col]) or pd.api.types.is_categorical_dtype(self.cleaned_df[col]):
                            fill_value = self.cleaned_df[col].mode()[0] if not self.cleaned_df[col].mode().empty else "Unknown"
                            self.cleaned_df[col].fillna(fill_value, inplace=True)
                            filled_count += self.cleaned_df[col].isnull().sum() # Should be 0 after fill
                            self.log_message(f"列 '{col}' 中的缺失值已用众数 ('{fill_value}') 填充。")
                        else:
                             self.log_message(f"列 '{col}' 类型未知，跳过填充。")
                action_taken = f"尝试填充缺失值。处理了 {missing_before - self.cleaned_df.isnull().sum().sum()} 个缺失单元格。"

            self.display_dataframe(self.cleaned_df)
            self.log_message(f"处理缺失值 ({strategy}): {action_taken} 当前数据形状: {self.cleaned_df.shape}")
        except Exception as e:
            messagebox.showerror("处理错误", f"处理缺失值时出错: {e}")
            self.log_message(f"处理缺失值时出错: {e}")

    def remove_duplicates(self):
        if self.cleaned_df is None:
            messagebox.showwarning("无数据", "请先加载数据。")
            return

        rows_before = len(self.cleaned_df)
        self.cleaned_df.drop_duplicates(inplace=True)
        rows_after = len(self.cleaned_df)
        removed_count = rows_before - rows_after

        self.display_dataframe(self.cleaned_df)
        self.log_message(f"移除了 {removed_count} 个重复行。当前数据形状: {self.cleaned_df.shape}")

    def save_file(self):
        if self.cleaned_df is None:
            messagebox.showwarning("无数据", "没有可保存的数据。")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=(("CSV 文件", "*.csv"), ("所有文件", "*.*")),
            title="保存清洗后的数据"
        )

        if not save_path:
            return

        try:
            self.cleaned_df.to_csv(save_path, index=False)
            messagebox.showinfo("保存成功", f"文件已保存到: {save_path}")
            self.log_message(f"清洗后的数据已保存到: {save_path}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存文件失败: {e}")
            self.log_message(f"保存文件失败: {e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = DataCleaningApp(root)
    root.mainloop()