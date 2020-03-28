# -*- coding:utf-8 -*-
'''
    图书管理系统
    碎碎念见最下方
    打包命令,切记要把exe放进csv在的文件夹...
    pyinstaller -F D:\Kiwi\Code\Assignments\library_management\lib_manage.py --noconsole
'''
import random
import string
import time
import requests
import csv
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from bs4 import BeautifulSoup

from collections import Iterable

# 好像明文储存有点过分不安全了...干脆不检测密码了
# 优化要在完成之后！
USR_IMPORT_PATH = 'data\datausr.csv'
BOOK_IMPORT_PATH = 'data\databook.csv'
BOOK_STORAGE_PATH = 'data\databook.csv'
LOGIN_PWD = 'PWD'
MAX_USR = 20
# data_columns = ['书籍名称', '可借复本', '馆藏复本', '作者或译者', '地址']  # 好像没用上

class usr:
    def __init__(self, id, name):
        self.name = name
        self.id = id
        self.__pwd = LOGIN_PWD

class book:
    def __init__(self, name=None, id=None, avaliable=None, all=None, author=None, addr=None):
        self.nm = name
        self.id = id
        self.ava = avaliable
        self.all = all
        self.athr = author
        self.addr = addr
        self.hstry = []
    def dis(self):
        print('书籍名称:{0}\n索书号:{1}\n可借复本:{2}\n馆藏复本:{3}\n作者或译者:{4}\n地址:{5}'\
              .format(self.nm, self.id, self.ava, self.all, self.athr, self.addr))
    def opr(self, reader, opr):
        if opr =='lend':
            self.hstry.append('****操作:借出****用户名:%s****用户编号:%s****操作时间:%s'\
                              %(reader.nm, reader.id, time.ctime()))
            # print(self.hstry[-1])
        elif opr =='return':
            self.hstry.append('****操作:归还****用户名:%s****用户编号:%s****操作时间:%s'\
                              %(reader.nm, reader.id, time.ctime()))
            # print(self.hstry[-1])
        else : print('图书操作失败!')
    def prnt_hstry(self):
        if len(self.hstry) == 0:
            print('暂无借阅记录')
        else:
            print('\n'.join(self.hstry))

class rd(usr):
    def __init__(self, id, name, *history):
        super().__init__(id, name)
        self.id = id
        self.type = 'Reader'
        self.b_book = []
        if history:
            # self.hstry = [{'name': 'test', 'opr': 'test', 'time': 'test'}]
            self.hstry = []
    # class opr_history():
    #     def __init__(self, name, operate, time):
    #         self.name = name
    #         self.operate = operate
    #         self.time = time

    def opr(self, book, opr):
        # book.opr(self, opr)
        # print('from usr class', self.hstry)

        if opr =='lend':
            # self.hstry.append(self.opr_history(book.nm, 'lend', time.time()))
            self.b_book.append(book.nm)
            # self.hstry.append({'name': book.nm, 'opr': 'lend', 'time': time.time()})
            self.hstry.append('****借入%s 编号:%s 操作时间:%s'%(book.nm, book.id, time.ctime()))

        elif opr =='return':
            # self.hstry.append(self.opr_history(book.nm, 'return', time.time()))
            self.b_book.remove(book.nm)
            # self.hstry.append({'name': book.nm, 'opr': 'return', 'time': time.time()})
            self.hstry.append('****归还%s 编号:%s 操作时间:%s' % (book.nm, book.id, time.ctime()))

        else:
            print('用户操作失败!')
    # def prnt_hstry(self):
    #     if len(self.hstry)==0:
    #         print('暂无借阅记录')
    #     else:
    #         print('\n'.join(self.hstry))

class admin(usr):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.type = 'Admin'
        # self.hstry = history

    def import_data(self, path):
        with open(path) as data_file:
            reader = csv.reader(data_file)
            data_cache = []
            for each_line in reader:
                if len(each_line) == 0:
                    continue
                else:
                    data_cache.append(each_line)
                    # print(each_line)
        return data_cache

    # def add_book(self, book_name, no=None, valid='1', all='1', author=None, addr=None):
    #     lib.lib_add_bk(book_name, no, valid, all, author, addr)
    # def edit_book(self, book_name, target, new_value):
    #     lib.lib_edit_bk(book_name, target, new_value)
    # def del_book(self, book):
    #     pass

