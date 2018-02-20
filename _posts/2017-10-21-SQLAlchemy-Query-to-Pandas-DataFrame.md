---
title: "SQLAlchemy Query를 Pandas DataFrame로 만들기"
date: 2017-10-21
layout: post
categories:
- flask
- sqlalchemy
- pandas
- tips
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/2017-10-21-SQLAlchemy-Query-to-Pandas-DataFrame.png
---

> 이번 글은 [기존 DB를 Flask-SQLAlchemy ORM Model로 사용하기](/2017/10/20/DB-To-SQLAlchemy-Model/)를 보고 오시면 좀더 빠르게 실 프로젝트에 적용이 가능합니다.

## 들어가며

> 전체 예시를 보시려면 [TL;DR](#tldr)를 참고하세요.

DB에 있는 정보를 파이썬 코드 속에서 SQL raw Query를 통해 정보를 가져오는 아래와 같은 코드의 형태는 대다수의 언어에서 지원합니다.

```python
import sqlite3

# 굳이 sqlite3이 아닌 다른 MySQL와 같은 DB의 connect를 이뤄도 상관없습니다.
# 여기서는 파이썬 파일과 같은 위치에 blog.sqlite3 파일이 있다고 가정합니다.
conn = sqlite3.connect("blog.sqlite3") 
cur = conn.cursor()
cur.execute("select * from post where id < 10;")
```

위와 같은 형식으로 코드를 사용할 경우 웹이 이루어지는 과정 중 2~3번째 과정인 "SQL쿼리 요청하기"와 "데이터 받기"라는 부분을 수동으로 처리해 줘야 하는 부분이 있습니다.

![]({{site.static_url}}/img/noun/how_web_works_DB_SQL.jpeg)

이런 경우 파이썬 파일이더라도 한 파일 안에 두개의 언어를 사용하게 되는 셈입니다. (python와 SQL)

만약 여러분이 Pandas DataFrame객체를 DB에서 가져와 만들려면 이런 문제가 생깁니다.

- DB에 연결을 구성해야 함
- 가져온 데이터를 데이터 타입에 맞춰 파이썬이 이해하는 형태로 변환
- 정리한 데이터를 Pandas로 불러오기

음, 보기만 해도 상당히 귀찮네요.

## 설치하기

우선 필요한 패키지들을 먼저 설치해 줍시다.

```bash
pip install flask
pip install Flask-SQLAlchemy
pip install pandas
```

## Pandas로 SQL요청하기

Pandas에서는 이런 귀찮은 점을 보완해 주기 위해 `read_sql_query`라는 함수를 제공합니다. 위 코드를 조금 바꿔봅시다.

```python
import sqlite3
import pandas as pd # NoQA

conn = sqlite3.connect("blog.sqlite3")
# 이 부분을 삭제
# cur = conn.cursor()
# cur.execute("select * from post where id < 10;")

# 아래 부분을 추가
df = pd.read_sql_query("select * from post where id < 10;", conn)
# df는 이제 Pandas Dataframe 객체
```

단순하게 DB 커넥션, 그리고 `read_sql_query`만으로 SQL Query를 바로 Pandas DataFrame 객체로 받아왔습니다. 이제 데이터를 수정하고 가공하는 처리는 Pandas에게 맡기면 되겠군요!

하지만, 여전히 우리는 SQL을 짜고있어요. 복잡한 쿼리라면 몰라도, 단순한 쿼리를 이렇게까지 할 필요가 있을까요?

## SQLAlchemy 모델 이용하기

Flask를 사용할때 많이 쓰는 SQLAlchemy는 ORM으로 수많은 DB를 파이썬만으로 제어하도록 도와줍니다. 그리고 이 점이 우리가 SQL을 SQLAlchemy를 통해 바로 만들 수 있도록 도와줍니다.

> NOTE: 이번 글에서는 Flask-SQLAlchemy 패키지를 사용합니다. SQLAlchemy와는 약간 다르게 동작할 수도 있습니다.

### 모델 클래스 만들기

모델 클래스를 기존 DB를 참조해 만드는 것은 [기존 DB를 Flask-SQLAlchemy ORM Model로 사용하기](/2017/10/20/DB-To-SQLAlchemy-Model/) 를 참고하세요.

### 예제 모델: Post

블로그에서 자주 쓸 법한 `Post`라는 이름의 모델 클래스를 하나 만들어 봅시다.

우선 `SQLAlchemy`를 `flask_sqlalchemy`에서 import 해옵시다. 그리고 Flask도 가져와 `app`을 만들어 줍시다. 그리고 `db`객체를 만들어줍시다.

```python
from datetime import datetime
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
# 현재 경로의 blog.sqlite3을 불러오기
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.sqlite3'
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
```

자, 이제 여러분은 `blog.sqlite3`파일 안에 `post`라는 테이블에 값들을 넣거나 뺄 수 있게 되었습니다.

### 루트 View 만들기

여러분이 app.run( ) 으로 Flask 개발 서버를 띄웠을 때 첫 화면('/' URL에서) 실행될 View 함수(`post_all`)를 만들어줍시다.

```python
from datetime import datetime
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.sqlite3'
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# 아래 줄을 추가해 줍시다.
# List post which id is less then 10
@app.route('/')
def post_all():
    df = pd.read_sql_query("select * from post where id < 10;", db.session.bind).to_json()
    return jsonify(json.loads(df))
```

자, 분명히 ORM을 쓰는데도 아직 SQL 쿼리를 쓰고있네요! SQL쿼리문을 지워버립시다!

### queryset 객체를 만들기

우리는 `Post`라는 모델을 만들어줬으니 이제 `Post`객체의 `.query`와 `.filter()`를 통해 객체들을 가져와 봅시다.

우선 `queryset`라는 이름에 넣어줍시다. 그리고 Pandas의 `read_sql`(유의: `read_sql_query`가 아닙니다.)에 `queryset`의 내용과 세션을 넘겨줘 DataFrame 객체로 만들어줍시다.

```python
from datetime import datetime
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.sqlite3'
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# List post which id is less then 10
@app.route('/')
def post_all():
    # 이 줄은 지우고,
    # df = pd.read_sql_query("select * from post where id < 10;", db.session.bind).to_json()
    # 아래 두줄을 추가해주세요.
    queryset = Post.query.filter(Post.id < 10)  # SQLAlchemy가 만들어준 쿼리, 하지만 .all()이 없어 실행되지는 않음
    df = pd.read_sql(queryset.statement, queryset.session.bind)  # 진짜로 쿼리가 실행되고 DataFrame이 만들어짐
    return jsonify(json.loads(df).to_json())
```

자, 위와 같이 코드를 짜 주면 이제 SQLAlchemy ORM와 Pandas의 `read_sql`을 통해 `df`이 DataFrame 객체로 자연스럽게 가져오게 됩니다.

## 정리하기

여러분이 Pandas를 사용해 데이터를 분석하거나 정제하려 할 때 웹앱으로 Flask를 사용하고 ORM을 이용한다면, 굳이 SQL Query를 직접 만드는 대신 이처럼 Pandas와 SQLAlchemy의 강력한 조합을 이용해 보세요. 조금 더 효율적인 시스템 활용을 고려한 파이썬 프로그램이 나올거에요!

## <a name="tldr"></a>TL;DR

아래 코드와 같이 모델을 만들고 `db` 객체를 만든 뒤 pandas의 `read_sql`을 사용하면 됩니다.

```python
from datetime import datetime
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.sqlite3'
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# List post which id is less then 10
@app.route('/')
def post_all():
    queryset = Post.query.filter(Post.id < 10)  # SQLAlchemy가 만들어준 쿼리, 하지만 .all()이 없어 실행되지는 않음
    df = pd.read_sql(queryset.statement, queryset.session.bind)  # 진짜로 쿼리가 실행되고 DataFrame이 만들어짐
    return jsonify(json.loads(df).to_json())
```
