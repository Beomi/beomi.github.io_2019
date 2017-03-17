---
author: livingmethod
comments: true
date: 2016-07-21 15:22:55+00:00
layout: post
link: http://blog.jblee.kr/2016/07/22/mac-os-x%ec%97%90%ec%84%9c-pip-virtualenvwrapper-%ec%84%a4%ec%b9%98-%ec%8b%9c-uninstalling-six-%ec%97%90%ec%84%9c-exception-%eb%b0%9c%ec%83%9d-%ec%8b%9c/
slug: mac-os-x%ec%97%90%ec%84%9c-pip-virtualenvwrapper-%ec%84%a4%ec%b9%98-%ec%8b%9c-uninstalling-six-%ec%97%90%ec%84%9c-exception-%eb%b0%9c%ec%83%9d-%ec%8b%9c
title: mac OS X에서 pip virtualenvwrapper 설치 시 uninstalling six 에서 Exception 발생 시
wordpress_id: 213
categories:
- MacOS
- Python
image: https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-00-16-03.png
---

![스크린샷 2016-07-22 00.16.03.png](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-22-00-16-03.png)

Mac OS X El Capitan(10.11.5)에서 pip로 virtualenvwrapper를 설치 시도시 six-1.4.1버전을 제거하는데 권한이 없다고 나온다.

Sudo를 통해 관리자 권한으로 실행해도 같은 오류가 발생하는데, 이것은
https://github.com/pypa/pip/issues/3165
이슈에서 답을 찾을 수 있다.

바로 Mac OS X El Capitan의 [System Integrity Protection](https://en.wikipedia.org/wiki/System_Integrity_Protection)때문이다. ROOT 계정으로도 제거하지 못하기 때문에, 해결방법은 다음과 같다.

    
    pip install virtualenvwrapper --ignore-installed six


위의 옵션으로 내장된 모듈 six를 건너뛰고 설치하게 만드는 것이다.
