# 导入所需的模块
import re
import threading
import time

import wx
import wx.adv
import random
from threading import Thread
from PlayVoice import PlayVoice
from EditClass import EditClass
from EditStudents import EditStudents
from backup_json import BackUp
from loadConfig import LoadConfig
from Roulette import Roulette


# 定义一个窗口类，继承自wx.Frame
class MyFrame(wx.Frame):
    def __init__(self):
        self.t_flag = threading.Event()  # 用于暂停线程的标识
        self.t_running = threading.Event()  # 用于停止线程的标识
        self.classes_name = {'示例班级': ['学生1', '学生2', '学生3']}
        self.bj = BackUp(self)  # 用于序列化self.classes_name
        self.bj.get_back_up()
        self.lc = LoadConfig()  # 用于从config.ini加载和保存用户常用默认选项
        self.par = self.lc.getParser()

        # 调用父类的构造函数，设置窗口标题和大小
        super().__init__(None, title="Roll Call System", size=(600, 700))

        # 使用 `wx.EvtHandler.Bind()` 方法，
        # 绑定 `wx.EVT_CLOSE`事件。这个事件会在用户关闭程序的主窗口时触发，可以在事件处理函数中执行一些自定义的操作，比如询问用户是否保存修改、释放一些内存等。
        self.Bind(wx.EVT_CLOSE, self.on_close)  # 绑定关闭事件

        # 设置窗口居中显示
        self.Center()
        # 创建一个面板，作为窗口的容器
        panel = wx.Panel(self)

        self.label_model = wx.StaticText(panel, label="请选择播音员：")

        self.choices_hardware = ['cuda', 'cpu']
        self.pv = PlayVoice(self.choices_hardware[0])

        self.charater = self.pv.get_characters()
        self.choice_char = wx.Choice(panel, choices=self.charater)
        if len(self.charater) >= 1:
            # 找出self.par['speed']对应的选项
            char_index = self.charater.index(self.par['character'])
            self.choice_char.SetSelection(char_index)
            self.pv.initTTS(self.choice_char.GetString(0))
        self.choice_char.Bind(wx.EVT_CHOICE, self.choseCharacter)  # 选择演员

        # self.label_speed = wx.StaticText(panel, label="请选择语速：    ")
        # l1 = ["1."+str(i) for i in range(0, 10)]
        # l2 = ["2." + str(i) for i in range(0, 10)]
        # self.speed = l1+l2
        # self.speed.append('3.0')
        # self.choice_speed = wx.Choice(panel, choices=self.speed)
        # # 找出self.par['speed']对应的选项
        # speed_index = self.speed.index(self.par['speed'])
        # self.choice_speed.SetSelection(speed_index)
        # self.choice_speed.Bind(wx.EVT_CHOICE, self.choseSpeed)  # 选择语速

        # 创建一个静态文本，显示提示信息
        self.label_hardware = wx.StaticText(panel, label="CPU或GPU合成音频：")
        self.choice_hardware = wx.Choice(panel, choices=self.choices_hardware)
        self.choice_hardware.SetSelection(int(self.par['hardware']))
        self.choice_hardware.Bind(wx.EVT_CHOICE, self.choseHardware)  # 选择音频合成设备

        self.label_sound_devices = wx.StaticText(panel, label="选择音频播放设备：  ")
        choices_sound_devices = self.pv.get_devices()
        self.choice_sound_devices = wx.Choice(panel, choices=choices_sound_devices)
        self.choice_sound_devices.Bind(wx.EVT_CHOICE, self.choseSoundDevice)  # 选择班级的行为
        if len(choices_sound_devices) >= 1:
            self.choice_sound_devices.SetSelection(0)
            self.chosen_device_index = 0
            # 音频输出设备
            sounddevice_item_index = self.choice_sound_devices.GetSelection()
            sounddevice_name = self.choice_sound_devices.GetString(sounddevice_item_index)
            parten = r'(.) .*'
            res = re.search(parten, sounddevice_name)
            index = res.group(1)
            self.chosen_device_index = int(index)
        else:
            print("error:没有可用的音频设备！")

        self.label_classes = wx.StaticText(panel, label="请选择班级：")
        self.choices_classes = list(self.classes_name.keys())  # 所有班级
        # print("self.choices_classes", self.choices_classes)
        self.choice_classes = wx.Choice(panel, choices=self.choices_classes)
        self.choice_classes.Bind(wx.EVT_CHOICE, self.choseClass)  # 选择班级的行为
        self.no_class = False
        if len(self.choices_classes) >= 1:
            class_index = 0
            if self.par['chosenclass'] in self.choices_classes:
                class_index = self.choices_classes.index(self.par['chosenclass'])
            else:
                self.par['chosenclass'] = self.choices_classes[0]
            self.choice_classes.SetSelection(class_index)
            self.chosen_class_index = class_index
        else:
            self.no_class = True
        self.ec = EditClass(self)  # 编辑班级的窗口

        # 分割线
        self.line0 = wx.StaticLine(panel, style=wx.LI_HORIZONTAL, size=(300, 5))  # size:长，宽

        # print(self.choice_classes.GetString(0))
        self.button_classes = wx.Button(panel, label="编辑班级")
        self.button_classes.Bind(wx.EVT_BUTTON, self.edit_classes)
        self.button_class = wx.Button(panel, label="编辑学生")
        self.button_class.Bind(wx.EVT_BUTTON, self.edit_students)
        self.es = EditStudents(self)  # 编辑学生的窗口

        self.label_class = wx.StaticText(panel, label="请选择学生：")
        class_stus = []
        if self.no_class is False:
            class_stus = self.classes_name[self.choices_classes[self.chosen_class_index]]
        self.choice_class = wx.Choice(panel, choices=class_stus)
        self.no_students = False
        if self.no_class is False and len(class_stus) >= 1:
            self.choice_class.SetSelection(0)
        else:
            self.no_students = True
        self.button_stu = wx.Button(panel, label="喊他")
        self.button_stu.Bind(wx.EVT_BUTTON, self.call_stu)

        # 喊话一个学生
        self.label_stu0 = wx.StaticText(panel, label="要喊的话：    ")
        self.input_stu = wx.TextCtrl(panel, style=wx.TEXT_ATTR_LINE_SPACING)
        self.button_stu0 = wx.Button(panel, label="喊他")
        self.button_stu0.Bind(wx.EVT_BUTTON, self.call_stu_words)

        # 班级喊话
        self.label_text = wx.StaticText(panel, label="请输入：")
        self.input_text = wx.TextCtrl(panel, size=(50, 20), style=wx.TE_MULTILINE)  # wx.TEXT_ATTR_LINE_SPACING不会多行显示style=wx.TE_MULTILINE`或者`style=wx.TE_WORDWRAP
        self.button_text = wx.Button(panel, label="班级喊话 ")
        self.button_text.Bind(wx.EVT_BUTTON, self.call_all_words)

        # 分割线
        self.line1 = wx.StaticLine(panel, style=wx.LI_HORIZONTAL, size=(300, 5))  # size:长，宽

        self.label_pause = wx.StaticText(panel, label="名字之间停顿时间间隔: ")
        pause_time = [str(i) for i in range(1, 6)]
        self.choice_pause = wx.Choice(panel, choices=pause_time)
        pause_index = int(self.par['pause'])-1
        self.choice_pause.SetSelection(pause_index)
        self.pause_time = int(self.choice_pause.GetString(self.choice_pause.GetSelection()))
        self.choice_pause.Bind(wx.EVT_CHOICE, self.chosePause)  # 选择时间间隔

        self.label_students = wx.StaticText(panel, label="请选择随机抽取的人数: ")
        self.choice_random = []
        if len(self.choices_classes) >= 1:
            chosen_class = self.choice_classes.GetString(self.choice_classes.GetSelection())
            student_num = self.classes_name[chosen_class]
            if len(student_num) >= 1:
                student_choices = range(1, len(student_num)+1)
                self.choice_random = ["{}".format(i) for i in student_choices]
            else:
                print("没有学生")
        self.choice_students = wx.Choice(panel, choices=self.choice_random)
        self.choice_students.SetSelection(0)
        self.button_students = wx.Button(panel, label="开始点名")
        self.button_students.Bind(wx.EVT_BUTTON, self.call_stus_random)

        self.button_lucky = wx.Button(panel, label="随机挑选一个幸运儿")
        self.button_lucky.Bind(wx.EVT_BUTTON, self.luck_one)

        self.label_random = wx.StaticText(panel, label="随机顺序点名整个班级  ")
        self.button_random = wx.Button(panel, label="开始点名")
        self.button_random.Bind(wx.EVT_BUTTON, self.call_all_stus_random)

        self.label_all = wx.StaticText(panel, label="名单顺序点名整个班级  ")
        self.button_all = wx.Button(panel, label="开始点名")
        self.button_all.Bind(wx.EVT_BUTTON, self.call_all_stus)

        self.button_pause = wx.Button(panel, label="暂停点名")
        self.button_pause.Bind(wx.EVT_BUTTON, self.call_pause)
        self.button_resume = wx.Button(panel, label="继续点名")
        self.button_resume.Bind(wx.EVT_BUTTON, self.call_resume)
        self.button_stop = wx.Button(panel, label="停止点名")
        self.button_stop.Bind(wx.EVT_BUTTON, self.call_stop)

        self.label_log = wx.StaticText(panel, label="准备就绪！")

        # 分割线
        self.line2 = wx.StaticLine(panel, style=wx.LI_HORIZONTAL, size=(300, 5))  # size:长，宽

        # 超链接
        self.label_info0 = wx.StaticText(panel, label="@云舒于野")
        # self.hyper_link0 = wx.lib.awg.HyperlinkCtrl(self.panel, id=wx.ID_ANY, label="github", url="https://github.com/yunshu-drwells?tab=repositories")
        # self.hyper_link1 = wx.lib.awg.HyperlinkCtrl(self.panel, id=wx.ID_ANY, label="gitee", url="https://github.com/yunshu-drwells?tab=repositories")
        # self.hyper_link2 = wx.lib.awg.HyperlinkCtrl(self.panel, id=wx.ID_ANY, label="bilibili", url="https://github.com/yunshu-drwells?tab=repositories")
        self.hyper_link0 = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="github",
                                                    url="https://github.com/yunshu-drwells/Roll-call-system.git")
        self.hyper_link1 = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="gitee",
                                                    url="https://gitee.com/yhviyr/Roll-call-system")
        self.hyper_link2 = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="bilibili",
                                                    url="https://github.com/yunshu-drwells?tab=repositories")

        # github gitee bilibili
        # 鸣谢vits
        # 本项目派蒙语音音色模型所有权归原神所有 禁止用于商业用途 仅限于交流学习
        # 如果想增加自己的角色模型需要自行炼丹
        # 使用GPU合成音频，至少需要一张Nvidia显卡并且cuda>=11.8
        # 在TTS/models中新建一个文件夹，文件夹支持中英文命名，文件夹里面需包含*.json和*.pth两个文件，启动软件会自动加载模型


        # 创建一个水平方向的盒子布局管理器，添加静态文本和下拉列表框，并设置间距和对齐方式
        hbox0_0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0_0.Add(self.label_model, 0, wx.EXPAND | wx.ALL, 5)
        hbox0_0.Add(self.choice_char, 100, wx.EXPAND | wx.ALL, 5)

        # hbox0_0_1 = wx.BoxSizer(wx.HORIZONTAL)
        # hbox0_0_1.Add(self.label_speed, 0, wx.EXPAND | wx.ALL, 5)
        # hbox0_0_1.Add(self.choice_speed, 100, wx.EXPAND | wx.ALL, 5)

        hbox0_1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0_1.Add(self.label_hardware, 0, wx.EXPAND | wx.ALL, 5)
        hbox0_1.Add(self.choice_hardware, 100, wx.EXPAND | wx.ALL, 5)

        hbox0_2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0_2.Add(self.label_sound_devices, 0, wx.EXPAND | wx.ALL, 5)
        hbox0_2.Add(self.choice_sound_devices, 100, wx.EXPAND | wx.ALL, 5)

        hbox0_3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0_3.Add(self.line0, 100, wx.EXPAND | wx.ALL, 5)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.label_classes, 0, wx.EXPAND | wx.ALL, 5)
        hbox1.Add(self.choice_classes, 80, wx.EXPAND | wx.ALL, 5)
        hbox1.Add(self.button_classes, 80, wx.EXPAND | wx.ALL, 5)
        hbox1.Add(self.button_class, 80, wx.EXPAND | wx.ALL, 5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.label_class, 0, wx.EXPAND | wx.ALL, 5)
        hbox2.Add(self.choice_class, 80, wx.EXPAND | wx.ALL, 5)
        hbox2.Add(self.button_stu, 80, wx.EXPAND | wx.ALL, 5)
        hbox2_0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2_0.Add(self.label_stu0, 0, wx.EXPAND | wx.ALL, 5)
        hbox2_0.Add(self.input_stu, 80, wx.EXPAND | wx.ALL, 5)
        hbox2_0.Add(self.button_stu0, 80, wx.EXPAND | wx.ALL, 5)
        hbox2_1 = wx.BoxSizer(wx.VERTICAL)
        hbox2_1.Add(self.label_text, 0, wx.EXPAND | wx.ALL, 5)
        hbox2_1.Add(self.input_text, 15, wx.EXPAND | wx.ALL, 5)
        hbox2_1.Add(self.button_text, 5, wx.EXPAND | wx.ALL, 5)

        hbox2_2 = wx.BoxSizer(wx.VERTICAL)
        hbox2_2.Add(self.line1, 100, wx.EXPAND | wx.ALL, 5)

        hbox2_3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2_3.Add(self.label_pause, 0, wx.EXPAND | wx.ALL, 5)
        hbox2_3.Add(self.choice_pause, 80, wx.EXPAND | wx.ALL, 5)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.label_students, 0, wx.EXPAND | wx.ALL, 5)
        hbox3.Add(self.choice_students, 80, wx.EXPAND | wx.ALL, 5)
        hbox3.Add(self.button_students, 80, wx.EXPAND | wx.ALL, 5)

        hbox3_1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3_1.Add(self.button_lucky, 80, wx.EXPAND | wx.ALL, 5)


        hbox3_0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3_0.Add(self.label_all, 0, wx.EXPAND | wx.ALL, 5)
        hbox3_0.Add(self.button_all, 70, wx.EXPAND | wx.ALL, 5)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(self.label_random, 0, wx.EXPAND | wx.ALL, 5)
        hbox4.Add(self.button_random, 70, wx.EXPAND | wx.ALL, 5)

        hbox4_1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4_1.Add(self.button_pause, 70, wx.EXPAND | wx.ALL, 5)
        hbox4_1.Add(self.button_resume, 70, wx.EXPAND | wx.ALL, 5)
        hbox4_1.Add(self.button_stop, 70, wx.EXPAND | wx.ALL, 5)

        hbox4_0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4_0.Add(self.label_log, 0, wx.EXPAND | wx.ALL, 5)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.Add(self.line2, 100, wx.EXPAND | wx.ALL, 5)

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6.Add(self.label_info0, 0, wx.EXPAND | wx.ALL, 5)
        hbox6.Add(self.hyper_link0, 70, wx.EXPAND | wx.ALL, 5)
        hbox6.Add(self.hyper_link1, 70, wx.EXPAND | wx.ALL, 5)
        hbox6.Add(self.hyper_link2, 70, wx.EXPAND | wx.ALL, 5)


        # 创建一个垂直方向的盒子布局管理器，添加水平布局管理器和按钮，并设置间距和对齐方式
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox0_0, 0, wx.EXPAND)
        # vbox.Add(hbox0_0_1, 0, wx.EXPAND)
        vbox.Add(hbox0_1, 0, wx.EXPAND)
        vbox.Add(hbox0_2, 0, wx.EXPAND)
        vbox.Add(hbox0_3, 0, wx.EXPAND)
        vbox.Add(hbox1, 0, wx.EXPAND)
        vbox.Add(hbox2, 0, wx.EXPAND)
        vbox.Add(hbox2_0, 0, wx.EXPAND)
        vbox.Add(hbox2_1, 0, wx.EXPAND)
        vbox.Add(hbox2_2, 0, wx.EXPAND)
        vbox.Add(hbox2_3, 0, wx.EXPAND)
        vbox.Add(hbox3, 0, wx.EXPAND)
        vbox.Add(hbox3_1, 0, wx.EXPAND)
        vbox.Add(hbox3_0, 0, wx.EXPAND)
        vbox.Add(hbox4, 0, wx.EXPAND)
        vbox.Add(hbox4_1, 0, wx.EXPAND)
        vbox.Add(hbox4_0, 0, wx.EXPAND)
        vbox.Add(hbox5, 0, wx.EXPAND)
        vbox.Add(hbox6, 0, wx.EXPAND)

        # 设置面板的布局管理器为垂直布局管理器
        panel.SetSizer(vbox)
        # 定义一个方法，用于处理按钮的点击事件

    def choseCharacter(self, event):
        char_index = self.choice_char.GetSelection()
        char = self.choice_char.GetString(char_index)
        self.par['character'] = char
        self.pv.initTTS(char)

    # def choseSpeed(self, event):
    #     speed_index = self.choice_speed.GetSelection()
    #     speed = self.choice_speed.GetString(speed_index)
    #     self.par['speed'] = speed
    #     # 重新构造tts对象
    #     char_index = self.choice_char.GetSelection()
    #     char = self.choice_char.GetString(char_index)
    #     self.pv.change_speed(char, speed)

    def choseHardware(self, event):
        chosen_hardware_index = self.choice_hardware.GetSelection()
        self.par['hardware'] = str(chosen_hardware_index)
        chosen_hardware = self.choices_hardware[chosen_hardware_index]
        # print(chosen_hardware)
        self.pv.set_hardware(chosen_hardware)

    # 刷新随机人数列表
    def refresh_random_list(self):
        if self.no_class is not True:
            chosen_class = self.choices_classes[self.chosen_class_index]
            students = self.classes_name[chosen_class]
            student_choices = range(1, len(students) + 1)
            self.choice_random = ["{}".format(i) for i in student_choices]
            # 刷新主窗口班级列表
            self.choice_students.SetItems(self.choice_random)
            if len(self.choice_random) >= 1:
                self.choice_students.SetSelection(0)
        else:
            self.choice_students.SetItems([])

    def choseClass(self, event):
        item_index = self.choice_classes.GetSelection()
        self.chosen_class_index = item_index
        chosen_class = self.choices_classes[self.chosen_class_index]
        self.par['chosenclass'] = self.choice_classes.GetString(item_index)
        # 刷新主窗口学生列表
        class_stus = self.classes_name[chosen_class]
        self.choice_class.SetItems(class_stus)
        if len(self.choices_classes) >= 1 and len(class_stus) >= 1:
            self.choice_class.SetSelection(0)
        # 刷新随机人数列表
        self.refresh_random_list()

    def chosePause(self, event):
        self.pause_time = int(self.choice_pause.GetString(self.choice_pause.GetSelection()))
        self.par['pause'] = self.pause_time

    def choseSoundDevice(self, event):
        # 获取选择的输出设备
        sounddevice_item_index = self.choice_sound_devices.GetSelection()
        sounddevice_name = self.choice_sound_devices.GetString(sounddevice_item_index)
        # print(sounddevice_name)
        parten = r'(.) .*'
        res = re.search(parten, sounddevice_name)
        index = res.group(1)
        # print(index)
        self.chosen_device_index = int(index)

    def edit_classes(self, event):
        self.ec.show_windows()

    def delete_classes(self, will_delete_classes):
        # 遍历元组will_delete_classes，删除字典self.classes_name
        for i in will_delete_classes:
            if i in self.classes_name.keys():
                del self.classes_name[i]
        # 更新self.choices_classes
        self.choices_classes = list(self.classes_name.keys())
        if self.par['chosenclass'] == will_delete_classes:
            if len(self.choices_classes) >= 1:
                self.par['chosenclass'] = self.choices_classes[0]
                self.no_class = False
            else:
                self.par['chosenclass'] = ""
                self.no_class = True
        # 刷新主窗口班级列表
        self.choice_classes.SetItems(self.choices_classes)
        if len(self.choices_classes) >= 1:
            self.choice_classes.SetSelection(0)
            self.chosen_class_index = 0
        else:
            self.no_class = True
        self.bj.write_back_up()
        # 刷新随机人数列表
        self.refresh_random_list()

    def add_classes(self, new_class):
        self.classes_name[new_class] = []
        # 更新self.choices_classes
        self.choices_classes = list(self.classes_name.keys())
        if len(self.choices_classes) >= 1:
            self.no_class = False
        # 刷新主窗口班级列表
        self.choice_classes.SetItems(self.choices_classes)
        self.choice_classes.SetSelection(0)
        self.chosen_class_index = 0
        self.bj.write_back_up()
        # 刷新随机人数列表
        self.refresh_random_list()

    def edit_students(self, event):
        self.es.show_windows()

    def delete_students(self, will_delete_stu):
        chosen_class = self.choices_classes[self.chosen_class_index]
        # 通过key删除指定val
        before = list(self.classes_name[chosen_class])
        after = []
        for i in before:
            if i not in will_delete_stu:
                after.append(i)
        self.classes_name[chosen_class] = after
        # 刷新主窗口学生列表
        class_stus = self.classes_name[chosen_class]
        self.choice_class.SetItems(class_stus)
        if len(self.choices_classes) >= 1 and len(class_stus) >= 1:
            self.choice_class.SetSelection(0)
        self.bj.write_back_up()
        # 刷新随机人数列表
        self.refresh_random_list()

    def add_students(self, new_stuent):
        chosen_class = self.choices_classes[self.chosen_class_index]
        # 通过key添加val
        stus = list(self.classes_name[chosen_class])
        stus.append(new_stuent)
        self.classes_name[chosen_class] = stus
        # 刷新主窗口学生列表
        class_stus = self.classes_name[chosen_class]
        self.choice_class.SetItems(class_stus)
        if len(self.choices_classes) >= 1 and len(class_stus) >= 1:
            self.choice_class.SetSelection(0)
        self.bj.write_back_up()
        # 刷新随机人数列表
        self.refresh_random_list()

    # 有班级并且有学生被选中
    def stu_was_chosen(self):
        if self.no_class is False:
            chosen_class = self.choices_classes[self.chosen_class_index]
            students = self.classes_name[chosen_class]
            if len(students) >= 1:
                return True

    def call_stu(self, event):
        try:
            t = Thread(target=self.call_stu_)
            t.daemon = True
            t.start()
        except:
            print("find_pwd Error: unable to start thread")

    def call_stu_(self):
        if self.stu_was_chosen():
            # 获取学生姓名
            stu_item_index = self.choice_class.GetSelection()
            stu_name = self.choice_class.GetString(stu_item_index)
            # print(stu_name)
            # 喊话
            self.pv.play_voice(stu_name, self.chosen_device_index)
        else:
            self.label_log.SetLabel("error0: 没有学生被选中")
            print("没有学生被选中")

    def call_stu_words(self, event):
        try:
            t = Thread(target=self.call_stu_words_)
            t.daemon = True
            t.start()
        except:
            print("find_pwd Error: unable to start thread")

    def call_stu_words_(self):
        if self.stu_was_chosen():
            # 获取学生姓名
            stu_item_index = self.choice_class.GetSelection()
            stu_name = self.choice_class.GetString(stu_item_index)
            # print(stu_name)
            words = stu_name+self.input_stu.GetLineText(0)
            # 喊话
            self.pv.play_voice(words, self.chosen_device_index)
        else:
            self.label_log.SetLabel("error1: 没有学生被选中")
            print("没有学生被选中")

    def call_all_words(self, event):
        try:
            t = Thread(target=self.call_all_words_)
            t.daemon = True
            t.start()
        except:
            print("find_pwd Error: unable to start thread")

    def call_all_words_(self):
        # 获取文本
        # words = self.input_text.GetLineText(0)  # 获取指定行号的文本
        words = self.input_text.GetValue()  # 获取指定行号的文本
        # 喊话
        self.pv.play_voice(words, self.chosen_device_index)

    def generate_random_names(self, nums):
        chosen_class = self.choices_classes[self.chosen_class_index]
        students = self.classes_name[chosen_class]
        # 生成nums个随机名单列表返回
        res = []
        chosen_stu = random.sample(range(0, len(students)), nums)  # 从学生中选出nums个
        for i in chosen_stu:
            res.append(students[i])
        return res

    def call_stus_random(self, event):
        try:
            t = Thread(target=self.call_stus_random_)
            t.daemon = True
            t.start()
        except:
            print("find_pwd Error: unable to start thread")

    def call_stus_random_(self):
        if self.stu_was_chosen():
            nums_index = self.choice_students.GetSelection()
            nums = self.choice_students.GetString(nums_index)  # 要随机点名的人数
            stu_names = self.generate_random_names(int(nums))  # 获得随机nums个学生的随机名单
            self.pv.roll_call(stu_names, self.chosen_device_index, self.pause_time)
        else:
            self.label_log.SetLabel("error2: 没有学生被选中")
            print("没有学生被选中")

    def call_pause(self, event):
        self.t_flag.clear()  # 设置为False, 让线程阻塞

    def call_resume(self, event):
        self.t_flag.set()  # 设置为True, 让线程停止阻塞

    def call_stop(self, event):
        self.t_flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.t_running.clear()  # 设置为False

    def luck_one(self, event):
        chosen_class = self.choices_classes[self.chosen_class_index]
        students = self.classes_name[chosen_class]
        self.r = Roulette('抽取一个幸运儿', students)
        self.r.start()
        self.r.draw_wheel()
        # 播放hhhhh的音频
        # self.pv.play_voice_audio_file('./sources/ohhhh.wav', self.chosen_device_index)
        # self.pv.play_voice_('./sources/ohhhh.wav')

    def call_all_stus_random(self, event):
        try:
            t_r = Thread(target=self.call_all_stus_random_)
            t_r.daemon = True
            # 通过标志位来控制线程阻塞、继续和终止
            self.t_running.set()  # 将running设置为True
            self.t_flag.set()  # 将flag设置为True
            t_r.start()
            # 如果点击了暂停按钮->阻塞子线程
        except:
            print("find_pwd Error: unable to start thread")

    def call_all_stus_random_(self):
        if self.no_class is not True:
            chosen_class = self.choices_classes[self.chosen_class_index]
            students = self.classes_name[chosen_class]
            students_num = len(students)
            if students_num >= 1:
                chosen_class = self.choices_classes[self.chosen_class_index]
                students = self.classes_name[chosen_class]
                stu_names = self.generate_random_names(len(students))
                if students_num >= 1:
                    chosen_class = self.choices_classes[self.chosen_class_index]
                    students = self.classes_name[chosen_class]
                    for i in range(len(students)):
                        if self.t_running.is_set():
                            if i == (len(students) - 1):
                                self.t_running.clear()
                            self.t_flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
                            self.pv.roll_call(students[i], self.chosen_device_index, self.pause_time)
                # self.pv.roll_call_list(stu_names, self.chosen_device_index, self.pause_time)
            else:
                self.label_log.SetLabel("error: 这个班级没有学生")
                print("这个班级没有学生")
        else:
            self.label_log.SetLabel("error: 没有任何班级，请通过编辑班级->添加班级")
            print("这个班级没有学生")

    def call_all_stus(self, event):
        try:
            t_a = Thread(target=self.call_all_stus_)
            t_a.daemon = True
            # 通过标志位来控制线程阻塞、继续和终止
            self.t_running.set()  # 将running设置为True
            self.t_flag.set()  # 将flag设置为True
            t_a.start()
        except:
            print("find_pwd Error: unable to start thread")

    def call_all_stus_(self):
        if self.no_class is not True:
            chosen_class = self.choices_classes[self.chosen_class_index]
            students = self.classes_name[chosen_class]
            students_num = len(students)
            if students_num >= 1:
                chosen_class = self.choices_classes[self.chosen_class_index]
                students = self.classes_name[chosen_class]
                for i in range(len(students)):
                    if self.t_running.is_set():
                        if i == (len(students)-1):
                            self.t_running.clear()
                        self.t_flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
                        self.pv.roll_call(students[i], self.chosen_device_index, self.pause_time)
                # self.pv.roll_call_list(students, self.chosen_device_index, self.pause_time)
            else:
                self.label_log.SetLabel("error: 这个班级没有学生")
                print("这个班级没有学生")
        else:
            self.label_log.SetLabel("error: 没有任何班级，请通过编辑班级->添加班级")
            print("这个班级没有学生")

    def on_close(self, event):
        print("on_close, The frame is closing")
        # 在这里执行一些自定义的操作
        self.lc.saveParser()
        event.Skip()  # 让默认的关闭行为继续执行s


