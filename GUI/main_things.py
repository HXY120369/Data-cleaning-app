import tkinter as tk
from PIL import Image, ImageTk
from data_cleaning.GUI import main_interface
from tkinter import ttk, filedialog, messagebox, scrolledtext
from data_cleaning.data_operation import data_preview, data_cleaning, data_audit, operation_record


class ThingsData:
    def __init__(self, master):
        self.master = master
        self.root = master
        master.title("对于‘物’的数据清洗")

        # 设置窗口居中
        window_width = 600
        window_height = 450
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # 使用 ttk 样式
        style = ttk.Style(master)
        style.theme_use("clam")

        # 主内容Frame
        main_frame = ttk.Frame(master, padding="10", relief="ridge", borderwidth=2)
        main_frame.pack(fill="both", expand=True)

        # 加载所需要的图片
        image_paths = ["images/image_things.png",
                       "images/document_icon.png",
                       "images/refresh.png",]
        image1 = Image.open(image_paths[0])
        image2 = Image.open(image_paths[1])
        image3 = Image.open(image_paths[2])
        resized_image1 = image1.resize((125, 125))
        resized_image2 = image2.resize((25, 25))
        resized_image3 = image3.resize((25, 25))
        photo1 = ImageTk.PhotoImage(resized_image1)
        photo2 = ImageTk.PhotoImage(resized_image2)
        photo3 = ImageTk.PhotoImage(resized_image3)

        # 1. left_frame来涵盖左边的组件
        left_frame = ttk.Frame(main_frame, relief="ridge", borderwidth=2)
        left_frame.pack(side='left', expand=True)

        # 1.1 left_top_frame
        left_top_frame = ttk.Frame(left_frame, relief="ridge", borderwidth=2)
        left_top_frame.pack(side='top', fill='x', padx=10, pady=8)

        self.image_label = ttk.Label(left_top_frame, image=photo1)
        self.image_label.image = photo1
        self.image_label.grid(column=0, row=0, padx=10, pady=10)

        self.label1 = ttk.Label(left_top_frame, text="生产设备信息数据", width=15)
        self.label1.grid(column=0, row=1, padx=10, pady=5)
        self.label2 = ttk.Label(left_top_frame, text="生产设备运行数据", width=15)
        self.label2.grid(column=0, row=2, padx=10, pady=5)
        self.label3 = ttk.Label(left_top_frame, text="能源消耗数据", width=15)
        self.label3.grid(column=0, row=3, padx=10, pady=5)
        self.label4 = ttk.Label(left_top_frame, text="……", width=15)
        self.label4.grid(column=0, row=4, padx=10, pady=6)
        self.info_button = ttk.Button(left_top_frame, text="了解更多", command=self.know_more)
        self.info_button.grid(column=0, row=5, padx=10, pady=10)

        # 1.2 left_bottom_frame
        left_bottom_frame = ttk.Frame(left_frame, borderwidth=2)
        left_bottom_frame.pack(side='top', fill='x', padx=10)

        self.back_button = ttk.Button(left_bottom_frame, text="返回", command=self.back)
        self.back_button.pack(side='top', padx=10, pady=4)

        # 2. right_frame来涵盖右边的组件，其中右边的组件又会分成上下两部分
        right_frame = ttk.Frame(main_frame, padding="10", relief="ridge", borderwidth=2)
        right_frame.pack(side='right', fill='x', padx=10, pady=10)

        # 2.1 right_top_frame 用于选择文件
        sub_title1 = ttk.Label(right_frame, text="文件选择", width=15)
        sub_title1.pack(side='top', fill='x', padx=10)
        right_top_frame = ttk.Frame(right_frame, padding="10", relief="ridge", borderwidth=2)
        right_top_frame.pack(side='top', fill='x', padx=10, pady=5)

        self.file_label = tk.Label(right_top_frame, text="请选择要清洗的文件", relief='sunken', bd=2, fg="gray", width=30, height=2)
        self.file_label.pack(side='top', padx=10, pady=5)
        self.open_button = ttk.Button(right_top_frame, image=photo2, command=self.open_file)
        self.open_button.image = photo2
        self.open_button.pack(side='left', padx=10, pady=5)
        self.refresh_button = ttk.Button(right_top_frame, image=photo3, command=self.refresh)
        self.refresh_button.image = photo3
        self.refresh_button.pack(side='left', pady=5)

        # 2.2 right_bottom_frame 用于数据操作
        blank_frame = ttk.Frame(right_frame, padding="10", borderwidth=2, height=40)
        blank_frame.pack(side='top', fill='x', padx=10, pady=10)
        sub_title2 = ttk.Label(right_frame, text="文件操作", width=15)
        sub_title2.pack(side='top', fill='x', padx=10, pady=5)
        right_bottom_frame = ttk.Frame(right_frame, padding="10", relief="ridge", borderwidth=2)
        right_bottom_frame.pack(side='top', fill='x', padx=10, pady=5)

        self.preview_button = ttk.Button(right_bottom_frame, text="文件预览", command=self.preview_file)
        self.preview_button.grid(row=0, column=0, padx=15, pady=6)
        self.check_button = ttk.Button(right_bottom_frame, text="数据审查", command=self.audit_file)
        self.check_button.grid(row=0, column=1, padx=10, pady=6)
        self.clean_button = ttk.Button(right_bottom_frame, text="数据清洗", command=self.clean_file)
        self.clean_button.grid(row=1, column=0, padx=15, pady=6)
        self.back_button = ttk.Button(right_bottom_frame, text="操作日志", command=self.operation_file)
        self.back_button.grid(row=1, column=1, padx=10, pady=6)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")])
        if file_path:
            # 若用户选择了文件夹，将文件夹路径显示在标签上
            self.file_label.config(text=f"{file_path}", fg="black")

    def refresh(self):
        if self.file_label.cget("text") != "请选择要清洗的文件":
            self.file_label.config(text="请选择要清洗的文件")
            self.file_label.config(fg="gray")

    def preview_file(self):
        if self.file_label.cget("text") == "请选择要清洗的文件":
            messagebox.showerror("尚未选择文件", "请选择 .xlsx, .xls 或 .csv 文件。")
        else:
            file_path = self.file_label.cget("text")
            root = tk.Toplevel()
            app = data_preview.DataPreviewApp(root, file_path)
            root.mainloop()

    def audit_file(self):
        if self.file_label.cget("text") == "请选择要清洗的文件":
            messagebox.showerror("尚未选择文件", "请选择 .xlsx, .xls 或 .csv 文件。")
        else:
            file_path = self.file_label.cget("text")
            root = tk.Toplevel()
            app = data_audit.DataAuditApp(root, file_path)
            root.mainloop()

    def clean_file(self):
        if self.file_label.cget("text") == "请选择要清洗的文件":
            messagebox.showerror("尚未选择文件", "请选择 .xlsx, .xls 或 .csv 文件。")
        else:
            file_path = self.file_label.cget("text")
            root = tk.Toplevel()
            app = data_cleaning.DataCleaningApp(root, file_path)
            root.mainloop()

    def operation_file(self):
        file_path = self.file_label.cget("text")
        root = tk.Toplevel()
        app = operation_record.LogDisplayApp(root)
        root.mainloop()

    def know_more(self):
        knowledge_window = tk.Toplevel()
        knowledge_window.title("关于‘物’的数据")
        knowledge_window.geometry("450x250+800+500")
        content = scrolledtext.ScrolledText(knowledge_window, wrap=tk.WORD, font=("Arial", 14))
        content.pack(side='top', fill='both', expand=True)
        sample_text = '''设备运行数据：在工业生产中，针对生产设备所采集的反映其运行状态和相关参数的一系列数据，包括设备的运行状态（开机、关机、运行中、故障等）、运行参数（温度、压力、转速、电流、电压等）、故障报警信息以及维护记录等，是设备管理和维护的重要依据。
        物料数据：是描述工业生产中物料相关信息的数据集合，涵盖物料的基本属性（名称、规格、型号、批次等）、库存数量、出入库记录以及质量检测数据等，用于实现物料的有效管理和质量控制。
        产品数据：指在工业生产过程中，与产品本身相关的各种数据，包括产品的设计参数、生产工艺参数、质量检测数据以及产品序列号等，是确保产品质量和实现产品全生命周期追溯的关键数据。'''
        content.insert(tk.END, sample_text)
        content.config(state='disabled')

    def back(self):
        self.root.destroy()
        main_interface.main_interface()


if __name__ == "__main__":
    root = tk.Tk()
    app = ThingsData(root)
    root.mainloop()