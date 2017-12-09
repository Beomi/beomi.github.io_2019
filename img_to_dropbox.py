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

dropbox_img_pattern = re.compile('https://www.dropbox.com/s/\w+/(.+\.png)')

md_files = search('./_posts', 'md')

def get_github_url(re_match_obj):
    origin_url = re_match_obj.group()
    ourstr = dropbox_img_pattern.findall(origin_url)[0]
    github_url = ourstr.replace('%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%20','')
    print('/img/dropbox/{})'.format(github_url))
    return '/img/dropbox/{})'.format(github_url)

for md in md_files:
    f = open(md, 'r')
    f_str = f.read()
    f.close()

    fw_str = re.sub('https://www.dropbox.com/s/\w+/(.+)', get_github_url, f_str)
    f = open(md, 'w')
    f.truncate()
    f.write(fw_str)
    f.close()

    dropbox_img_url_list = dropbox_img_pattern.findall(f_str)
    for img in dropbox_img_url_list:
        img = unquote(img.split('?')[0])
        s = os.path.join('/Users/beomi/Dropbox/스크린샷', img)
        if s:
            print(s)
            copyfile(s, '/Users/beomi/beomi.github.io/img/dropbox/' + img.replace('스크린샷 ',''))
