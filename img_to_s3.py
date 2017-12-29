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

img_pattern = re.compile('\\(/img/.+')

md_files = search('./_posts', 'md')

def get_github_url(re_match_obj):
    origin_url = re_match_obj.groups()[0]
    return '({{site.static_url}}'+'{}'.format(origin_url)

for md in md_files:
    f = open(md, 'r')
    f_str = f.read()
    f.close()

    s3_url = 'https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com'
    fw_str = re.sub('image: (/img/.+)', lambda x: 'image: '+ s3_url +x.groups()[0], f_str)
    fw_str = re.sub('\\((/img/.+)', get_github_url, fw_str)

    f = open(md, 'w')
    f.truncate()
    f.write(fw_str)
    f.close()
