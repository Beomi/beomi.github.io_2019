---
title: "React+JSX(ES6)를 빌드 없이 사용하기: browser.js"
date: 2017-03-20
layout: post
categories:
- React
- JavaScript
- ES6
published: true
image: /img/React/react_icon.png
---

## Babel: ES6를 ES5로

바벨(Babel)은 ES6(ECMAScript6)을 ES5 문법으로 변환시켜 오래된 브라우저들에서도 ES6의 기능을 이용할 수 있도록 도와주는 자바스크립트 모듈이다. React는 개발시 ES6 문법을 주로 이용하기 때문에 이러한 Babel은 필수적이라고 말할 수 있다.

## 그러나...

React에서 공식적인 이용 방법 중 하나인 CDN을 이용할 경우 (아래 사진처럼) 실제 첫 튜토리얼을 할 경우 JavaScript에서 JSX를 공식적으로 지원하지 않기 때문에 JS문법 에러가 난다.

![](/img/dropbox/2017-03-21%2000.17.14.png

> 아래 코드는 작동하지 않는다.

```xml
ReactDOM.render(
  <h1>Hello, world!</h1>,
  document.getElementById('root')
);
```

물론 실제 배포시에는 빌드 과정을 거쳐 나온 파일을 관리해야 한다. 하지만 React를 처음 배우는 과정에서는 로컬의 한 HTML파일 안에서 모든 과정이 작동하기를 원하게 된다. 따라서 클라이언트 렌더링을 고려할 수 있다.

> 물론 클라이언트 렌더링은 성능 이슈가 있기 때문에 실 배포시에는 사용하지 않아야 한다.

## Browser.js 사용하기

Babel은 6버전부터 Browser.js를 업데이트 하지 않았다. 하지만 정상적으로 동작하는 파일이 CDN에 존재하기 때문에, HTML문서에 다음 세 줄을 추가해 주면 `script`태그에 `type="text/babel"`이라는 타입을 가진 코드들을 ES6로 간주하고 ES5로 변환해 준다.

```html
<script src="https://unpkg.com/react@15/dist/react.js"></script>
<script src="https://unpkg.com/react-dom@15/dist/react-dom.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-core/5.8.34/browser.js"></script>
```

Browser.js파일을 추가해서 우리는 위 코드를 아래와 같이 쓸 수 있게 된다.

```xml
<script src="https://unpkg.com/react@15/dist/react.js"></script>
<script src="https://unpkg.com/react-dom@15/dist/react-dom.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-core/5.8.34/browser.js"></script>

<div id="root"></div>

<script type="text/babel">
    ReactDOM.render(
        <h1>Hello, world!</h1>,
        document.getElementById('root')
    );
</script>
```

위 코드를 살펴보면 정상적으로 동작한다는 것을 알 수 있다.

## 입문/개발 전용!!

단, 이 방법은 React에 입문하는 사람이 HTML 문서 하나만으로, 그리고 NPM을 사용하지 않고 작업할 경우에 사용할 수 있는 방법이며, 실 프로젝트에서 이와 같이 사용하는 것은 여러 문제를 일으킬 수 있다. 

그러니 입문/개발때에만 사용하자 :) 