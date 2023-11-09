
import tkinter as tk
import random
import math

class Roulette():
    def __init__(self, title, prizes):
        # 创建一个窗口对象
        self.window = tk.Tk()
        self.window.title(title)

        # 创建一个画布对象，用来绘制轮盘
        self.canvas = tk.Canvas(self.window, width=300, height=300)
        self.canvas.pack()

        # 创建一个标签对象，用来显示奖项名称和提示信息
        self.label = tk.Label(self.window, text="")
        self.label.pack()

        # 定义轮盘的颜色列表
        self.colors = ["red", "orange", "yellow", "green", "blue", "purple"]

        # 定义轮盘的奖项名称列表
        self.prizes = prizes

        # 定义轮盘的半径
        self.radius = 100

        # 定义轮盘的中心坐标
        self.center_x = 150
        self.center_y = 150

        # 定义轮盘的每个扇形的角度
        self.angle = 360 / len(self.prizes)

    # 定义一个函数，用来绘制轮盘
    def draw_wheel(self):
        # 定义轮盘的起始角度
        start_angle = 0

        # 遍历颜色列表，绘制轮盘的每个扇形
        for i in range(len(self.prizes)):
            # 计算扇形的结束角度
            end_angle = start_angle + self.angle

            # 计算扇形的弧度
            radians = (start_angle + end_angle) / 2 * 3.14 / 180

            # 计算扇形的文本坐标
            text_x = self.center_x + self.radius * 0.8 * math.cos(radians)
            text_y = self.center_y + self.radius * 0.8 * math.sin(radians)

            # 绘制扇形
            self.canvas.create_arc(self.center_x - self.radius, self.center_y - self.radius, self.center_x + self.radius, self.center_y + self.radius, start=start_angle, extent=self.angle, fill=self.colors[i % 6])

            # # 绘制文本
            # self.canvas.create_text(text_x, text_y, text=self.prizes[i])

            # 更新起始角度
            start_angle = end_angle

        # 遍历颜色列表，绘制轮盘的每个扇形
        for i in range(len(self.prizes)):
            # 计算扇形的结束角度
            end_angle = start_angle + self.angle

            # 计算扇形的弧度
            radians = (start_angle + end_angle) / 2 * 3.14 / 180

            # 计算扇形的文本坐标
            text_x = self.center_x + self.radius * 0.8 * math.cos(radians)
            text_y = self.center_y + self.radius * 0.8 * math.sin(radians)

            # 绘制文本
            self.canvas.create_text(text_x, text_y, text=self.prizes[i])

            # 更新起始角度
            start_angle = end_angle

        self.window.mainloop()


    # 定义一个函数，用来旋转轮盘
    def spin_wheel(self):
        # 随机生成一个旋转的角度
        spin_angle = random.randint(0, 360)

        # 旋转画布
        # canvas.rotate(spin_angle)
        self.canvas.create_text(100, 100, text='', angle=spin_angle)

        # 计算奖项编号
        prize_index = int((spin_angle // self.angle) % len(self.prizes))

        # 获取奖项名称
        prize = self.prizes[prize_index]

        # 显示奖项名称和提示信息
        self.label.config(text=f"恭喜 {prize} 成为幸运儿！")

    def start(self):
        # 创建一个按钮对象，用来触发旋转轮盘的函数
        button = tk.Button(self.window, text="开始抽奖", command=self.spin_wheel)
        button.pack()

if __name__ == "__main__":
    # # 创建一个按钮对象，用来触发旋转轮盘的函数
    # button = tk.Button(window, text="开始抽奖", command=spin_wheel)
    # button.pack()
    #
    # # 调用绘制轮盘的函数
    # draw_wheel()
    #
    # # 进入主循环
    # window.mainloop()
    prizes = ["iPhone 13", "iPad Pro", "AirPods", "MacBook Air", "Apple Watch", "谢谢参与"]
    r = Roulette("轮盘游戏", prizes)
    r.start()
    r.draw_wheel()