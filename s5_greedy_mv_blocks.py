#coding:utf-8
import pandas as pd
import numpy as np
import os
import time
from mouse_simu import block_mouse_operation
from s3_screen_shot_and_process import block_h_line,block_v_line,block_size
from s3_screen_shot_and_process import block_path,pred_path
from misc import set_cursor_to_console

bmo = block_mouse_operation(block_size)

src_path = r'F:\zlgz\reorg_data\train_valid_test\train'
_classes = [ i for i in os.listdir(src_path) ]

global block_map

direc_map = {}
direcs    = range(4)
symbol = ['^','v','<','>']

opposite_direcs  = [1,0,3,2]
direcs_see_sides = [(2,3),(2,3),(0,1),(0,1)]

global block_map,stop_flag
global first_valid_up,first_valid_down,first_valid_left,first_valid_right
global first_invalid_up,first_invalid_down,first_invalid_left,first_invalid_right

block_id_loc_sets = {}
block_map_valid   = []
block_map_invalid = []

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

_not  = lambda x: not x
_yes  = lambda x: x

def update_valid_and_invalid_map_disappear_or_redisappear(x,y,_disappear = True):

    valid_invalid_zip = ((block_map_valid,is_valid,_yes), (block_map_invalid,not_valid,_not))
    
    _dir = 0
    for iblock_map,ifunc,ilogic in valid_invalid_zip:
        tblock = iblock_map[_dir]
        for i in range(y + 1,block_v_line):
            tblock.loc[i,x] =  tblock.loc[i - 1,x] if ilogic(_disappear) else y
            if ifunc(block_map.loc[i,x]):
                break
    
    _dir = 1
    for iblock_map,ifunc,ilogic in valid_invalid_zip:
        tblock = iblock_map[_dir]
        for i in range(y)[::-1]:
            tblock.loc[i,x] =  tblock.loc[i + 1,x] if ilogic(_disappear) else y
            if ifunc(block_map.loc[i,x]):
                break
    
    _dir = 2
    for iblock_map,ifunc,ilogic in valid_invalid_zip:
        tblock = iblock_map[_dir]
        for i in range(x + 1,block_h_line):
            tblock.loc[y,i] =  tblock.loc[y,i - 1] if ilogic(_disappear) else x
            if ifunc(block_map.loc[y,i]):
                break
    
    _dir = 3
    for iblock_map,ifunc,ilogic in valid_invalid_zip:
        tblock = iblock_map[_dir]
        for i in range(x)[::-1]:
            tblock.loc[y,i] =  tblock.loc[y,i + 1] if ilogic(_disappear) else x
            if ifunc(block_map.loc[y,i]):
                break

def update_valid_and_invalid_map_disappear(x,y):
    update_valid_and_invalid_map_disappear_or_redisappear(x, y, True)
    
def update_valid_and_invalid_map_redisappear(x,y):
    update_valid_and_invalid_map_disappear_or_redisappear(x, y, False)
    
# def first_valid(x,y,_dir):
#     ret = first_valid_or_invalid(x,y,_dir,is_valid)
#     print('first_valid:',(y,x),symbol[_dir],ret[::-1])
#     return ret
# 
# def first_invalid(x,y,_dir):
#     ret = first_valid_or_invalid(x,y,_dir,not_valid)
#     print('first_invalid:',(y,x),symbol[_dir],ret[::-1])
#     return ret

def first_valid(x,y,_dir,init = False):
    if init is True:
        ret = first_valid_or_invalid(x,y,_dir,is_valid)
#     print('first_valid:',(y,x),symbol[_dir],ret[::-1])
    else:
        x_or_y = block_map_valid[_dir].loc[y,x]
        if x_or_y == -1:
            return (-1,-1)
        ret = (x_or_y,y) if _dir > 1 else (x,x_or_y)
    return ret

def first_invalid(x,y,_dir,init = False):
    if init is True:
        ret = first_valid_or_invalid(x,y,_dir,not_valid)