# 定义一个应用程序类，继承自wx.App
class MyApp(wx.App):
    def OnInit(self):
        # 创建窗口对象并显示
        frame = MyFrame()
        frame.Show()
        return True

    def loop(self):
        print("hello")

    # # 重构 def closeEvent(self, event)——在UI线程销毁的时候，需要把后台线程也销毁掉
    # def closeEvent(self, event):
    #     # self.stop_event.set()
    #     print("程序结束就会执行的方法！")
    #     sys.exit(app.exec_())
    #     print("程序结束就会执行的方法！")

    # 使用 `wx.App.OnExit()` 方法。这是一个虚拟方法，可以在子类中重写，以便在程序退出前执行一些清理或保存的操作。这个方法会在 `wx.App.MainLoop()` 结束后，但在销毁所有窗口和对象之前被调用¹
    def OnExit(self):
        print("OnExit, The app is exiting")
        # 在这里执行一些清理或保存的操作


# 如果是主模块，则运行应用程序对象的主循环
if __name__ == "__main__":
    app = MyApp()
    app.SetExitOnFrameDelete(True)  # SetExitOnFrameDelete(flag) 防止关闭UI界面，后台进程仍然运行
    app.MainLoop()
    # 使用 `wx.App.CleanUp()` 方法。这是一个静态方法，可以在程序退出前调用，以便释放 wxPython 分配的所有资源，包括图像、字体、画笔等。这个方法会在 `wx.App.OnExit()` 之后被调用²
    # app.CleanUp()

# 加密方式
'''
- **WEP**（Wired Equivalent Privacy）：这是最早的一种Wifi加密协议，它使用相同的密钥对数据进行加密和解密，属于对称加密¹。但是，由于WEP的密钥容易被破解，它已经被认为是不安全的，不建议使用²。
- **WPA**（Wi-Fi Protected Access）：这是一种改进的Wifi加密协议，它使用动态的密钥分配和认证机制，提高了数据的安全性。WPA有两个版本，分别是WPA-Personal（适用于个人和家庭用户）和WPA-Enterprise（适用于企业和组织用户）²。
- **WPA2**：这是WPA的升级版，它使用了更高级的加密算法（AES）和更强大的认证协议（802.1X），提供了更高的安全性。WPA2也有两个版本，分别是WPA2-Personal和WPA2-Enterprise²。
- **WPA3**：这是最新的一种Wifi加密协议，它在WPA2的基础上增加了更多的安全特性，例如更强的密码保护、更好的隐私保护、更高的加密强度等。WPA3同样有两个版本，分别是WPA3-Personal和WPA3-Enterprise³。
'''
