---
title: "기존 DB를 Flask-SQLAlchemy ORM Model로 사용하기"
date: 2017-10-20
layout: post
categories:
- Flask
- SQLAlchemy
published: true
image: /img/2017-10-20-DB-To-SQLAlchemy-Model.jpeg
---

> 본 게시글에서는 MySQL/Sqlite을 예제로 하고있지만, Flask-SQLAlchemy가 지원하는 다른 DB에서도 사용 가능합니다.

## 들어가며

Flask로 웹 개발 진행 시 SQLAlchemy(Flask-SQLAlchemy)를 사용해 ORM구조를 구성할 때 데이터를 저장할 DB의 구조를 직접 확인하며 진행하는 것은 상당히 귀찮고 어려운 일입니다.

Django에는 내장된 `inspectdb`라는 명령어를 통해 Django와 일치하는 DB Model구조를 만들어주지만 SQLAlchemy 자체에 내장된 `automap`은 우리가 상상하는 모델 구조를 바로 만들어주지는 않습니다.

따라서 다른 패키지를 고려해볼 필요가 있습니다.

## flask-sqlacodegen

`flask-sqlacodegen`은 기존 DB를 Flask-SQLAlchemy에서 사용하는 Model 형식으로 변환해 보여주는 패키지입니다. 기존 `sqlacodegen`에서 포크해 Flask-SQLAlchemy에 맞게 기본 설정이 갖추어져있어 편리합니다.

## 설치하기

설치는 `pip`로 간단하게 진행해 주세요.

> 글쓰는 시점 최신버전은 1.1.6.1입니다.

> 글쓴것과 같은 버전으로 설치하려면 flask-sqlacodegen==1.1.6.1 로 설치해 주세요.

```bash
# 최신 버전 설치하기
pip install flask-sqlacodegen
# 글쓴 시점과 같게 설치하려면
# pip install flask-sqlacodegen==1.1.6.1
```

설치가 완료되면 명령줄에서 `flask-sqlacodegen`라는 명령어를 사용할 수 있습니다.

> 주의: `sqlacodegen`이 이미 깔려있다면 다른 가상환경(virtuale / venv)를 만드시고 진행해 주세요. `sqlacodegen`이 깔려있으면 `--flask`이 동작하지 않습니다.

## DB 구조 뜯어내기

`flask-sqlacodegen`는 `sqlacodegen`과 거의 동일한 문법을 사용합니다.(포크를 뜬 프로젝트니까요!)

`flask-sqlacodegen` 명령어로 DB를 지정하면 구조를 알 수 있습니다.

### SQLite의 경우

```bash
flask-sqlacodegen "sqlite:///db.sqlite3" --flask > models.py # 상대경로, 현재 위치의 db.sqlite3파일
```

SQLite는 로컬에 있는 DB의 위치를 지정하면 됩니다.

위 명령어를 실행하면 `models.py`파일 안에 `db.sqlite3` DB의 모델이 정리됩니다.

> NOTE: Sqlite의 파일을 지정할 경우 "sqlite://"가 아닌 "sqlite:///" 로 `/`를 3번 써주셔야 상대경로로 지정 가능하며, "sqlite:////"로 `/`를 4번 써주셔야 절대경로로 지정이 가능합니다.

### mysql 서버의 경우

```bash
flask-sqlacodegen "mysql://username:password@DB_IP/DB_NAME" --flask > models.py
```

MySQL의 경우 mysql에 접속하는 방식 그대로 사용자 이름, 비밀번호, IP(혹은 HOST도메인), DB이름을 넣어준 뒤 진행해주면 됩니다.

> NOTE: mysql은 "mydql://" 로 `/`가 2번입니다.

> NOTE: mysql에 연결하려면 pip패키지 중 `mysqlclient`가 설치되어있어야 합니다.
설치가 되어있지 않으면 아래와 같이 `ModuleNotFoundError`가 발생합니다.
![]({{site.static_url}}/img/dropbox/Screenshot%202017-10-20%2012.21.08.png?dl=1)

> MAC에서 진행 중 혹시 `mysqlclient`설치 중 아래와 같은 에러가 발생한다면
![]({{site.static_url}}/img/dropbox/Screenshot%202017-10-20%2012.23.07.png?dl=1)

> 아래 명령어를 실행해 `xcode cli developer tool`와 `openssl`을 설치해주신 후 `mysqlclient`를 설치해 주세요.
```bash
xcode-select --install
brew install openssl
export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
pip install mysqlclient
```
![]({{site.static_url}}/img/dropbox/Screenshot%202017-10-20%2012.25.22.png?dl=1)

## 실행결과

아래 결과는 장고 프로젝트를 생성하고 첫 `migrate`를 진행할 때 생기는 예시 `db.sqlite3`파일을 	`flask-sqlacodegen`을 사용한 결과입니다.

Index, PK등을 잘 잡아주고 있는 모습을 볼 수 있습니다.

