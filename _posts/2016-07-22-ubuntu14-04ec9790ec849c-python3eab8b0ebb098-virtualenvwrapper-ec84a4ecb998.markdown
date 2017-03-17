---
author: livingmethod
comments: true
date: 2016-07-22 04:09:08+00:00
layout: post
link: http://blog.jblee.kr/2016/07/22/ubuntu14-04%ec%97%90%ec%84%9c-python3%ea%b8%b0%eb%b0%98-virtualenvwrapper-%ec%84%a4%ec%b9%98/
slug: ubuntu14-04%ec%97%90%ec%84%9c-python3%ea%b8%b0%eb%b0%98-virtualenvwrapper-%ec%84%a4%ec%b9%98
title: Ubuntu14.04에서 Python3기반 virtualenvwrapper 설치
wordpress_id: 227
categories:
- MacOS
- Python
image: http://aeguana.com/blog/wp-content/uploads/2015/06/python-virtualenv.jpg
---

우분투 14.04에는 기본적으로 Python2와 Python3이 설치되어있다.

그러나 pip로 virtualenv를 설치할 경우 기본적으로 python2를 가상환경의 기본 Python으로 잡게 되는데,
이번 게시글에서는 mkvirtualenv명령어의 기본값을 python3으로 설정하는 방법을 안내한다.

따라서 virtualenv를 사용하기 위해서는 APT를 통해 다음 모듈들을 설치한다.

    
    apt update && upgrade



    
    apt install python-dev python3-dev python3-pip


(참고: python-pip는 python2용 pip, python3-pip는 python3용 pip3을 설치한다.)

    
    pip3 install virtualenv virtualenvwrapper


설치가 완료된 후, nano / vi / vim 등의 편집기로

bash 쉘을 사용할 경우

    
    nano ~/.bashrc


zsh 쉘을 사용할 경우

    
    nano ~/.zshrc


편집기에 들어가

    
    # python virtualenv settings
    export WORKON_HOME=~/.virtualenvs
    export VIRTUALENVWRAPPER_PYTHON="$(command \which python3)"  # location of python3
    source /usr/local/bin/virtualenvwrapper.sh

위 내용을 붙여준다.

네번째 문장에서의 virtualenvwrapper.sh는

    
    find /usr -name virtualenvwrapper.sh




을 통해 나오는 스크립트의 위치로 지정해 주면 된다.




bashrc나 zshrc의 수정이 끝난 경우




    
    mkdir ~/.virtualenvs




를 통해 virtualenv들이 담길 폴더를 만든다.




이제 쉘을 종료한 후 다시 연결한 후




    
    mkvirtualenv 가상환경이름




하면 ~/.virtualenvs 안에 가상환경이 생긴다.




    
    workon 가상환경이름




을 통해 가상환경을 활성화 시킬 수 있으며, 가상환경 이름을 입력하지 않는 경우 가상환경의 리스트가 출력된다.




가상환경을 빠져나오기 위해서는




    
    deactivate




를 입력하면 된다.