#     print('first_invalid:',(y,x),symbol[_dir],ret[::-1])
    else:
        x_or_y = block_map_invalid[_dir].loc[y,x]
        if x_or_y == -1:
            return (-1,-1)
        ret = (x_or_y,y) if _dir > 1 else (x,x_or_y)
    return ret

def last_invalid(x,y,_dir):
    ret = first_valid(x,y,_dir)
    return ret

def last_valid(x,y,_dir):
    ret = first_invalid(x,y,_dir)
    return ret

def find_max_step(x,y,_dir):
    
    _x, _y   = first_invalid(x,y,_dir)
    if _x == -1 or _y == -1:
        return 0
    
    _x1,_y1  = last_invalid(_x,_y,_dir)
    
    if  _dir == 0:
        if _y1 == -1: 
            return _y + 1
        else:
            return _y - _y1
    
    elif  _dir == 1:
        if _y1 == -1: 
            return block_v_line - _y
        else:
            return _y1 - _y 
            
    elif  _dir == 2:
        if _x1 == -1: 
            return _x + 1
        else: 
            return _x - _x1
    
    elif  _dir == 3:
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
    
    _cache = []
    erase_len = np.abs(_y - y) + np.abs(_x - x)
    for i in range(erase_len):
        tt = xy_transform(x,y,_dir,i)
        _cache.append(block_map.loc[tt[1],tt[0]])
        block_id_loc_sets[ block_map.loc[tt[1],tt[0]] ].remove(tt)
        block_map.loc[tt[1],tt[0]] = -1
        update_valid_and_invalid_map_disappear(*tt)
        
#     if _dir == 0:
#         block_map.loc[_y - step + 1:y - step, x]  = block_map.loc[_y + 1:y, x].values
#         block_map.loc[ y - step + 1:y,        x]  = -1
#     elif _dir == 1:
#         block_map.loc[y + step:_y - 1 + step, x]  = block_map.loc[y: _y - 1,x].values
#         block_map.loc[       y:y + step - 1,  x]  = -1
#     if _dir == 2:
#         block_map.loc[y, _x - step + 1:x - step]  = block_map.loc[y, _x + 1:x].values
#         block_map.loc[y,  x - step + 1:x       ]  = -1
#     elif _dir == 3:
#         block_map.loc[y, x + step:_x + step - 1]  = block_map.loc[y, x:_x - 1].values
#         block_map.loc[y,        x:x  + step - 1]  = -1
    
    for i in range(erase_len):
        tt = xy_transform(x, y, _dir, i + step)
        block_map.loc[tt[1],tt[0]] = _cache[i]
        block_id_loc_sets[ block_map.loc[tt[1],tt[0]] ].add(tt)
        update_valid_and_invalid_map_redisappear(*tt)
        
#     print(block_map.head(n=14))

    smoke_for_awhile()
    return xy_transform(_x, _y, _dir, step - 1)

def xy_transform(x,y,_dir,step):
    if _dir == 0:
        return x, y - step
    elif _dir == 1:
        return x, y + step
    elif _dir == 2:
        return x - step, y 
    elif _dir == 3:
        return x + step, y

def try_move(x,y,_dir):
    
    _class = block_map.loc[y,x]

    (_x,_y) = first_valid(x,y,_dir)
    if is_same(x,y,_x,_y):
        disappear(x,y)
        #use block id set
        block_id_loc_sets[_class].remove((x,y))
        #use 4 dp map
        update_valid_and_invalid_map_disappear(x,y)
        
        disappear(_x,_y)
        block_id_loc_sets[_class].remove((_x,_y))
        update_valid_and_invalid_map_disappear(_x,_y)
        #click (x,y) (_x,_y)
        bmo.click_block(y,x)
        bmo.click_block(_y,_x)
        smoke_for_awhile()
        return True
    
    max_step = find_max_step(x,y,_dir)
    print('max_step :',max_step)
    
    #use block_id_set
    step_direc_zip = []
    for (_x,_y) in block_id_loc_sets[_class]:
        
        if (_x,_y) != (x,y):
            dx = x - _x
            dy = y - _y
            
            find_direc_x = 2 if dx > 0 else 3
            find_direc_y = 0 if dy > 0 else 1
            
            if _dir < 2   and ( _dir == find_direc_y ) and ( dx != 0 ) and ( 0 < np.abs(dy) <= max_step ):
                print((y,x),(_y,_x))
                step_direc_zip.append((np.abs(dy),find_direc_x))
                
            elif _dir > 1 and ( _dir == find_direc_x ) and ( dy != 0 ) and ( 0 < np.abs(dx) <= max_step ) :
                print((y,x),(_y,_x))
                step_direc_zip.append((np.abs(dx),find_direc_y))
    
    for i,_d in step_direc_zip:
        print('step_direc_zip = ',symbol[_dir],i,symbol[_d])
