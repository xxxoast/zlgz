#coding:utf-8
import pandas as pd
import os
import time
from mouse_simu import block_mouse_operation,block_size
from s3_screen_shot_and_process import block_h_line,block_v_line
from s3_screen_shot_and_process import block_path,pred_path
from misc import set_cursor_to_console

bmo = block_mouse_operation(block_size)

src_path = r'F:\zlgz\reorg_data\train_valid_test\train'
_classes = [ i for i in os.listdir(src_path) ]

global block_map

direc_map = {}
direcs    = range(4)

symbol = ['^','v','<','>']

DEBUG = False
GAME_SPEED = 1

def smoke_for_awhile():
    if DEBUG is True:
        input()
        set_cursor_to_console()
    else:
        time.sleep(GAME_SPEED)

def is_valid(v):
    return v != -1

def not_valid(v):
    return v == -1

def is_same(x,y,_x,_y):
    if _x != -1 and _y != -1 and x != -1 and y != -1:
        return block_map.loc[y,x] == block_map.loc[_y,_x]
    else:
        return False

def first_valid_or_invalid(x,y,_dir,f):
    if _dir == 0:
        for i in range(y)[::-1]:
            if f(block_map.loc[i,x]):
                return (x,i)
    elif _dir == 1:
        for i in range(y+1,block_v_line):
            if f(block_map.loc[i,x]):
                return (x,i)
    if _dir == 2:
        for i in range(x)[::-1]:
            if f(block_map.loc[y,i]):
                return (i,y)
    elif _dir == 3:
        for i in range(x+1,block_h_line):
            if f(block_map.loc[y,i]):
                return (i,y)
                
    return (-1,-1)

def first_valid(x,y,_dir):
    ret = first_valid_or_invalid(x,y,_dir,is_valid)
    print('first_valid:',(y,x),symbol[_dir],ret[::-1])
    return ret

def first_invalid(x,y,_dir):
    ret = first_valid_or_invalid(x,y,_dir,not_valid)
    print('first_invalid:',(y,x),symbol[_dir],ret[::-1])
    return ret

def last_invalid_or_valid(x,y,_dir,f):
    if x == -1 or y == -1:
        return (-1,-1)
        
    if _dir == 0:
        for i in range(y)[::-1]:
            if f(block_map.loc[i,x]):
                return (x,i)
    elif _dir == 1:
        for i in range(y+1,block_v_line):
            if f(block_map.loc[i,x]):
                return (x,i)
    if _dir == 2:
        for i in range(x)[::-1]:
            if f(block_map.loc[y,i]):
                return (i,y)
    elif _dir == 3:
        for i in range(x+1,block_h_line):
            if f(block_map.loc[y,i]):
                return (i,y)

    return (-1,-1)

def last_invalid(x,y,_dir):
    ret = last_invalid_or_valid(x,y,_dir,is_valid)
    print('last_invalid:',(y,x),symbol[_dir],ret[::-1])
    return ret

def last_valid(x,y,_dir):
    ret = last_invalid_or_valid(x,y,_dir,not_valid)
    print('last_valid:',(y,x),symbol[_dir],ret[::-1])
    return ret

def find_max_step(x,y,_dir):
    
    _x, _y   = first_invalid(x,y,_dir)
    _x1,_y1  = last_invalid(_x,_y,_dir)
    
    if  _dir == 0 and _y != -1:
        if _y1 == -1: 
            return _y + 1
        else:
            return (_y - _y1)
    
    elif  _dir == 1 and _y != -1:
        if _y1 == -1: 
            return block_v_line - _y
        else:
            return _y1 - _y 
            
    elif  _dir == 2 and _x != -1:
        if _x1 == -1: 
            return _x + 1
        else: 
            return (_x - _x1)
    
    elif  _dir == 3 and _x != -1:
        if _x1 == -1: 
            return block_h_line - _x
        else:
            return _x1 - _x 

    return 0

def disappear(x,y):
    block_map.loc[y,x]  = -1
    print('disappear :',(y,x))

def move(x,y,step,_dir):
    _x,_y = last_valid(x,y,_dir)
    print('move :',(y,x,),symbol[_dir],(_y,_x),step)
#     print(block_map.head(n=14))
    if _dir == 0:
        block_map.loc[_y - step + 1:y - step, x]  = block_map.loc[_y + 1:y,x].values
        block_map.loc[ y - step + 1:y,        x]  = -1
    elif _dir == 1:
