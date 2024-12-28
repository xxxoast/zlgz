# -*- coding:utf-8 -*-
import cv2
import numpy as np
import win32api
import win32gui
import win32con
from PIL import ImageGrab
import time
import random

from s3_screen_shot_and_process import left,top,right,bottom,\
                                block_h_line,block_v_line,\
                                block_size

class mouse_simu(object):
    
    def __init__(self,TIME_INTERVAL_MIN = 0.3, TIME_INTERVAL_MAX = 0.5):
        self.num_steps = 5
        self.sleep_per_time = 0.01
        self.TIME_INTERVAL_MIN,self.TIME_INTERVAL_MAX = TIME_INTERVAL_MIN,TIME_INTERVAL_MAX 
    
    def set_cursor(self,x,y):
        win32api.SetCursorPos((x, y))
        time.sleep(random.uniform(self.TIME_INTERVAL_MIN, self.TIME_INTERVAL_MAX))

    def mouse_left_click(self,x,y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
        time.sleep(random.uniform(self.TIME_INTERVAL_MIN, self.TIME_INTERVAL_MAX))
    
    def mouse_up(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    
    def mouse_down(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    
    def mouse_move(self, x, y):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)
    
    def drag_mouse(self, start_x, start_y, target_x, target_y):
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        max_coord = 65535
    
        start_x_abs  = int(start_x / screen_width * max_coord)
        start_y_abs  = int(start_y / screen_height * max_coord)
        target_x_abs = int(target_x / screen_width * max_coord)
        target_y_abs = int(target_y / screen_height * max_coord)
        

        self.mouse_down(start_x, start_y)

        step_x = (target_x_abs - start_x_abs) / self.num_steps
        step_y = (target_y_abs - start_y_abs) / self.num_steps

        for _ in range(self.num_steps):
            start_x_abs += step_x
            start_y_abs += step_y
            self.mouse_move(int(start_x_abs), int(start_y_abs))
            time.sleep(self.sleep_per_time)  
    

        self.mouse_up(target_x, target_y)
        time.sleep(random.uniform(self.TIME_INTERVAL_MIN, self.TIME_INTERVAL_MAX))
        
class block_mouse_operation(object):
    
    def __init__(self,block_size):
        self.ms = mouse_simu()
        self.block_size = block_size

    def click_block(self, y, x):
        _x = left + int( x * self.block_size ) + int ( self.block_size / 2 )
        _y = top  + int( y * self.block_size ) + int ( self.block_size / 2 )
        self.ms.mouse_left_click(_x,_y)
    
    def move_block(self, y, x, step, _dir):
        
        _x = left + int( x * self.block_size ) + int ( self.block_size / 2 )
        _y = top  + int( y * self.block_size ) + int ( self.block_size / 2 )
        #^
        if _dir == 0:
            _x1 = _x
            _y1 = _y - int( step * self.block_size )
        #v
        if _dir == 1:
            _x1 = _x
            _y1 = _y + int( step * self.block_size )
        #<
        if _dir == 2:
            _x1 = _x - int( step * self.block_size )
            _y1 = _y 
        #>
        if _dir == 3:
            _x1 = _x + int( step * self.block_size )
            _y1 = _y
           
        self.ms.drag_mouse(_x,_y,_x1,_y1)

def unitest_click():
    bmo = block_mouse_operation(block_size)
    bmo.click_block(0,0)
    bmo.click_block(0,2)

def unitest_move():
    bmo = block_mouse_operation(block_size)
    bmo.move_block(0,2,1,1)

if __name__ == '__main__':
    unitest_click()
    unitest_move()
    
     