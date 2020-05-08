'''
一个24点游戏....界面仅生成存在答案的序列
内置一个简单计算器

bug还有很多很多(主要是括号)
有时编译会出现
    NameError: name 'usrinput' is not defined
重新运行即可(不知道为什么)

by kiwi in 29FEB20
'''

import tkinter as tk
from tkinter import messagebox
import random
import re

# 打开计算器界面
def opencal():
    cal_win = tk.Tk()
    cal_win.title('This is a calculator =w=')
    cal_win.geometry('450x550')
    cal_win.bind('<Escape>', lambda e: cal_win.destroy())

    res_label = tk.Label(cal_win, text='0', bg='white', font=('Arial', 32))
    res_label.grid(columnspan=5, row=1, column=1, padx=10, pady=10, ipadx=10, ipady=10)

    def calnum(n1, n2, ope):
        if ope == 10:
            return n1 + n2
        if ope == 11:
            return n1 - n2
        if ope == 12:
            return n1 * n2
        if ope == 13:
            return n1 / n2

    caldat = []
    def restore_value(val):
        if val == '=':
            res = eval(''.join(caldat))
            res_label.configure(text=res)
            pass
        elif val == 'AC':
            caldat.clear()
            res_label.configure(text='0')
        else:
            caldat.append(val)
            res_label.configure(text=caldat[-1])


    b1 = tk.Button(cal_win, text='1', font=('Arial', 12), command=lambda: restore_value('1')) \
        .grid(row=2, column=1, padx=20, pady=20, ipadx=20, ipady=20)
    b2 = tk.Button(cal_win, text='2', font=('Arial', 12), command=lambda: restore_value('2')) \
        .grid(row=2, column=2, padx=20, pady=20, ipadx=20, ipady=20)
    b3 = tk.Button(cal_win, text='3', font=('Arial', 12), command=lambda: restore_value('3')) \
        .grid(row=2, column=3, padx=20, pady=20, ipadx=20, ipady=20)

    b4 = tk.Button(cal_win, text='4', font=('Arial', 12), command=lambda: restore_value('4')) \
        .grid(row=3, column=1, padx=20, pady=20, ipadx=20, ipady=20)
    b5 = tk.Button(cal_win, text='5', font=('Arial', 12), command=lambda: restore_value('5')) \
        .grid(row=3, column=2, padx=20, pady=20, ipadx=20, ipady=20)
    b6 = tk.Button(cal_win, text='6', font=('Arial', 12), command=lambda: restore_value('6')) \
        .grid(row=3, column=3, padx=20, pady=20, ipadx=20, ipady=20)

    b7 = tk.Button(cal_win, text='7', font=('Arial', 12), command=lambda: restore_value('7')) \
        .grid(row=4, column=1, padx=20, pady=20, ipadx=20, ipady=20)
    b8 = tk.Button(cal_win, text='8', font=('Arial', 12), command=lambda: restore_value('8')) \
        .grid(row=4, column=2, padx=20, pady=20, ipadx=20, ipady=20)
    b9 = tk.Button(cal_win, text='9', font=('Arial', 12), command=lambda: restore_value('9')) \
        .grid(row=4, column=3, padx=20, pady=20, ipadx=20, ipady=20)

    badd = tk.Button(cal_win, text='+', font=('Arial', 12), command=lambda: restore_value('+')) \
        .grid(row=2, column=4, padx=20, pady=20, ipadx=20, ipady=20)
    bminus = tk.Button(cal_win, text='-', font=('Arial', 12), command=lambda: restore_value('-')) \
        .grid(row=3, column=4, padx=20, pady=20, ipadx=20, ipady=20)
    bmultiply = tk.Button(cal_win, text='*', font=('Arial', 12), command=lambda: restore_value('*')) \
        .grid(row=4, column=4, padx=20, pady=20, ipadx=20, ipady=20)
    bdiv = tk.Button(cal_win, text='/', font=('Arial', 12), command=lambda: restore_value('/')) \
        .grid(row=5, column=4, padx=20, pady=20, ipadx=20, ipady=20)

    beq = tk.Button(cal_win, text='=', font=('Arial', 12), command=lambda: restore_value('=')) \
        .grid(columnspan=2, row=5, column=1, padx=20, pady=20, ipadx=20, ipady=20)
    bac = tk.Button(cal_win, text='AC', font=('Arial', 12), command=lambda: restore_value('AC')) \
        .grid(row=5, column=3, padx=20, pady=20, ipadx=20, ipady=20)


    cal_win.mainloop()

# generate 函数 用于生成下一题
def gen(nums):
    num_new = [str(x) for x in nums]
    if len(cal24(' '.join(num_new))) > 0:
        return (cal24(' '.join(num_new))[0])
    else:
        print('refresh')
        refreshgame()

# 获取entry中用户输入的信息
def getinfo():
    res = usrinput.get()
    if re.match('\d', res[-1]) is None and res[-1]!=')':
        print(res[-1])
        messagebox.showerror(title='No~', message='好好答题')
    else:
        fir = re.findall('\d', res)
        if len(fir):
            fin = re.findall(str(nums[0])+'|'+str(nums[1])+'|'+str(nums[2])+'|'+str(nums[3]), ''.join(fir))
            if len(fin) == len(fir):
                if eval(res) == 24:
                    messagebox.showinfo(title='Congradulations!', message='可喜可贺!')
                else:
                    messagebox.showerror(title='No~', message='不对的')
            else:
                messagebox.showerror(title='No~', message='只能用给定的数字')


