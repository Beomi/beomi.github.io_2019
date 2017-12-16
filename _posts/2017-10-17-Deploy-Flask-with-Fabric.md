---
title: "Fabric으로 Flask 자동 배포하기"
date: 2017-10-17
layout: post
categories:
- Python
- Flask
- Fabric
published: true
image: https://beomi-tech-blog.s3.ap-northeast-2.amazonaws.com/img/deploy_flask_with_fabric.jpeg
---

> 이번 글은 Ubuntu16.04 LTS / Python3 / Apache2.4 서버 환경으로 진행합니다.

## 들어가며

플라스크를 서버에 배포하는 것은 장고 배포와는 약간 다릅니다. 기본적으로 Apache2를 사용하기 때문에 `mod_wsgi`를 사용하는 것은 동일하지만, 그 외 다른 점이 조금 있습니다.

우선 간단한 플라스크 앱 하나가 있다고 생각을 해봅시다. 가장 단순한 형태는 아래와 같이 루트로 접속시 `Hello world!`를 보여주는 것이죠.

```python
# app.py
from flask import Flask

app = Flask(__file__)

@app.route('/')
def hello():
    return "Hello world!"
```

물론 여러분이 실제로 만들고 썼을 프로젝트는 이것보다 훨씬 복잡하겠지만, 일단은 이걸로 시작은 할 수 있답니다.

## wsgi.py 파일 만들기

로컬에서 `app.run()` 을 통해 실행했던 테스트서버와는 달리 실 배포 상황에서는 Apache나 NginX와 같은 웹서버를 거쳐 웹을 구동하고, 따라서 `app.run()`의 방식은 더이상 사용할 수 없습니다. 대신 여러가지 웹서버와 Flask를 연결시켜주는 방법이 있는데, 이번엔 그 중 `wsgi`를 통해 Apache서버가 Flask 앱을 실행하도록 만들어줄 것이랍니다.

우선 `wsgi.py`파일을 하나 만들어야 합니다. 이 파일은 나중에 Apache서버가 이 파일을 실행시켜 Flask서버를 구동하게 됩니다. 그리고 이 파일은 위에서 만든 변수인 `app = Flask(__file__)`, 즉 `app`변수를 import할 수 있는 위치에 있어야 합니다. (`app.py`파일과 동일한 위치에 두면 무방합니다.)

```python
# wsgi.py # app.py와 같은 위치
import sys
import os

CURRENT_DIR = os.getcwd()

sys.stdout = sys.stderr
sys.path.insert(0, CURRENT_DIR)

from app import app as application
```

우리가 `wsgi`를 통해 실행할 경우 프로그램은 `application`이라는 변수를 찾아 `run()`와 비슷한 명령을 실행해 서버를 구동합니다. 따라서 우리는 `wsgi.py`파일 내 `application`이라는 변수를 만들어줘야 하는데, 이 변수는 바로 `app.py`내의 `app`변수입니다. 

위 코드를 보시면 `sys`모듈과 `os`모듈을 사용합니다. `os`모듈의 `getcwd()`함수를 통해 현재 파일의 위치를 시스템의 `PATH` 경로에 넣어줍니다. 이 줄을 통해 바로 아래에 있는 `from app import app`이라는 구문에서 `from app` 부분이 현재 `wsgi.py`파일의 경로에서 `app.py`를 import할 수 있게 되는 것이죠. 만약 이 줄이 빠져있다면 `ImportError`가 발생하며 `app`이라는 모듈을 찾을 수 없다는 익셉션이 발생합니다.

## Fabric3 설치하기

Fabric3은 Python2만 지원하던 `fabric`프로젝트를 포크해 Python3을 지원하도록 업데이트한 패키지입니다. 우선 pip로 패키지를 설치해 줍시다.


```bash
pip install fabric3
# 맥/리눅스라면 pip3 install fabric3
```

이제 우리는 `fab`이라는 명령어를 사용할 수 있습니다. 이 명령어를 통해 `fabfile.py` 파일 내의 함수를 실행할 수 있게 됩니다.

## fabfile.py 파일 만들기

Fabric은 그 자체로는 하는 일이 없습니다. 사실 fabric은 우리가 서버에 들어가서 'Git으로 소스를 받고', 'DB를 업데이트하고', 'Static파일을 정리하며', '웹서버 설정을 업데이트'해주는 일들을 하나의 마치 배치파일처럼 자동으로 실행할 수 있도록 도와주는 도구입니다.

