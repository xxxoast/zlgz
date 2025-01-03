#coding:utf-8
import pyautogui
import os
import shutil
from mouse_simu import mouse_simu

console_x,console_y = (1038, 1001)
ms = mouse_simu()
def set_cursor_to_console():
    ms.mouse_left_click(console_x,console_y)

def clear_folder_pngs(src_path):
    pngs = [ i for i in os.listdir(src_path) if i.endswith('.png') or i.endswith('.jpg') ]
    for ipng in pngs:
        to_be_deleted = os.path.join(src_path,ipng)
        os.remove(to_be_deleted)

def get_cursor_position():
    try:
        x, y = pyautogui.position()
        print(f"鼠标坐标: ({x}, {y})")
    except pyautogui.FailSafeException as e:
        print(f"获取鼠标坐标失败: {e}")
    
def swap_folder_names(folder1_path, folder2_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder1_path) or not os.path.exists(folder2_path):
        raise ValueError("两个文件夹路径必须都存在")

    # 创建临时文件夹名称
    temp_folder_name = "temp_folder"
    temp_folder_path = os.path.join(os.path.dirname(folder1_path), temp_folder_name)

    # 将第一个文件夹移动到临时位置
    shutil.move(folder1_path, temp_folder_path)

    # 将第二个文件夹移动到第一个文件夹原来的位置
    shutil.move(folder2_path, folder1_path)

    # 将临时位置的文件夹（原来的第一个文件夹）移动到第二个文件夹原来的位置
    shutil.move(temp_folder_path, folder2_path)

if __name__ == '__main__':
    get_cursor_position()
        