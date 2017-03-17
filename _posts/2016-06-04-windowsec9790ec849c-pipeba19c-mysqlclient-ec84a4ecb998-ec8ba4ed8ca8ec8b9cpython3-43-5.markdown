---
author: livingmethod
comments: true
date: 2016-06-04 01:30:24+00:00
layout: post
link: http://blog.jblee.kr/2016/06/04/windows%ec%97%90%ec%84%9c-pip%eb%a1%9c-mysqlclient-%ec%84%a4%ec%b9%98-%ec%8b%a4%ed%8c%a8%ec%8b%9cpython3-43-5/
slug: windows%ec%97%90%ec%84%9c-pip%eb%a1%9c-mysqlclient-%ec%84%a4%ec%b9%98-%ec%8b%a4%ed%8c%a8%ec%8b%9cpython3-43-5
title: Windows에서 pip로 mysqlclient 설치 실패시(python3.4/3.5)
wordpress_id: 156
categories:
- Python
tags:
- mysqlclient
- pip
- python3
- vsc++
image: https://livingmethod.files.wordpress.com/2016/06/pip-install-mysqlclient-with-error.png
---

윈도우 python3(3.4/3.5)에서 pip로 mysqlclient를 설치하려 시도시 아래와 같은 에러를 만날 수 있다.

[![pip install mysqlclient with error](https://livingmethod.files.wordpress.com/2016/06/pip-install-mysqlclient-with-error.png?w=809)](https://livingmethod.files.wordpress.com/2016/06/pip-install-mysqlclient-with-error.png)

에러 내용은 MS VS C++ 10.0(py3.4) / MS VS C++ 14.0(py3.5)를 설치해달라는 내용이다.

하지만 VS C++은 설치하는데 용량도 꽤 크고 설치시간도 오래걸려서 부담이 크다. 그리고 설령 설치를 하더라도 깔끔하게 맵핑이 되지 않는 경우도 많다.

그래서 차선책으로 mingw를 사용해 gcc컴파일러를 설치해 사용하는 경우도 있지만, 시스템에 설치된 python의 설정을 변경해줘야하기 때문에 라이트유저에게는 부담이 된다.

다행히 mysqlclient의 경우에는 win32/64, py3.4/3.5용으로 미리 컴파일된 pip용 whl파일을 제공한다.



    
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient


위 링크에서 윈도우에 설치한 python버전(3.4인지, 3.5인지 / 32비트인지, 64비트인지)을 확인후 whl파일을 받는다.

다운받은 후 whl 파일이 있는 곳에서

    
    pip install [다운받은파일이름]


(아래에서는 mysqlclient-1.3.7-cp34-none-win32.whl) 을 입력하면 말끔하게 설치됨을 알 수 있다.

[![pip install mysqlclient](https://livingmethod.files.wordpress.com/2016/06/pip-install-mysqlclient.png)](https://livingmethod.files.wordpress.com/2016/06/pip-install-mysqlclient.png)
