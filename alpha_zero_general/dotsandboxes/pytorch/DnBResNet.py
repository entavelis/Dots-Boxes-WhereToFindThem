import sys
sys.path.append('..')
try:
    from utils import *
except:
    from alpha_zero_general.utils import *

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

import torch.nn as nn
import math
import torch.utils.model_zoo as model_zoo


def conv3x3(in_planes, out_planes, stride=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out

class ResNet(nn.Module):

    def __init__(self, game, args, num_of_blocks = 5):
        super(ResNet, self).__init__()

        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args
        self.num_of_blocks = num_of_blocks

        self.conv1 = nn.Conv2d(1, args.num_channels, 3, stride=1, padding=1)
        # self.conv1 = nn.Conv2d(1, args.num_channels, kernel_size=3, stride=1, padding=1,

        self.bn1 = nn.BatchNorm2d(args.num_channels)
        self.relu = nn.ReLU(inplace=True)


        self.layers = []
        for _ in range(self.num_of_blocks):
            self.layers.append(BasicBlock(args.num_channels, args.num_channels))
            if args.cuda:
                self.layers[-1] = self.layers[-1].cuda()

        self.fc1 = nn.Linear(args.num_channels*(self.board_x)*(self.board_y), 1024)
        self.fc_bn1 = nn.BatchNorm1d(1024)

        self.fc2 = nn.Linear(1024, 512)
        self.fc_bn2 = nn.BatchNorm1d(512)

        self.fc3 = nn.Linear(512, self.action_size)

        self.fc4 = nn.Linear(512, 1)

    def forward(self, x):
        x = x.view(-1, 1, self.board_x, self.board_y)                # batch_size x 1 x board_x x board_y
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        for i in range(self.num_of_blocks):
            x = self.layers[i](x)

        x = x.view(x.size(0), -1)

        x = F.dropout(F.relu(self.fc_bn1(self.fc1(x))), p=self.args.dropout, training=self.training)  # batch_size x 1024
        x = F.dropout(F.relu(self.fc_bn2(self.fc2(x))), p=self.args.dropout, training=self.training)  # batch_size x 512

        pi = self.fc3(x)                                                                         # batch_size x action_size
        v = self.fc4(x)                                                                          # batch_size x 1

        return F.log_softmax(pi, dim=1), F.tanh(v)