```python
# models.py 파일
# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AuthGroup(db.Model):
    __tablename__ = 'auth_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


class AuthGroupPermission(db.Model):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        db.Index('auth_group_permissions_group_id_permission_id_0cd325b0_uniq', 'group_id', 'permission_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.ForeignKey('auth_group.id'), nullable=False, index=True)
    permission_id = db.Column(db.ForeignKey('auth_permission.id'), nullable=False, index=True)

    group = db.relationship('AuthGroup', primaryjoin='AuthGroupPermission.group_id == AuthGroup.id', backref='auth_group_permissions')
    permission = db.relationship('AuthPermission', primaryjoin='AuthGroupPermission.permission_id == AuthPermission.id', backref='auth_group_permissions')


class AuthPermission(db.Model):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        db.Index('auth_permission_content_type_id_codename_01ab375a_uniq', 'content_type_id', 'codename'),
    )

    id = db.Column(db.Integer, primary_key=True)
    content_type_id = db.Column(db.ForeignKey('django_content_type.id'), nullable=False, index=True)
    codename = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    content_type = db.relationship('DjangoContentType', primaryjoin='AuthPermission.content_type_id == DjangoContentType.id', backref='auth_permissions')


class AuthUser(db.Model):
    __tablename__ = 'auth_user'

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime)
    is_superuser = db.Column(db.Boolean, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    is_staff = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False)
    username = db.Column(db.String(150), nullable=False)


class AuthUserGroup(db.Model):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        db.Index('auth_user_groups_user_id_group_id_94350c0c_uniq', 'user_id', 'group_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('auth_user.id'), nullable=False, index=True)
    group_id = db.Column(db.ForeignKey('auth_group.id'), nullable=False, index=True)

    group = db.relationship('AuthGroup', primaryjoin='AuthUserGroup.group_id == AuthGroup.id', backref='auth_user_groups')
    user = db.relationship('AuthUser', primaryjoin='AuthUserGroup.user_id == AuthUser.id', backref='auth_user_groups')


class AuthUserUserPermission(db.Model):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        db.Index('auth_user_user_permissions_user_id_permission_id_14a6b632_uniq', 'user_id', 'permission_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('auth_user.id'), nullable=False, index=True)
    permission_id = db.Column(db.ForeignKey('auth_permission.id'), nullable=False, index=True)

    permission = db.relationship('AuthPermission', primaryjoin='AuthUserUserPermission.permission_id == AuthPermission.id', backref='auth_user_user_permissions')
    user = db.relationship('AuthUser', primaryjoin='AuthUserUserPermission.user_id == AuthUser.id', backref='auth_user_user_permissions')


class DjangoAdminLog(db.Model):
    __tablename__ = 'django_admin_log'

    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Text)
    object_repr = db.Column(db.String(200), nullable=False)
    action_flag = db.Column(db.Integer, nullable=False)
    change_message = db.Column(db.Text, nullable=False)
    content_type_id = db.Column(db.ForeignKey('django_content_type.id'), index=True)
    user_id = db.Column(db.ForeignKey('auth_user.id'), nullable=False, index=True)
    action_time = db.Column(db.DateTime, nullable=False)

    content_type = db.relationship('DjangoContentType', primaryjoin='DjangoAdminLog.content_type_id == DjangoContentType.id', backref='django_admin_logs')
    user = db.relationship('AuthUser', primaryjoin='DjangoAdminLog.user_id == AuthUser.id', backref='django_admin_logs')


class DjangoContentType(db.Model):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        db.Index('django_content_type_app_label_model_76bd3d3b_uniq', 'app_label', 'model'),
    )

    id = db.Column(db.Integer, primary_key=True)
    app_label = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)


class DjangoMigration(db.Model):
    __tablename__ = 'django_migrations'

    id = db.Column(db.Integer, primary_key=True)
    app = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    applied = db.Column(db.DateTime, nullable=False)


class DjangoSession(db.Model):
    __tablename__ = 'django_session'

    session_key = db.Column(db.String(40), primary_key=True)
    session_data = db.Column(db.Text, nullable=False)
    expire_date = db.Column(db.DateTime, nullable=False, index=True)


t_sqlite_sequence = db.Table(
    'sqlite_sequence',
    db.Column('name', db.NullType),
    db.Column('seq', db.NullType)
)
```

## Flask의 app에 덧붙이기

이렇게 만들어진 model은 다른 Extension과 동일하게 Flask app에 붙일 수 있습니다.

`app.py`라는 파일을 하나 만들고 아래 내용으로 채워주세요.

```python
# app.py (models.py와 같은 위치)
from flask import Flask

import models # models.py파일을 가져옵시다.

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:password@DB_IP/DB_NAME"
    models.db.init_app(app)
    return app

if __name__=='__main__':
    app = create_app()
    app.run()
```

앞서 만들어준 `models.py`파일을 가져와 `create_app` 함수를 통해 `app`을 lazy_loading해주는 과정을 통해 진행해 줄 수 있습니다.

## 마치며

기존에 사용하던 DB를 Flask와 SqlAlchemy를 통해 ORM으로 이용해 좀 더 빠른 개발이 가능하다는 것은 큰 이점입니다. ORM에서 DB 생성을 하지 않더라도 이미 있는 DB를 ORM으로 관리하고 Flask 프로젝트에 바로 가져다 쓸 수 있다는 점이 좀 더 빠른 프로젝트 진행에 도움이 될거랍니다.