class login_page:
    def __init__(self):
        self.login = tk.Tk()
        self.login.title('登陆窗口')
        self.login.geometry('300x420')
        self.text = tk.Label(text='欢迎登陆\n用户图书管理系统', font=('Arial', 24))\
            .pack(pady=20)
        self.name = tk.Label(text='用户名:').place(x=50, y=180)
        self.usr_name = tk.Entry()
        self.usr_name.place(x=100, y=180)
        self.name = tk.Label(text='密码:').place(x=50, y=240)
        self.usr_pwd = tk.Entry()
        self.usr_pwd.place(x=100, y=240)
        self.submit = tk.Button(text='登陆', command=lambda: self.usr_login(), width=10)\
            .place(x=50, y=300)
        self.exit = tk.Button(text='退出', command=lambda: self.usr_exit(), width=10)\
            .place(x=170, y=300)
        self.login.mainloop()

    def usr_login(self):
        self.name = self.usr_name.get()
        self.pwd = self.usr_pwd.get()
        with open(USR_IMPORT_PATH, 'r', newline='') as user_list:
            reader = csv.reader(user_list)
            check_flag = False
            for each_line in reader:
                if self.name == each_line[1]:
                    check_flag = True
                    if each_line[2] == 'admin':
                        # 'user id', 'user name', 'history'
                        self.a_admin = admin(each_line[0], each_line[1])
                        self.a_admin_page = admin_page(usr_class=self.a_admin, parent=self.login, usr_name='admin')
                        break
                    elif each_line[2] == 'reader':
                        self.a_rd = rd(each_line[0], each_line[1], each_line[3])
                        self.a_rd_page = rd_page(self.a_rd, self.login, 'reader_1')
                        break
            if not check_flag:
                messagebox.showwarning(title='警告', message='登陆失败! 请检查用户名')

    def usr_exit(self):
        self.login.destroy()

