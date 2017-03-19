---
title: "Fabric으로 Django 배포하기"
date: 2017-03-19 17:30:00+09:00
layout: post
categories:
- Python
- Fabric
- Django
published: true
image: /img/old_post/python-fabric-logo.jpg
---

> 이번 가이드는 완성된 상태의 Django 프로젝트가 있다고 가정합니다. 예제로 [https://github.com/Beomi/irkshop](https://github.com/Beomi/irkshop) 을 배포해 봅니다.

> [https://gist.github.com/Beomi/945cd905175c3b21370f8f04abd57404](https://gist.github.com/Beomi/945cd905175c3b21370f8f04abd57404)의 예제를 설명합니다.

# Fabric으로 Django 배포하기

Django는 내장된 `runserver`라는 개발용 웹 서버가 있습니다. 하지만 개발용 웹 서버를 상용 환경에서 사용하는 것은 여러가지 문제를 가져옵니다. 메모리 문제등의 성능 이슈부터 Static file서빙의 보안 문제까지 다양한데요, 이 때문에 Django는 웹 서버(ex: `Apache2` `NginX`등)를 통해 배포하게 됩니다.

하지만 이러한 배포작업은 아마존 EC2등의 VPS나 리얼 서버에서 `Apache2`를 깔고, `python3`와 `mod_wsgi`등을 깔아야만 동작하기 때문에 배포 자체가 어려움을 갖게 됩니다. 또한 SSH에 접속히 직접 명령어를 치는 경우 오타나 실수등으로 인해 정상적으로 작동하지 않는 경우도 부지기수입니다.

따라서 이러한 작업을 자동화해주는 도구가 바로 Fabric이고, 이번 가이드에서는 Django 프로젝트를 Vultr VPS, Ubuntu에 올리는 방법을 다룹니다.

## Vultr VPS 생성하기

[Vultr](vultr.com)는 VPS(가상서버) 제공 회사입니다. 최근 가격 인하로 유사 서비스 대비 절반 가격에 이용할 수 있어 가성비가 좋습니다.

사용자가 많지 않은 (혹은 혼자 사용하는..) 서비스라면 최소 가격인 1cpu 512MB의 월 2.5달러짜리를 이용하시면 됩니다.

Vultr는 일본 Region에 서버가 있어 한국에서 사용하기에도 핑이 25ms정도로 양호합니다.

VPS하나를 만든 후 root로 접속해 장고를 구동할 사용자를 만들어 봅시다.

![예제VPS](https://www.dropbox.com/s/008m622z6x869ig/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-03-19%2023.20.21.png?dl=1)

## `django` 유저 만들기(sudo권한 가진 유저 만들기)

Fabric을 사용할 때 초기에 `apt`를 이용해 패키지를 설치해야 할 필요가 있습니다.

하지만 처음에 제공되는 `root`계정은 사용하지 않는 것을 보안상 추천합니다. 따라서 우리는 `sudo`권한을 가진 `django`라는 유저를 생성하고 Fabric으로 진행해 보겠습니다.

```sh
adduser django # `django`라는 유저를 만듭니다.
adduser django sudo # django유저를 `sudo`그룹에 추가합니다.
```

> 비밀번호를 만드는 것을 제외하면 나머지는 빈칸으로 만들어 두어도 무방합니다.

## Fabric 설치하기

`Fabric`은 기본적으로 서버가 아닌 클라이언트에 설치합니다. 개념상 로컬에서 SSH로 서버에 접속해 명령을 처리하는 것이기 때문에 당연히 SSH 명령을 입려하는 로컬에 설치되어야 합니다.

Fabric은 공식적으로는 Python2.7만을 지원합니다. 하지만 이 프로젝트를 Fork해서 Python3을 지원하는 프로젝트인 `Fabric3`이 있습니다. 이번 가이드에서는 이 `Fabric3`을 설치합니다.

```sh
pip3 install fabric3
# 혹은
python3 -m pip install fabric3
```

## fabfile 만들기

### Fabric import하기

Fabric을 설치하시면 `fab`이라는 명령어를 사용할 수 있습니다. 이 명령어는 `fab some_func`라는 방식을 통해 `fabfile.py`파일 안의 함수를 실행할 수 있습니다.

fabfile은 기본적으로 `manage.py`파일와 같은 위치인 프로젝트 폴더에 두시는 것을 권장합니다.

```python
from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
```

우선 fabric에서 사용하는 API들을 import해줍니다.

`fabric.contrib.files`에서는 원격(혹은 로컬)의 파일을 관리하는 API입니다. `fabric.api`는 Fabric에서 사용하는 환경이나, SSH로 연결한 원격 서버에서 명령어를 실행하는 API입니다.

### PROJECT_DIR, BASE_DIR 지정하기

장고의 `settings.py`파일에 기본적으로 지정된 `BASE_DIR`와 같은 장고 프로젝트의 폴더 위치를 지정하는 `PROJECT_DIR`와 `BASE_DIR`을 지정해 줍니다.

`PROJECT_DIR`은 `settings.py`가 있는 폴더의 위치이고, `BASE_DIR`은 `manage.py`가 있는 폴더입니다.

```python
from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
import random
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
```

### 배포용 변수 불러오기

서버에 배포를 하기 위해 `git`을 이용합니다. 따라서 소스가 올라가 있는 깃헙(혹은 gitlab, bitbucket 등)의 주소(`REPO_URL`)가 필요합니다.

그리고 원격으로 SSH접속을 하기 때문에 원격 서버에 접속할 수 있는 SSH용 주소(`REMOTE_HOST_SSH`), 원격 계정 ID(`REMOTE_USER`), 원격 계정 비밀번호(`REMOTE_PASSWORD`)가 필요합니다.

또한, 장고 `settings.py`의 `ALLOWED_HOSTS`에 추가할 도메인(`REMOTE_HOST`)이 필요합니다.

이러한 변수들은 보통 json파일에 저장하고 `.gitignore`에 이 json파일을 지정해 git에 올라가지 않도록 관리합니다. 이번 가이드에서는 `deploy.json`이라는 파일에 아래 변수들을 저장하고 관리해 보겠습니다.

`deploy.json`파일을 `fabfile.py`파일이 있는 곳에 아래 내용을 담고 저장해주세요.

> `REPO_URL`와 `PROJECT_NAME`을 제외한 설정은 위 Vultr에서 만들어준 대로 진행해주세요. 단, REMOTE_USER는 root이면 안됩니다!

```json
{
  "REPO_URL":"https://github.com/Beomi/irkshop.git",
  "PROJECT_NAME":"irkshop",
  "REMOTE_HOST_SSH":"45.77.20.73",
  "REMOTE_HOST":"45.77.20.73",
  "REMOTE_USER":"django",
  "REMOTE_PASSWORD":"django_pwd123"
}
```

> 만약 SSH 포트가 다르다면 `REMOTE_HOST_SSH` 뒤 포트를 :으로 붙여주면 됩니다. (ex: 45.77.20.73:22)

> REMOTE_HOST는 도메인 주소(ex: irkshop.testi.kr)일 수 있습니다. 하지만 이번 배포에서는 도메인을 다루지 않으므로 IP주소로 대신합니다.

json파일을 만들었다면 이 파일을 이제 `fabfile.py`에서 불러와 사용해 봅시다.


```python
from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
import random
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# deploy.json파일을 불러와 envs변수에 저장합니다.
with open(os.path.join(PROJECT_DIR, "deploy.json")) as f:
    envs = json.loads(f.read())

REPO_URL = envs['REPO_URL']
PROJECT_NAME = envs['PROJECT_NAME']
REMOTE_HOST_SSH = envs['REMOTE_HOST_SSH']
REMOTE_HOST = envs['REMOTE_HOST']
REMOTE_USER = envs['REMOTE_USER']
REMOTE_PASSWORD = envs['REMOTE_PASSWORD']
# 아래 부분은 Django의 settings.py에서 지정한 STATIC_ROOT 폴더 이름, STATID_URL, MEDIA_ROOT 폴더 이름을 입력해주시면 됩니다.
STATIC_ROOT_NAME = 'static_deploy'
STATIC_URL_NAME = 'static'
MEDIA_ROOT = 'uploads'
```

### Fabric 환경 설정하기

이제 Fabric이 사용할 `env`를 설정해 줍시다. 대표적으로 `env.user`와 `env.hosts`, `env.password`가 있습니다.

```python
from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
import random
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(PROJECT_DIR, "deploy.json")) as f:
    envs = json.loads(f.read())

REPO_URL = envs['REPO_URL']
PROJECT_NAME = envs['PROJECT_NAME']
REMOTE_HOST_SSH = envs['REMOTE_HOST_SSH']
REMOTE_HOST = envs['REMOTE_HOST']
REMOTE_USER = envs['REMOTE_USER']
REMOTE_PASSWORD = envs['REMOTE_PASSWORD']
STATIC_ROOT_NAME = 'static_deploy'
STATIC_URL_NAME = 'static'
MEDIA_ROOT = 'uploads'

# Fabric이 사용하는 env에 값들을 저장합니다.
env.user = REMOTE_USER
username = env.user
env.hosts = [
    REMOTE_HOST_SSH, # 리스트로 만들어야 합니다.
    ]
env.password = REMOTE_PASSWORD
# 원격 서버에서 장고 프로젝트가 있는 위치를 정해줍니다.
project_folder = '/home/{}/{}'.format(env.user, PROJECT_NAME)
```

이와 같이 설정시 `fab`명령어를 실행할 경우에 추가적인 값을 입력할 필요가 없어집니다.

### APT 설치 목록 지정하기

VPS에 따라 설치되어있는 리눅스 패키지가 다릅니다. 이번 가이드에서는 `Apache2`와 `mod-wsgi-py3`을 사용하기 때문에 이 패키지와 파이썬 의존 패키지들을 설치해 줘야 합니다.

```python
from fabric.contrib.files import append, exists, sed, put
from fabric.api import env, local, run, sudo
import random
import os
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(PROJECT_DIR, "deploy.json")) as f:
    envs = json.loads(f.read())

REPO_URL = envs['REPO_URL']
PROJECT_NAME = envs['PROJECT_NAME']
REMOTE_HOST_SSH = envs['REMOTE_HOST_SSH']
REMOTE_HOST = envs['REMOTE_HOST']
REMOTE_USER = envs['REMOTE_USER']
REMOTE_PASSWORD = envs['REMOTE_PASSWORD']
STATIC_ROOT_NAME = 'static_deploy'
STATIC_URL_NAME = 'static'
MEDIA_ROOT = 'uploads'

env.user = REMOTE_USER
username = env.user
env.hosts = [REMOTE_HOST_SSH,]
env.password = REMOTE_PASSWORD
project_folder = '/home/{}/{}'.format(env.user, PROJECT_NAME)

# APT로 설치할 목록을 정해줍니다.
apt_requirements = [
    'ufw', # 방화벽
    'curl',
    'git', # 깃
    'python3-dev', # Python 의존성
    'python3-pip', # PIP
    'build-essential', # C컴파일 패키지
    'python3-setuptools', # PIP
    'apache2', # 웹서버 Apache2
    'libapache2-mod-wsgi-py3', # 웹서버~Python3 연결
    # 'libmysqlclient-dev', # MySql
    'libssl-dev', # SSL
    'libxml2-dev', # XML
    'libjpeg8-dev', # Pillow 의존성 패키지(ImageField)
    'zlib1g-dev', # Pillow 의존성 패키지
]
```

### Fab 함수 만들기

Fabric은 fabfile있는 곳에서 `fab 함수이름`의 명령어로 실행 가능합니다. 단, `_`로 시작하는 함수는 Fabric이 관리하지 않습니다.

이제 서버에서 실행할 SSH를 캡슐화한다고 보면 됩니다. 크게 `setup`와 `deploy`로 나눌 수 있다고 봅니다. Setup은 장고 코드와 무관한 OS의 패키지 관리와 VirtualEnv관리, Deploy는 장고 소스가 변화할 경우 업데이트 되어야 하는 코드입니다.

Setup에는 APT 최신 패키지 설치와 `apt_requirements`설치, 그리고 `virtualenv`를 만드는 것까지를 다룹니다.

Deploy에서는 Git에서 최신 소스코드를 가져오고, Git에서 관리되지 않는 환경변수 파일을 서버에 업로드하고, 장고 `settings.py`파일을 상용 환경으로 바꿔주고, virtualenv로 만든 가상환경에 pip 패키지를 설치하고, StaticFile들을 collect하고, DB를 migrate해주고, Apache2의 VirtualHost에 장고 웹 서비스를 등록하고, 폴더 권한을 잡아주고, 마지막으로 Apache2 웹서버를 재부팅하는 과정까지를 다룹니다.

> 여기서부터는 코드가 너무 길어지는 관계로 `apt_requirements` 포함한 윗부분을 생략합니다. 

```python
# 앞부분 생략
def new_server():
    setup()
    deploy()

def setup():
    _get_latest_apt() # APT update/upgrade
    _install_apt_requirements(apt_requirements) # APT install
    _make_virtualenv() # Virtualenv

def deploy():
    _get_latest_source() # Git에서 최신 소스 가져오기
    _put_envs() # 환경변수 json파일 업로드
    _update_settings() # settings.py파일 변경
    _update_virtualenv() # pip 설치
    _update_static_files() # collectstatics
    _update_database() # migrate
    _make_virtualhost() # Apache2 VirtualHost
    _grant_apache2() # chmod
    _grant_sqlite3() # chmod
    _restart_apache2() # 웹서버 재시작
```

이와 같이 함수를 등록해주면 `fab new_server`, `fab setup`, `fab deploy`를 통해 바로바로 배포를 할 수 있습니다.

이제 `_`로 시작하는, 진짜 Fabric함수들을 만들어 보겠습니다.

> _ 로 시작하는 함수들을 설명할 때는 함수만 각각 설명합니다. 모두 모인 코드는 글 하단을 참고해주세요.

- `_get_latest_apt`: APT 업데이트 & 업그레이드

```python
def _get_latest_apt():
    update_or_not = input('would you update?: [y/n]')
    if update_or_not=='y':
        sudo('sudo apt-get update && sudo apt-get -y upgrade')
```

- `_install_apt_requirements`: apt_requirements에 적은 패키지들을 설치합니다.

```python
def _install_apt_requirements(apt_requirements):
    reqs = ''
    for req in apt_requirements:
        reqs += (' ' + req)
    sudo('sudo apt-get -y install {}'.format(reqs))
```

- `_make_virtualenv`: 원격 서버에 `~/.virtualenvs`폴더가 없는 경우 virtualenv와 virtualenvwrapper를 설치하고 `.bashrc`파일에 virtualenvwrapper를 등록해 줍니다.

```python
def _make_virtualenv():
    if not exists('~/.virtualenvs'):
        script = '''"# python virtualenv settings
                    export WORKON_HOME=~/.virtualenvs
                    export VIRTUALENVWRAPPER_PYTHON="$(command \which python3)"  # location of python3
                    source /usr/local/bin/virtualenvwrapper.sh"'''
        run('mkdir ~/.virtualenvs')
        sudo('sudo pip3 install virtualenv virtualenvwrapper')
        run('echo {} >> ~/.bashrc'.format(script))
```

- `_get_latest_source`: 만약 `.git`폴더가 없다면 원격 git repo에서 clone해오고, 있다면 fetch해온 후 최신 커밋으로 reset합니다.

```python
def _get_latest_source():
    if exists(project_folder + '/.git'):
        run('cd %s && git fetch' % (project_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, project_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (project_folder, current_commit))
```

- `_put_envs`: 로컬의 `envs.json`이름의 환경변수를 서버에 업로드 합니다.

> Apache2는 웹서버가 OS의 환경변수를 사용하지 않기 때문에 json와 같은 파일을 통해 환경변수를 관리해 줘야 합니다. 저는 `envs.json`이라는 파일을 `manage.py`파일이 있는 프로젝트 폴더에 만든 후 환경변수를 장고의 `settings.py`에서 불러와 사용합니다.

```python
def _put_envs():
    put(os.path.join(PROJECT_DIR, 'envs.json'), '~/{}/envs.json'.format(PROJECT_NAME))
```

- `_update_settings`: `settings.py`파일을 바꿔줍니다. DEBUG를 False로 바꾸고, ALLOWED_HOSTS에 호스트 이름을 등록하고, 장고에서 만들어준 키 파일이 아니라 서버에서 랜덤으로 만든 Secret KEY를 사용하게 합니다.

```python
def _update_settings():
    settings_path = project_folder + '/{}/settings.py'.format(PROJECT_NAME)
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS = .+$',
        'ALLOWED_HOSTS = ["%s"]' % (REMOTE_HOST,)
    )
    secret_key_file = project_folder + '/{}/secret_key.py'.format(PROJECT_NAME)
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')
```

- `_update_virtualenv`: virtualenv에 `requirements.txt`파일로 지정된 pip 패키지들을 설치합니다.

```python
def _update_virtualenv():
    virtualenv_folder = project_folder + '/../.virtualenvs/{}'.format(PROJECT_NAME)
    if not exists(virtualenv_folder + '/bin/pip'):
        run('cd /home/%s/.virtualenvs && virtualenv %s' % (env.user, PROJECT_NAME))
    run('%s/bin/pip install -r %s/requirements.txt' % (
        virtualenv_folder, project_folder
    ))
```

- `_update_static_files`: CollectStatic을 해줍니다.

```python
def _update_static_files():
    virtualenv_folder = project_folder + '/../.virtualenvs/{}'.format(PROJECT_NAME)
    run('cd %s && %s/bin/python3 manage.py collectstatic --noinput' % (
        project_folder, virtualenv_folder
    ))
```

- `_update_database`: DB migrate를 해줍니다.

```python
def _update_database():
    virtualenv_folder = project_folder + '/../.virtualenvs/{}'.format(PROJECT_NAME)
    run('cd %s && %s/bin/python3 manage.py migrate --noinput' % (
        project_folder, virtualenv_folder
    ))
```

- `_make_virtualhost`: Apache2가 관리하는 VirtualHost를 만들어줍니다. 80포트로 지정하고 Static파일을 Apache2가 서빙합니다.

> 만약 SSL을 사용하고 싶으시다면 *:443으로 관리되는 파일을 추가적으로 만드셔야 합니다. 이번 가이드에서는 다루지 않습니다.

```python
def _make_virtualhost():
    script = """'<VirtualHost *:80>
    ServerName {servername}
    Alias /{static_url} /home/{username}/{project_name}/{static_root}
    Alias /{media_url} /home/{username}/{project_name}/{media_url}
    <Directory /home/{username}/{project_name}/{media_url}>
        Require all granted
    </Directory>
    <Directory /home/{username}/{project_name}/{static_root}>
        Require all granted
    </Directory>
    <Directory /home/{username}/{project_name}/{project_name}>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    WSGIDaemonProcess {project_name} python-home=/home/{username}/.virtualenvs/{project_name} python-path=/home/{username}/{project_name}
    WSGIProcessGroup {project_name}
    WSGIScriptAlias / /home/{username}/{project_name}/{project_name}/wsgi.py
    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined
    </VirtualHost>'""".format(
        static_root=STATIC_ROOT_NAME,
        username=env.user,
        project_name=PROJECT_NAME,
        static_url=STATIC_URL_NAME,
        servername=REMOTE_HOST,
        media_url=MEDIA_ROOT
    )
    sudo('echo {} > /etc/apache2/sites-available/{}.conf'.format(script, PROJECT_NAME))
    sudo('a2ensite {}.conf'.format(PROJECT_NAME))
```

- `_grant_apache2`: 프로젝트 폴더내 파일을 `www-data`그룹(Apache2)이 관리할 수 있도록 소유권을 변경합니다.

```python
def _grant_apache2():
    sudo('sudo chown -R :www-data ~/{}'.format(PROJECT_NAME))
```

- `_grant_sqlite3`: 만약 Sqlite3을 그대로 이용할 경우 `www-data`가 쓰기 권한을 가져야 합니다.

```python
def _grant_sqlite3():
    sudo('sudo chmod 775 ~/{}/db.sqlite3'.format(PROJECT_NAME))
```

- `_restart_apache2`: 모든 설정을 마친 후 Apache2 웹서버를 재실행해 설정을 적용해줍니다.

```python
def _restart_apache2():
    sudo('sudo service apache2 restart')
```

## 배포해보기

이제 `manage.py`파일이 있는 곳에서 아래 명령어를 입력해 봅시다.

```sh
fab new_server
```

이 명령어를 치면 자동으로 모든 과정이 완료되고 서버가 뜹니다.

만약 파일을 수정하고 커밋했다면, Github Repo에 올린 후 `deploy` 명령어를 통해 새 코드를 서버에 배포할 수 있습니다.

```sh
fab deploy
```

## 짜잔!

프로젝트 하나가 배포가 완료되었습니다! 아무것도 없어보이지만, DB에 자료를 추가하면 [IRKSHOP 예제](http://irkshop.testi.kr)처럼 예쁘게 생성됩니다.

![Simple IRKSHOP](https://www.dropbox.com/s/t67go56jnho0g0w/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202017-03-20%2000.28.56.png?dl=1)

