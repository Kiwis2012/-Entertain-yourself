
'''  generate the example figure of dividing linear and nonlinear data by svm in presention of week 13'''


import numpy as np
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap
from sklearn.model_selection import GridSearchCV

# linear data
X = np.r_[np.random.randn(20, 2)*2 - [2, 2], np.random.randn(20, 2)*2 + [2, 2]]  # r_用于按行合并随机数据点
y = [0] * 20 + [1] * 20
# circle data
# X, y = make_circles(noise=0.2, factor=0.5, random_state=1)
clf = svm.SVC(kernel='linear').fit(X, y)
C = 10
gamma = 0.1

w = clf.coef_[0]
k = -w[0] / w[1]
#  WX+b=0
#        [x0]
# [w0,w1][x1] + b = 0
# x0 = [-5, 5]
# x1 = -w0/w1 - b/w1
axis_x = np.linspace(-5,5)
plt.figure(1)
plt.title('Linear Kernel')
plt.plot(axis_x, k * axis_x - (clf.intercept_[0]) / w[1], 'k-')
plt.plot(axis_x, k * axis_x + (clf.support_vectors_[0][1] - k * clf.support_vectors_[0][0]), 'k--')
plt.plot(axis_x, k * axis_x + (clf.support_vectors_[-1][1] - k * clf.support_vectors_[-1][0]), 'k--')
plt.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=2*len(y), facecolors='none')
plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Paired)
plt.axis('tight')


X = StandardScaler().fit_transform(X)
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max,0.02),
                     np.arange(y_min, y_max, 0.02))
clf_rbf = svm.SVC(kernel='rbf', C=C, gamma=gamma).fit(X, y)
Z = clf_rbf.predict(np.c_[xx.ravel(), yy.ravel()])
# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure(2)
plt.title('Rbf Kernel')
plt.contourf(xx, yy, Z, cmap=plt.cm.coolwarm, alpha=0.8)
plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.coolwarm)
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.xticks(())
plt.yticks(())
plt.xlabel(" gamma=" + str(gamma) + " C=" + str(C))

plt.show()
