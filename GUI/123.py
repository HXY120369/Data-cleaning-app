import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Listbox, simpledialog
from unicodedata import category

import pandas as pd
from datetime import datetime
import numpy as np # 用于异常值处理中的计算
import os

from sklearn.ensemble import RandomForestRegressor

# 尝试导入sklearn组件
try:
    from sklearn.experimental import enable_iterative_imputer
    from sklearn.impute import IterativeImputer
    from sklearn.linear_model import BayesianRidge
    from sklearn.preprocessing import MinMaxScaler, OneHotEncoder # 用于神经网络
    from sklearn.compose import ColumnTransformer # 用于神经网络
    from sklearn.pipeline import Pipeline # 用于神经网络
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    MinMaxScaler, OneHotEncoder, ColumnTransformer, Pipeline = None, None, None, None
# 尝试导入TensorFlow组件
try:
    import tensorflow as tf
    from tensorflow import keras
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Input
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    Sequential, Dense, Dropout, Input = None, None, None, None # 占位符

# --- 功能模块的基类 (可选，用于共享功能) ---
class BaseProcessingFrame(ttk.Frame):
    def __init__(self, master, app_controller, title="处理模块"):
        super().__init__(master, padding="10")
        self.app = app_controller # 主应用的引用，用于数据交互和日志记录

        # 通用列选择组件 (每个子类可以决定如何使用或覆盖)
        self.column_selection_frame = ttk.LabelFrame(self, text=f"{title} - 选择列", padding="5")
        self.column_selection_frame.pack(fill='x', pady=5)

        self.column_listbox = Listbox(self.column_selection_frame, selectmode=tk.MULTIPLE, exportselection=False, height=7)
        self.column_listbox_scrollbar_y = ttk.Scrollbar(self.column_selection_frame, orient='vertical', command=self.column_listbox.yview)
        self.column_listbox_scrollbar_x = ttk.Scrollbar(self.column_selection_frame, orient='horizontal', command=self.column_listbox.xview)
        self.column_listbox.configure(yscrollcommand=self.column_listbox_scrollbar_y.set, xscrollcommand=self.column_listbox_scrollbar_x.set)

        self.column_listbox_scrollbar_y.pack(side='right', fill='y')
        self.column_listbox_scrollbar_x.pack(side='bottom', fill='x')
        self.column_listbox.pack(side='left', fill='both', expand=True)

    def populate_columns_list(self):
        self.column_listbox.delete(0, tk.END)
        columns = self.app.get_column_list()
        if columns:
            for col in columns:
                self.column_listbox.insert(tk.END, col)

    def get_selected_columns(self):
        selected_indices = self.column_listbox.curselection()
        if not selected_indices:
            # messagebox.showwarning("提示", "请先在列表中选择一个或多个列。") # 可以选择是否在这里提示
            return [] # 返回空列表，让调用者决定如何处理
        return [self.column_listbox.get(i) for i in selected_indices]

    def log(self, message):
        self.app.log_action(message)

    def get_df(self):
        return self.app.get_cleaned_df()

    def set_df(self, new_df, description="操作"):
        self.app.set_cleaned_df(new_df, change_description=description)

