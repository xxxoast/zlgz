#coding:utf-8
from s3_screen_shot_and_process import cut_screen,pred_path
from s4_pred_every_block import predict_every_block

import pandas as pd
import os

desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
     
block_map_path       = os.path.join(desktop_path,'block_map.csv')
operation_path = os.path.join(desktop_path,'oplist.csv')

def create_block_map():
    block_map = pd.DataFrame(0, index = range(14), columns = range(10),dtype = int)
    pics = [ i.split('.')[0] for i in os.listdir(pred_path) if i.endswith('.png') ]
    for pic in pics:
        y,x,_c,_t,_s = pic.split('_')
        block_map.loc[int(y),int(x)] = int(_c)
        if _t == 'kb':
           block_map.loc[int(y),int(x)] = -1
        
    block_map.to_csv(block_map_path)

if __name__ == '__main__':
    cut_screen()
    predict_every_block()
    create_block_map()

    