class main_page:
    def __init__(self, usr_class, parent=None, usr_name='null'):
        if parent is not None:
            parent.destroy()
        self.usr_class = usr_class
        self.usr_name = usr_name
        self.main = tk.Tk()
        self.main.title('用户图书管理系统')
        # 划分主要区域
        self.left_top_frm = tk.Frame(width=200, height=300)
        self.left_top_frm.grid(row=0, column=0, sticky='NW', padx=20, pady=10)
        self.left_down_frm = tk.Frame(width=200, height=300)
        self.left_down_frm.grid(row=1, column=0, sticky='NW', padx=40, pady=10)
        self.right_frm = tk.Frame(width=600, height=600)
        self.right_frm.grid(row=0, column=1, rowspan=2, sticky='NW', padx=20, pady=10)
        # 左上的部件
        self.welc_msg = tk.Label(self.left_top_frm, text="欢迎回来!", font=('Verdana', 12))\
            .grid(row=0, column=1, ipady=5, sticky='w')
        self.time = tk.Label(self.left_top_frm, text=time.strftime('%y-%m-%d %I:%M:%S %p'), font=('Verdana', 12))
        self.time.grid(row=1, column=1, ipady=5, sticky='w')
        self.usr_info = tk.Label(self.left_top_frm, text="用户ID: %s" % self.usr_class.id, font=('Verdana', 12))\
            .grid(row=2, column=1, ipady=5, sticky='w')
        self.usr_name = tk.Label(self.left_top_frm, text="用户名:%s" % self.usr_name, font=('Verdana', 12))\
            .grid(row=3, column=1, ipady=5, sticky='w')
        self.usr_type = tk.Label(self.left_top_frm, text="用户类型:管理员", font=('Verdana', 12))
        self.usr_type.grid(row=4, column=1, ipady=5, sticky='w')
        # 左下角部件
        self.find = tk.Entry(self.left_down_frm, width=20, fg='gray')
        self.find.insert(index=0, string='请输入查找内容')
        self.find.bind('<Button-1>', func=self.find_book)
        self.find.bind('<Return>', func=self.dis_res)
        self.find.grid(row=0, column=1, pady=5)
        self.b1 = tk.Button(self.left_down_frm, text='', width=20, command=None)
        self.b1.grid(row=1, column=1, pady=5)
        self.b2 = tk.Button(self.left_down_frm, text='', width=20, command=None)
        self.b2.grid(row=2, column=1, pady=5)
        self.b3 = tk.Button(self.left_down_frm, text='', width=20, command=None)
        self.b3.grid(row=3, column=1, pady=5)
        self.b4 = tk.Button(self.left_down_frm, text='', width=20, command=None)
        self.b4.grid(row=4, column=1, pady=5)
        self.exit = tk.Button(self.left_down_frm, text='退出', width=20, command=lambda: self.usr_exit(self.usr_class))
        self.exit.grid(row=5, column=1, pady=5)
        # 右侧的treeview
        self.columns = ('书籍名称', '索书号', '可借复本', '馆藏复本', '作者或译者', '地址')
        self.book_list = ttk.Treeview(self.right_frm, show='headings', height=20, columns=self.columns)
        # self.book_list.bind('<Double-Button-1>', self.find_book)
        self.scroll = ttk.Scrollbar(self.right_frm, orient='vertical', command=self.book_list.yview)
        self.book_list.configure(yscrollcommand=self.scroll.set)
        # 这里只是用来设定宽度
        self.book_list.column('书籍名称', width=120, anchor='center')
        self.book_list.column('索书号', width=100, anchor='center')
        self.book_list.column('可借复本', width=50, anchor='center')
        self.book_list.column('馆藏复本', width=50, anchor='center')
        self.book_list.column('作者或译者', width=150, anchor='center')
        self.book_list.column('地址', width=200, anchor='center')
        self.book_list.grid(row=0, column=0, sticky='NSEW')
        self.scroll.grid(row=0, column=1, sticky='NS')
        # 绑定headings
        for i in self.columns:
            self.book_list.heading(i, text=i)
        # self.main.bind('<Button-1>', func=self.dis_res)
        self.update_time()

    def update_time(self):
        self.time.configure(text=time.strftime('%y-%m-%d %I:%M:%S %p'))
        self.time.after(ms=1000, func=self.update_time)

    def find_book(self, event):
        self.find.delete(0, len(self.find.get()))
        self.find.configure(fg='black')
        self.find.bind('<FocusOut>', func=self.dis_res)

    def dis_res(self, event):
        # 没找到暂时没有提醒
        self.target = self.find.get()
        # print(self.book_list.selection())
        for each_selected in self.book_list.selection():
            self.book_list.selection_remove(each_selected)
        for each_col in self.book_list.get_children():
            for each_cell in self.book_list.item(each_col, 'values'):
                if self.target is not '' and self.target in each_cell:
                    self.book_list.selection_add((each_col))
                    self.book_list.move(each_col, '', 0)



    # def find_pop(self, event):
    #     try:
    #         self.find_entry
    #     except NameError:
    #         print('test')
    #     else:
    #         self.find_entry.destroy()
    #     finally:
    #         self.row = self.book_list.identify_row(event.y)
    #         self.col = self.book_list.identify_column(event.x)
    #         x, y, width, height = self.book_list.bbox(self.row, self.col)
    #         print(self.row, self.col)
    #         print(self.book_list.bbox(self.row, self.col))
    #         self.find_entry = tk.Entry(self.book_list, '', width=width//4)
    #         self.find_entry.place(x=x, y=y)
        # print(self.book_list.heading(column=self.col)['text'])
        # if self.book_list.identify_region(x=event.x, y=event.y) == 'heading':
        #     pass
        # print(self.book_list.identify_region(x=event.x, y=event.y))

    def usr_exit(self, usr_class):

        with open(BOOK_STORAGE_PATH, 'w', newline='') as csvfile:
            print('saving books...')
            writer = csv.writer(csvfile)
            for each_line in self.book_list.get_children():
                writer.writerow(self.book_list.item(each_line, 'values'))
        with open(USR_IMPORT_PATH, 'a', newline='') as csvfile:
            print('saving users...')
            writer = csv.writer(csvfile)
            print(usr_class.type)
            if usr_class.type=='Reader':
                print(usr_class.id, usr_class.name, usr_class.type,\
                                ''.join(usr_class.b_book), ''.join(usr_class.hstry))
                writer.writerow([usr_class.id, usr_class.name, usr_class.type,\
                                 ''.join(usr_class.hstry), ''.join(usr_class.b_book),])
            elif usr_class.type == 'Admin':
                writer.writerow([usr_class.id, usr_class.name, usr_class.type])
        self.main.destroy()
        login_again = login_page()
        login_again.login.mainloop()


