import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
from datetime import datetime
import numpy as np
import os  # 引入 os 模块


# ... (您之前提供的 BaseProcessingFrame, StandardizationFrame, OutlierFrame, MissingValueFrame 类定义) ...
# (确保这些类中的 populate_columns_list 和其他与列相关的操作能正确处理空的或已更新的列列表)

class BaseProcessingFrame(ttk.Frame):
    def __init__(self, master, app_controller, title="处理模块"):
        super().__init__(master, padding="10")
        self.app = app_controller # 主应用的引用，用于数据交互和日志记录

        # 通用列选择组件 (每个子类可以决定如何使用或覆盖)
        self.column_selection_frame = ttk.LabelFrame(self, text=f"{title} - 选择列", padding="5")
        self.column_selection_frame.pack(fill=tk.X, pady=5)

        self.column_listbox = tk.Listbox(self.column_selection_frame, selectmode=tk.MULTIPLE, exportselection=False, height=5)
        self.column_listbox_scrollbar_y = ttk.Scrollbar(self.column_selection_frame, orient=tk.VERTICAL, command=self.column_listbox.yview)
        self.column_listbox_scrollbar_x = ttk.Scrollbar(self.column_selection_frame, orient=tk.HORIZONTAL, command=self.column_listbox.xview)
        self.column_listbox.configure(yscrollcommand=self.column_listbox_scrollbar_y.set, xscrollcommand=self.column_listbox_scrollbar_x.set)

        self.column_listbox_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.column_listbox_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.column_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


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


