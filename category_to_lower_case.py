import re
import os
from urllib.parse import unquote
from shutil import copyfile


def search(dirname, i_filename=None):
    _list = []
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        if i_filename:
            if i_filename in filename:
                _list.append(full_filename)
    return _list

category_patterns = re.compile('categories:\n(.+)\npublished', flags=re.S)

md_files = search('./_posts', 'md')

for md in md_files:
    f = open(md, 'r')
    f_str = f.read()
    f.close()
    
    fw_str = category_patterns.sub(lambda x: x[0].lower(), f_str)

    # print(fw_str)

    f = open(md, 'w')
    f.truncate()
    f.write(fw_str)
    f.close()
