#coding:utf-8

from mouse_simu import block_mouse_operation
from s3_screen_shot_and_process import block_size
from autorun import operation_path

import os
import pandas as pd
import time

desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

def auto_move():

    cpp_exe_path = os.path.join(desktop_path,r'dfs_move.cpp.exe')
    os.system(cpp_exe_path)
    
    bmo = block_mouse_operation(block_size)
    df = pd.read_csv(operation_path,header = None,dtype = int)
    print(df.head())
     
    for i,row in df.iterrows():
        y,x,step,_dir = row[1],row[2],row[3],row[4]
        print(y,x,step,_dir)
        if row[0] == 0:
            bmo.click_block(y,x)
        elif row[0] == 1:
            bmo.move_block(y,x,step,_dir)
#         time.sleep(0.5)
        
if __name__ == '__main__':
    auto_move()
    