class StandardizationFrame(BaseProcessingFrame):  # 示例，其他Frame类似
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, title="数据标准化")
        # --- 日期时间标准化区 ---
        datetime_lf = ttk.LabelFrame(self, text="日期时间格式化", padding="10")
        datetime_lf.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(datetime_lf, text="目标格式:").pack(side=tk.LEFT, padx=(0, 5))
        self.datetime_format_entry = ttk.Entry(datetime_lf, width=25)
        self.datetime_format_entry.insert(0, "%Y-%m-%d %H:%M:%S")
        self.datetime_format_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.apply_datetime_button = ttk.Button(datetime_lf, text="应用", command=self.apply_datetime_formatting)
        self.apply_datetime_button.pack(side=tk.LEFT, padx=5)

        # --- 浮点数标准化区 ---
        float_lf = ttk.LabelFrame(self, text="浮点数格式化 (四舍五入)", padding="10")
        float_lf.pack(fill=tk.X, pady=5, padx=5)
        ttk.Label(float_lf, text="保留小数位数:").pack(side=tk.LEFT, padx=(0, 5))
        self.float_decimals_spinbox = ttk.Spinbox(float_lf, from_=0, to=15, width=5)
        self.float_decimals_spinbox.set(2)
        self.float_decimals_spinbox.pack(side=tk.LEFT, padx=5)
        self.apply_float_button = ttk.Button(float_lf, text="应用", command=self.apply_float_formatting)
        self.apply_float_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- 文本操作区 ---
        text_lf = ttk.LabelFrame(self, text="文本操作", padding="10")
        text_lf.pack(fill=tk.X, pady=5, padx=5)
        self.text_to_lower_var = tk.BooleanVar()
        self.text_to_upper_var = tk.BooleanVar()
        self.text_strip_var = tk.BooleanVar(value=True)  # 默认勾选去除空格
        ttk.Checkbutton(text_lf, text="转小写", variable=self.text_to_lower_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(text_lf, text="转大写", variable=self.text_to_upper_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(text_lf, text="去除首尾空格", variable=self.text_strip_var).pack(side=tk.LEFT, padx=5)
        self.apply_text_button = ttk.Button(text_lf, text="应用", command=self.apply_text_operations)
        self.apply_text_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- 类型转换区 ---
        type_conversion_lf = ttk.LabelFrame(self, text="类型转换", padding="10")
        type_conversion_lf.pack(fill=tk.X, pady=5, padx=5)
        self.to_numeric_button = ttk.Button(type_conversion_lf, text="转为数值型",
                                            command=lambda: self.apply_type_conversion('numeric'))
        self.to_numeric_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.to_string_button = ttk.Button(type_conversion_lf, text="转为字符型",
                                           command=lambda: self.apply_type_conversion('string'))
        self.to_string_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.to_boolean_button = ttk.Button(type_conversion_lf, text="转为布尔型",
                                            command=lambda: self.apply_type_conversion('boolean'))
        self.to_boolean_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def apply_datetime_formatting(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return
        selected_cols = self.get_selected_columns()
        if not selected_cols: messagebox.showwarning("提示", "请选择要操作的列。"); return

        target_format = self.datetime_format_entry.get()
        if not target_format: messagebox.showerror("错误", "请输入日期时间目标格式。"); return

        new_df = df.copy()
        try:
            for col in selected_cols:
                original_series = new_df[col].copy()
                # 尝试转换为datetime对象，无法转换的变为NaT
                converted_series = pd.to_datetime(original_series, errors='coerce')
                num_nat_initial = original_series.notna().sum() - converted_series.notna().sum()

                # 格式化为字符串
                formatted_series = converted_series.copy().astype(object)
                mask_not_nat = converted_series.notna()
                # 仅对有效日期时间对象进行strftime
                if mask_not_nat.any():  # 确保至少有一个有效日期可以格式化
                    formatted_series.loc[mask_not_nat] = converted_series[mask_not_nat].dt.strftime(target_format)

                formatted_series.loc[~mask_not_nat] = None  # NaT 值在格式化后设为 None (或特定占位符)

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
            messagebox.showerror("错误", "小数位数必须是整数。");
            return

        new_df = df.copy()
        try:
            for col in selected_cols:
                original_series = new_df[col]
                numeric_series = pd.to_numeric(original_series, errors='coerce')
                num_failed_conversion = pd.isna(original_series).sum() - pd.isna(numeric_series).sum()
                # 更准确的说法是新增了多少NaN，或者多少非NaN值变成了NaN
                # num_failed_conversion = numeric_series.isnull().sum() - original_series.isnull().sum() # 这样是新增的NaN
                # 或者是：
                num_actually_failed = 0
                if hasattr(original_series, 'notna'):  # 确保是Series
                    num_actually_failed = (original_series.notna() & numeric_series.isna()).sum()

                new_df[col] = numeric_series.round(decimals)
                self.log(f"列 '{col}': 浮点数保留 {decimals} 位小数。{num_actually_failed}个值在转为数值型时失败。")
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
        if to_lower and to_upper:  # 逻辑上不应同时发生
            self.text_to_upper_var.set(False)  # 例如，取消一个
            messagebox.showwarning("提示", "转小写优先，已取消转大写。")
            # return # 或者直接返回提示用户修改

        new_df = df.copy()
        try:
            for col in selected_cols:
                # 先确保是字符串类型，处理NaN为特定字符串或保留NaN
                s = new_df[col].astype(str).fillna('')  # 将NaN转为空字符串进行操作
                if strip_ws: s = s.str.strip()
                if to_lower:
                    s = s.str.lower()
                elif to_upper:
                    s = s.str.upper()  # 使用elif确保小写和大写不同时作用（尽管UI上可能已处理）
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

    def apply_type_conversion(self, target_type):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return
        selected_cols = self.get_selected_columns()
        if not selected_cols: messagebox.showwarning("提示", "请选择要操作的列。"); return

        new_df = df.copy()
        try:
            for col in selected_cols:
                original_dtype_str = str(new_df[col].dtype)  # 获取原始类型字符串
                original_nan_count = new_df[col].isnull().sum()

                if target_type == 'numeric':
                    new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
                    # 计算由于转换失败而新增的NaN数量
                    failed_count = new_df[col].isnull().sum() - original_nan_count
                    self.log(
                        f"列 '{col}' (原类型: {original_dtype_str}): 转为数值型。{failed_count if failed_count > 0 else 0}个值转换失败变为NaN。")
                elif target_type == 'string':
                    new_df[col] = new_df[col].astype(str)  # NaNs will become 'nan'
                    self.log(f"列 '{col}' (原类型: {original_dtype_str}): 转为字符型。")
                elif target_type == 'boolean':
                    true_values = ['true', 'yes', '1', 't', 'y']
                    false_values = ['false', 'no', '0', 'f', 'n']
                    # 先转为小写字符串并去除首尾空格，对NaN填充一个不太可能与真/假值冲突的特殊标记
                    temp_series = new_df[col].fillna("__TEMP_NAN_FOR_BOOL_CONV__").astype(str).str.lower().str.strip()

                    # 初始化为pd.NA (pandas的nullable boolean)
                    new_col_data = pd.Series(pd.NA, index=new_df.index, dtype='boolean')
                    new_col_data[temp_series.isin(true_values)] = True
                    new_col_data[temp_series.isin(false_values)] = False
                    # 原本就是NaN的值(现在是'__TEMP_NAN_FOR_BOOL_CONV__')，在new_col_data中已经是pd.NA
                    new_df[col] = new_col_data
                    self.log(f"列 '{col}' (原类型: {original_dtype_str}): 转为布尔型 (True/False/NA)。")

            self.set_df(new_df, f"类型转换为 {target_type}")
        except Exception as e:
            self.log(f"错误: 类型转换为 {target_type} 失败 - {e}")
            messagebox.showerror("错误", f"类型转换为 {target_type} 失败: {e}")


class OutlierFrame(BaseProcessingFrame):  # 保持不变
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, title="异常值处理")

        options_lf = ttk.LabelFrame(self, text="参数设置", padding="10")
        options_lf.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(options_lf, text="方法:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.method_var = tk.StringVar(value="IQR")
        method_options = ["IQR", "Z-score", "百分位"]
        self.method_combo = ttk.Combobox(options_lf, textvariable=self.method_var, values=method_options,
                                         state="readonly", width=10)
        self.method_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.method_combo.bind("<<ComboboxSelected>>", self.update_params_ui)

        self.iqr_lf = ttk.Frame(options_lf)
        ttk.Label(self.iqr_lf, text="IQR乘数:").pack(side=tk.LEFT, padx=5)
        self.iqr_multiplier_entry = ttk.Entry(self.iqr_lf, width=5)
        self.iqr_multiplier_entry.insert(0, "1.5")
        self.iqr_multiplier_entry.pack(side=tk.LEFT, padx=5)

        self.zscore_lf = ttk.Frame(options_lf)
        ttk.Label(self.zscore_lf, text="Z-score阈值:").pack(side=tk.LEFT, padx=5)
        self.zscore_threshold_entry = ttk.Entry(self.zscore_lf, width=5)
        self.zscore_threshold_entry.insert(0, "3")
        self.zscore_threshold_entry.pack(side=tk.LEFT, padx=5)

        self.percentile_lf = ttk.Frame(options_lf)
        ttk.Label(self.percentile_lf, text="下限百分位:").pack(side=tk.LEFT, padx=5)
        self.lower_percentile_entry = ttk.Entry(self.percentile_lf, width=5)
        self.lower_percentile_entry.insert(0, "1")
        self.lower_percentile_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.percentile_lf, text="上限百分位:").pack(side=tk.LEFT, padx=5)
        self.upper_percentile_entry = ttk.Entry(self.percentile_lf, width=5)
        self.upper_percentile_entry.insert(0, "99")
        self.upper_percentile_entry.pack(side=tk.LEFT, padx=5)

        self.params_ui_frames = {
            "IQR": self.iqr_lf,
            "Z-score": self.zscore_lf,
            "百分位": self.percentile_lf
        }
        self.current_params_lf = None
        self.update_params_ui()

        ttk.Label(options_lf, text="处理方式:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.action_var = tk.StringVar(value="替换为NaN")
        action_options = ["移除行", "替换为边界值(Capping)", "替换为NaN"]
        self.action_combo = ttk.Combobox(options_lf, textvariable=self.action_var, values=action_options,
                                         state="readonly", width=20)
        self.action_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        options_lf.columnconfigure(1, weight=1)

        apply_button = ttk.Button(self, text="应用异常值处理到选中数值列", command=self.apply_outlier_handling)
        apply_button.pack(pady=10, padx=5, fill=tk.X)

    def update_params_ui(self, event=None):
        method = self.method_var.get()
        if self.current_params_lf:
            self.current_params_lf.grid_remove()

        self.current_params_lf = self.params_ui_frames.get(method)
        if self.current_params_lf:
            self.current_params_lf.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    def apply_outlier_handling(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return
        selected_cols_all = self.get_selected_columns()
        if not selected_cols_all: messagebox.showwarning("提示", "请选择要操作的列。"); return

        selected_cols = [col for col in selected_cols_all if pd.api.types.is_numeric_dtype(df[col])]
        non_numeric_cols = [col for col in selected_cols_all if not pd.api.types.is_numeric_dtype(df[col])]

        if not selected_cols:
            messagebox.showerror("错误", "选中的列均非数值型，无法进行异常值处理。");
            return
        if non_numeric_cols:
            self.log(f"警告: 列 {', '.join(non_numeric_cols)} 非数值型，已在异常值处理中跳过。")

        method = self.method_var.get()
        action = self.action_var.get()
        new_df = df.copy()
        outlier_indices = pd.Index([])

        try:
            for col in selected_cols:
                s = new_df[col].dropna()
                if s.empty:  # 如果去除NaN后列为空，则跳过
                    self.log(f"列 '{col}': 去除NaN后为空，跳过异常值检测。")
                    continue

                lower_bound, upper_bound = None, None

                if method == "IQR":
                    multiplier = float(self.iqr_multiplier_entry.get())
                    q1 = s.quantile(0.25)
                    q3 = s.quantile(0.75)
                    iqr_val = q3 - q1
                    if iqr_val == 0:  # 如果IQR为0，例如列中大部分值相同
                        # 可以选择将此列视为无IQR定义的异常值，或者根据具体情况处理
                        # 这里我们简单跳过，或者可以基于q1, q3来定义一个微小范围
                        self.log(f"列 '{col}': IQR值为0，跳过IQR异常值检测。")
                        continue
                    lower_bound = q1 - multiplier * iqr_val
                    upper_bound = q3 + multiplier * iqr_val
                elif method == "Z-score":
                    threshold = float(self.zscore_threshold_entry.get())
                    mean = s.mean()
                    std = s.std()
                    if std == 0 or pd.isna(std):
                        self.log(f"列 '{col}': Z-score法检测，标准差为0或NaN，跳过。")
                        continue
                    lower_bound = mean - threshold * std
                    upper_bound = mean + threshold * std
                elif method == "百分位":
                    lower_p = float(self.lower_percentile_entry.get()) / 100.0
                    upper_p = float(self.upper_percentile_entry.get()) / 100.0
                    if not (0 <= lower_p < upper_p <= 1):  # 确保百分位有效
                        messagebox.showerror("错误",
                                             f"百分位设置无效（应为 0 <= 下限 ({lower_p * 100}) < 上限 ({upper_p * 100}) <= 100）。");
                        return
                    lower_bound = s.quantile(lower_p)
                    upper_bound = s.quantile(upper_p)

                if lower_bound is None or upper_bound is None:  # 安全检查
                    self.log(f"列 '{col}': 未能计算出边界值，跳过。")
                    continue

                current_col_outliers_mask = (new_df[col] < lower_bound) | (new_df[col] > upper_bound)
                current_col_outliers_indices = new_df[current_col_outliers_mask].index

                self.log(
                    f"列 '{col}' ({method}): 检测到 {len(current_col_outliers_indices)} 个异常值。范围: [{lower_bound:.2f}, {upper_bound:.2f}]")

                if action == "替换为NaN":
                    new_df.loc[current_col_outliers_indices, col] = np.nan
                elif action == "替换为边界值(Capping)":
                    new_df.loc[new_df[col] < lower_bound, col] = lower_bound
                    new_df.loc[new_df[col] > upper_bound, col] = upper_bound
                elif action == "移除行":
                    outlier_indices = outlier_indices.union(current_col_outliers_indices)

            if action == "移除行" and not outlier_indices.empty:
                rows_before = len(new_df)
                new_df.drop(index=outlier_indices.unique(), inplace=True)  # 使用unique确保索引不重复
                self.log(f"根据所有选中列的异常值检测，共移除了 {rows_before - len(new_df)} 行。")

            self.set_df(new_df, f"异常值处理 ({method}, {action})")
        except ValueError as ve:
            self.log(f"错误: 异常值处理参数错误 - {ve}")
            messagebox.showerror("参数错误", f"异常值处理参数无效: {ve}")
        except Exception as e:
            self.log(f"错误: 异常值处理失败 - {e}")
            messagebox.showerror("错误", f"异常值处理失败: {e}")


class MissingValueFrame(BaseProcessingFrame):  # 保持不变
    def __init__(self, master, app_controller):
        super().__init__(master, app_controller, title="缺失值处理")
        options_lf = ttk.LabelFrame(self, text="处理选项", padding="10")
        options_lf.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(options_lf, text="策略:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.strategy_var = tk.StringVar(value="移除行(dropna)")
        strategies = ["移除行(dropna)", "移除列(dropcol)", "填充(fill)"]
        self.strategy_combo = ttk.Combobox(options_lf, textvariable=self.strategy_var, values=strategies,
                                           state="readonly")
        self.strategy_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.strategy_combo.bind("<<ComboboxSelected>>", self.update_fill_options_ui)

        self.fill_options_lf = ttk.Frame(options_lf)
        ttk.Label(self.fill_options_lf, text="填充方法:").pack(side=tk.LEFT, padx=5)
        self.fill_method_var = tk.StringVar(value="均值(mean)")
        fill_methods = ["均值(mean)", "中位数(median)", "众数(mode)", "固定值", "前向填充(ffill)", "后向填充(bfill)"]
        self.fill_method_combo = ttk.Combobox(self.fill_options_lf, textvariable=self.fill_method_var,
                                              values=fill_methods, state="readonly", width=15)
        self.fill_method_combo.pack(side=tk.LEFT, padx=5)
        self.fill_method_combo.bind("<<ComboboxSelected>>", self.update_fill_options_ui)

        self.fill_value_label = ttk.Label(self.fill_options_lf, text="固定值:")
        self.fill_value_entry = ttk.Entry(self.fill_options_lf, width=10)

        self.dropcol_options_lf = ttk.Frame(options_lf)
        ttk.Label(self.dropcol_options_lf, text="缺失比例阈值(%):").pack(side=tk.LEFT, padx=5)
        self.dropcol_threshold_spinbox = ttk.Spinbox(self.dropcol_options_lf, from_=0, to=100, increment=5, width=5)
        self.dropcol_threshold_spinbox.set(50)
        self.dropcol_threshold_spinbox.pack(side=tk.LEFT, padx=5)

        options_lf.columnconfigure(1, weight=1)
        self.update_fill_options_ui()

        apply_button = ttk.Button(self, text="应用缺失值处理", command=self.handle_missing_values)
        apply_button.pack(pady=10, padx=5, fill=tk.X)

    def update_fill_options_ui(self, event=None):
        strategy = self.strategy_var.get()
        fill_method = self.fill_method_var.get()

        self.fill_options_lf.grid_remove()
        self.fill_value_label.pack_forget()
        self.fill_value_entry.pack_forget()
        self.dropcol_options_lf.grid_remove()

        if strategy == "填充(fill)":
            self.fill_options_lf.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
            if fill_method == "固定值":
                self.fill_value_label.pack(side=tk.LEFT, padx=(10, 0))
                self.fill_value_entry.pack(side=tk.LEFT, padx=5)
        elif strategy == "移除列(dropcol)":
            self.dropcol_options_lf.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

    def handle_missing_values(self):
        df = self.get_df()
        if df is None: messagebox.showerror("错误", "请先加载数据"); return

        selected_cols = self.get_selected_columns()
        # 如果没有选择列，则默认对所有列操作（某些策略如填充可能需要逐列，某些如dropna可以全局）
        # 对于填充，我们希望迭代选择的列或所有列。
        # 对于dropna行，subset应该是选择的列，如果没选则是None（所有列）。
        # 对于drop列，操作对象是df的所有列，而不是选择的列。

        strategy = self.strategy_var.get()
        new_df = df.copy()
        action_description = f"缺失值处理 - 策略: {strategy}"

        try:
            if strategy == "移除行(dropna)":
                rows_before = len(new_df)
                subset_to_check = selected_cols if selected_cols else None  # 如果用户选了列，则只在这些列中检查NaN
                new_df.dropna(subset=subset_to_check, inplace=True)
                rows_after = len(new_df)
                self.log(
                    f"移除了 {rows_before - rows_after} 行 (基于 {'选中列' if subset_to_check else '所有列'} 的缺失值)。")
                action_description += f", 移除了 {rows_before - rows_after} 行"

            elif strategy == "移除列(dropcol)":
                cols_before_set = set(new_df.columns)
                try:
                    threshold_percent = float(self.dropcol_threshold_spinbox.get())
                except ValueError:
                    messagebox.showerror("错误", "移除列的阈值必须是数字。");
                    return
                if not (0 <= threshold_percent <= 100):
                    messagebox.showerror("错误", "阈值必须在0到100之间。");
                    return

                threshold_ratio = threshold_percent / 100.0

                # 计算每列的缺失比例，然后决定删除哪些
                # 这里的cols_to_process应该是DataFrame的所有列
                cols_to_drop_final = []
                for col_name in new_df.columns.tolist():
                    if new_df[col_name].isnull().sum() / len(new_df) > threshold_ratio:
                        cols_to_drop_final.append(col_name)

                if cols_to_drop_final:
                    new_df.drop(columns=cols_to_drop_final, inplace=True)
                    self.log(f"移除了缺失值超过 {threshold_percent}% 的列: {', '.join(cols_to_drop_final)}。")
                    action_description += f", 移除了列: {', '.join(cols_to_drop_final)}"
                else:
                    self.log(f"没有列的缺失值超过 {threshold_percent}%。")


            elif strategy == "填充(fill)":
                fill_method_str = self.fill_method_var.get()
                action_description += f", 方法: {fill_method_str}"

                # 如果用户没有选择列，则对所有列应用填充策略
                cols_for_fill = selected_cols if selected_cols else new_df.columns.tolist()
                if not cols_for_fill:
                    messagebox.showwarning("无列操作", "没有选中列，并且DataFrame为空，无法填充。");
                    return

                for col in cols_for_fill:
                    if new_df[col].isnull().any():  # 只处理有缺失值的列
                        original_nan_count = new_df[col].isnull().sum()
                        if fill_method_str == "均值(mean)":
                            if pd.api.types.is_numeric_dtype(new_df[col]):
                                fill_val = new_df[col].mean()
                                if pd.isna(fill_val):  # 如果均值是NaN (例如全NaN列)
                                    self.log(f"列 '{col}': 均值为NaN，无法填充。")
                                else:
                                    new_df[col].fillna(fill_val, inplace=True)
                                    self.log(
                                        f"列 '{col}': 用均值 ({fill_val:.2f}) 填充了 {original_nan_count} 个缺失值。")
                            else:
                                self.log(f"列 '{col}': 非数值型，跳过均值填充。")
                        elif fill_method_str == "中位数(median)":
                            if pd.api.types.is_numeric_dtype(new_df[col]):
                                fill_val = new_df[col].median()
                                if pd.isna(fill_val):
                                    self.log(f"列 '{col}': 中位数值为NaN，无法填充。")
                                else:
                                    new_df[col].fillna(fill_val, inplace=True)
                                    self.log(
                                        f"列 '{col}': 用中位数 ({fill_val:.2f}) 填充了 {original_nan_count} 个缺失值。")
                            else:
                                self.log(f"列 '{col}': 非数值型，跳过中位数填充。")
                        elif fill_method_str == "众数(mode)":
                            mode_val = new_df[col].mode()
                            if not mode_val.empty:
                                fill_val = mode_val[0]
                                new_df[col].fillna(fill_val, inplace=True)
                                self.log(f"列 '{col}': 用众数 ('{fill_val}') 填充了 {original_nan_count} 个缺失值。")
                            else:
                                self.log(f"列 '{col}': 找不到众数，跳过填充。")
                        elif fill_method_str == "固定值":
                            fill_val_str = self.fill_value_entry.get()
                            action_description += f", 固定值: '{fill_val_str}'"
                            try:
                                target_dtype = df[col].dtype  # 使用原始df的类型判断
                                if pd.api.types.is_numeric_dtype(target_dtype):
                                    fill_val = pd.to_numeric(fill_val_str)
                                elif pd.api.types.is_datetime64_any_dtype(target_dtype):
                                    fill_val = pd.to_datetime(fill_val_str)
                                elif pd.api.types.is_bool_dtype(target_dtype) or (
                                        hasattr(target_dtype, 'name') and target_dtype.name == 'boolean'):
                                    if fill_val_str.lower() in ['true', '1', 'yes', 't', 'y']:
                                        fill_val = True
                                    elif fill_val_str.lower() in ['false', '0', 'no', 'f', 'n']:
                                        fill_val = False
                                    else:
                                        raise ValueError("布尔值转换失败，请输入 True/False/Yes/No/1/0 等")
                                else:
                                    fill_val = fill_val_str  # 默认为字符串
                                new_df[col].fillna(fill_val, inplace=True)
                                self.log(f"列 '{col}': 用固定值 ('{fill_val}') 填充了 {original_nan_count} 个缺失值。")
                            except ValueError as e_conv:
                                new_df[col].fillna(fill_val_str, inplace=True)
                                self.log(
                                    f"列 '{col}': 固定值 '{fill_val_str}' 无法按原类型转换 ({e_conv})，已按字符串填充 {original_nan_count} 个缺失值。")

                        elif fill_method_str == "前向填充(ffill)":
                            new_df[col].ffill(inplace=True)
                            filled_after = original_nan_count - new_df[col].isnull().sum()
                            self.log(f"列 '{col}': 执行前向填充，填充了 {filled_after} 个缺失值。")
                        elif fill_method_str == "后向填充(bfill)":
                            new_df[col].bfill(inplace=True)
                            filled_after = original_nan_count - new_df[col].isnull().sum()
                            self.log(f"列 '{col}': 执行后向填充，填充了 {filled_after} 个缺失值。")
            else:
                messagebox.showwarning("未知策略", f"未知的缺失值处理策略: {strategy}")
                return

            self.set_df(new_df, action_description)
        except Exception as e:
            self.log(f"错误: 缺失值处理失败 - {e}")
            messagebox.showerror("错误", f"缺失值处理失败: {e}")


class DataCleaningApp:
    def __init__(self, master):
        self.master = master
        master.title("Python 数据清洗工具")
        master.geometry("1000x750")

        self.df_original = None
        self.df_cleaned = None
        self.current_filepath = None
        self.undo_stack = []

        top_frame = ttk.Frame(master)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        load_button = ttk.Button(top_frame, text="加载数据", command=self.load_file)
        load_button.pack(side=tk.LEFT, padx=5)
        save_button = ttk.Button(top_frame, text="保存数据", command=self.save_file)
        save_button.pack(side=tk.LEFT, padx=5)
        save_as_button = ttk.Button(top_frame, text="另存为...", command=lambda: self.save_file(save_as=True))
        save_as_button.pack(side=tk.LEFT, padx=5)
        reset_button = ttk.Button(top_frame, text="重置数据", command=self.reset_data)
        reset_button.pack(side=tk.LEFT, padx=5)
        undo_button = ttk.Button(top_frame, text="撤销(Undo)", command=self.undo_last_operation)
        undo_button.pack(side=tk.LEFT, padx=5)

        main_content_frame = ttk.Frame(master)
        main_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.notebook = ttk.Notebook(main_content_frame, width=380)

        self.tab_std = StandardizationFrame(self.notebook, self)
        self.notebook.add(self.tab_std, text=" 数据标准化 ")

        self.tab_outlier = OutlierFrame(self.notebook, self)
        self.notebook.add(self.tab_outlier, text=" 异常值处理 ")

        self.tab_missing = MissingValueFrame(self.notebook, self)
        self.notebook.add(self.tab_missing, text=" 缺失值处理 ")

        self.notebook.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        data_display_frame = ttk.LabelFrame(main_content_frame, text="数据预览 (最多显示前100行)")
        data_display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(data_display_frame, show="headings")
        tree_vsb = ttk.Scrollbar(data_display_frame, orient="vertical", command=self.tree.yview)
        tree_hsb = ttk.Scrollbar(data_display_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_vsb.set, xscrollcommand=tree_hsb.set)
        tree_vsb.pack(side="right", fill="y")
        tree_hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        log_frame = ttk.LabelFrame(master, text="操作日志", height=100)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        log_frame.pack_propagate(False)

        self.log_text_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=6,
                                                       font=("Arial", 9))
        self.log_text_area.pack(fill=tk.BOTH, expand=True)

        self.log_action("应用程序启动。")

    def on_tab_changed(self, event):
        try:
            # Notebook.select() 返回的是 widget 的路径名字符串
            selected_tab_widget_path = self.notebook.select()
            if selected_tab_widget_path:  # 确保有选中的tab
                selected_tab_object = self.master.nametowidget(selected_tab_widget_path)
                if isinstance(selected_tab_object, BaseProcessingFrame):
                    selected_tab_object.populate_columns_list()
        except tk.TclError:
            # 当Notebook中没有tab时select()可能返回空字符串，nametowidget会报错
            pass

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=(("CSV 文件", "*.csv"),
                       ("Excel 文件", "*.xlsx *.xls"),
                       ("所有文件", "*.*"))
        )
        if not filepath:
            return

        try:
            if filepath.lower().endswith(('.xlsx', '.xls')):
                df_temp = pd.read_excel(filepath)
            elif filepath.lower().endswith('.csv'):
                try:
                    df_temp = pd.read_csv(filepath, encoding='utf-8')
                except UnicodeDecodeError:
                    df_temp = pd.read_csv(filepath, encoding='gbk')
            else:
                messagebox.showerror("文件类型错误", "不支持的文件类型。请选择CSV或Excel文件。")
                return

            # 检查并处理重复列名，为Treeview和后续操作做准备
            cols = pd.Series(df_temp.columns)
            if cols.duplicated().any():
                self.log_action(f"警告：文件 '{os.path.basename(filepath)}' 中包含重复列名，将自动重命名。")
                seen = {}
                new_columns = []
                for col in df_temp.columns:
                    original_col = col
                    count = seen.get(original_col, 0)
                    if count > 0:  # 如果已经见过，则添加后缀
                        col = f"{original_col}_{count}"
                    seen[original_col] = count + 1
                    new_columns.append(col)
                df_temp.columns = new_columns

            self.df_original = df_temp
            self.df_cleaned = self.df_original.copy()
            self.current_filepath = filepath
            self.undo_stack.clear()
            self.update_all_ui_elements()  # 这一步会更新treeview和所有tab的列列表
            self.log_action(f"成功加载文件: {os.path.basename(filepath)}. 数据形状: {self.df_cleaned.shape}")
            self.master.title(f"Python 数据清洗工具 - {os.path.basename(filepath)}")

        except Exception as e:
            messagebox.showerror("加载错误", f"加载文件失败: {e}")
            self.log_action(f"错误: 加载文件 '{filepath}' 失败 - {e}")
            self.df_original = None
            self.df_cleaned = None
            self.current_filepath = None
            self.update_all_ui_elements()
            self.master.title("Python 数据清洗工具")

    def save_file(self, save_as=False):
        if self.df_cleaned is None:
            messagebox.showwarning("无数据", "没有可保存的数据。")
            return

        filepath_to_save = self.current_filepath
        if save_as or not filepath_to_save:  # 如果是另存为，或者当前没有文件路径（比如刚加载就想另存）
            initial_filename = f"cleaned_{os.path.basename(self.current_filepath) if self.current_filepath else 'data'}_{datetime.now().strftime('%Y%m%d')}.csv"
            filepath_to_save = filedialog.asksaveasfilename(
                title="保存数据文件",
                defaultextension=".csv",
                initialfile=initial_filename,
                filetypes=(("CSV 文件", "*.csv"), ("Excel 文件", "*.xlsx"), ("所有文件", "*.*"))
            )
        if not filepath_to_save:  # 用户取消
            return

        try:
            if filepath_to_save.lower().endswith('.xlsx'):
                self.df_cleaned.to_excel(filepath_to_save, index=False)
            elif filepath_to_save.lower().endswith('.csv'):
                self.df_cleaned.to_csv(filepath_to_save, index=False, encoding='utf-8-sig')
            else:  # 用户可能输入了没有后缀的文件名，但通过defaultextension应已添加
                messagebox.showerror("保存错误", "不支持的保存文件类型或未指定后缀。请使用 .csv 或 .xlsx 后缀。")
                return

            if not save_as:  # 只有当不是“另存为”且保存成功时，才更新 self.current_filepath
                self.current_filepath = filepath_to_save

            self.log_action(f"数据成功保存到: {filepath_to_save}")
            messagebox.showinfo("保存成功", f"数据已保存到 {filepath_to_save}")
            self.master.title(f"Python 数据清洗工具 - {os.path.basename(filepath_to_save)}")

        except Exception as e:
            messagebox.showerror("保存错误", f"保存文件失败: {e}")
            self.log_action(f"错误: 保存文件 '{filepath_to_save}' 失败 - {e}")

    def reset_data(self):
        if self.df_original is not None:
            if messagebox.askyesno("确认重置", "您确定要将所有更改还原到最初加载的状态吗？此操作会清空撤销记录。"):
                self.df_cleaned = self.df_original.copy()
                self.undo_stack.clear()  # 重置时也清空撤销栈
                self.update_all_ui_elements()
                self.log_action("数据已重置为原始加载状态。")
        else:
            messagebox.showwarning("无数据", "尚未加载任何数据。")

    def _add_to_undo_stack(self):
        if self.df_cleaned is not None:
            # 避免撤销栈中连续出现完全相同的DataFrame状态
            if self.undo_stack and self.df_cleaned.equals(self.undo_stack[-1]):
                return
            self.undo_stack.append(self.df_cleaned.copy())
            if len(self.undo_stack) > 10:  # 限制撤销栈大小
                self.undo_stack.pop(0)
            # self.log_action("当前状态已保存到撤销记录。") # 这个日志可能太频繁

    def undo_last_operation(self):
        if not self.undo_stack:
            messagebox.showinfo("提示", "没有可撤销的操作。")
            return
        # 在恢复之前，把当前（即将被丢弃的）状态也记录一下，以便可以“重做”下一步，但这会使逻辑复杂
        # 这里简单实现：只撤销
        self.df_cleaned = self.undo_stack.pop()
        self.update_all_ui_elements()
        self.log_action("已撤销上一步操作。")

    def update_treeview_display(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.df_cleaned is not None and not self.df_cleaned.empty:
            df_display = self.df_cleaned.head(100)

            # --- 关键修改：为Treeview生成唯一的列ID ---
            actual_df_columns = df_display.columns.tolist()
            tree_column_ids = []
            seen_ids = {}  # 用于确保生成的ID是唯一的
            for col_name_obj in actual_df_columns:
                col_name_str = str(col_name_obj)  # 确保列名是字符串
                temp_id = col_name_str
                count = 0
                while temp_id in seen_ids:  # 如果生成的ID已存在，则添加后缀
                    count += 1
                    temp_id = f"{col_name_str}_{count}"
                seen_ids[temp_id] = True
                tree_column_ids.append(temp_id)
            # --- 结束关键修改 ---

            self.tree["columns"] = tree_column_ids
            self.tree["displaycolumns"] = tree_column_ids  # 通常显示所有列

            for i, col_id in enumerate(tree_column_ids):
                original_col_name = actual_df_columns[i]  # 表头仍然显示原始列名
                self.tree.heading(col_id, text=str(original_col_name), anchor='w')
                self.tree.column(col_id, anchor="w", width=100, stretch=tk.YES, minwidth=40)

            for index, row_data in df_display.iterrows():
                # 将行数据转换为字符串列表进行显示
                self.tree.insert("", "end", values=[str(x) for x in row_data.tolist()])
        else:  # 如果DataFrame为空或None
            self.tree["columns"] = []
            self.tree["displaycolumns"] = []

        self.master.update_idletasks()  # 请求Tkinter处理挂起的UI更新

    def log_action(self, message):
        self.log_text_area.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text_area.see(tk.END)
        self.log_text_area.config(state=tk.DISABLED)

    def get_cleaned_df(self):
        return self.df_cleaned.copy() if self.df_cleaned is not None else None

    def set_cleaned_df(self, new_df, change_description="数据已更新"):
        if self.df_cleaned is not None:  # 只有当存在旧的df_cleaned时才添加到撤销栈
            self._add_to_undo_stack()
        self.df_cleaned = new_df
        self.update_all_ui_elements()  # 更新UI，包括Treeview和所有tab的列列表
        self.log_action(
            f"操作完成: {change_description}. 当前数据形状: {self.df_cleaned.shape if self.df_cleaned is not None else 'N/A'}")

    def get_column_list(self):
        if self.df_cleaned is not None:
            return self.df_cleaned.columns.tolist()
        return []

    def update_all_ui_elements(self):
        self.update_treeview_display()
        # 更新所有选项卡中的列列表，确保在数据改变后所有tab的列选择框都是最新的
        # 需要在主线程中安全地调用，或者通过 on_tab_changed 自动处理
        # 这里我们直接调用每个tab的 populate_columns_list
        if hasattr(self, 'tab_std') and self.tab_std: self.tab_std.populate_columns_list()
        if hasattr(self, 'tab_outlier') and self.tab_outlier: self.tab_outlier.populate_columns_list()
        if hasattr(self, 'tab_missing') and self.tab_missing: self.tab_missing.populate_columns_list()


if __name__ == '__main__':
    root = tk.Tk()
    app = DataCleaningApp(root)
    root.mainloop()