import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import io  # 用于捕获 df.info() 的输出


# Matplotlib 用于嵌入图表
import  matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class DataAuditApp:
    def __init__(self, master, initial_path=None):
        self.master = master
        self.root = master
        self.initial_path = initial_path
        master.title("数据审查 (Excel/CSV)")

        # 设置窗口居中
        window_width = 800
        window_height = 600
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.df = None
        self.current_filepath = None

        # --- 样式 ---
        style = ttk.Style(master)
        style.theme_use("clam")

        # --- 最顶部：文件名、路径显示区 与 重新选择按钮 ---
        file_controls_frame = ttk.Frame(master, padding="5 10 5 10")  # 上 右 下 左
        file_controls_frame.pack(fill='x', side='top')

        self.filename_display_var = tk.StringVar(value="文件名: N/A")
        filename_label = ttk.Label(file_controls_frame, textvariable=self.filename_display_var, anchor='w')
        filename_label.pack(side='left', padx=(10, 10))

        self.filepath_display_var = tk.StringVar(value="文件路径: N/A")
        filepath_label = ttk.Label(file_controls_frame, textvariable=self.filepath_display_var, anchor='w')
        filepath_label.pack(side='left', padx=(20, 20), fill='x', expand=True)

        self.reselect_button = ttk.Button(file_controls_frame, text="重新选择文件", command=self.select_and_load_new_file)
        self.reselect_button.pack(side='left', padx=(5, 5))

        self.back_button = ttk.Button(file_controls_frame, text="返回", command=self.master.destroy)
        self.back_button.pack(side='left', padx=(10, 15))

        # --- 中部 Notebook (选项卡) ---
        self.notebook = ttk.Notebook(master, padding="5")
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # 创建各个分析页面的 Frame
        self.tab_overview = ttk.Frame(self.notebook, padding="10")
        self.tab_sample = ttk.Frame(self.notebook, padding="10")
        self.tab_descriptive_stats = ttk.Frame(self.notebook, padding="10")
        self.tab_missing_values = ttk.Frame(self.notebook, padding="10")
        self.tab_column_analysis = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.tab_overview, text=' 文件概览 ', )
        self.notebook.add(self.tab_sample, text=' 数据样本 ')
        self.notebook.add(self.tab_descriptive_stats, text=' 描述性统计 ')
        self.notebook.add(self.tab_missing_values, text=' 缺失值分析 ')
        self.notebook.add(self.tab_column_analysis, text=' 列数据分布 ')

        # 初始化各个选项卡的内容区
        self._setup_overview_tab()
        self._setup_sample_tab()
        self._setup_descriptive_stats_tab()
        self._setup_missing_values_tab()
        self._setup_column_analysis_tab()

        # 如果初始时提供了文件路径，则加载它
        if initial_path:
            self.load_data_from_filepath(initial_path)
        else:
            self.clear_all_tabs_content()


    # 创建带有垂直滚动条的文本区域
    def _create_scrolled_text_area(self, parent_tab):
        st = scrolledtext.ScrolledText(parent_tab, wrap=tk.WORD, state=tk.DISABLED, relief=tk.SUNKEN, borderwidth=1, height=10, font=18)
        st.pack(fill='both', expand=True)
        return st

    # 设置 scrolled_text 中的文本内容（先删除后插入）
    def _set_scrolled_text_content(self, st_widget, content):
        st_widget.config(state=tk.NORMAL)
        st_widget.delete(1.0, tk.END)
        st_widget.insert(tk.END, content)
        st_widget.config(state=tk.DISABLED)

    def _create_treeview_area(self, parent_tab, columns, column_widths=None, show_headings=True, height=10):
        frame = ttk.Frame(parent_tab)
        frame.pack(fill='both', expand=True)

        tree = ttk.Treeview(frame, columns=columns, show="headings" if show_headings else "", height=height)

        if show_headings:
            for i, col in enumerate(columns):
                tree.heading(col, text=col, anchor='w')
                width = column_widths[i] if column_widths and i < len(column_widths) else 120
                tree.column(col, anchor="w", width=width, stretch=tk.YES)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        return tree

    def _populate_treeview(self, tree, df_subset, clear_existing=True):
        if clear_existing:
            for i in tree.get_children():
                tree.delete(i)

        if df_subset is None or df_subset.empty:
            return

        for index, row in df_subset.iterrows():
            values = [str(v) if pd.notna(v) else "" for v in row.values]
            tree.insert("", "end", values=values)

    # 一共五个选项卡，设置每个选项卡的文本区域
    def _setup_overview_tab(self):
        self.overview_text_area = self._create_scrolled_text_area(self.tab_overview)

    def _setup_sample_tab(self):
        top_frame = ttk.Frame(self.tab_sample)
        top_frame.pack(fill='both', expand=True, side='top', pady=(0, 10))
        ttk.Label(top_frame, text="数据头部 (Head):").pack(anchor='w')
        self.sample_head_tree = self._create_treeview_area(top_frame, columns=[], height=7)  # Columns will be set later

        bottom_frame = ttk.Frame(self.tab_sample)
        bottom_frame.pack(fill='both', expand=True, side='bottom')
        ttk.Label(bottom_frame, text="数据尾部 (Tail):").pack(anchor='w')
        self.sample_tail_tree = self._create_treeview_area(bottom_frame, columns=[],height=7)  # Columns will be set later

    def _setup_descriptive_stats_tab(self):
        self.descriptive_stats_text_area = self._create_scrolled_text_area(self.tab_descriptive_stats)

    def _setup_missing_values_tab(self):
        cols = ("列名 (Column)", "缺失数量 (Missing Count)", "缺失百分比 (Missing %)")
        widths = (230, 190, 190)
        self.missing_values_tree = self._create_treeview_area(self.tab_missing_values, columns=cols, column_widths=widths)

    def _setup_column_analysis_tab(self):
        controls_frame = ttk.Frame(self.tab_column_analysis)
        controls_frame.pack(fill='x', pady=5)

        ttk.Label(controls_frame, text="选择列:").pack(side='left', padx=(0, 5))
        self.col_analysis_var = tk.StringVar()
        self.col_analysis_menu = ttk.Combobox(controls_frame, textvariable=self.col_analysis_var, state="readonly",
                                              width=30)
        self.col_analysis_menu.pack(side='left')
        self.col_analysis_menu.bind("<<ComboboxSelected>>", self.update_column_analysis_display)

        analysis_results_frame = ttk.Frame(self.tab_column_analysis)
        analysis_results_frame.pack(fill='both', expand=True, pady=5)

        # 左侧文本信息区
        text_info_frame = ttk.Frame(analysis_results_frame, width=300)
        text_info_frame.pack(side='left', fill='y', padx=(0, 10))
        text_info_frame.pack_propagate(False)  # 固定宽度
        self.col_analysis_text_area = self._create_scrolled_text_area(text_info_frame)

        # 右侧图表区
        self.col_plot_frame = ttk.Frame(analysis_results_frame)  # No relief, just container
        self.col_plot_frame.pack(side='left', fill='both', expand=True)

        self.col_fig = Figure(figsize=(5, 4), dpi=100)
        self.col_plot_ax = self.col_fig.add_subplot(111)
        self.col_canvas = FigureCanvasTkAgg(self.col_fig, master=self.col_plot_frame)
        self.col_canvas_widget = self.col_canvas.get_tk_widget()
        self.col_canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.col_toolbar = NavigationToolbar2Tk(self.col_canvas, self.col_plot_frame) # Optional
        self.col_toolbar.update()

    # 清除所有文本内容
    def clear_all_tabs_content(self):
        self._set_scrolled_text_content(self.overview_text_area, "请先加载文件。")

        self.current_filepath = None
        self.filename_display_var.set("文件名：N/A")
        self.filepath_display_var.set("文件路径：N/A")
        self.sample_head_tree.config(columns=[])
        self._populate_treeview(self.sample_head_tree, None)
        self.sample_tail_tree.config(columns=[])
        self._populate_treeview(self.sample_tail_tree, None)

        self._set_scrolled_text_content(self.descriptive_stats_text_area, "")
        self._populate_treeview(self.missing_values_tree, None)

        self.col_analysis_menu['values'] = []
        self.col_analysis_var.set("")
        self._set_scrolled_text_content(self.col_analysis_text_area, "")
        self.col_plot_ax.clear()
        self.col_canvas.draw_idle()

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
                     self.clear_all_tabs_content()
                return


            # 加载新文件后，清空旧内容并填充新内容
            self.clear_all_tabs_content()  # 清空是为了防止旧数据残留

            self.current_filepath = filepath_to_load
            self.filename = os.path.basename(self.current_filepath)  # 使用 os.path.basename 获取文件名
            self.filename_display_var.set(f"文件名: {self.filename}")
            self.filepath_display_var.set(f"文件路径: {self.current_filepath}")
            self.populate_all_tabs()

        except Exception as e:
            import traceback  # 导入traceback模块
            print(f"--- DEBUG: Error occurred while loading file ---")
            print(f"Filepath attempted: {filepath_to_load!r}")  # 打印尝试的路径
            print(f"Type of filepath: {type(filepath_to_load)}")  # 打印路径类型
            print(f"Error type: {type(e).__name__}")  # 打印错误类型
            print(f"Error message: {str(e)}")  # 打印错误消息
            print("Full Traceback:")
            traceback.print_exc()  # 打印完整的错误追踪信息
            print(f"--- END DEBUG ---")
            messagebox.showerror("读取文件错误", f"无法加载文件 '{os.path.basename(filepath_to_load)}':\n{e}")
            self.clear_all_tabs_content() # 加载失败时清除所有数据和显示
            self.df = None
            self.current_filepath = None


    # 加载所有空白文本框上的内容
    def populate_all_tabs(self):
        if self.df is None:
            self.clear_all_tabs_content()
            return

        # 1. 概览
        # file_name = os.path.basename(self.current_filepath)
        overview_content = f"文件名：{self.filename}\n"
        overview_content += f"文件路径: {self.current_filepath}\n"
        overview_content += f"数据形状 (行, 列): {self.df.shape}\n"
        overview_content += f"总条目数: {self.df.size}\n"
        overview_content += f"内存占用: {self.df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB\n"
        overview_content += f"重复行数量: {self.df.duplicated().sum()}\n\n"
        overview_content += "列数据类型及非空值统计 (df.info()):\n"

        # 捕获 df.info() 的输出
        buffer = io.StringIO()
        self.df.info(buf=buffer, verbose=True, show_counts=True)
        info_str = buffer.getvalue()
        overview_content += info_str
        self._set_scrolled_text_content(self.overview_text_area, overview_content)

        # 2. 数据样本
        cols = list(self.df.columns)
        self.sample_head_tree.config(columns=cols)
        for col in cols:
            self.sample_head_tree.heading(col, text=col, anchor='w')
            self.sample_head_tree.column(col, width=100, anchor='w', stretch=tk.NO)
        self._populate_treeview(self.sample_head_tree, self.df.head(), clear_existing=False)

        self.sample_tail_tree.config(columns=cols)
        for col in cols:
            self.sample_tail_tree.heading(col, text=col, anchor='w')
            self.sample_tail_tree.column(col, width=100, anchor='w', stretch=tk.NO)
        self._populate_treeview(self.sample_tail_tree, self.df.tail(), clear_existing=False)

        # 3. 描述性统计
        try:
            desc_stats_str = self.df.describe(include='all', datetime_is_numeric=True).to_string()
        except TypeError:  # For older pandas versions
            desc_stats_str = self.df.describe(include='all').to_string()
        self._set_scrolled_text_content(self.descriptive_stats_text_area, desc_stats_str)

        # 4. 缺失值
        missing_summary = []
        if not self.df.empty:
            missing_counts = self.df.isnull().sum()
            missing_percentages = (missing_counts / len(self.df)) * 100
            for col in self.df.columns:
                missing_summary.append((col, missing_counts[col], f"{missing_percentages[col]:.2f}%"))

        missing_df = pd.DataFrame(missing_summary, columns=self.missing_values_tree['columns'])
        self._populate_treeview(self.missing_values_tree, missing_df)

        # 5. 列数据分布 - 填充下拉菜单
        if not self.df.empty:
            self.col_analysis_menu['values'] = list(self.df.columns)
            if list(self.df.columns):  # 如果有列，默认选中第一个
                self.col_analysis_var.set(list(self.df.columns)[0])
                self.update_column_analysis_display(None)  # 手动触发更新
        else:
            self.col_analysis_menu['values'] = []
            self.col_analysis_var.set("")

    def update_column_analysis_display(self, event):  # event is passed by ComboboxSelected
        if self.df is None or self.df.empty or not self.col_analysis_var.get():
            self._set_scrolled_text_content(self.col_analysis_text_area, "")
            self.col_plot_ax.clear()
            self.col_canvas.draw_idle()
            return

        selected_col = self.col_analysis_var.get()
        col_data = self.df[selected_col]

        # 文本信息
        text_analysis = f"列名: {selected_col}\n"
        text_analysis += f"数据类型: {col_data.dtype}\n"
        text_analysis += f"唯一值数量: {col_data.nunique()}\n"

        unique_values = col_data.unique()
        if len(unique_values) < 20 and len(unique_values) > 0:  # 只显示少量唯一值
            text_analysis += f"唯一值列表: {', '.join(map(str, unique_values[:20]))}\n"
        elif len(unique_values) == 0:
            text_analysis += "唯一值列表: (无唯一值或全为NaN)\n"

        text_analysis += "\n频数最高的前5个值:\n"
        value_counts_sorted = col_data.value_counts().sort_values(ascending=False)
        for val, count in value_counts_sorted.head(5).items():
            text_analysis += f"  - \"{val}\": {count}\n"

        self._set_scrolled_text_content(self.col_analysis_text_area, text_analysis)

        # 图表信息
        self.col_plot_ax.clear()
        try:
            if pd.api.types.is_numeric_dtype(col_data) and col_data.nunique() > 15:  # 数值型且唯一值较多，画直方图
                col_data.dropna().plot(kind='hist', ax=self.col_plot_ax, bins=30, edgecolor='k')
                self.col_plot_ax.set_ylabel("频数 (Frequency)")
            elif col_data.nunique() > 0 and col_data.nunique() <= 50:  # 类别型或唯一值较少的数值型，画条形图 (限制数量)
                plot_data = col_data.value_counts().nlargest(20).sort_index()  # 最多画20个bar, 按值排序
                plot_data.plot(kind='bar', ax=self.col_plot_ax, rot=45)
                self.col_plot_ax.set_ylabel("计数 (Count)")
            else:  # 唯一值过多或无法绘图
                self.col_plot_ax.text(0.5, 0.5, '数据无法生成合适图表\n(如唯一值过多或类型不支持)',
                                      horizontalalignment='center', verticalalignment='center',
                                      transform=self.col_plot_ax.transAxes, fontsize=9, color='gray')

            self.col_plot_ax.set_title(f"'{selected_col}' 数据分布", fontsize=10)
            #self.col_fig.tight_layout()  # 调整布局防止标签重叠
        except Exception as e:
            self.col_plot_ax.text(0.5, 0.5, f'无法为列 "{selected_col}" 生成图表:\n{e}',
                                  horizontalalignment='center', verticalalignment='center',
                                  transform=self.col_plot_ax.transAxes, color='red', fontsize=9)
        self.col_canvas.draw_idle()



if __name__ == "__main__":
    root = tk.Tk()
    app = DataAuditApp(root)
    # 初始时清空所有选项卡内容，提示用户加载文件
    app.clear_all_tabs_content()
    root.mainloop()