#         print(block_map)
        #move to (xt,yt)
        xt,yt   = xy_transform(x, y, _dir, i)
        #match (_x,_y)
        (_x,_y) = first_valid(xt, yt, _d)
        if is_same(x,y,_x,_y):
            #0
            xh,yh = move(x,y,i,_dir)
            #i
            disappear(_x,_y)
            block_id_loc_sets[_class].remove((_x,_y))
            update_valid_and_invalid_map_disappear(_x,_y)
            #ii
            disappear(xt,yt)
            block_id_loc_sets[_class].remove((xt,yt))
            update_valid_and_invalid_map_disappear(xt,yt)
            #iii
            bmo.move_block(y,x,i,_dir)
            bmo.click_block(_y,_x)
            if DEBUG is True:
                set_cursor_to_console()
            #iii
            return True
        
#     #don't use block_id_set       
#     for i in range(1,max_step + 1):
#         xt,yt = xy_transform(x, y, _dir, i)
#         for _d in direcs_see_sides[_dir]: 
#             (_x,_y) = first_valid(xt,yt,_d)
#             if is_same(x,y,_x,_y):
#                 move(x,y,i,_dir)
#                 disappear(_x,_y)
#                 disappear(xt,yt)
#                 #move block
#                 bmo.move_block(y,x,i,_dir)
#                 bmo.click_block(_y,_x)
#                 if DEBUG is True:
#                     set_cursor_to_console()
#                 return True
                           
    return False

def get_x_or_y_depend_on(x,y,_dir):
    return y if _dir < 2 else x

def create_block_map():
    global block_map
    block_map = pd.DataFrame(0, index = range(14), columns = range(10),dtype = int)
    pics = [ i.split('.')[0] for i in os.listdir(pred_path) if i.endswith('.png') ]
    for pic in pics:
        y,x,_c,_t,_s = pic.split('_')
        block_map.loc[int(y),int(x)] = int(_c)
        if _t == 'kb':
           block_map.loc[int(y),int(x)] = -1 
           
        if int(_c) not in block_id_loc_sets.keys():
            block_id_loc_sets[int(_c)] = set()
        block_id_loc_sets[int(_c)].add((int(x),int(y)))

    #first valid cache
    for i in direcs:
        block_map_valid.append(pd.DataFrame(0,index = range(14), columns = range(10),dtype = int))
        block_map_invalid.append(pd.DataFrame(0,index = range(14), columns = range(10),dtype = int))
        
    #init block_map_valid
    for x in range(block_h_line):
        for y in range(block_v_line):
            for _dir in direcs:
#                 _x,_y = xy_transform(x,y,_dir,1)
#                 this_block_map.loc[j,i] = is_valid(first_valid_up.loc[_j,_i]) if (( 0 < _j < block_v_line ) and ( 0 < _i < block_h_line ) ) else -1
                block_map_valid[_dir].loc[y,x]   = get_x_or_y_depend_on(*first_valid(x, y, _dir, True),  _dir)
                block_map_invalid[_dir].loc[y,x] = get_x_or_y_depend_on(*first_invalid(x, y, _dir, True),_dir)
       
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
                    if is_valid(block_map.loc[j,i]):
                        print('\nsearch y = {}, x = {}, dir = {}'.format(j,i,direction))
                        moved = try_move(i,j,direction)
                        if moved:
                            move_count += 1
                print('-------------------------------------')
                 
        if last_count == move_count:
            print('nothing to move')
            break
    print('total move = ',move_count)
    