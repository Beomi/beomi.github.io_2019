---
author: livingmethod
comments: true
date: 2016-05-27 09:22:04+00:00
layout: post
link: http://blog.jblee.kr/2016/05/27/pip%eb%a1%9c-mysqlclient%ec%84%a4%ec%b9%98-%ec%a4%91-mac-os-x%ec%97%90%ec%84%9c-egg_info-oserror-%eb%b0%9c%ec%83%9d%ec%8b%9c-%eb%8c%80%ec%b2%98%eb%b0%a9%eb%b2%95/
slug: pip%eb%a1%9c-mysqlclient%ec%84%a4%ec%b9%98-%ec%a4%91-mac-os-x%ec%97%90%ec%84%9c-egg_info-oserror-%eb%b0%9c%ec%83%9d%ec%8b%9c-%eb%8c%80%ec%b2%98%eb%b0%a9%eb%b2%95
title: pip로 mysqlclient설치 중 mac os x에서 egg_info / OSError 발생시 대처방법
wordpress_id: 2
categories:
- Python
tags:
- brew
- mac
- Python
image: https://livingmethod.files.wordpress.com/2016/05/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-05-27-e1848be185a9e18492e185ae-6-19-59.png?w=809
---

[![스크린샷 2016-05-27 오후 6.19.59](https://livingmethod.files.wordpress.com/2016/05/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-05-27-e1848be185a9e18492e185ae-6-19-59.png?w=809)
](https://livingmethod.files.wordpress.com/2016/05/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-05-27-e1848be185a9e18492e185ae-6-19-59.png)

    
    (venv) Beomiui-MacBook:Downloads beomi$ pip install mysqlclient-1.3.7.tar.gz
     Processing ./mysqlclient-1.3.7.tar.gz
     Complete output from command python setup.py egg_info:
     /bin/sh: mysql_config: command not found
     Traceback (most recent call last):
     File "", line 20, in
     File "/var/folders/52/v_mf5ys167q67b6cn_hnfzg00000gn/T/pip-0zi6xkoz-build/setup.py", line 17, in
     metadata, options = get_config()
     File "/private/var/folders/52/v_mf5ys167q67b6cn_hnfzg00000gn/T/pip-0zi6xkoz-build/setup_posix.py", line 44, in get_config
     libs = mysql_config("libs_r")
     File "/private/var/folders/52/v_mf5ys167q67b6cn_hnfzg00000gn/T/pip-0zi6xkoz-build/setup_posix.py", line 26, in mysql_config
     raise EnvironmentError("%s not found" % (mysql_config.path,))
     OSError: mysql_config not found
    
    ----------------------------------------
     Command "python setup.py egg_info" failed with error code 1 in /var/folders/52/v_mf5ys167q67b6cn_hnfzg00000gn/T/pip-0zi6xkoz-build
     You are using pip version 7.1.2, however version 8.1.2 is available.
     You should consider upgrading via the 'pip install --upgrade pip' command.
    



    
    (venv) Beomiui-MacBook:Downloads beomi$ brew install mysql
     ==> Downloading https://homebrew.bintray.com/bottles/mysql-5.7.12.el_capitan.bottle.tar.gz
     ######################################################################## 100.0%
     ==> Pouring mysql-5.7.12.el_capitan.bottle.tar.gz
     ==> /usr/local/Cellar/mysql/5.7.12/bin/mysqld --initialize-insecure --user=beomi --basedir=/usr/local/Cellar/mysql/5.7.12 --datadir=/usr/local/var/mysql --tmpdir=/tmp
     ==> Caveats
     We've installed your MySQL database without a root password. To secure it run:
     mysql_secure_installation
    To connect run:
     mysql -uroot
    To have launchd start mysql now and restart at login:
     brew services start mysql
     Or, if you don't want/need a background service you can just run:
     mysql.server start
     ==> Summary
     🍺 /usr/local/Cellar/mysql/5.7.12: 13,281 files, 444.8M



    
     (venv) Beomiui-MacBook:Downloads beomi$ pip install mysqlclient-1.3.7.tar.gz
     Processing ./mysqlclient-1.3.7.tar.gz
     Installing collected packages: mysqlclient
     Running setup.py install for mysqlclient
     Successfully installed mysqlclient-1.3.7
     You are using pip version 7.1.2, however version 8.1.2 is available.
     You should consider upgrading via the 'pip install --upgrade pip' command.


이와 같이

    
    brew install mysql


을 진행하면 된다.