#         print((y + step,_y - 1 + step),(y,_y - 1))
#         print((y,y + step - 1))
        block_map.loc[y + step:_y - 1 + step, x]  = block_map.loc[y:_y - 1,x].values
        block_map.loc[       y:y + step - 1,  x]  = -1
    if _dir == 2:
        block_map.loc[y, _x - step + 1:x - step]  = block_map.loc[y, _x + 1:x].values
        block_map.loc[y,  x - step + 1:x       ]  = -1
    elif _dir == 3:
        block_map.loc[y, x + step:_x + step - 1]   = block_map.loc[y, x:_x - 1].values
        block_map.loc[y,        x:x  + step - 1]   = -1
#     print(block_map.head(n=14))
    smoke_for_awhile()
    
def try_move(x,y,_dir):
    
    (_x,_y) = first_valid(x,y,_dir)
    if is_same(x,y,_x,_y):
        disappear(x,y)
        disappear(_x,_y)
        #click (x,y) (_x,_y)
        bmo.click_block(y,x)
        bmo.click_block(_y,_x)
        smoke_for_awhile()
        return True
    
    max_step = find_max_step(x,y,_dir) + 1
    print('max_step :',max_step - 1)
    #up  
    if _dir == 0:        
        for i in range(1,max_step):
            for _d in [2,3]: 
                (_x,_y) = first_valid(x, y - i, _d)
                if is_same(x,y,_x,_y):
                    move(x,y,i,_dir)
                    disappear(_x,_y)
                    disappear(x,y - i)
                    #move block
                    bmo.move_block(y,x,i,_dir)
                    #可能出现同时消两个的情况，主动点掉一个
                    bmo.click_block(_y,_x)
                    if DEBUG is True:
                        set_cursor_to_console()
                    return True
            
    #down
    elif _dir == 1:        
        for i in range(1,max_step):
            for _d in [2,3]: 
                (_x,_y) = first_valid(x, y + i, _d)
                if is_same(x,y,_x,_y):
                    move(x,y,i,_dir)
                    disappear(_x,_y)
                    disappear(x,y + i)
                    #move block
                    bmo.move_block(y,x,i,_dir)
                    bmo.click_block(_y,_x)
                    if DEBUG is True:
                        set_cursor_to_console()
                    return True
    #left  
    elif _dir == 2:        
        for i in range(1,max_step):
            for _d in [0,1]: 
                (_x,_y) = first_valid(x - i, y, _d)
                if is_same(x,y,_x,_y):
                    move(x,y,i,_dir)
                    disappear(_x,_y)
                    disappear(x - i,y)
                    #move block
                    bmo.move_block(y,x,i,_dir)
                    bmo.click_block(_y,_x)
                    if DEBUG is True:
                        set_cursor_to_console()
                    return True            
    #right  
    elif _dir == 3:        
        for i in range(1,max_step):
            for _d in [0,1]: 
                (_x,_y) = first_valid(x + i, y, _d)
                if is_same(x,y,_x,_y):
                    move(x,y,i,_dir)
                    disappear(_x,_y)
                    disappear(x + i,y)
                    #move block
                    bmo.move_block(y,x,i,_dir)
                    bmo.click_block(_y,_x)
                    if DEBUG is True:
                        set_cursor_to_console()
                    return True            
                  
    return False

def create_block_map():
    global block_map
    block_map = pd.DataFrame(0, index = range(14), columns = range(10),dtype = int)
    pics = [ i.split('.')[0] for i in os.listdir(pred_path) if i.endswith('.png') ]
    for pic in pics:
        y,x,_c,_t,_s = pic.split('_')
        block_map.loc[int(y),int(x)] = int(_c)
        if _t == 'kb':
           block_map.loc[int(y),int(x)] = -1 

if __name__ == '__main__':    
    
#     block_map = pd.read_csv('block_map.csv',index_col = 0)
#     block_map.columns = range(10)
    
    create_block_map()
    
    move_count = 0
    while True:
        last_count = move_count
         
        for i in range(block_h_line):
            for j in range(block_v_line):
                for direction in range(4):
                    if is_valid(block_map.loc[j,i]) != -1:
                        print('\nsearch y = {}, x = {}, dir = {}'.format(j,i,direction))
                        moved = try_move(i,j,direction)
                        if moved:
                            move_count += 1
                print('-------------------------------------')
                 
        if last_count == move_count:
            print('nothing to move')
            break
        