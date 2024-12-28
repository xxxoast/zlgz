#coding:utf-8
from s3_screen_shot_and_process import cut_screen
from s4_pred_every_block import predict_every_block

if __name__ == '__main__':
    cut_screen()
    predict_every_block()