# --- 各功能模块的Frame ---
class StandardizationFrame(BaseProcessingFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, title="数据标准化")

        # --- 日期时间标准化区 ---
        datetime_lf = ttk.LabelFrame(self, text="日期时间格式化", padding="10")
        datetime_lf.pack(fill='x', pady=5, padx=5)

        # 常见的日期时间格式列表
        DATETIME_FORMATS = [
            "%Y-%m-%d %H:%M:%S",  # 年-月-日 时:分:秒
            "%Y/%m/%d %H:%M:%S",  # 年/月/日 时:分:秒
            "%Y-%m-%d %H:%M",  # 年-月-日 时:分
            "%Y/%m/%d %H:%M",  # 年/月/日 时:分
            "%Y-%m-%d",  # 年-月-日
            "%m/%d/%Y %H:%M:%S",  # 月/日/年 时:分:秒
            "%m/%d/%Y %H:%M",  # 月/日/年 时:分
        ]

        ttk.Label(datetime_lf, text="目标格式:").grid(row=0, column=0, padx=(0,5))
        self.datetime_format_entry = ttk.Combobox(datetime_lf, values=DATETIME_FORMATS, width=20, state='readonly')
        self.datetime_format_entry.set(DATETIME_FORMATS[0])
        self.datetime_format_entry.grid(row=1, column=0, padx=5)
        self.apply_datetime_button = ttk.Button(datetime_lf, text="应用", command=self.apply_datetime_formatting)
        self.apply_datetime_button.grid(row=1, column=1, padx=5)

        # --- 浮点数标准化区 ---
        float_lf = ttk.LabelFrame(self, text="浮点数格式化 (四舍五入)", padding="10")
        float_lf.pack(fill='x', pady=5, padx=5)
        ttk.Label(float_lf, text="保留小数位数:").pack(side='left', padx=5)
        self.float_decimals_spinbox = ttk.Spinbox(float_lf, from_=0, to=15, width=6)
        self.float_decimals_spinbox.set(2)
        self.float_decimals_spinbox.pack(side='left', padx=10)
        self.apply_float_button = ttk.Button(float_lf, text="应用", command=self.apply_float_formatting, width=5)
        self.apply_float_button.pack(side='left', padx=(18,0), fill='x', expand=True)

        # --- 文本操作区 ---
        text_lf = ttk.LabelFrame(self, text="文本操作", padding="10")
        text_lf.pack(fill='x', pady=5, padx=5)
        self.text_to_lower_var = tk.BooleanVar()
        self.text_to_upper_var = tk.BooleanVar()
        self.text_strip_var = tk.BooleanVar(value=True) # 默认勾选去除空格
        ttk.Checkbutton(text_lf, text="转小写", variable=self.text_to_lower_var).pack(side='left', padx=5)
        ttk.Checkbutton(text_lf, text="转大写", variable=self.text_to_upper_var).pack(side='left', padx=5)
        ttk.Checkbutton(text_lf, text="去除首尾空格", variable=self.text_strip_var).pack(side='left', padx=5)
        self.apply_text_button = ttk.Button(text_lf, text="应用", command=self.apply_text_operations)
        self.apply_text_button.pack(side='left', padx=5, fill='x', expand=True)

    def apply_datetime_formatting(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return
        selected_cols = self.get_selected_columns()
        if not selected_cols: messagebox.showwarning("提示", "请选择要操作的列。"); return

        target_format = self.datetime_format_entry.get()

        new_df = df.copy()
        try:
            for col in selected_cols:
                original_series = new_df[col].copy()
                # 尝试转换为datetime对象，无法转换的变为NaT
                converted_series = pd.to_datetime(original_series, errors='coerce')
                num_nat_initial = original_series.notna().sum() - converted_series.notna().sum()

                # 格式化为字符串
                # NaT值在strftime后如果直接调用会报错，或在某些版本下变为'NaT'字符串
                # 我们只格式化非NaT的值
                formatted_series = converted_series.copy().astype(object) # 转为object以接收字符串和NaT
                mask_not_nat = converted_series.notna()
                formatted_series[mask_not_nat] = converted_series[mask_not_nat].dt.strftime(target_format)
                formatted_series[~mask_not_nat] = None # 或者 "格式化失败" 等占位符

                new_df[col] = formatted_series
                self.log(f"列 '{col}': 日期格式化为 '{target_format}'。{num_nat_initial}个值无法解析为日期。")
            self.set_df(new_df, "日期时间格式化")
        except Exception as e:
            self.log(f"错误: 日期时间格式化失败 - {e}")
            messagebox.showerror("错误", f"日期时间格式化失败: {e}")

    def apply_float_formatting(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return
        selected_cols = self.get_selected_columns()
        if not selected_cols: messagebox.showwarning("提示", "请选择要操作的列。"); return

        try:
            decimals = int(self.float_decimals_spinbox.get())
        except ValueError:
            messagebox.showerror("错误", "小数位数必须是整数。"); return

        new_df = df.copy()
        try:
            for col in selected_cols:
                # 尝试转为数值型，记录无法转换的数量
                original_series = new_df[col]
                numeric_series = pd.to_numeric(original_series, errors='coerce')
                num_failed_conversion = original_series.notna().sum() - numeric_series.notna().sum()

                new_df[col] = numeric_series.round(decimals)
                self.log(f"列 '{col}': 浮点数保留 {decimals} 位小数。{num_failed_conversion}个值无法转为数值。")
            self.set_df(new_df, "浮点数格式化")
        except Exception as e:
            self.log(f"错误: 浮点数格式化失败 - {e}")
            messagebox.showerror("错误", f"浮点数格式化失败: {e}")

    def apply_text_operations(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return
        selected_cols = self.get_selected_columns()
        if not selected_cols: messagebox.showwarning("提示", "请选择要操作的列。"); return

        to_lower = self.text_to_lower_var.get()
        to_upper = self.text_to_upper_var.get()
        strip_ws = self.text_strip_var.get()

        if not (to_lower or to_upper or strip_ws):
            messagebox.showinfo("提示", "未选择任何文本操作。")
            return
        if to_lower and to_upper:
            messagebox.showwarning("冲突", "不能同时选择转小写和转大写。")
            return

        new_df = df.copy()
        try:
            for col in selected_cols:
                # 先确保是字符串类型，处理NaN为特定字符串或保留NaN
                s = new_df[col].astype(str).fillna('') # 将NaN转为空字符串进行操作，或用 .map(str) 对非NaN操作
                if strip_ws: s = s.str.strip()
                if to_lower: s = s.str.lower()
                if to_upper: s = s.str.upper()
                new_df[col] = s
                ops_applied = []
                if strip_ws: ops_applied.append("去除空格")
                if to_lower: ops_applied.append("转小写")
                if to_upper: ops_applied.append("转大写")
                self.log(f"列 '{col}': 应用文本操作 ({', '.join(ops_applied)})。")
            self.set_df(new_df, "文本操作")
        except Exception as e:
            self.log(f"错误: 文本操作失败 - {e}")
            messagebox.showerror("错误", f"文本操作失败: {e}")

class OutlierFrame(BaseProcessingFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, title="异常值处理")

        options_lf = ttk.LabelFrame(self, text="参数设置", padding="15", width=100, height=200)
        options_lf.pack(fill='x', pady=5, padx=5)

        ttk.Label(options_lf, text="方法:").grid(row=0, column=0, padx=1, pady=5, sticky='w')
        self.method_var = tk.StringVar(value="IQR")
        method_options = ["IQR", "Z-score", "百分位"]
        self.method_combo = ttk.Combobox(options_lf, textvariable=self.method_var, values=method_options, state="readonly", width=10)
        self.method_combo.grid(row=0, column=1, padx=2, sticky='ew')
        self.method_combo.bind("<<ComboboxSelected>>", self.update_params_ui)
        self.question_label = ttk.Label(options_lf, text="什么是IQR？", font=("Arial", 11), foreground='gray')
        self.question_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.question_label.bind("<Button-1>", lambda e: self.label_info())
        ttk.Label(options_lf, text="参数:").grid(row=1, column=0, padx=1, pady=5, sticky='w')

        # IQR 参数
        self.iqr_lf = ttk.Frame(options_lf) # No border for sub-parameters
        self.iqr_lf.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
        ttk.Label(self.iqr_lf, text="IQR乘数:").pack(side='left')
        self.iqr_multiplier_entry = ttk.Entry(self.iqr_lf, width=5)
        self.iqr_multiplier_entry.insert(0, "1.5")
        self.iqr_multiplier_entry.pack(side='left', padx=5)

        # Z-score 参数
        self.zscore_lf = ttk.Frame(options_lf)
        ttk.Label(self.zscore_lf, text="Z-score阈值:").pack(side='left')
        self.zscore_threshold_entry = ttk.Entry(self.zscore_lf, width=5)
        self.zscore_threshold_entry.insert(0, "3")
        self.zscore_threshold_entry.pack(side='left', padx=5)

        # 百分位参数
        self.percentile_lf = ttk.Frame(options_lf)
        ttk.Label(self.percentile_lf, text="下限百分位:").pack(side='left')
        self.lower_percentile_entry = ttk.Entry(self.percentile_lf, width=4)
        self.lower_percentile_entry.insert(0, "1")
        self.lower_percentile_entry.pack(side='left', padx=2)
        ttk.Label(self.percentile_lf, text="上限百分位:").pack(side='left', padx=1)
        self.upper_percentile_entry = ttk.Entry(self.percentile_lf, width=4)
        self.upper_percentile_entry.insert(0, "99")
        self.upper_percentile_entry.pack(side='left', padx=2)

        # 动态显示参数UI
        self.params_ui_frames = {
            "IQR": self.iqr_lf,
            "Z-score": self.zscore_lf,
            "百分位": self.percentile_lf
        }
        self.current_params_lf = None
        self.update_params_ui() # Initial setup

        ttk.Label(options_lf, text="处理方式:").grid(row=2, column=0, padx=1, pady=5, sticky='w')
        self.action_var = tk.StringVar(value="替换为NaN")
        action_options = ["移除行", "替换为边界值(Capping)", "替换为NaN"]
        self.action_combo = ttk.Combobox(options_lf, textvariable=self.action_var, values=action_options, state="readonly", width=20)
        self.action_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        options_lf.columnconfigure(1, weight=1) # Allow combobox to expand

        apply_button = ttk.Button(self, text="应用异常值处理到选中数值列", command=self.apply_outlier_handling)
        apply_button.pack(pady=10, padx=5, fill='x')

    def update_params_ui(self, event=None):
        method = self.method_var.get()
        if self.current_params_lf:
            self.current_params_lf.grid_remove()

        self.current_params_lf = self.params_ui_frames.get(method)
        if self.current_params_lf:
            self.current_params_lf.grid(row=1, column=1, columnspan=2, pady=5, sticky='ew')
            self.question_label.configure(text='什么是'+method+'?')

    def label_info(self):
        method = self.method_var.get()
        window1 = tk.Toplevel()
        window1.title("关于" + method)
        window1.geometry("450x250+800+500")
        content = scrolledtext.ScrolledText(window1, wrap=tk.WORD, font=("Arial", 14))
        content.pack(side='top', fill='both', expand=True)
        if method == "IQR":
            sample_text = '''IQR 即四分位距（Inter - Quartile Range），是描述统计学中的一种度量数据离散程度的统计量。
            衡量数据离散程度：IQR表示数据中间\(50\%\)部分的范围，其值越大，说明数据越分散；值越小，说明数据越集中。与极差（最大值减去最小值）相比，IQR不易受极端值的影响，能更稳健地反映数据的离散程度。
            识别异常值：通常可以利用IQR来识别数据中的异常值。一般认为，小于\(Q1 - 1.5timesIQR\)或大于\(Q3 + 1.5times IQR\)的数据点可能是异常值。'''
        elif method == "Z-score":
            sample_text = '''Z-score（标准分数），也叫标准化值，是一个数与平均数的差再除以标准差的过程。用公式表示为：\(z=frac{x-\mu}{\sigma}\)，其中x是原始数据，\(\mu\)是数据集的均值，\(\sigma\)是数据集的标准差。
            Z-score 有以下作用：
            数据标准化：它可以将不同均值和标准差的数据集转化为均值为 0、标准差为 1 的标准正态分布，方便对不同数据进行比较和分析。
            异常值检测：一般来说，Z-score 的绝对值大于 3 的数据点可能被视为异常值，因为在正态分布中，大约 99.7% 的数据会落在均值加减 3 个标准差的范围内。
            概率计算：通过 Z-score，可以利用标准正态分布表来计算数据点在正态分布中出现的概率，从而对数据的分布情况进行推断。'''
        else :
            sample_text = '''百分位是一种用于描述数据在一组数据中位置的统计量，如果将一组数据从小到大排序，并计算相应的累计百分位，则某一百分位所对应数据的值就称为这一百分位的百分位数。
            例如，第p百分位数是这样一个值，它使得至少有p%的数据项小于或等于这个值，且至少有(100−p)%的数据项大于或等于这个值。通过设置上下限百分位来确定数据的合理范围，从而实现基于百分位的异常值检测功能。'''
        content.insert(tk.END, sample_text)
        content.config(state='disabled')

    def apply_outlier_handling(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return
        selected_cols_all = self.get_selected_columns()
        if not selected_cols_all: messagebox.showwarning("提示", "请选择要操作的列。"); return

        # 筛选出数值列
        selected_cols = [col for col in selected_cols_all if pd.api.types.is_numeric_dtype(df[col])]
        non_numeric_cols = [col for col in selected_cols_all if not pd.api.types.is_numeric_dtype(df[col])]

        if not selected_cols:
            messagebox.showerror("错误", "选中的列均非数值型，无法进行异常值处理。"); return
        if non_numeric_cols:
            self.log(f"警告: 列 {', '.join(non_numeric_cols)} 非数值型，已在异常值处理中跳过。")

        method = self.method_var.get()
        action = self.action_var.get()
        new_df = df.copy()
        outlier_indices = pd.Index([]) # 用于收集所有异常值行的索引

        try:
            for col in selected_cols:
                s = new_df[col].dropna() # 处理前去除NaN值，因为异常值检测通常不考虑它们
                lower_bound, upper_bound = None, None

                if method == "IQR":
                    multiplier = float(self.iqr_multiplier_entry.get())
                    q1 = s.quantile(0.25)
                    q3 = s.quantile(0.75)
                    iqr_val = q3 - q1
                    lower_bound = q1 - multiplier * iqr_val
                    upper_bound = q3 + multiplier * iqr_val
                elif method == "Z-score":
                    threshold = float(self.zscore_threshold_entry.get())
                    mean = s.mean()
                    std = s.std()
                    if std == 0: # 如果标准差为0，所有值相同，没有异常值
                         self.log(f"列 '{col}': Z-score法检测，标准差为0，跳过。")
                         continue
                    lower_bound = mean - threshold * std
                    upper_bound = mean + threshold * std
                elif method == "百分位":
                    lower_p = float(self.lower_percentile_entry.get()) / 100
                    upper_p = float(self.upper_percentile_entry.get()) / 100
                    if not (0 <= lower_p < upper_p <= 1):
                        messagebox.showerror("错误", "百分位设置无效（应为 0 <= 下限 < 上限 <= 100）。"); return
                    lower_bound = s.quantile(lower_p)
                    upper_bound = s.quantile(upper_p)

                # 找出当前列的异常值
                current_col_outliers = new_df[(new_df[col] < lower_bound) | (new_df[col] > upper_bound)]
                self.log(f"列 '{col}' ({method}): 检测到 {len(current_col_outliers)} 个异常值。范围: [{lower_bound:.2f}, {upper_bound:.2f}]")

                if action == "替换为NaN":
                    new_df.loc[current_col_outliers.index, col] = np.nan
                elif action == "替换为边界值(Capping)":
                    new_df.loc[new_df[col] < lower_bound, col] = lower_bound
                    new_df.loc[new_df[col] > upper_bound, col] = upper_bound
                elif action == "移除行":
                    outlier_indices = outlier_indices.union(current_col_outliers.index) # 收集索引，最后统一删除

            if action == "移除行" and not outlier_indices.empty:
                rows_before = len(new_df)
                new_df.drop(index=outlier_indices, inplace=True)
                self.log(f"根据所有选中列的异常值检测，共移除了 {rows_before - len(new_df)} 行。")

            self.set_df(new_df, f"异常值处理 ({method}, {action})")
        except ValueError as ve:
            self.log(f"错误: 异常值处理参数错误 - {ve}")
            messagebox.showerror("参数错误", f"异常值处理参数无效: {ve}")
        except Exception as e:
            self.log(f"错误: 异常值处理失败 - {e}")
            messagebox.showerror("错误", f"异常值处理失败: {e}")

class MissingValueFrame(BaseProcessingFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, title="缺失值处理")
        # 缺失值处理界面元素
        options_lf = ttk.LabelFrame(self, text="处理选项", padding="10")
        options_lf.pack(fill='x', pady=5, padx=5)

        ttk.Label(options_lf, text="策略:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.strategy_var = tk.StringVar(value="移除行") # 默认策略
        strategies = ["移除行(drop)", "填充(fill)", "预测(predict)"]
        self.strategy_combo = ttk.Combobox(options_lf, textvariable=self.strategy_var, values=strategies, state="readonly")
        self.strategy_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.strategy_combo.bind("<<ComboboxSelected>>", self.update_fill_options_ui)

        # --- 填充选项 (动态显示) ---
        self.fill_options_lf = ttk.Frame(options_lf) # 无边框
        ttk.Label(self.fill_options_lf, text="填充方法:").pack(side='left', padx=5)
        self.fill_method_var = tk.StringVar(value="均值(mean)")
        fill_methods = ["均值(mean)", "中位数(median)", "众数(mode)", "固定值"]
        self.fill_method_combo = ttk.Combobox(self.fill_options_lf, textvariable=self.fill_method_var, values=fill_methods, state="readonly", width=15)
        self.fill_method_combo.pack(side='left', padx=5)
        self.fill_method_combo.bind("<<ComboboxSelected>>", self.update_fill_options_ui)
        self.fill_value_label = ttk.Label(self.fill_options_lf, text="固定值:") # 先创建，按需显示
        self.fill_value_entry = ttk.Entry(self.fill_options_lf, width=10)  # 先创建，按需显示

        # --- 预测选项 (动态显示) ---
        self.predict_options_lf = ttk.Frame(options_lf)
        ttk.Label(self.predict_options_lf, text="预测模型:").pack(side='left', padx=5)
        self.predict_method_var = tk.StringVar(value="线性模型")
        predict_methods = ["线性模型", "随机森林", "MLP"]
        self.predict_method_combo = ttk.Combobox(self.predict_options_lf, textvariable=self.predict_method_var, values=predict_methods, state="readonly", width=15)
        self.predict_method_combo.pack(side='left', padx=5)
        self.predict_method_combo.bind("<<ComboboxSelected>>", self.update_fill_options_ui)

        options_lf.columnconfigure(1, weight=1) # 让Combobox扩展
        self.update_fill_options_ui() # 初始化UI状态

        apply_button = ttk.Button(self, text="应用缺失值处理到选中列", command=self.handle_missing_values)
        apply_button.pack(pady=10, padx=5, fill='x')

    def update_fill_options_ui(self, event=None):
        strategy = self.strategy_var.get()
        fill_method = self.fill_method_var.get()
        if strategy == "填充(fill)":
            self.predict_options_lf.grid_remove()
            self.fill_value_label.pack_forget()
            self.fill_value_entry.pack_forget()
            self.fill_options_lf.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
            if fill_method == "固定值":
                self.fill_value_label.pack(side='left', padx=(10,0)) # 显示固定值标签和输入框
                self.fill_value_entry.pack(side='left', padx=5)
        if strategy == "预测(predict)":
            self.fill_options_lf.grid_remove()
            self.predict_options_lf.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

    def handle_missing_values(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return

        selected_cols = self.get_selected_columns()
        # 如果没有选择列，则默认对所有列操作（某些策略如填充可能需要逐列，某些如dropna可以全局）
        cols_to_process = selected_cols if selected_cols else df.columns.tolist()
        if not cols_to_process: messagebox.showwarning("无列", "DataFrame中没有列可操作。"); return

        strategy = self.strategy_var.get()
        new_df = df.copy()
        action_description = f"缺失值处理 - 策略: {strategy}"

        try:
            if strategy == "移除行(dropna)":
                rows_before = len(new_df)
                # 如果选择了列，则只在这些列中查找NaN来决定是否删除行
                # 如果没选列，则在所有列中查找NaN来决定是否删除行
                subset_to_check = selected_cols if selected_cols else None
                new_df.dropna(subset=subset_to_check, inplace=True)
                rows_after = len(new_df)
                self.log(f"移除了 {rows_before - rows_after} 行 (基于 {'选中列' if subset_to_check else '所有列'} 的缺失值)。")
                action_description += f", 移除了 {rows_before - rows_after} 行"

            elif strategy == "填充(fill)":
                fill_method_str = self.fill_method_var.get()
                action_description += f", 方法: {fill_method_str}"

                for col in cols_to_process: # 用户选择的列，或所有列
                    if new_df[col].isnull().any(): # 只处理有缺失值的列
                        original_nan_count = new_df[col].isnull().sum()
                        if fill_method_str == "均值(mean)":
                            if pd.api.types.is_numeric_dtype(new_df[col]):
                                fill_val = new_df[col].mean()
                                new_df[col].fillna(fill_val, inplace=True)
                                self.log(f"列 '{col}': 用均值 ({fill_val:.2f}) 填充了 {original_nan_count} 个缺失值。")
                            else: self.log(f"列 '{col}': 非数值型，跳过均值填充。")
                        elif fill_method_str == "中位数(median)":
                            if pd.api.types.is_numeric_dtype(new_df[col]):
                                fill_val = new_df[col].median()
                                new_df[col].fillna(fill_val, inplace=True)
                                self.log(f"列 '{col}': 用中位数 ({fill_val:.2f}) 填充了 {original_nan_count} 个缺失值。")
                            else: self.log(f"列 '{col}': 非数值型，跳过中位数填充。")
                        elif fill_method_str == "众数(mode)":
                            mode_val = new_df[col].mode()
                            if not mode_val.empty:
                                fill_val = mode_val[0]
                                new_df[col].fillna(fill_val, inplace=True)
                                self.log(f"列 '{col}': 用众数 ('{fill_val}') 填充了 {original_nan_count} 个缺失值。")
                            else: self.log(f"列 '{col}': 找不到众数，跳过填充。")
                        elif fill_method_str == "固定值":
                            fill_val_str = self.fill_value_entry.get()
                            action_description += f", 固定值: '{fill_val_str}'"
                            try: # 尝试转换为列的原始类型或合适的类型
                                if pd.api.types.is_numeric_dtype(df[col]): # 用原始df的类型判断
                                    fill_val = pd.to_numeric(fill_val_str)
                                elif pd.api.types.is_bool_dtype(df[col]): # pandas boolean type
                                    if fill_val_str.lower() in ['true', '1', 'yes']: fill_val = True
                                    elif fill_val_str.lower() in ['false', '0', 'no']: fill_val = False
                                    else: raise ValueError("布尔值转换失败")
                                else: # 默认为字符串
                                    fill_val = fill_val_str
                                new_df[col].fillna(fill_val, inplace=True)
                                self.log(f"列 '{col}': 用固定值 ('{fill_val}') 填充了 {original_nan_count} 个缺失值。")
                            except ValueError:
                                new_df[col].fillna(fill_val_str, inplace=True) # 转换失败则按字符串填充
                                self.log(f"列 '{col}': 固定值 '{fill_val_str}' 无法转换为列类型，已按字符串填充 {original_nan_count} 个缺失值。")

            elif strategy == "预测(predict)":
                if not SKLEARN_AVAILABLE:
                    messagebox.showerror("缺少库", "预测功能需要 scikit-learn 库。\n请运行：pip install scikit-learn");
                    self.log("错误: scikit-learn 库未找到，无法执行预测填充。")
                    return
                self.log("开始执行预测填充策略……")

                # 识别数值列和类别列
                numeric_cols = new_df[cols_to_process].select_dtypes(include=np.number).columns.tolist()
                category_cols = new_df[cols_to_process].select_dtypes(include='object').columns.tolist()
                df_for_predict = new_df.copy()

                numeric_cols_to_impute_actually = [
                    col for col in numeric_cols
                    if col in cols_to_process and df_for_predict[col].isnull().any()
                ]
                if not numeric_cols_to_impute_actually:
                    self.log("选定列中没有需要预测填充的数值型缺失值")
                else:
                    self.log(f"将对以下数值列进行迭代插补: {', '.join(numeric_cols_to_impute_actually)}")
                    all_numeric_df_cols = new_df.select_dtypes(include=np.number).columns.tolist()
                    temp_numeric_df = new_df[all_numeric_df_cols].copy()

                    for col in temp_numeric_df.columns:
                        if temp_numeric_df[col].isnull().any():
                            temp_numeric_df[col].fillna(temp_numeric_df[col].median(), inplace=True) # 用中位数进行初步填充

                    imputer = IterativeImputer(
                        estimator=BayesianRidge(),
                        max_iter=10,
                        random_state=0,
                        initial_strategy='median'
                    )
                    self.log("IterativeImputer 正在拟合和转换数据...")
                    imputed_values = imputer.fit_transform(temp_numeric_df)
                    # 将插补后的值放回DataFrame
                    imputed_df_numeric = pd.DataFrame(imputed_values, columns=all_numeric_df_cols, index=new_df.index)

                    for col in numeric_cols_to_impute_actually:  # 只更新那些被选作目标且是数值的列
                        if col in imputed_df_numeric.columns:
                            # 只有当原始值是 NaN 时才用预测值更新，以保留原始非NaN值
                            nan_mask_original = new_df[col].isnull()
                            new_df.loc[nan_mask_original, col] = imputed_df_numeric.loc[nan_mask_original, col]
                            self.log(f"列 '{col}': 使用预测模型填充了 {nan_mask_original.sum()} 个缺失值。")

                category_cols_to_fill = [
                    col for col in category_cols
                    if col in cols_to_process and new_df[col].isnull().any()
                ]
                if category_cols_to_fill:
                    self.log(f"对选定非数值列使用众数填充: {', '.join(category_cols_to_fill)}")
                    for col in category_cols_to_fill:
                        mode_val = new_df[col].mode()
                        if not mode_val.empty:
                            original_nan_count = new_df[col].isnull().sum()
                            new_df[col].fillna(mode_val[0], inplace=True)
                            self.log(
                                f"列 '{col}': 用众数 ('{mode_val[0]}') 填充了 {original_nan_count} 个缺失值 (作为预测策略的补充)。")
                        else:
                            self.log(f"列 '{col}': 找不到众数，跳过补充填充。")
                action_description += ", 使用IterativeImputer(数值列)和众数(类别列)"

            else:
                messagebox.showwarning("未知策略", f"未知的缺失值处理策略: {strategy}")
                return

            self.set_df(new_df, action_description)
        except Exception as e:
            self.log(f"错误: 缺失值处理失败 - {e}")
            messagebox.showerror("错误", f"缺失值处理失败: {e}")
            import traceback
            traceback.print_exc()

class DataCleaningApp:
    def __init__(self, master, initial_path=None):
        self.master = master
        self.root = master
        self.initial_path = initial_path
        master.title("Python 数据清洗工具")

        # 设置窗口居中
        window_width = 1000
        window_height = 750
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # 使用 ttk 样式
        style = ttk.Style(master)
        style.theme_use("clam")

        self.df_original = None
        self.df_cleaned = None
        self.current_filepath = None
        self.undo_stack = [] # 用于简单的撤销功能

        # --- 主布局 ---
        top_frame = ttk.Frame(master)
        top_frame.pack(side='top', fill='x', padx=5, pady=5)

        # 文件名与文件路径显示区域
        self.filename_display_var = tk.StringVar(value="文件名: N/A")
        filename_label = ttk.Label(top_frame, textvariable=self.filename_display_var, anchor='w')
        filename_label.pack(side='left', padx=(10, 10))
        self.filepath_display_var = tk.StringVar(value="文件路径: N/A")
        filepath_label = ttk.Label(top_frame, textvariable=self.filepath_display_var, anchor='w')

        # 顶部文件操作按钮
        filepath_label.pack(side='left', padx=(20, 20), fill="x", expand=True)
        undo_button = ttk.Button(top_frame, text="撤销", command=self.undo_last_operation)
        undo_button.pack(side='right', padx=5)
        load_button = ttk.Button(top_frame, text="加载数据", command=self.select_and_load_new_file)
        load_button.pack(side='right', padx=5)
        reset_button = ttk.Button(top_frame, text="重置数据", command=self.reset_data)
        reset_button.pack(side='right', padx=5)

        # 主内容区 (左侧Notebook, 右侧Treeview)
        main_content_frame = ttk.Frame(master)
        main_content_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Notebook (控制面板)
        self.notebook = ttk.Notebook(main_content_frame, width=380) # 给Notebook一个初始宽度
        self.tab_std = StandardizationFrame(self.notebook, self)
        self.notebook.add(self.tab_std, text=" 数据标准化 ")
        self.tab_outlier = OutlierFrame(self.notebook, self)
        self.notebook.add(self.tab_outlier, text=" 异常值处理 ")
        self.tab_missing = MissingValueFrame(self.notebook, self)
        self.notebook.add(self.tab_missing, text=" 缺失值处理 ")
        self.notebook.pack(side='left', fill='y', padx=(0,5)) # Y方向填充，左侧放置
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Treeview (数据显示)
        data_display_frame = ttk.LabelFrame(main_content_frame, text="数据预览")
        data_display_frame.pack(side='left', fill='both', expand=True)
        self.tree = ttk.Treeview(data_display_frame, show="headings")
        tree_vsb = ttk.Scrollbar(data_display_frame, orient="vertical", command=self.tree.yview)
        tree_hsb = ttk.Scrollbar(data_display_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_vsb.set, xscrollcommand=tree_hsb.set)
        tree_vsb.pack(side="right", fill="y")
        tree_hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # 底部日志区域和文件保存区域
        bottom_frame = ttk.Frame(master)
        bottom_frame.pack(side='bottom', fill='x', padx=5, pady=5)
        log_frame = ttk.LabelFrame(bottom_frame, text="操作日志", height=160, width= 830) # 给日志区一个初始高度
        log_frame.pack(side='left', fill='x', padx=5, pady=5)
        log_frame.pack_propagate(False) # 防止子组件撑大Frame
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side='right', fill='x', padx=5, pady=(12,2))
        save_button = ttk.Button(button_frame, text="保存数据", command=self.save_file)
        save_button.pack(side='top', padx=(0,10), pady=10)
        save_as_button = ttk.Button(button_frame, text="数据另存为", command=lambda: self.save_file(save_as=True))
        save_as_button.pack(side='top', padx=(0,10), pady=8)
        exit_button = ttk.Button(button_frame, text="退出清洗", command=root.destroy)
        exit_button.pack(side='top', padx=(0,10), pady=(8,0))

        self.log_text_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=6, font=("Arial", 14))
        self.log_text_area.pack(fill='both', expand=True)
        self.log_action("应用程序启动。")

        if initial_path:
            self.load_file(initial_path)

    def on_tab_changed(self, event):
        # 当选项卡切换时，确保列列表已更新
        selected_tab_object = self.master.nametowidget(self.notebook.select())
        if isinstance(selected_tab_object, BaseProcessingFrame):
            selected_tab_object.populate_columns_list()

    def select_and_load_new_file(self):
        filepath = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=(("CSV 文件", "*.csv"),
                       ("Excel 文件", "*.xlsx *.xls"),
                       ("所有文件", "*.*"))
        )
        if not filepath:
            return
        if filepath:
            self.load_file(filepath)

    def load_file(self, filepath_to_load):

        if filepath_to_load is None:
            messagebox.showerror("文件路径错误", "未选择有效文件路径")
            return
        try:
            if filepath_to_load.lower().endswith(('.xlsx', '.xls')):
                self.df_original = pd.read_excel(filepath_to_load)
            elif filepath_to_load.lower().endswith('.csv'):
                # 尝试多种编码
                try:
                    self.df_original = pd.read_csv(filepath_to_load, encoding='utf-8')
                except UnicodeDecodeError:
                    self.df_original = pd.read_csv(filepath_to_load, encoding='gbk')
            else:
                messagebox.showerror("文件类型错误", "不支持的文件类型。请选择CSV或Excel文件。")
                return

            self.df_cleaned = self.df_original.copy()
            self.current_filepath = filepath_to_load
            self.undo_stack.clear() # 清空撤销栈
            self.update_all_ui_elements()
            self.log_action(f"成功加载文件: {filepath_to_load}")
            self.filename_display_var.set(f"文件名: {os.path.basename(filepath_to_load)}")
            self.filepath_display_var.set(f"文件路径: {filepath_to_load}")

        except Exception as e:
            messagebox.showerror("加载错误", f"加载文件失败: {e}")
            self.log_action(f"错误: 加载文件 '{filepath_to_load}' 失败 - {e}")
            self.df_original = None
            self.df_cleaned = None
            self.current_filepath = None
            self.update_all_ui_elements() # 清空显示

    def save_file(self, save_as=False):
        if self.df_cleaned is None:
            messagebox.showwarning("无数据", "没有可保存的数据。")
            return

        filepath_to_save = self.current_filepath
        if save_as or not filepath_to_save:
            filepath_to_save = filedialog.asksaveasfilename(
                title="保存数据文件",
                defaultextension=".csv",
                initialfile=f"cleaned_data_{datetime.now().strftime('%Y%m%d')}.csv",
                filetypes=(("CSV 文件", "*.csv"), ("Excel 文件", "*.xlsx"), ("所有文件", "*.*"))
            )
        if not filepath_to_save:
            return

        try:
            if filepath_to_save.lower().endswith('.xlsx'):
                self.df_cleaned.to_excel(filepath_to_save, index=False)
            elif filepath_to_save.lower().endswith('.csv'):
                self.df_cleaned.to_csv(filepath_to_save, index=False, encoding='utf-8-sig') # utf-8-sig for Excel compatibility with BOM
            else:
                messagebox.showerror("保存错误", "不支持的保存文件类型。请使用 .csv 或 .xlsx 后缀。")
                return

            self.current_filepath = filepath_to_save # 更新当前文件路径，如果执行的是 "保存" 而非 "另存为" 的话
            self.log_action(f"数据成功保存到: {filepath_to_save}")
            messagebox.showinfo("保存成功", f"数据已保存到 {filepath_to_save}")

        except Exception as e:
            messagebox.showerror("保存错误", f"保存文件失败: {e}")
            self.log_action(f"错误: 保存文件 '{filepath_to_save}' 失败 - {e}")

    def reset_data(self):
        if self.df_original is not None:
            if messagebox.askyesno("确认重置", "您确定要将所有更改还原到最初加载的状态吗？"):
                self._add_to_undo_stack() # 将当前状态存入撤销栈
                self.df_cleaned = self.df_original.copy()
                self.update_all_ui_elements()
                self.log_action("数据已重置为原始加载状态。")
        else:
            messagebox.showwarning("无数据", "尚未加载任何数据。")

    def _add_to_undo_stack(self):
        if self.df_cleaned is not None:
            # 为避免占用过多内存，可以考虑限制栈的大小或只保存差异
            # 这里简单地保存副本
            if len(self.undo_stack) > 0 and self.df_cleaned.equals(self.undo_stack[-1]): # 避免重复添加相同状态
                 return
            self.undo_stack.append(self.df_cleaned.copy())
            if len(self.undo_stack) > 10: # 限制撤销栈大小
                self.undo_stack.pop(0)
            self.log_action("当前状态已保存到撤销记录。")

    def undo_last_operation(self):
        if not self.undo_stack:
            messagebox.showinfo("提示", "没有可撤销的操作。")
            return
        self.df_cleaned = self.undo_stack.pop()
        self.update_all_ui_elements()
        self.log_action("已撤销上一步操作。")

    def update_treeview_display(self):
        # 清空Treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree["columns"] = []

        if self.df_cleaned.empty or self.df_cleaned is None:
            self.log_action("数据为空，无法显示")
            return

        df_display = self.df_cleaned.head(100)
        self.tree["columns"] = list(df_display.columns)
        self.tree["show"] = "headings"

        for col in df_display.columns:
            self.tree.heading(col, text=col, anchor='w')
            self.tree.column(col, anchor="w", width=100, stretch=tk.YES)
        for index, row in df_display.iterrows():
            self.tree.insert("", "end", values=[str(x) for x in row.tolist()]) #确保所有值都是字符串

        self.master.update_idletasks()

    def log_action(self, message):
        self.log_text_area.config(state='normal')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text_area.see(tk.END)
        self.log_text_area.config(state='disabled')

    def get_cleaned_df(self):
        return self.df_cleaned.copy() if self.df_cleaned is not None else None # 返回副本以防意外修改

    def set_cleaned_df(self, new_df, change_description="数据已更新"):
        if self.df_cleaned is not None:
            self._add_to_undo_stack() # 在修改前，将当前状态存入撤销栈

        self.df_cleaned = new_df
        self.update_all_ui_elements()
        self.log_action(change_description) # 记录导致数据更改的操作

    def get_column_list(self):
        if self.df_cleaned is not None:
            return self.df_cleaned.columns.tolist()
        return []

    def update_all_ui_elements(self):
        self.update_treeview_display()
        # 更新所有选项卡中的列列表
        for tab_name_widget in self.notebook.tabs():
            tab_widget = self.master.nametowidget(tab_name_widget)
            if hasattr(tab_widget, 'populate_columns_list'):
                tab_widget.populate_columns_list()


if __name__ == '__main__':
    root = tk.Tk()
    app = DataCleaningApp(root)
    root.mainloop()