class rd_page(main_page):
    def __init__(self, usr_class, parent=None, usr_name='null'):
        super().__init__(usr_class, parent, usr_name)
        # self.main.title('图书借阅管理系统') 切换title?
        self.usr_class = usr_class
        self.usr_type.configure(text="用户类型:读者")
        self.b1.configure(text='借入', command=lambda: self.borr_book(self.usr_class,\
                        globals()['book_'+ str(self.book_list.index(self.book_list.selection()))]))
        self.b2.configure(text='归还', command=lambda: self.rtrn_book(self.usr_class,\
                        globals()['book_'+ str(self.book_list.index(self.book_list.selection()))]))
        self.b3.configure(text='已借书籍',  command=lambda: self.dis_list(usr_class))
        self.b4.configure(text='借阅记录', command=lambda: self.dis_hstry(usr_class))

        with open(BOOK_STORAGE_PATH) as data_file:
            reader = csv.reader(data_file)
            i=0
            for each_line in reader:
                if len(each_line) == 0:
                    continue
                else:
                    globals()['book_'+ str(i)] = book(each_line[0], each_line[1], each_line[2],\
                                                  each_line[3],each_line[4], each_line[5])
                    # '书籍名称:{0}\n索书号:{1}\n可借复本:{2}\n馆藏复本:{3}\n作者或译者:{4}\n地址:{5}'
                    i+=1
                    self.book_list.insert('', 'end', values=each_line)
        self.update_time()
        self.main.mainloop()

    def borr_book(self, usr_class, book):
        if int(book.ava) > 0:
            book.ava = int(book.ava) - 1
            self.book_list.set(self.book_list.selection(), 2, book.ava)
            usr_class.opr(book, 'lend')
            print(usr_class.hstry)
            # messagebox.showinfo(message='借书成功!')
        else:
            messagebox.showwarning(message='书籍可借数量不足!')
        # self.ava = int(book.ava)
        # if self.ava > 0:
        #     self.ava -= 1
        #     self.book_list.set(self.book_list.selection(), 2, self.ava)
        #     usr_class.opr(book, 'lend')
        #     print(len(usr_class.hstry), usr_class.hstry[-1].name, 'lend', usr_class.hstry[-1].time)
        #     messagebox.showinfo(message='借书成功!')
        # else:
        #     messagebox.showwarning(title='警告', message='剩余书籍数量不足！')
    def rtrn_book(self, usr_class, book):
        if book.nm in usr_class.b_book:
            book.ava = int(book.ava) + 1
            self.book_list.set(self.book_list.selection(), 2, book.ava)
            usr_class.opr(book, 'return')
            print(usr_class.hstry[1:])
        else:
            messagebox.showinfo(message='未查询到借阅记录')

    def dis_list(self, usr_class):
        if len(usr_class.b_book) == 0:
            messagebox.showinfo(message='还没有借书哦')
        else:
            messagebox.showinfo(message='您的已借阅书籍为\n        %s'%'\n        '.join(usr_class.b_book))
    def dis_hstry(self, usr_class):
        if len(usr_class.b_book) == 0:
            messagebox.showinfo(message='未查询到借阅记录')
        else:
            messagebox.showinfo(message='您的已借阅记录为\n%s' % '\n'.join(usr_class.hstry))

