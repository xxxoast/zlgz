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
pred_path2  = r'F:\zlgz\pred3'

WINDOW_TITLE = u'砖了个砖'

# game_windows  = (1872, 18, 2487, 1135)
# block_windows = (1900, 186,2462, 985)

#2015.11.02 new version
game_windows  = (1798, 28, 2488, 1277)
block_windows = (1828, 289,2457, 1181)

left_margin_ratio   = ( block_windows[0] - game_windows[0] ) / ( game_windows[2] - game_windows[0] )
top_margin_ratio    = ( block_windows[1] - game_windows[1] ) / ( game_windows[3] - game_windows[1] )
right_margin_ratio  = ( game_windows[2] - block_windows[2] ) / ( game_windows[2] - game_windows[0] )
bottom_margin_ratio = ( game_windows[3] - block_windows[3] ) / ( game_windows[3] - game_windows[1] )

left, top, right, bottom = 0, 0, 0, 0

block_h_line = 10
block_v_line = 14
global block_size
global all_square_list

margin_pixel_min_thres = 1000

def get_block_pos():
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
        return pos

    cur_game_pos = getGameWindow()

    global left, top, right, bottom
    left   = int(cur_game_pos[0] +  ( cur_game_pos[2]  - cur_game_pos[0] )* left_margin_ratio )
    top    = int(cur_game_pos[1] +  ( cur_game_pos[3]  - cur_game_pos[1] )* top_margin_ratio )
    right  = int(cur_game_pos[2] -  ( cur_game_pos[2]  - cur_game_pos[0] )* right_margin_ratio )
    bottom = int(cur_game_pos[3] -  ( cur_game_pos[3]  - cur_game_pos[1] )* bottom_margin_ratio )

    global block_size
    block_size = float(((right - left) / block_h_line + (bottom - top) / block_v_line) / 2)

    print('left = {}, top = {}, right = {}, bottom = {}, block_size = {}'.format(left,top,right,bottom,block_size))

def getScreenImage():
    print('Shot screen...')
    region = (left, top, right, bottom)
    print(region)
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
    screen_image = getScreenImage()
    dumpAllSquare(screen_image)

get_block_pos()

if __name__ == '__main__':
    cut_screen()