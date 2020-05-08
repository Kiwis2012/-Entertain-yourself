import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
from tensorflow.keras import models, optimizers, regularizers, losses
from tensorflow.keras.layers import Dense, Conv1D, MaxPooling1D, Flatten
from scipy.io.wavfile import read
from python_speech_features import mfcc

RAW_PATH = './audio'  # 源文件位置
DATA_PATH = './data'
MODEL_PATH = './model/'
epoach = 20
split_ratio = 0.7
opt = 'adam'  # 有sgd adam RMSprop等等
aug = True


# 提取mfcc系数
def wav2mfcc(file_path):
    sr, y = read(filename=file_path)
    mfcc_feature = mfcc(y, samplerate=sr, winlen=0.04, winstep=0.02, numcep=100, nfft=640)
    return mfcc_feature


def relu(x):
    if x > 0:
       return x
    else:
       return 0


def softmax(x):
   a = np.max(x)
   c = x - a
   exp_c = np.exp(c)
   sum_c = np.sum(exp_c)
   return exp_c / sum_c


def raw_audio_process(data_path, generate_path):
    file_list = []
    for dirpath, dirnames, filenames in os.walk(data_path):
        for file in filenames:
            if os.path.splitext(file)[1] == '.wav':
                file_list.append(os.path.join(dirpath, file).replace('\\', '/'))

    for each_file in file_list:
        if each_file[-3:] == 'wav':
            class_name = each_file[-7:-6]
            if not (os.path.exists(generate_path)):
                os.mkdir(generate_path)
            save_path = os.path.join(generate_path, class_name)
            if not (os.path.exists(save_path)):
                os.mkdir(save_path)
            save_name = os.path.join(save_path, class_name+'_'+str(len(os.listdir(save_path)))+'.wav')
            shutil.copyfile(each_file, save_name)
    print('Done')


def data_prepare(data_path, save_path):
    label_lis = []; audio_lis = [] #同时赋值会让audio的第一个值错误,为啥
    for dirpath, dirnames, filenames in os.walk(data_path):  #这里为啥不能直接复制 too many values to unpack
        for each_wav in filenames:
            wav_path = os.path.join(dirpath, each_wav)
            label_lis.append(each_wav[:1]) #因为文件按标签命名
            mfcc_lis = np.ma.resize(wav2mfcc(wav_path), (500))
            # mfcc_lis = wav2mfcc(wav_path).flatten()
            audio_lis.append(mfcc_lis)
    input_data = np.array(audio_lis) #这是mfcc数据
    input_label = np.array(label_lis).reshape((200, 1)) #这是标签
    if not (os.path.exists(save_path)):
        os.mkdir(save_path)
    np.save(save_path+'data', input_data); np.save(save_path+'label', input_label)  # 保存个npy
    print('data saved in {0}'.format(save_path))
    return input_data, input_label


def data_load(save_path, split_ratio, augment=False):
    X = np.load(save_path +'data.npy')
    Y = np.load(save_path +'label.npy')
    # 确认个数相同
    assert X.shape[0] == Y.shape[0]
    # 切割一下数据集
    X_train, X_test, y_train, y_test = train_test_split\
        (X, Y, test_size=(1 - split_ratio), random_state=42, shuffle=True)
    if augment:
        noise = np.random.rand(X_train.shape[0], X_train.shape[1]) * (np.max(X_train)-np.min(X_train))/4
        X_noisy_train = noise + X_train
        X_train = np.concatenate((X_train, X_noisy_train), axis=0)
        y_train = np.concatenate((y_train, y_train), axis=0)
        print(np.max(X_train), np.min(X_train), X_train.shape)
    return X_train, X_test, y_train, y_test


def dense_net(X_train, X_test, y_train, y_test):
    x_train = X_train.reshape(-1, 500)
    x_test = X_test.reshape(-1, 500)
    # 将标签转换成one-hot编码
    y_train_hot = to_categorical(y_train, num_classes=10)
    y_test_hot = to_categorical(y_test, num_classes=10)
    # 四个全连接
    model = models.Sequential()
    model.add(Dense(64, activation='relu', input_shape=(500,)))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(10, activation='softmax'))
    # optimizer = optimizers.RMSprop()  # https://keras.io/api/optimizers/
    model.compile(loss=losses.categorical_crossentropy, optimizer=opt, metrics=['accuracy'])
    print('training start...')
    history = model.fit(x_train, y_train_hot, batch_size=70, epochs=epoach, verbose=1,
                        validation_data=(x_test, y_test_hot))
    # plt.figure(1)
    plt.subplot(121)
    plt.title('Dense-Net')
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='validation')
    plt.xlabel('epoaches'); plt.ylabel('acc'); plt.legend()
    # plt.show()


def cnn_net(X_train, X_test, y_train, y_test):
    x_train = X_train.reshape(-1, 25, 20)
    x_test = X_test.reshape(-1, 25, 20)
    # 将标签转换成one-hot编码
    y_train_hot = to_categorical(y_train, num_classes=10)
    y_test_hot = to_categorical(y_test, num_classes=10)
    # 试试更深
    model = models.Sequential()
    model.add(Conv1D(64, 3, activation='relu', padding='same', input_shape=(25, 20)))
    model.add(Conv1D(64, 3, activation='relu', padding='same'))
    model.add(MaxPooling1D(2))

    model.add(Conv1D(64, 3, activation='relu', padding='same'))
    model.add(Conv1D(64, 3, activation='relu', padding='same'))
    model.add(MaxPooling1D(2))

    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dense(10, activation='softmax'))

    model.compile(loss=losses.categorical_crossentropy, optimizer=opt, metrics=['accuracy'])
    print('training start...')
    history = model.fit(x_train, y_train_hot, batch_size=70, epochs=epoach, verbose=1,
                        validation_data=(x_test, y_test_hot))
    # plt.figure(2)
    plt.subplot(122)
    plt.title('CNN-Net')
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='validation')
    plt.xlabel('epoaches'); plt.ylabel('acc')
    plt.legend()


def svm_method(X_train, X_test, y_train, y_test):
    # clf_rbf = svm.SVC(kernel='rbf', C=0.1, gamma=0.1).fit(X_train, y_train)
    linear = svm.SVC(kernel='linear').fit(X_train, y_train)

    # res = clf_rbf.predict(X_test)
    res = linear.predict(X_test)

    count = 0
    assert res.shape[0] == y_test.shape[0]
    for data, label in zip(res, y_test):
        if data == label:
            count += 1
    acc = count/res.shape[0]
    print('sample result: {}/{}'.format(count, res.shape[0]))
    print('acc:%.2f%%' % acc)


if __name__ == "__main__":
    # raw_audio_process(RAW_PATH, DATA_PATH)
    # data_prepare(DATA_PATH, MODEL_PATH)
    X_train, X_test, y_train, y_test = data_load(MODEL_PATH, split_ratio=split_ratio, augment=aug)
    dense_net(X_train, X_test, y_train, y_test)
    # cnn_net(X_train, X_test, y_train, y_test)
    # svm_method(X_train, X_test, y_train, y_test)
    # plt.show()

