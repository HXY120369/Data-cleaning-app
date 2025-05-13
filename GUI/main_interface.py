import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from PIL import Image, ImageTk
import main_people
import main_things
from data_cleaning.GUI import main_business


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

# 创建主页面
def main_interface():
    main_window = tk.Tk()
    main_window.title("主界面")

    # 设置窗口居中
    window_width = 600
    window_height = 400
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    main_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    # 使用 ttk 样式
    style = ttk.Style(main_window)
    style.theme_use("clam")

    # 主内容Frame
    main_frame = ttk.Frame(main_window, padding="10", relief="ridge", borderwidth=2)
    main_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(main_frame, text="请选择你要清洗的数据类型", font=("Arial", 16))
    title_label.grid(row=0, column=1, pady=10)

    image_paths = ["images/image_people.png",
                   "images/image_things.png",
                   "images/image_business.png",]
    image1 = Image.open(image_paths[0])
    image2 = Image.open(image_paths[1])
    image3 = Image.open(image_paths[2])
    resized_image1 = image1.resize((110, 110))
    resized_image2 = image2.resize((110, 110))
    resized_image3 = image3.resize((110, 110))
    photo1 = ImageTk.PhotoImage(resized_image1)
    photo2 = ImageTk.PhotoImage(resized_image2)
    photo3 = ImageTk.PhotoImage(resized_image3)

    # 设置页面跳转
    def jump_to_page1():
        main_window.destroy()
        temp=tk.Tk()
        app = main_people.PeopleData(temp)
        temp.mainloop()
    def jump_to_page2():
        main_window.destroy()
        temp = tk.Tk()
        app = main_things.ThingsData(temp)
        temp.mainloop()
    def jump_to_page3():
        main_window.destroy()
        temp = tk.Tk()
        app = main_business.BusinessData(temp)
        temp.mainloop()


    # 创建 Button 组件并显示图像
    button_people = ttk.Button(main_frame, image=photo1, command=jump_to_page1)
    button_people.image = photo1
    button_people.grid(row=1, column=0, padx=30, pady=10)
    label_people = ttk.Label(main_frame, text="'人'的数据", font=("Arial", 15))
    label_people.grid(row=2, column=0, padx=30)

    button_things = ttk.Button(main_frame, image=photo2, command=jump_to_page2)
    button_things.image = photo2
    button_things.grid(row=1, column=1, padx=30, pady=10)
    label_things = ttk.Label(main_frame, text="'物'的数据", font=("Arial", 15))
    label_things.grid(row=2, column=1, padx=30)

    button_people = ttk.Button(main_frame, image=photo3, command=jump_to_page3)
    button_people.image = photo3
    button_people.grid(row=1, column=2, padx=30, pady=10)
    label_business = ttk.Label(main_frame, text="'业务'的数据", font=("Arial", 15))
    label_business.grid(row=2, column=2, padx=30)

    button_feedback = ttk.Button(main_frame, text="建议", command=feedback, width=8)
    button_feedback.grid(row=5, column=2, padx=30, pady=(30,15))

    button_exit = ttk.Button(main_frame, text="退出", command=main_window.destroy, width=8)
    button_exit.grid(row=6, column=2, padx=30)

    main_window.mainloop()

def feedback():
    feedback_window = tk.Toplevel()
    feedback_window.title("建议")

    # 设置窗口居中
    window_width = 500
    window_height = 300
    screen_width = feedback_window.winfo_screenwidth()
    screen_height = feedback_window.winfo_screenheight()
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    feedback_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    # 使用 ttk 样式
    style = ttk.Style(feedback_window)
    style.theme_use("clam")

    # 主内容Frame
    main_frame = ttk.Frame(feedback_window, padding="10", relief="ridge", borderwidth=2)
    main_frame.pack(fill="both", expand=True)

    label_contact = ttk.Label(main_frame, text="请输入您的联系方式：", font=("Arial", 14))
    label_contact.place(x=10, y=20)
    entry_contact = ttk.Entry(main_frame, width=29, font=("Arial", 16))
    entry_contact.place(x=180, y=20)
    feedback_label = ttk.Label(main_frame, text="请输入您对本软件的建议：", font=("Arial", 14))
    feedback_label.place(x=10, y=60)
    feedback_text = tk.Text(main_frame, width=29, height=7, font=("Arial", 16))
    feedback_text.place(x=180, y=60)

    def submit_feedback():
        contact = entry_contact.get()
        feedback = feedback_text.get("1.0", tk.END).strip()
        if contact == '':
            messagebox.showerror("提示", "请填写您的联系方式")
        elif feedback == '':
            messagebox.showerror("提示", "请填写完整的建议内容")
        else:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                insert_query = "INSERT INTO feedback (contact, advice) VALUES (%s, %s)"
                cursor.execute(insert_query, (contact, feedback))
                connection.commit()
            messagebox.showinfo("提示", "感谢您的宝贵意见！我们会尽快处理并将处理结果发送给您")
            feedback_window.destroy()

    submit_button = ttk.Button(main_frame, text="提交建议", command=submit_feedback, width=6)
    submit_button.place(x=285, y=205)
    exit_button = ttk.Button(main_frame, text="返回", command=feedback_window.destroy, width=6)
    exit_button.place(x=377, y=205)

    feedback_window.mainloop()


if __name__ == "__main__":
    main_interface()