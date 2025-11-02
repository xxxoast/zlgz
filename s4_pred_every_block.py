#coding:utf-8
#classified into blocks
import os
import torch
import torchvision
from torch import nn
from d2l import torch as d2l
from PIL import Image
import numpy as np
from misc import clear_folder_pngs

from s2_train_resnet_classify import transform_test,ft_model_path,batch_size,data_dir
from s3_screen_shot_and_process import block_path,pred_path,pred_path2

warning_thres_hold = 0.75

test_ds = torchvision.datasets.ImageFolder(block_path, transform=transform_test) 
test_iter = torch.utils.data.DataLoader(test_ds, batch_size, shuffle=False, drop_last=False)

test_input = torchvision.datasets.ImageFolder(block_path).imgs
test_input_iter = [ test_input[ i * batch_size: (i+1) * batch_size ] for i in range(len(test_input)//batch_size + 1) ]


def predict_every_block():
    net = torch.load(ft_model_path, weights_only=False)
    devices = d2l.try_all_gpus()
    pngs = os.listdir(os.path.join(data_dir,'train_valid_test','train'))
    
    clear_folder_pngs(pred_path)
    clear_folder_pngs(pred_path2)

    uncertains = []

    for (data, label), src_iter in zip(test_iter,test_input_iter):
        output = torch.nn.functional.softmax(net(data.to(devices[0])), dim=1)
        tmp = output.cpu().detach().numpy()
        for iimg,ioutput in zip(src_iter,tmp):
            idx = np.argmax(ioutput)
            image = Image.open(iimg[0])
            image_name = os.path.split(iimg[0])[-1].split('.')[0]
            
            des_path = os.path.join(pred_path,'_'.join((image_name,str(idx),pngs[idx],'{:.2f}'.format(np.max(ioutput)))) + '.png')
            image.save(des_path)
            
            #人工智障
            des_path2 = os.path.join(pred_path2,'_'.join((str(idx),pngs[idx],image_name,'{:.2f}'.format(np.max(ioutput)))) + '.png')
            image.save(des_path2)
             
            if np.max(ioutput) < warning_thres_hold:
                print(image_name,idx,pngs[idx],np.max(ioutput))
                uncertains.append((image_name,idx,pngs[idx],np.max(ioutput)))

    return uncertains
                
if __name__ == '__main__':
    predict_every_block()
    
            