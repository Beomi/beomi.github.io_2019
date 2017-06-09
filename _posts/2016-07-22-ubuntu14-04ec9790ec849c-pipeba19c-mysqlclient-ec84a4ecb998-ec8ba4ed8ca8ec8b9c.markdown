---
author: livingmethod
comments: true
date: 2016-07-22
layout: post
link: http://blog.jblee.kr/2016/07/22/ubuntu14-04%ec%97%90%ec%84%9c-pip%eb%a1%9c-mysqlclient-%ec%84%a4%ec%b9%98-%ec%8b%a4%ed%8c%a8%ec%8b%9c/
slug: ubuntu14-04%ec%97%90%ec%84%9c-pip%eb%a1%9c-mysqlclient-%ec%84%a4%ec%b9%98-%ec%8b%a4%ed%8c%a8%ec%8b%9c
title: Ubuntu14.04에서 pip로 mysqlclient 설치 실패시
wordpress_id: 274
categories:
- Python
image: https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-16-38-29.png
---

# 아래 내용은 root 계정 + virtualenv환경에서 진행됩니다.

![스크린샷 2016-07-22 16.36.07](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-16-36-07.png)

Ubuntu 14.04 LTS / Python3.4.4 에서 pip로 mysqlclient를 설치하려고 하면 다음과 같은 에러가 발행한다.

    
    OSError: mysql_config not found


이 에러는 다음의 apt 패키지 설치로 해결할 수 있다.

![스크린샷 2016-07-22 16.36.54](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-16-36-54.png)

    
    apt install libmysqlclient-dev


그러나, 이 모듈을 설치한 이후에도 아래와 같은 에러가 발생 할 수 있다.

![스크린샷 2016-07-22 16.38.00](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-16-38-00.png)

    
    unable to execute 'x86_64-linux-gnu-gcc': No such file or directory


즉, GCC가 없어 컴파일을 할 수 없다는 에러이기 때문에 다음과 같이 build-essential을 설치해줘야 한다.

![스크린샷 2016-07-22 16.38.29](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-16-38-29.png)

    
    apt install build-essential


![스크린샷 2016-07-22 16.39.02](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-16-39-02.png)

다음을 모두 설치한 후에는 위와 같이 설치가 깔끔하게 된다.
