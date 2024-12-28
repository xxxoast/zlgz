#coding:utf-8
import random
from PIL import Image
import os
import shutil
import pandas as pd
from misc import clear_folder_pngs,swap_folder_names

from torchvision import transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomAffine(degrees = 0, translate=(0.08, 0.08))
])

desired_length = 10

src_dir = r'F:\zlgz\reorg_data'

def convert(img_path,out_path):
    img = Image.open(img_path)
    imgt = transform(img)
    imgt.save(out_path)

#add new class for train
#add folder--new_class--img0,img1,img2...
def random_create_train_data(retransform = False):
    train_path = os.path.join(src_dir,'train_valid_test','train')
    for root,cur_dir,files in os.walk(train_path):
        for idir in cur_dir:
            print(idir)
            pngs = [ os.path.join(root,idir,i) for i in os.listdir(os.path.join(root,idir)) if i.endswith('.png') or i.endswith('.jpg')] 
    
            cur_len = len(pngs)
            fill_length =  desired_length - len(pngs)
            
            if retransform is True:
                for i in pngs:
                    convert(i,i)
            
            for i in range(fill_length):
                out_path = os.path.join(root, idir, str(cur_len + i) + '.png' )
                r = random.randint(0,cur_len-1)
                convert(pngs[r],out_path)
    print('done')

# from folder--class0--img0,img1,img2,img3...
#            --class0--img0,img1,img2,img3...    
# create folder--img_class0_0,img_class0_1...
#              --labels.csv
# than use d2l reorg data to create train/train_valid/valid/test dataset       
#生成d2l标准数据格式文件夹
def create_d2l_data_src():
    src_path = os.path.join(src_dir,'train_valid_test','train')
    des_path = os.path.join(src_dir,'train2')
    
    if not os.path.exists(des_path):
        os.mkdir(des_path)
    
    clear_folder_pngs(des_path)
    
    df = pd.DataFrame(columns = ['id','breed'])
    
    for root_dir,cur_dir,files in os.walk(src_path):
        for idir in cur_dir:
            label = idir
            print(idir)
            pngs = [ os.path.join(root_dir,idir,i) for i in os.listdir(os.path.join(root_dir,idir)) if i.endswith('.jpg') or i.endswith('.png')] 
            for src_img_path in pngs:
                fname = os.path.split(src_img_path)[-1]
                des_img_path = os.path.join(des_path, idir + fname)
                
                #print(src_img_path,des_img_path)
                shutil.copy(src_img_path,des_img_path)
                new_row = {'id':os.path.split(des_img_path)[-1].split('.')[0] , 'breed':idir}
                new_df = pd.DataFrame([new_row])
                df = pd.concat([df, new_df], ignore_index=True)
    
    df.to_csv(os.path.join(src_dir,r'labels.csv'),index = False)
    swap_folder_names(os.path.join(src_dir,'train2'),os.path.join(src_dir,'train'))
    
    print('done')
    
def png2jpg():
    _root_path = r'F:\zlgz\reorg_data\train_valid_test'
    for root_dir,cur_dir,files in os.walk(_root_path):
        for idir in cur_dir:
            label = idir
            pngs = [ i for i in os.listdir(os.path.join(root_dir,idir)) if i.endswith('.png')] 
            for src_img_path in pngs:
                fname = src_img_path.split('.')[:-1]
                fname = '.'.join(fname)                
                src_img_path = os.path.join(root_dir, idir, fname + '.png')
                des_img_path = os.path.join(root_dir, idir, fname + '.jpg')
                print(src_img_path,des_img_path)
                img = Image.open(src_img_path)
                img.save(des_img_path)
                os.remove(src_img_path)
    
    
if __name__ == '__main__':
#     random_create_train_data()
#     create_d2l_data_src()
    pass

    
    