---
title: "파이썬으로 HTML을 PDF로 만들기"
date: 2017-04-08
layout: post
categories:
- Python
- Django
published: false
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/Python/PDF-icon.png
---

> 이번 가이드는 HTML문서를 PDF로 만드는 함수를 소개합니다. Python기반 웹 프레임워크에서 사용하는 것을 추천합니다.

## HTML? PDF?
---

웹 개발 프레임워크를 사용할 경우 지속적으로 만나게 되는 것이 바로 서버 사이드 HTML렌더링입니다.

유저가 사용하는 브라우저가 받는 파일은 결국 HTML이기 때문이죠. 물론, API방식을 통해 브라우저에서 프론트엔드 프레임워크를 사용할 수도 있지만, 이번 경우에는 HTML을 렌더링하는 함수가 있다고 가정하고, 그 함수에서 나온 HTML을 PDF로 바꿔보게습니다.

## 문제점 / 해결법
---

pypi에 올라와있는 수많은 pdf용 패키지가 있지만, 그 중에서 `한글`을 지원해주는 패키지는 드뭅니다. 대체적으로 영문만을 지원하며, 이로 인해 UTF-8로 된 HTML문서를 제대로 파싱하지 못합니다.

지금까지 시도 해 본 패키지들은 다음과 같습니다.

### ReportLab

Reportlab은 [Django의 공식 문서: Outputting PDF](https://docs.djangoproject.com/en/1.10/howto/outputting-pdf/)에서도 언급될만큼 광범위하게 사용되는 패키지입니다.

또한, 외부 모듈을 사용하지 않아도 바로 동작하기 때문에 편리하게 이용이 가능합니다.

하지만 장고 공식문서의 코드에서 한글을 입력할 경우 ■ 문자로 나타납니다. 이때문에 한글 문자를 지정해야하는 점이 있습니다.

아래와 같이 `pdfmetrics`와 `TTFont`를 통해 reportlab에 폰트를 강제 지정하면 한글이 잘 나타납니다.

```python
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings # BASE_DIR
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics # reportlab Font setting
from reportlab.pdfbase.ttfonts import TTFont # Font loading
import os # font(ttf file) path

# 폰트 파일의 위치를 지정합니다. django 프로젝트의 manage.py파일이 있는 곳에 두었습니다.
FONT_FILE = os.path.join(settings.BASE_DIR, 'nanum.ttf')
# 폰트의 이름을 지정합니다. 폰트 파일을 열어보았을때 나오는 영문 이름으로 등록해줘야 합니다.
FONT_NAME = 'NanumGothic'
# 이 부분에서 reportlab에 폰트 파일을 등록합니다.
pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))

def some_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    p = canvas.Canvas(response)
    # 이 부분에서 문서(canvas)에서 사용할 폰트와 기본 문자 크기를 지정합니다.
    p.setFont(FONT_NAME, 10)
    p.drawString(100, 100, "안녕안녕") # 이제 한글을 입력해도 깨지지 않습니다.
    p.showPage()
    p.save()
    return response
```

하지만 문제는 여전히 남아있는데, `drawString`함수는 단순하게 문자열을 배치하는 것일 뿐, HTML태그를 Escaping해 실제로 `<html>`와 같은 형식으로 나옵니다.

따라서 썩 좋은 방법이라고 보기는 어렵습니다.

### xhtml2pdf



### pyPdf



### PyPDF2


### WeasyPrint

