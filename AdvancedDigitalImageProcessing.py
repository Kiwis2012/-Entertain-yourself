##!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : ${11DEC19}
# @Author  : Kiwi Pan
# @FileName: ${AdvancedDigitalImageProcessing}.py
# import math
# from scipy.misc import derivative
import numpy as np
import sympy
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

DIGIT = 4
COUNT = 0
f1 = lambda x: x**2 - 4*sympy.sin(x)


def f2(x1, x2):
    return x1+x2/(x1*x2-1)


def f3(x, y):
    a1 = sympy.sin((x**2)/2 - (y**2)/4 + 3)
    a2 = sympy.cos(2*x + 1 - sympy.exp(y))
    return a1*a2


''' 
    二分法与Fibonacci法, 输入参数依次为函数, 左区间端点, 右区间断点, 停止迭代精度
'''
def Dichotomous(f, bracket_left, bracket_right, delta=0.001):
    global COUNT
    length = bracket_right - bracket_left
    x1 = bracket_left + length/2 - length/128
    x2 = bracket_right - length/2 + length/128
    presult = (x1+x2)/2

    if f(x1) - f(x2) >= delta:
        bracket_left = x1
        # print('left discarded')
        COUNT +=1
        Dichotomous(f, bracket_left, bracket_right, delta)
    elif f(x1) - f(x2) <= -delta:
        bracket_right = x2
        # print('right discarded')
        COUNT += 1
        Dichotomous(f, bracket_left, bracket_right, delta)
    else:
        print('Dichotomous final result', '(', round(presult, DIGIT), round(f(presult), DIGIT), ')', 'iterCount=', COUNT)
        COUNT = 0


def Fibonacci(f, bracket_left, bracket_right, delta=0.001):
    global COUNT
    length = bracket_right - bracket_left
    x1 = bracket_left + length/8
    x2 = bracket_right - length/8
    presult = (x1+x2)/2
    if f(x1) - f(x2) >= delta:
        bracket_left = x1
        # print('left discarded')
        COUNT += 1
        Fibonacci(f, bracket_left, bracket_right, delta)
    elif f(x1) - f(x2) <= -delta:
        bracket_right = x2
        # print('right discarded')
        COUNT +=1
        Fibonacci(f, bracket_left, bracket_right, delta)
    else:
        print('Fibonacci final result', '(', round(presult, DIGIT), round(f(presult), DIGIT), ')', 'iterCount=', COUNT)
        COUNT = 0

'''
    一维牛顿法与梯度下降法, 输入参数为函数与初始点, 停止迭代精度
'''
def Newton(f, x0, delta=0.001):
    global COUNT
    x = sympy.Symbol('x')
    fx = f(x)
    dfx = sympy.diff(fx, x)
    dffx = sympy.diff(dfx, x)
    df = dfx.evalf(subs={x: x0})
    dff = dffx.evalf(subs={x: x0})
    # df = derivative(f, x0)  # scipy methods
    # dff = derivative(f, x0, n=2)
    newx = x0 - df/(dff+0.1)  # 这里加0.1是为了防止初始点过远时分母无限逼近于0导致的bug
    if abs(newx-x0) <= delta:
        print('Newton final result', '(', round(newx, DIGIT), round(f(newx), DIGIT), ')', 'iterCount=', COUNT)
        COUNT = 0
    else:
        # print('iter', newx)
        COUNT += 1
        Newton(f, newx, delta)


def GradientDescent(f, x0, lr=0.1, delta=0.001):
    global COUNT
    x = sympy.Symbol('x')
    fx = f(x)
    dfx = sympy.diff(fx, x)
    deltax = dfx.evalf(subs={x: x0})
    # deltax = derivative(f, x0)
    newx = x0 - lr*deltax
    if abs(newx-x0) <= delta:
        print('GradientDescent final result', ')', round(newx, DIGIT), round(f(newx), DIGIT), ')',
              'iterCount=', COUNT, 'with learning rate:%f'%lr)
        COUNT = 0
    else:
        COUNT += 1
        GradientDescent(f, newx, delta)

'''
    二维牛顿法与梯度下降法, 输入参数为函数与初始点数组,停止迭代精度
'''
def MNewton(f, var, delta=0.001):
    global COUNT
    x0, y0 = var[0], var[1]
    x, y = sympy.symbols('x y')
    fxy = f(x, y)
    dfx = sympy.diff(fxy, x)
    dfy = sympy.diff(fxy, y)
    dfxx = sympy.diff(dfx, x)
    dfxy = sympy.diff(dfx, y)
    dfyy = sympy.diff(dfy, y)

    df = [dfx.evalf(subs={x: x0, y: y0}), dfy.evalf(subs={x: x0, y: y0})]
    dff = [[dfxx.evalf(subs={x: x0, y: y0}), dfxy.evalf(subs={x: x0, y: y0})],
           [dfxy.evalf(subs={x: x0, y: y0}), dfyy.evalf(subs={x: x0, y: y0})]]
    dfn = np.array(df, dtype='float')
    dffn = np.mat(dff, dtype='float')
    ivar = np.array(var)
    newvar = ivar.reshape(2, 1) - (dffn.I * dfn.reshape(2, 1))
    newone = [newvar.tolist()[0][0], newvar.tolist()[1][0]]
    # print(var, dfn, '\n', dffn, '\n', dffn.I, '\n', dffn.I * dfn.reshape(2, 1), '\n', newvar)
    if abs(f(var[0], var[1])-f(newone[0], newone[1]))<=delta:
        print('Newton final result', '(', newone, f(newone[0], newone[1]), ')', 'iterCount=', COUNT)
        COUNT = 0
    else:
        COUNT += 1
        MNewton(f, newone)


def MGrad(f, var, lr=0.1, delta=1e-6):
    global COUNT
    x0, y0 = var[0], var[1]
    x, y = sympy.symbols('x y')
    fxy = f(x, y)
    dfx = sympy.diff(fxy, x)
    dfy = sympy.diff(fxy, y)

    df = [dfx.evalf(subs={x: x0, y: y0}), dfy.evalf(subs={x: x0, y: y0})]
    dfn = np.array(df, dtype='float')

    ivar = np.array(var)
    newvar = ivar.reshape(2, 1) - lr*dfn
    newone = [newvar.tolist()[0][0], newvar.tolist()[1][0]]
    # print(var, dfn, '\n', dffn, '\n', dffn.I, '\n', dffn.I * dfn.reshape(2, 1), '\n', newvar)
    if abs(f(var[0], var[1])-f(newone[0], newone[1]))<= delta:
        print('Grad final result', '(', newone, f(newone[0], newone[1]), ')', 'iterCount=', COUNT, 'with learning rate:%f'%lr)
        COUNT = 0
    else:
        COUNT += 1
        MGrad(f, newone)


print('F1')
Dichotomous(f1, 0, 10)
Fibonacci(f1, 0, 10)
Newton(f1, 10)
GradientDescent(f1, 10)
print('F2')
MNewton(f2, [-0.1, 0.1])
MGrad(f2, [1, 2])
print('F3')
MNewton(f3, [3, 3])
MGrad(f3, [2, 2])



# fig = plt.figure(1)
# ax = Axes3D(fig)
# X = np.arange(-10, 10, 0.25)
# Y = np.arange(-10, 10, 0.25)
# X, Y = np.meshgrid(X, Y)
# Z = f2(X, Y)
# ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=plt.get_cmap('rainbow'))#彩虹
# plt.show()
