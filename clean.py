import glob
import os
import sys

def list_dir(path, ext='*.*', recursive=False) -> list:
    """_summary_

    Args:
        path (_type_): path
        ext (str, optional): _description_. Defaults to '.*'.
        recursive (bool, optional): _description_. Defaults to False.

    Returns:
        list: list of files from defined path
    """
    work_list = []
    os.chdir(path)
    # print(os.getcwd())
    for file in glob.iglob(ext):
        work_list.append(file)
    return work_list

def get_file_size(file, out='kb'):
    if out == 'kb': out_div = 1024; ext = 'KB'
    elif out == 'mb': out_div = 1024*1024; ext = 'MB'
    return f'{file} : {round(os.stat(file).st_size/out_div,2)}{ext}'
        
# print(get_file_stat('/home/twarr58/.bash_history'))
for file in list_dir('/usr/bin', recursive=True):
    print(get_file_size(file))


