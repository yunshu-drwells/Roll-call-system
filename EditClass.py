import wx


class EditClass(wx.Frame):

    def __init__(self, mc):
        self.mc = mc

    def show_windows(self):
        # 子窗口0
        self.sub_window0 = wx.Frame(None, title="编辑班级")
        self.sub_window0.SetSize(500, 320)
        self.sub_window0.Hide()

        # 设置窗口居中显示
        self.sub_window0.Center()
        # 创建一个面板，作为窗口的容器
        self.panel0 = wx.Panel(self.sub_window0)

        self.check_list_box = wx.CheckListBox(self.panel0, size=(500, 200), choices=self.mc.choices_classes, pos=(0, 0))
        self.button_delete = wx.Button(self.panel0, label="删除")
        self.button_delete.Bind(wx.EVT_BUTTON, self.delete_class)

        self.label = wx.StaticText(self.panel0, label="请输入要添加的班级名称：")
        self.input = wx.TextCtrl(self.panel0, style=wx.TEXT_ATTR_LINE_SPACING)
        self.button_add = wx.Button(self.panel0, label="添加")
        self.button_add.Bind(wx.EVT_BUTTON, self.add_class)
        # 创建一个水平方向的盒子布局管理器，添加静态文本和下拉列表框，并设置间距和对齐方式
        self.hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox0.Add(self.check_list_box, 100, wx.EXPAND | wx.ALL, 5)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.button_delete, 100, wx.EXPAND | wx.ALL, 5)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox2.Add(self.label, 0, wx.EXPAND | wx.ALL, 5)
        self.hbox2.Add(self.input, 100, wx.EXPAND | wx.ALL, 5)
        self.hbox2.Add(self.button_add, 100, wx.EXPAND | wx.ALL, 5)

        # 创建一个垂直方向的盒子布局管理器，添加水平布局管理器和按钮，并设置间距和对齐方式
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.hbox0, 0, wx.EXPAND)
        vbox.Add(self.hbox1, 0, wx.EXPAND)
        vbox.Add(self.hbox2, 0, wx.EXPAND)
        # 设置面板的布局管理器为垂直布局管理器
        self.panel0.SetSizer(vbox)
        # 显示一个新窗口
        self.sub_window0.Show()
        self.sub_window0.Raise()


    def add_class(self, event):
        # 获取输入框内容
        new_class = self.input.GetLineText(0)
        # 在mc中添加classes_name中对应的项目
        self.mc.add_classes(new_class)
        # 刷新checklistbox
        self.check_list_box.SetItems(self.mc.choices_classes)


    def delete_class(self, event):
        # 获取选择的项目
        will_delete_classes = self.check_list_box.GetCheckedStrings()  # 返回被选中的元素的元组
        # 在mc中删除classes_name中对应的项目
        self.mc.delete_classes(will_delete_classes)
        # 刷新checklistbox
        self.check_list_box.SetItems(self.mc.choices_classes)

