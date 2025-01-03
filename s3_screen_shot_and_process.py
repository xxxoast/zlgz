#coding:utf-8
#screen shot
import os,sys
import cv2
import numpy as np
import win32api,win32gui,win32con
from PIL import ImageGrab,Image
import time
import random
import itertools

desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    
des_path   = os.path.join(desktop_path,'screen.png')

block_path = r'F:\zlgz\blocks'
pred_path  = r'F:\zlgz\pred2'

WINDOW_TITLE = u'砖了个砖'

left   = 1827 
top    = 182
right  = 2431
bottom = 1036

#hx90
# left   = 1358
# top    = 169
# right  = 1892
# bottom = 934

block_h_line = 10
block_v_line = 14

block_size = float( ( ( right - left ) / block_h_line + ( bottom - top ) / block_v_line )  / 2)

# print('block_size = ',block_size)

margin_pixel_min_thres = 1000

global all_square_list

def getGameWindow():
    # FindWindow(lpClassName=None, lpWindowName=None)  窗口类名 窗口标题名
    window = win32gui.FindWindow(None, WINDOW_TITLE)
    print(window)

    while not window:
        print('Failed to locate the game window , reposition the game window after 10 seconds...')
        time.sleep(10)
        window = win32gui.FindWindow(None, WINDOW_TITLE)

    win32gui.SetForegroundWindow(window)
    pos = win32gui.GetWindowRect(window)
    print("Game windows at " + str(pos))
    return (pos[0], pos[1])

def getScreenImage():
    print('Shot screen...')
    region = (left, top, right, bottom)
    scim = ImageGrab.grab(region)
    scim.save(des_path)
    return cv2.imread(des_path)

def dumpAllSquare(screen_image):
#     cv2.imshow('Generated Image', screen_image)
    print('Processing pictures...')
    dump_path = os.path.join(block_path,'unknown')
    for x in range(0, block_v_line):
        for y in range(0, block_h_line):
            square = screen_image[int(x * block_size):int((x + 1) * block_size),int(y * block_size):int((y + 1) * block_size)]
            if square.size > margin_pixel_min_thres:
                cv2.imwrite(os.path.join(dump_path,'{}_{}.png'.format(x,y)), square) 
    return 

def cut_screen():
    getGameWindow()
    screen_image = getScreenImage()
    dumpAllSquare(screen_image)
    
if __name__ == '__main__':
    getGameWindow()
    screen_image = getScreenImage()
    