#     def __init__(self, parent, usr_name='null'):
#         parent.destroy()
#         self.usr_name = usr_name
#         self.main = tk.Tk()
#         self.main.title('用户图书管理系统')
#         self.main.geometry('800x600')
#         self.clock = tk.Label(font=('Arial', 16), text='时间:%s' % time.ctime(), bg='#F8F8FF').place(x=450, y=10)
#         self.usr_info = tk.Label(font=('Arial', 16), text='用户名: %s\n 用户权限:%s'%(self.usr_name, self.usr_type),\
#                             bg='#F8F8FF').place(x=50, y=30)
#         self.book_dis = tk.Button(text='查看', font=('Arial', 16), width=12, \
#                              command=lambda: self.book_dis).place(x=50, y=100)
#         self.book_edit = tk.Button(text='编辑', font=('Arial', 16), width=12, \
#                               command=lambda: self.book_dis).place(x=50, y=160)
#         self.book_add = tk.Button(text='添加', font=('Arial', 16), width=12, \
#                              command=lambda: self.book_dis).place(x=50, y=220)
#         self.book_del = tk.Button(text='删除', font=('Arial', 16), width=12, \
#                              command=lambda: self.book_dis).place(x=50, y=280)
#         self.main.mainloop()
#     def book_dis(self):
#         pass
class admin_page(main_page):
    def __init__(self, usr_class, parent=None, usr_name='null'):
        super().__init__(usr_class, parent, usr_name)

        self.b1.configure(text='导入', command=lambda: self.import_data())
        self.b2.configure(text='添加', command=lambda: self.add_book())
        self.b3.configure(text='删除', command=lambda: self.del_book())
        self.b4.configure(text='编辑', command=lambda: self.edit_book())
        self.main.mainloop()

    # GUI的函数全部只做按钮,以及管理员类的函数对接,不做文件操作
    # 这里有点问题就是点完确定主界面不会刷新, 叉掉才会刷新
    def add_book(self):
    # 在关闭窗口后才会刷新...
        add_page = book_details('书籍详情添加')
        self.main.wait_window(add_page.details)
        self.book_list.insert('', 'end', values=(add_page.book_info))

    def edit_book(self):
        edit_page = book_details('书籍详情编辑')
        self.main.wait_window(edit_page.details)
        count = 0
        for value in edit_page.book_info:
            if value != '':
                self.book_list.set(self.book_list.selection(), count, value)
            count += 1

    def del_book(self):
        self.book_list.delete(self.book_list.selection())
        # print(self.book_list.index(self.book_list.selection()))

    def import_data(self):
        # 没有加入数据的补全
        for each_line in self.usr_class.import_data(BOOK_IMPORT_PATH):
            self.book_list.insert('', 'end', values=each_line)

class book_details():
    def __init__(self, title):
        self.details = tk.Toplevel()
        self.details.title(title) #根据改查不同
        # self.details.geometry('400x300')

        self.msg = tk.Label(self.details, text='').grid(row=0)
        self.name_ = tk.Label(self.details, text='书籍名称:').grid(row=1, column=0, padx=20, pady=5)
        self.name = tk.Entry(self.details)
        self.name.grid(row=1, column=1, padx=20)
        self.id_ = tk.Label(self.details, text='索书号:').grid(row=2, column=0, pady=5)
        self.id = tk.Entry(self.details)
        self.id.grid(row=2, column=1)
        self.ava_ = tk.Label(self.details, text='可借复本:').grid(row=3, column=0, pady=5)
        self.ava = tk.Entry(self.details)
        self.ava.grid(row=3, column=1)
        self.all_ = tk.Label(self.details, text='馆藏复本:').grid(row=4, column=0, pady=5)
        self.all = tk.Entry(self.details)
        self.all.grid(row=4, column=1)
        self.ath_ = tk.Label(self.details, text='作者/译者:').grid(row=5, column=0, pady=5)
        self.ath = tk.Entry(self.details)
        self.ath.grid(row=5, column=1)
        self.addr_ = tk.Label(self.details, text='所在地址:').grid(row=6, column=0, pady=5)
        self.addr = tk.Entry(self.details)
        self.addr.grid(row=6, column=1)

        self.submit = tk.Button(self.details, text='确认', command = lambda: self.edit_submit())
        self.submit.grid(row=7, column=0, sticky='e', pady=20)
        self.cancel = tk.Button(self.details, text='取消', command=lambda: self.back())
        self.cancel.grid(row=7, column=1, pady=20)
        # self.submit = tk.Button(self.details, text='确认', command=lambda: self.edit_submit())
        # self.submit.grid(row=7, column=0, sticky='e', pady=20)
        # self.cancel = tk.Button(self.details, text='取消', command=lambda: self.back())
        # self.cancel.grid(row=7, column=1, pady=20)

        # self.hsty = tk.Label(self.details, text='这里是借阅历史')
        # self.hsty.grid(row=0, column=2, padx=20, pady=5)
        # self.details.mainloop()

    def edit_submit(self):
        self.book_info = []
        self.book_info = [self.name.get(), self.id.get(), self.ava.get(),\
                          self.all.get(), self.ath.get(), self.addr.get()]
        if len(self.book_info) == 0:
            messagebox.showwarning(title='警告', message='请输入要修改的内容')
        self.details.destroy()
        # 这里不知道为啥蹦不出来?

    def back(self):
        self.details.destroy()
        # new_main = admin_page()
        pass