def refreshgame():
    usrinput.delete(0, 'end')
    global nums
    nums = [random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9)]
    num1.configure(text=str(nums[0]))
    num2.configure(text=str(nums[1]))
    num3.configure(text=str(nums[2]))
    num4.configure(text=str(nums[3]))

# display answer 显示计算后的答案
def disans():
    messagebox.showinfo(title='Answer', message=gen(nums))

# 文本框后插入各种符号
def add_entry(add):
    usrinput.insert(len(usrinput.get()), add)

# 借鉴其他代码 用于计算24点答案
# http://v5b7.com/python/python_24.html
def perm(items, n=None):
    if n is None:
        n = len(items)
    for i in range(len(items)):
        v = items[i:i+1]
        if n == 1:
            yield v
        else:
            rest = items[:i] + items[i+1:]
            for p in perm(rest, n-1):
                yield v + p

def check(a,b):
    arr={}
    for i in a:
        for j in b:
            va=a[i]
            vb=b[j]
            arr.update({"("+i+"+"+j+")":va+vb})
            arr.update({"("+i+"-"+j+")":va-vb})
            arr.update({"("+j+"-"+i+")":vb-va})
            arr.update({"("+i+"*"+j+")":va*vb})
            vb>0 and arr.update({"("+i+"/"+j+")":va/vb})
            va>0 and arr.update({"("+j+"/"+i+")":vb/va})
    return arr


def cal24(string):
    arr=[]
    num = string.split(' ')
    for i in num:
        arr.append(float(i))
    res=[]
    for i in perm(arr):
        dic=[{"a":i[0]},{"b":i[1]},{"c":i[2]},{"d":i[3]}]
        alist=check(check(check(dic[0],dic[1]),dic[2]),dic[3])
        blist=check(check(dic[0],dic[1]),check(dic[2],dic[3]))
        for i in alist:
            if alist[i]==24.0:
                res.append(i.replace('a',str(dic[0]['a'])).replace('b',str(dic[1]['b'])).\
                           replace('c',str(dic[2]['c'])).replace('d',str(dic[3]['d'])))
        for i in blist:
            if blist[i]==24.0:
                 res.append(i.replace('a',str(dic[0]['a'])).replace('b',str(dic[1]['b'])).\
                            replace('c',str(dic[2]['c'])).replace('d',str(dic[3]['d'])))
    return res


# 主界面函数开始
if __name__ == '__main__':
    game_win = tk.Tk()
    game_win.title('24 points game')
    game_win.geometry('600x400')

    num1 = tk.Label(game_win, text='\n使用以下四个数字进行四则运算, 点击提交查看结果\n'
                                   '注意表达式内只能使用+-*/四种符号与括号',\
                    font=(12)).place(x=65, y=20, anchor='nw')

    # blank = tk.Label(game_win).grid(row=2, column=1)
    nums = [random.randint(1, 9), random.randint(1, 9), random.randint(1, 9), random.randint(1, 9)]
    if gen(nums):
        num1 = tk.Label(game_win, text=str(nums[0]), font=('Arial', 24))
        num1.place(x=160, y=100, anchor='nw')
        num2 = tk.Label(game_win, text=str(nums[1]), font=('Arial', 24))
        num2.place(x=240, y=100, anchor='nw')
        num3 = tk.Label(game_win, text=str(nums[2]), font=('Arial', 24))
        num3.place(x=320, y=100, anchor='nw')
        num4 = tk.Label(game_win, text=str(nums[3]), font=('Arial', 24))
        num4.place(x=400, y=100, anchor='nw')

    # blank = tk.Label(game_win).grid(row=4, column=1)
    usrinput = tk.Entry(game_win, font=('Arial', 24))
    usrinput.place(x=120, y=170, anchor='nw')
    blank = tk.Label(game_win).grid(row=6, column=1)
    bsym_add = tk.Button(game_win, text='+', command=lambda: add_entry('+'),\
                         font=('Arial', 18)).place(x=80, y=240, anchor='nw')
    bsym_add = tk.Button(game_win, text='-', command=lambda: add_entry('-'), \
                         font=('Arial', 18)).place(x=160, y=240, anchor='nw')
    bsym_add = tk.Button(game_win, text='*', command=lambda: add_entry('*'), \
                         font=('Arial', 18)).place(x=240, y=240, anchor='nw')
    bsym_add = tk.Button(game_win, text='/', command=lambda: add_entry('/'), \
                         font=('Arial', 18)).place(x=320, y=240, anchor='nw')
    bsym_add = tk.Button(game_win, text='(', command=lambda: add_entry('('), \
                         font=('Arial', 18)).place(x=400, y=240, anchor='nw')
    bsym_add = tk.Button(game_win, text=')', command=lambda: add_entry(')'), \
                         font=('Arial', 18)).place(x=480, y=240, anchor='nw')
    # blank = tk.Label(game_win).grid(row=8, column=1)
    okbutton = tk.Button(game_win, text='提交', command=getinfo, font=(18)).place(x=115, y=320, anchor='nw')
    bref = tk.Button(game_win, text='下一题', command=refreshgame, font=(18)).place(x=200, y=320, anchor='nw')
    bcal = tk.Button(game_win, text='计算器', command=opencal, font=(18)).place(x=300, y=320, anchor='nw')
    bans = tk.Button(game_win, text='答案', command=disans, font=(18)).place(x=400, y=320, anchor='nw')
    # blank = tk.Label(game_win).grid(row=10, column=1)


    game_win.mainloop()

