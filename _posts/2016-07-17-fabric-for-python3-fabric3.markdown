---
author: livingmethod
comments: true
date: 2016-07-17
layout: post
link: http://blog.jblee.kr/2016/07/17/fabric-for-python3-fabric3/
slug: fabric-for-python3-fabric3
title: Fabric for Python3 (Fabric3)
wordpress_id: 177
categories:
- Python
image: https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-16-23-15-38.png
---

Python3에서 Fabric을 설치해 사용하려하면

![스크린샷 2016-07-16 23.10.37.png](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-16-23-10-37.png)

이와 같이

    
    <span class="s1">ImportError: cannot import name 'isMappingType'</span>




라는 임포트 에러를 마주치게 된다.




이렇게 되는 이유는 python2에서 지원하던 isMappingType 모듈이 python3에서는 제거되었기 때문이고, fabric모듈을 제작하는 FabFile(http://www.fabfile.org)에서는 현재 python2.7까지만 지원하기 때문이다.![스크린샷 2016-07-16 23.13.55.png](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-16-23-13-55.png)




따라서 python3 환경에서는 fabric을 사용할 수 없게 되는데, 이러한 경우가 많아서 해외 python이용자가 기존 프로젝트를 포크해 python3(3.4+)으로 만든 것이 있다.




![스크린샷 2016-07-16 23.15.38.png](https://livingmethod.files.wordpress.com/2016/07/e18489e185b3e1848fe185b3e18485e185b5e186abe18489e185a3e186ba-2016-07-16-23-15-38.png)




바로 Fabric3이라는 이름으로 Pypi에서 제공중인 모듈이라 설치도 간단히,




    
    pip3 install fabric3




위 명령만으로 설치할 수 있다. 기존에 fabric을 설치했다면




    
    pip3 uninstall fabric
    deactivate (virtualenv / pyvenv 등의 가상환경을 이용해 작업중이던 경우, 필수!)
    source 가상환경/bin/activate (가상환경 활성화)
    pip3 install fabric




(만약 python3버전의 가상환경을 사용중이었다면 pip3대신 pip로 사용해도 무방하다)




가상환경을 이용중일 경우 비활성화 후 다시 활성화 하지 않고 그대로 이용할 경우 메모리에 올라가 있는 python실행 상태로 인하여 여전히 에러가 날 수 있다. 따라서 반드시 비활성화 후 다시 활성화 하기를 권장한다.




위 과정을 마친 경우 fabric을 사용하듯이 자연스럽게 fabric을 이용할수 있다!