하지만 이 도구를 사용하려면 우선 `fabfile.py`라는 파일이 있어야 fabric이 이 파일을 읽고 파일 속의 함수를 실행할 수 있게 됩니다.

`fabfile`을 만들기 전 `deploy.json`이라는 이름의 json파일을 만들어 아래와 같이 설정을 담아줍시다.

우선 `REPO_URL`을 적어줍시다. 이 REPO에서 소스코드를 받아 처리해줄 예정이기 때문이죠. 그리고 `PROJECT_NAME`을 설정해 주세요. 일반적인 상황이라면 REPO의 이름과 같에 넣어주면 됩니다. 그리고 `REMOTE_HOST`는 서버의 주소가 됩니다. http등을 제외한 '도메인'부분만 넣어주세요. 그리고 서버에 SSH로 접속할 수 있는 IP를 `REMOTE_HOST_SSH`에 넣어주고, 마지막으로 `sudo`권한을 가진 유저이름을 `REMOTE_USER`에 넣어주세요.

```json
{
  "REPO_URL": "https://github.com/Beomi/our_project",
  "PROJECT_NAME": "our_project",
  "REMOTE_HOST": "our_project.com",
  "REMOTE_HOST_SSH": "123.32.1.4",
  "REMOTE_USER": "sudouser"
}
```

자, 이제 아래 코드를 통해 `fabfile.py`파일을 만들어 줍시다. (이것도 `app.py`와 같은 위치에 두면 관리하기가 편합니다.) 

이부분은 파일에 설명을 담을 예정이니 코드의 주석을 참고해주세요.

```python
# fabfile.py
from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
import os
import json

# 현재 fabfile.py가 있는 폴더의 경로
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# deploy.json이라는 파일을 열어 아래의 변수들에 담아줍니다.
envs = json.load(open(os.path.join(PROJECT_DIR, "deploy.json")))

REPO_URL = envs['REPO_URL']
PROJECT_NAME = envs['PROJECT_NAME']
REMOTE_HOST = envs['REMOTE_HOST']
REMOTE_HOST_SSH = envs['REMOTE_HOST_SSH']
REMOTE_USER = envs['REMOTE_USER']

# SSH에 접속할 유저를 지정하고,
env.user = REMOTE_USER
# SSH로 접속할 서버주소를 넣어주고,
env.hosts = [
    REMOTE_HOST_SSH,
]
# 원격 서버중 어디에 프로젝트를 저장할지 지정해준 뒤,
project_folder = '/home/{}/{}'.format(env.user, PROJECT_NAME)
# 우리 프로젝트에 필요한 apt 패키지들을 적어줍니다.
apt_requirements = [
    'curl',
    'git',
    'python3-dev',
    'python3-pip',
    'build-essential',
    'apache2',
    'libapache2-mod-wsgi-py3',
    'python3-setuptools',
    'libssl-dev',
    'libffi-dev',
]

# _로 시작하지 않는 함수들은 fab new_server 처럼 명령줄에서 바로 실행이 가능합니다.
def new_server():
    setup()
    deploy()


def setup():
    _get_latest_apt()
    _install_apt_requirements(apt_requirements)
    _make_virtualenv()


def deploy():
    _get_latest_source()
    _put_envs()
    _update_virtualenv()
    _make_virtualhost()
    _grant_apache2()
    _restart_apache2()

# put이라는 방식으로 로컬의 파일을 원격지로 업로드할 수 있습니다.
def _put_envs():
    pass  # activate for envs.json file
    # put('envs.json', '~/{}/envs.json'.format(PROJECT_NAME))

# apt 패키지를 업데이트 할 지 결정합니다.
def _get_latest_apt():
    update_or_not = input('would you update?: [y/n]')
    if update_or_not == 'y':
        sudo('apt-get update && apt-get -y upgrade')

# 필요한 apt 패키지를 설치합니다.
def _install_apt_requirements(apt_requirements):
    reqs = ''
    for req in apt_requirements:
        reqs += (' ' + req)
    sudo('apt-get -y install {}'.format(reqs))

# virtualenv와 virtualenvwrapper를 받아 설정합니다.
def _make_virtualenv():
    if not exists('~/.virtualenvs'):
        script = '''"# python virtualenv settings
                    export WORKON_HOME=~/.virtualenvs
                    export VIRTUALENVWRAPPER_PYTHON="$(command \which python3)"  # location of python3
                    source /usr/local/bin/virtualenvwrapper.sh"'''
        run('mkdir ~/.virtualenvs')
        sudo('pip3 install virtualenv virtualenvwrapper')
        run('echo {} >> ~/.bashrc'.format(script))

# Git Repo에서 최신 소스를 받아옵니다.
# 깃이 있다면 fetch를, 없다면 clone을 진행합니다.
def _get_latest_source():
    if exists(project_folder + '/.git'):
        run('cd %s && git fetch' % (project_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, project_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (project_folder, current_commit))

# Repo에서 받아온 requirements.txt를 통해 pip 패키지를 virtualenv에 설치해줍니다.
def _update_virtualenv():
    virtualenv_folder = project_folder + '/../.virtualenvs/{}'.format(PROJECT_NAME)
    if not exists(virtualenv_folder + '/bin/pip'):
        run('cd /home/%s/.virtualenvs && virtualenv %s' % (env.user, PROJECT_NAME))
    run('%s/bin/pip install -r %s/requirements.txt' % (
        virtualenv_folder, project_folder
    ))

# (optional) UFW에서 80번/tcp포트를 열어줍니다.
def _ufw_allow():
    sudo("ufw allow 'Apache Full'")
    sudo("ufw reload")

# Apache2의 Virtualhost를 설정해 줍니다. 
# 이 부분에서 wsgi.py와의 통신, 그리고 virtualenv 내의 파이썬 경로를 지정해 줍니다.
def _make_virtualhost():
    script = """'<VirtualHost *:80>
    ServerName {servername}
    <Directory /home/{username}/{project_name}>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    WSGIDaemonProcess {project_name} python-home=/home/{username}/.virtualenvs/{project_name} python-path=/home/{username}/{project_name}
    WSGIProcessGroup {project_name}
    WSGIScriptAlias / /home/{username}/{project_name}/wsgi.py
    {% raw %}
    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined
    {% endraw %}
    </VirtualHost>'""".format(
        username=REMOTE_USER,
        project_name=PROJECT_NAME,
        servername=REMOTE_HOST,
    )
    sudo('echo {} > /etc/apache2/sites-available/{}.conf'.format(script, PROJECT_NAME))
    sudo('a2ensite {}.conf'.format(PROJECT_NAME))

# Apache2가 프로젝트 파일을 읽을 수 있도록 권한을 부여합니다.
def _grant_apache2():
    sudo('chown -R :www-data ~/{}'.format(PROJECT_NAME))
    sudo('chmod -R 775 ~/{}'.format(PROJECT_NAME))

# 마지막으로 Apache2를 재시작합니다.
def _restart_apache2():
    sudo('sudo service apache2 restart')
```

