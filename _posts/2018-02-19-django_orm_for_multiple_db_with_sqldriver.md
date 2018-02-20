---
title: "DjangoORM에서 SQL Driver 지정해 Query & Pandas DataFrame 얻어내기"
date: 2018-02-19
layout: post
categories:
- django
- tips
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/django_orm_for_multiple_db_with_sqldriver.png
---

## 들어가며

장고의 매력적인 기능 중 하나는 ORM을 통해 SQL을 직접 작성하지 않아도 된다는 점입니다. 즉, 우리가 파이썬 코드를 작성하면 모델 매니저와 SQL Driver를 거쳐 실제로 SQL문으로 만들어주는 일을 장고가 대신해줍니다.

그리고 장고가 DB를 바라보는 방법은 `settings.py`파일 내 `DATABASE`설정 통합니다. 그리고 `default`로 설정된 데이터베이스를 참고해 ORM을 제공합니다. 하지만 이점은 장고 프로젝트 하나에서 여러 데이터베이스를 바라보며 사용할 경우 문제가 발생합니다.

만약 단순하게 모델의 특정 클래스만을 특정 데이터베이스를 바라보게 하려면 다음과 같이 `settings.py`를 작성할 수 있습니다.

장고의 데이터베이스가 아래와 같이 `default`와 `anotherdb`로 두개가 있다고 가정해 봅시다. `default`는 MySQL을, `anotherdb`는 MSSQL을 사용합니다. (SQL 문법이 비슷하지만 약간 다릅니다.)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # MYSQL
        'NAME': 'MYSQLDB',
        'HOST': 'localhost',
        'USER': 'dbuser',
        'PASSWORD': 'dbpassword',
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    },
    'anotherdb': {
        'ENGINE': 'sql_server.pyodbc', # MSSQL
        'HOST': '1.23.4.56', 
        'USER': 'anotheruser',
        'PASSWORD': 'anotherpassword',
    }
}
```

이와 같은 경우 모델 클래스별로 다른 DB를 사용하도록 커스텀 데이터베이스 라우터를 만들어 줄 수 있습니다. 

```python
# settings.py 내
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        return getattr(model, "_DATABASE", None)

    def db_for_write(self, model, **hints):
        return getattr(model, "_DATABASE", None)

    def allow_relation(self, obj1, obj2, **hints):
        db_list = ('default')
        return obj1._state.db in db_list and obj2._state.db in db_list

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'default':
            return True
        else:
            return False

DATABASE_ROUTERS = [
    DatabaseRouter(),
]
```

그리고 `models.py`파일에서는 아래와 같이 `_DATABASE`속성을 넣어주는 방법으로 라우터를 이용할 수 있습니다.

```python
# someapp/models.py
class Post(models.Model):
    _DATABASE = 'anotherdb' # 없으면 자동으로 'default' Fallback

    title = models.CharField(max_length=200)
    content = models.TextField()
```

이후 아래와 같이 `Post` 모델의 모델매니저를 통해 액세스 할 경우 `anotherdb`를 이용하게 됩니다.

```python
queryset = Post.objects.all() # anotherdb로 연결
```

## 문제

하지만 문제가 발생하는 부분이 있습니다. 만약 Queryset을 통해 실제 동작하는 query와 params를 알아내 pandas에서 SQL Query를 읽어 DataFrame 객체로 바꾸는 경우에는 아래와 같이 `queryset.query`로 쿼리에 접근하게 됩니다.

```python
import pandas as pd
from django.db import connections

queryset = Post.objects.all() # QuerySet
query, params = queryset.query.sql_with_params()
# df는 Pandas의 DataFrame가 된다.
df = pd.read_sql_query(query, connections['anotherdb'], params=params)
```

위 코드에서 `Post` 모델의 속성중 `_DATABASE`를 통해 커스텀 데이터베이스 라우터로 `anotherdb`를 바라보도록 만들어주었지만 실제 쿼리를 출력해 볼 경우 MSSQL 쿼리 대신 MySQL 쿼리로 나오는 것을 볼 수 있습니다. 따라서 동작시 에러가 발생합니다.

## 해결법

쿼리셋을 만들고 query 객체에 접근한 뒤 `.sql_with_params()` 대신 `.as_sql()`메소드를 이용해 `compiler`옵션에 해당 데이터베이스의 SQLCompiler 클래스를 직접 전달해주거나 혹은 문자열로 경로를 지정해준 뒤, `connection`에 실제 사용할 데이터베이스 명칭(`DATABASES`의 키값, 없으면 `default`가 됩니다.)을 넣어줍니다.

```python
query, params = queryset.query.as_sql(compiler='sql_server.pyodbc.compiler.SQLCompiler', connection=connections['anotherdb'])
df = pd.read_sql_query(query, connections['anotherdb'], params=params)
```

이제 `df`에 정상적으로 데이터가 들어온 DataFrame 객체가 만들어집니다.

## 편하게 씁시다, 함수 만들기

매번 저렇게 커넥션을 처리해주는 것도 사실 귀찮은 일입니다. 그래서 간단하게 `to_df`라는 함수를 만들어 세가지 인자를 넣으면 처리할 수 있도록 해줍시다.

- `queryset`: 장고의 QuerySet 혹은 raw SQL(str)
- `using`: `settings.py`에 등록한 DB이름('default', 'anotherdb'등)
- `compiler`: 해당 DB의 SQLCompiler, `import`를 통해 가져온 실제 SQLCompiler 클래스 혹은 해당 경로의 문자열

```python
import pandas as df
from django.db import connections
from django.core.exceptions import EmptyResultSet

def to_df(queryset, using=None, compiler=None):
    try:
        if type(queryset) == str: # SQL이 문자열로 그대로 들어올 경우
            query = queryset
            params = None
        else:
            if using: # 어떤 DB를 사용할지 지정한다면..
                con = connections[using]
            else:
                con = connections['default']
            if compiler: # 어떤 SQLCompiler를 사용할지 지정한다면..
                query, params = queryset.query.as_sql(compiler=compiler, connection=con)
            else:
                query, params = queryset.query.sql_with_params()
    except EmptyResultSet: # 만약 쿼리셋의 결과가 비어있다면 빈 DataFrame 반환
        return pd.DataFrame()
    if using: # 어떤 DB를 사용할지 지정했다면 해당 DB connection 이용
        df = pd.read_sql_query(query, connections[using], params=params)
    else:
        df = pd.read_sql_query(query, connection, params=params)
    return df
```