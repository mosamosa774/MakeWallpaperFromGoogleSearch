# soup -*- coding: utf-8 -*-
import sys
import os
import cv2
import numpy as np
from PIL import Image
import GoogleSearchImgs as GSI


def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = min(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)


def vconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    w_min = min(im.shape[1] for im in im_list)
    im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in im_list]
    return cv2.vconcat(im_list_resize)


def concat_tile_resize(im_list_2d, interpolation=cv2.INTER_CUBIC):
    im_list_v = [hconcat_resize_min(
        im_list_h, interpolation=cv2.INTER_CUBIC) for im_list_h in im_list_2d]
    return vconcat_resize_min(im_list_v, interpolation=cv2.INTER_CUBIC)


_max = int(sys.argv[1])
size = {}
size['width'] = int(sys.argv[2])
size['height'] = int(sys.argv[3])
word = sys.argv[4]
try:
    i = 0
    while(True):
        word += " " + sys.argv[5 + i]
        i += 120
except:
    print("search max", _max)
    print("search word", word)
    print("wallpaper size", size)
imgs = GSI.translateBase64_2_Img(GSI.getSearchedImages(_max, word))

#imgs = []
# for i in range(100):
#    imgs.append(cv2.imread('output_2019-01-02_13_23_12/img' + str(i) + '.jpg'))
param = []
try:
    if (size['width'] >= size['height']):
        alphaH = 1
        alphaW = size['width'] / size['height']
        oneImgCounts = len(imgs) / (alphaH + alphaW)
        x_limit = int(alphaW * oneImgCounts + 0.5)
        y_limit = int(alphaH * oneImgCounts + 0.5)
        print(oneImgCounts, alphaH, alphaW, x_limit, y_limit)
        while ((x_limit * y_limit) > len(imgs)):
            x_limit = int(0.9*x_limit+0.5)
            y_limit = int(0.9*y_limit+0.5)
        print(x_limit, y_limit)
        count = 0
        for i in range(y_limit):
            count += 1
            param.append(
                [j for j in imgs[i * x_limit:i * x_limit + x_limit - 1]])
        for i in imgs[x_limit*count:len(imgs) - 1]:
            param[len(param)-1].append(i)
    else:
        alphaH = size['height'] / size['width']
        alphaW = 1
        oneImgCounts = len(imgs) / (alphaH + alphaW)
        x_limit = int(alphaW * oneImgCounts + 0.5)
        y_limit = int(alphaH * oneImgCounts + 0.5)
        print(oneImgCounts, alphaH, alphaW, x_limit, y_limit)
        while ((x_limit * y_limit) > len(imgs)):
            x_limit = int(0.9*x_limit + 0.5)
            y_limit = int(0.9*y_limit + 0.5)
        print(x_limit, y_limit)
        count = 0
        for i in range(y_limit):
            count += 1
            param.append(
                [j for j in imgs[i * x_limit:i * x_limit + x_limit - 1]])
        param.append([i for i in imgs[x_limit * count:len(imgs) - 1]])
except:
    print('error', count)
    pass

width = len(param[0])
delflg = []
for i in range(len(param)):
    if (len(param[i]) == 0):
        delflg.append(i)
    elif ((len(param[i]) - width) > width/2):
        param.append([j for j in param[i][width - 1:-1]])
        del param[i][width - 1:-1]

for i in reversed(delflg):
    print('del', i)
    del param[i]

print('col', len(param))
for i in param:
    print('raw', len(i))

im_tile_resize = concat_tile_resize(param)
cv2.imwrite('output_wallpaper.jpg', im_tile_resize)

print('start resize')
img = Image.open('output_wallpaper.jpg')

img_resize_lanczos = img.resize((size['width'], size['height']), Image.LANCZOS)
img_resize_lanczos.save('output_wallpaper_resized.jpg',)