위 코드를 `fabfile.py`에 넣어주고 나서 

첫 실행시에는 `fab new_server`

코드를 수정하고 push한 뒤 서버에 배포시에는 `fab deploy`

명령을 실행해 주면 됩니다.

> NOTE: _ 로 시작하는 함수는 `fab 함수이름`으로 실행하지 못합니다.

자, 이제 서버에 올릴 준비가 되었습니다.

## 서버에 올리기

우분투 서버를 만들고 첫 배포라면 `new_server`를, 한번 `new_server`를 했다면 `deploy`로 배포를 진행합니다.

```bash
fab new_server # 첫 배포
fab deploy # 첫 배포를 제외한 나머지
```

## 끝났습니다!

여러분의 사이트는 이제 http://REMOTE_HOST 으로 접속 가능할거에요!


## 유의할 점

`fabfile`내의 `apt_requirements` 리스트에는 프로젝트마다 필요한 다른 패키지들을 적어줘야 합니다.

만약 여러분의 프로젝트에서 `mysqlclient`패키지등을 사용한다면 `libmysqlclient-dev`를 `apt_requirements`리스트에 추가해줘야 합니다. 혹은 PostgreSQL을 사용한다면 `libpq-dev`가 필요할 수도 있습니다. 그리고 여러분이 이미지 처리를 하는 `pillow`패키지를 사용한다면 `libjpeg62-dev`를 `apt_requirements`에 추가해야 할 수도 있습니다.

이처럼 여러분이 파이썬 패키지에서 어떤 상황이냐에 따라 다른 apt패키지 리스트를 넣어줘야 합니다. 

이 부분만 유의해 넣어준다면 Fabric으로 한번에 배포에 성공할 수 있을거랍니다! :)