def init_test_usr():
    print('Initializing some test users...')
    with open(USR_IMPORT_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        print('start writing...')
        writer.writerow(['user id', 'user name', 'user type', 'history'])
        writer.writerow(['0', 'admin', 'admin', 'NULL'])
        writer.writerow(['1', 'reader', 'reader', '1'])
        for i in range(MAX_USR):
            type = random.choice(['admin', 'reader'])
            writer.writerow([''.join(random.sample(string.digits, 3)),\
                  type+'_'+''.join(random.sample(string.ascii_letters, 3)),\
                  type, ''])
        print('Completed')

def go_get_some_books():
    print('finding the book details...')
    headers = {
        # 获取自浏览器开发工具network页签,请求详情中的resuest headers里
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    url = 'http://lib.ecust.edu.cn/books/advquery?type=%E7%BA%B8%E8%B4%A8&title=%E5%9B%BE%E4%B9%A6&author=&publish=&isbn=&callNo=&form_build_id=form-mdM6uT9s9O3wqxWNkPyKAP0WzKLU4g_omjvqw--FIdM&form_id=ecust_lib_form_book_adv_query&op=%E6%90%9C%E7%B4%A2'
    res = requests.get(url, headers=headers)
    # res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    tlist = soup.find_all(class_='title')
    athr_list = soup.find_all(class_='author')
    addr_list = soup.find_all(class_='addr')
    with open(BOOK_IMPORT_PATH, 'w') as csvfile:
        writer = csv.writer(csvfile)
        print('start writing...')
        writer.writerow(['书籍名称', '索书号', '可借复本', '馆藏复本','作者或译者', '地址'])
        for i in range(len(tlist)):
            writer.writerow([tlist[i].text.split()[0], tlist[i].text.split()[-1],\
                             athr_list[i].text.split()[1], athr_list[i].text.split()[3],\
                             athr_list[i].text.split()[5], addr_list[i].text.split()[-1]])
            # print(tlist[i].text.split())
            # print(athr_list[i].text.split())
            # print(addr_list[i].text.split())
        print('Complete')

if __name__ == '__main__':
    # init_test_usr()
    # 第一测试层级
    login_1st = login_page()
    # 第二测试层级
    # admin_test = admin('3', 'test')
    # admin_page = admin_page(admin_test, usr_name='admin')
    # admin_page.main.mainloop()

    # rd_test = rd(23, 'test', '')
    # rd_page = rd_page(rd_test, usr_name='reader')
    # rd_page.main.mainloop()

    # 第三测试层级
    # test = book_details('test')
    #

'''
20-3-28 更新
目标
    可借数量不得大于总共 用户登录检查 搜索实时刷新 可借数量还有些微妙的bug
20-3-27 更新
基本完成GUI界面,放弃多文件编译
目前实现功能
    登陆界面-> 读者/管理员界面
    读者界面-> 借入 归还 查看已借 查看借阅记录 退出(->登陆)
    管理员界面-> 导入 添加/编辑(->图书详情) 删除 退出(->登陆)
目标
    加入图书被借阅记录, 没确定位置
    加入查找功能,

20-3-21 更新
    基本画好GUI, 用了treeview控件可以绑定鼠标事件
    写了三个文件一堆堆函数和类,但是完全结合不起来的样子, mysql也很麻烦还是用csv吧

20-3-16 画饼
    总之写了很多类, 但是互相还没什么关系
    用csv和pandas的库操作了下数据, pandas不大适合这种类型

    usr class def & all things
    # 基类：
    # 用户类：具有用户名、密码、用户编号等属性；
    # 具有登陆、查看主界面、查看图书详情等功能；
    # 图书类：具有名称、索书号、作者等属性；
    # 派生类：
    # 用户类派生类有管理员类、用户类，用户编号区间不同，
    # 衍生功能有管理员对图书的增删改查，用户对图书的借还功能；
    # 图书类派生有一些具体类别，主要衍生了一个类别属性。
'''




