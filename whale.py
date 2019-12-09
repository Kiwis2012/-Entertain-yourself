'''

    humpback whale identification

    https://www.kaggle.com/c/humpback-whale-identification/overview

    still working
    the basic code was from
    no use of CUDA, performs better if pre-trained models loaded
'''
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader,Dataset
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
import torch.optim as optim
from torch.optim import lr_scheduler
import time
from PIL import Image
# train_on_gpu = True
from torch.utils.data.sampler import SubsetRandomSampler
import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)

DATA_PATH = 'G:/Datasets/humpback-whale-identification/'

train_df = pd.read_csv(DATA_PATH + 'train.csv')

print(f"There are {len(os.listdir(DATA_PATH + 'train'))} images in train dataset with {train_df.Id.nunique()} unique classes.")
print(f"There are {len(os.listdir(DATA_PATH + 'test'))} images in test dataset.")

fig = plt.figure(figsize=(25, 4))
train_imgs = os.listdir(DATA_PATH + "train")
for idx, img in enumerate(np.random.choice(train_imgs, 20)):
    ax = fig.add_subplot(2, 20//2, idx+1, xticks=[], yticks=[])
    im = Image.open(DATA_PATH + "train/" + img)
    plt.imshow(im)
    lab = train_df.loc[train_df.Image == img, 'Id'].values[0]
    ax.set_title(f'Label: {lab}')

for i in range(1, 4):
    print(f'There are {train_df.Id.value_counts()[train_df.Id.value_counts().values==i].shape[0]} classes with {i} samples in train data.')

data_transforms = transforms.Compose([
                                      transforms.Resize((100, 100)),
                                      transforms.ToTensor(),
                                      transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                             std=[0.229, 0.224, 0.225])
    ])
data_transforms_test = transforms.Compose([
                                           transforms.Resize((100, 100)),
                                           transforms.ToTensor(),
                                           transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                 std=[0.229, 0.224, 0.225])
])

def prepare_labels(y):
    # From here: https://www.kaggle.com/pestipeti/keras-cnn-starter
    values = np.array(y)
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    onehot_encoder = OneHotEncoder(sparse=False, categories='auto')
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    y = onehot_encoded
    return y, label_encoder

y, le = prepare_labels(train_df['Id'])

class WhaleDataset(Dataset):
    def __init__(self, datafolder, datatype='train', df=None, transform=transforms.Compose([transforms.ToTensor()]),
                 y=None):
        self.datafolder = datafolder
        self.datatype = datatype
        self.y = y
        if self.datatype == 'train':
            self.df = df.values
        self.image_files_list = [s for s in os.listdir(datafolder)]
        self.transform = transform

    def __len__(self):
        return len(self.image_files_list)

    def __getitem__(self, idx):
        if self.datatype == 'train':
            img_name = os.path.join(self.datafolder, self.df[idx][0])
            label = self.y[idx]

        elif self.datatype == 'test':
            img_name = os.path.join(self.datafolder, self.image_files_list[idx])
            label = np.zeros((5005,))

        image = Image.open(img_name).convert('RGB')
        image = self.transform(image)
        if self.datatype == 'train':
            return image, label
        elif self.datatype == 'test':
            # so that the images will be in a correct order
            return image, label, self.image_files_list[idx]


train_dataset = WhaleDataset(datafolder=DATA_PATH + 'train/', datatype='train',
                             df=train_df, transform=data_transforms, y=y)
test_set = WhaleDataset(datafolder=DATA_PATH + 'test/', datatype='test',
                        transform=data_transforms_test)

train_sampler = SubsetRandomSampler(list(range(len(os.listdir(DATA_PATH + 'train')))))
valid_sampler = SubsetRandomSampler(list(range(len(os.listdir(DATA_PATH + 'test')))))
# batch_size = 512  # just not enough RAM
batch_size = 256
num_workers = 0

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, sampler=train_sampler, num_workers=num_workers)
# less size for test loader.
test_loader = torch.utils.data.DataLoader(test_set, batch_size=32, num_workers=num_workers)

# Basic CNN

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 7, padding=1)
        self.conv2_bn = nn.BatchNorm2d(32)
        self.pool = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool2 = nn.AvgPool2d(3, 3)

        self.fc1 = nn.Linear(64 * 4 * 4 * 16, 1024)
        self.fc2 = nn.Linear(1024, 5005)

        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv2_bn(self.conv1(x))))
        x = self.pool2(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 4 * 4 * 16)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x

# print(torch.cuda.is_available())
# Initializing model
model_conv = Net()
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model_conv.parameters(), lr=0.01)
exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

# model_conv.cuda()
n_epochs = 5
for epoch in range(1, n_epochs+1):
    print(time.ctime(), 'Epoch:', epoch)
    train_loss = []

    for batch_i, (data, target) in enumerate(train_loader):
        print(batch_i)
        # data, target = data.cuda(), target.cuda()
        optimizer.zero_grad()
        output = model_conv(data)
        loss = criterion(output, target.float())
        train_loss.append(loss.item())
        loss.backward()
        optimizer.step()
    exp_lr_scheduler.step()
    print(f'Epoch {epoch}, train loss: {np.mean(train_loss):.4f}')

sub = pd.read_csv(DATA_PATH + 'sample_submission.csv')
model_conv.eval()
for (data, target, name) in test_loader:
    # data = data.cuda()
    output = model_conv(data)
    output = output.cpu().detach().numpy()
    for i, (e, n) in enumerate(list(zip(output, name))):
        sub.loc[sub['Image'] == n, 'Id'] = ' '.join(le.inverse_transform(e.argsort()[-5:][::-1]))
sub.to_csv('submission.csv', index=False)

