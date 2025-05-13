import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import main_interface
from PIL import Image, ImageTk

# 连接到 MySQL 数据库
def create_connection():
    try:
        connection = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "mm190322",
            database = "data_clean"
        )
        return connection
    except mysql.connector.Error as e:
        messagebox.showerror("数据库连接错误", f"错误信息：{e}")
        return None

# 窗口居中
def middle_set(location, width, height, window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    location[0] = x
    location[1] = y


def login():

    # 创建登录窗口
    login_window = tk.Tk()
    login_window.title("数据清洗工具")

    # 设置窗口居中
    location = [0, 0]
    window_width = 600
    window_height = 420
    middle_set(location, window_width, window_width, login_window)
    login_window.geometry(f"{window_width}x{window_height}+{location[0]}+{location[1]}")

    # 使用 ttk 样式
    style = ttk.Style()
    style.theme_use("clam")

    # 加载相应的图片
    image_path = ["images/data_collect.png",
                  "images/data_cleaning.png",
                  "images/data_analyze.png",
                  "images/arrow.png", ]

    # 主内容Frame
    main_frame = ttk.Frame(login_window)
    main_frame.pack(fill="both", expand=True)

    # 1.上方Frame，用于存在顶部文字信息
    top_frame = ttk.Frame(main_frame, padding="10", relief="ridge", borderwidth=2)
    top_frame.pack(side="top", fill="x", padx=10, pady=5)

    top_label = ttk.Label(top_frame, text="欢迎使用本数据清洗软件，在使用之前，请先登录", font=("Arial", 16))
    top_label.pack(side="left", padx=10)

    # 2.中部Frame，用于存放登录组件
    middle_frame = ttk.Frame(main_frame, padding="10", relief="ridge", borderwidth=2, width=300, height=200)
    middle_frame.pack(side='top', fill='x', padx=10, pady=5)

    # 用户名标签和输入框
    label_username = ttk.Label(middle_frame, text="用户名:", font=("Arial", 16))
    label_username.place(x=40, y=22)
    entry_username = ttk.Entry(middle_frame, font=("Arial", 18))
    entry_username.place(x=130, y=20)

    # 密码标签和输入框
    label_password = ttk.Label(middle_frame, text="密码:", font=("Arial", 16))
    label_password.place(x=40, y=75)
    entry_password = ttk.Entry(middle_frame, show="*", font=("Arial", 18))
    entry_password.place(x=130, y=73)

    # 密码显示按钮
    def toggle_button():
        if entry_password.cget('show') == '':
            entry_password.config(show="*")
            toggle_button.config(text="显示")
        else:
            entry_password.config(show='')
            toggle_button.config(text="隐藏")

    toggle_button = ttk.Button(middle_frame, text="显示",  command=toggle_button, width=5)
    toggle_button.place(x=365, y=70)

    # 中部图片插入
    image_middle = Image.open(image_path[1]).resize((100, 100))
    photo_middle = ImageTk.PhotoImage(image_middle)
    label_image = ttk.Label(middle_frame, image=photo_middle)
    label_image.image = photo_middle
    label_image.place(x=440, y=30)

    # 设置一个额外的组件存放登录、注册和退出按钮
    def login_button():
        username = entry_username.get()
        password = entry_password.get()
        if not username or not password:
            messagebox.showerror("输入错误", "用户名和密码不能为空！")
            return
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            select_query = "SELECT * FROM users WHERE user_name = %s AND user_password = %s"
            cursor.execute(select_query, (username, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            if user:
                messagebox.showinfo("登录成功", "登录成功！")
                login_window.destroy()
                main_interface.main_interface()
            else:
                messagebox.showerror("登录失败", "用户名或密码错误，请重试。")

    login_button = ttk.Button(middle_frame, text="登录", width=8, command=login_button)
    login_button.place(x=40, y=143)

    register_button = ttk.Button(middle_frame, text="注册", width=8, command=register)
    register_button.place(x=160, y=143)

    exit_button = ttk.Button(middle_frame, text="退出", width=8, command=exit)
    exit_button.place(x=280, y=143)

    # 添加一个副标题
    sub_title = ttk.Label(main_frame, text="数据处理流程", font=("Arial", 14))
    sub_title.pack(side='top', fill='x', padx=10, pady=3)

    # 底部Frame，用于存放图片
    bottom_frame = ttk.Frame(main_frame, padding="10", relief="ridge", borderwidth=2)
    bottom_frame.pack(side='top', fill='x', padx=10)

    # 插入底部响应的各个图片
    image1 = Image.open(image_path[0]).resize((60, 60))
    image2 = Image.open(image_path[1]).resize((70, 70))
    image3 = Image.open(image_path[2]).resize((70, 70))
    image4 = Image.open(image_path[3]).resize((80, 40))
    photo1 = ImageTk.PhotoImage(image1)
    photo2 = ImageTk.PhotoImage(image2)
    photo3 = ImageTk.PhotoImage(image3)
    photo4 = ImageTk.PhotoImage(image4)
    label1 = ttk.Label(bottom_frame, image=photo1)
    label1.image = photo1
    label1.grid(row=0, column=0, padx=10)
    label4 = ttk.Label(bottom_frame, image=photo4)
    label4.image = photo4
    label4.grid(row=0, column=1)
    label2 = ttk.Label(bottom_frame, image=photo2)
    label2.image = photo2
    label2.grid(row=0, column=2)
    label5 = ttk.Label(bottom_frame, image=photo4)
    label5.image = photo4
    label5.grid(row=0, column=3)
    label3 = ttk.Label(bottom_frame, image=photo3)
    label3.image = photo3
    label3.grid(row=0, column=4)

    label6 = ttk.Label(bottom_frame, text="数据采集", font=("Arial", 16))
    label6.grid(row=1, column=0)
    label7 = ttk.Label(bottom_frame, text="数据清洗", font=("Arial", 16))
    label7.grid(row=1, column=2)
    label8 = ttk.Label(bottom_frame, text="数据分析", font=("Arial", 16))
    label8.grid(row=1, column=4)

    login_window.mainloop()

def register():

    # 创建用户注册窗口
    register_window = tk.Tk()
    register_window.title("账户创建")

    # 设置窗口居中
    location = [0, 0]
    window_width = 500
    window_height = 300
    middle_set(location, window_width, window_height, register_window)
    register_window.geometry(f"{window_width}x{window_height}+{location[0]}+{location[1]}")

    # 使用 ttk 样式
    style = ttk.Style(register_window)
    style.theme_use("clam")

    # 主内容Frame
    main_frame = ttk.Frame(register_window, padding="10", relief="ridge", borderwidth=2)
    main_frame.pack(fill="both", expand=True)

    # 用户名标签和输入框
    label_username = ttk.Label(main_frame, text="用户名:", font=("Arial", 16))
    label_username.grid(row=0, column=0, padx=10, pady=10)
    entry_username = ttk.Entry(main_frame, font=("Arial", 18))
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    # 密码标签和输入框
    label_password1 = ttk.Label(main_frame, text="密码:", font=("Arial", 16))
    label_password1.grid(row=1, column=0, padx=10, pady=10)
    entry_password1 = ttk.Entry(main_frame, show="*", font=("Arial", 18))
    entry_password1.grid(row=1, column=1, padx=10, pady=10)

    # 确认密码标签和输入框
    label_password2 = ttk.Label(main_frame, text="确认密码:", font=("Arial", 16))
    label_password2.grid(row=2, column=0, padx=10, pady=10)
    entry_password2 = ttk.Entry(main_frame, show="*", font=("Arial", 18))
    entry_password2.grid(row=2, column=1, padx=10, pady=10)

    def toggle_button1():
        if entry_password1.cget('show') == '':
            entry_password1.config(show="*")
            toggle_button1.config(text="显示")
        else:
            entry_password1.config(show='')
            toggle_button1.config(text="隐藏")

    def toggle_button2():
        if entry_password2.cget('show') == '':
            entry_password2.config(show="*")
            toggle_button2.config(text="显示")
        else:
            entry_password2.config(show='')
            toggle_button2.config(text="隐藏")

    toggle_button1 = ttk.Button(main_frame, text="显示", command=toggle_button1, width=6)
    toggle_button1.grid(row=1, column=2, pady=10)

    toggle_button2 = ttk.Button(main_frame, text="显示", command=toggle_button2, width=6)
    toggle_button2.grid(row=2, column=2, pady=10)

    def register_button():
        username = entry_username.get()
        password1 = entry_password1.get()
        password2 = entry_password2.get()
        if password1 == '' or password2 == '' or username == '':
            messagebox.showerror("注册失败", "用户名或密码不能为空")
            return
        if password1 != password2:
            messagebox.showerror("注册失败", "两次输入的密码不一致")
            return

        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            insert_query = "INSERT INTO users (user_name, user_password) VALUES (%s, %s)"
            try:
                cursor.execute(insert_query, (username, password1))
                connection.commit()
                messagebox.showinfo("注册成功", "注册成功！")
                register_window.destroy()
            except mysql.connector.Error as e:
                if e.errno == 1062: # 若用户名已经存在
                    messagebox.showerror("注册失败", "该用户名已被注册，请选择其他用户名。")
                else:
                    messagebox.showerror("注册时出错", f"错误信息：{e}")


    # 确认注册按钮
    button_login = ttk.Button(main_frame, text="确认注册", command=register_button)
    button_login.grid(row=3, column=1, pady=10)
    button_back = ttk.Button(main_frame, text="返回", command=register_window.destroy, width=6)
    button_back.grid(row=3, column=2, pady=10)

    register_window.mainloop()


if __name__ == "__main__":
    login()
