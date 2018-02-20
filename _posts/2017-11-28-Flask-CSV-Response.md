---
title: "한글이 보이는 Flask CSV Response 만들기"
date: 2017-11-28
layout: post
categories:
- python
- flask
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/flask.jpg
---

## 들어가며

웹 사이트를 만들다 보면 테이블 등을 csv파일로 다운받을 수 있도록 만들어달라는 요청이 자주 있습니다. 이번 글에서는 Flask에서 특정 URL로 들어갈 때 CSV파일을 받을 수 있도록 만들고, 다운받은 CSV파일을 엑셀로 열 때 한글이 깨지지 않게 처리해 봅시다.

이번에는 Flask + SQLAlchemy + Pandas를 사용합니다.

## Flask 코드짜기

우선 Flask 코드를 하나 봅시다. `app.py`라는 이름을 갖고 있다고 생각해 봅시다.

아래 코드는 `Post`라는 모델을 모두 가져와 `df`라는 DataFrame객체로 만든 뒤 `.to_csv`를 통해 csv 객체로 만들어 준 뒤 `StringIO`를 통해 실제 io가 가능한 바이너리형태로 만들어 줍니다.

또, `output`을 해주기 전 `u'\ufeff'`를 미리 넣어줘 이 파일이 'UTF-8 with BOM'이라는 방식으로 인코딩 되어있다는 것을 명시적으로 알려줍니다.

> 인코딩 명시를 빼면 엑셀에서 파일을 열 때 한글이 깨져서 나옵니다.

```python
# app.py
from io import StringIO
from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # Flask App 만들기
app.config['SQLALCHEMY_DATABASE_URI'] = '데이터베이스 URI' # SQLAlchemy DB 연결하기

db = SQLAlchemy()
db.init_app(app)

# 기타 설정을 해줬다고 가정합니다.

@app.route('/api/post/csv/') # URL 설정하기
def post_list_csv(self):
    queryset = Post.query.all()
    df = pd.read_sql(queryset.statement, queryset.session.bind) # Pandas가 SQL을 읽도록 만들어주기
    output = StringIO()
    output.write(u'\ufeff') # 한글 인코딩 위해 UTF-8 with BOM 설정해주기
    df.to_csv(output)
    # CSV 파일 형태로 브라우저가 파일다운로드라고 인식하도록 만들어주기
    response = Response(
        output.getvalue(),
        mimetype="text/csv",
        content_type='application/octet-stream',
    )
    response.headers["Content-Disposition"] = "attachment; filename=post_export.csv" # 다운받았을때의 파일 이름 지정해주기
    return response 
```
