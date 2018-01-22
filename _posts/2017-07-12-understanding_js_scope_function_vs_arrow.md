---
title: "자바스크립트: function declaration와 Arrow Function의 this 스코프 차이"
date: 2017-07-12
layout: post
categories:
- JavaScript
published: true
image: https://d1sr4ybm5bj1wl.cloudfront.net/img/understanding_js_scope_function_vs_arrow.png
---

> 이번 포스팅은 ES6 JavaScript 대상입니다.

자바스크립트가 ES6로 개정되며 새로 들어온 것 중 `Arrow Function`이라는 것이 있습니다. `() => {}`의 모양을 갖고 있고 동작하는 것도 비슷하게 보입니다.

하지만 기존의 `function() {}` 함수형태를 1:1로 바로 변환할 수 있는 것은 아닙니다.

## `this`, `arguments`의 바인딩이 다르다.

`Arrow Function`은 `this` 바인딩을 갖지 않습니다. 기존의 `function`에서 `this`의 탐색 범위가 함수의 `{}` 안에서 찾은 반면 `Arrow Function`에서 `this`는 일반적인 인자/변수와 동일하게 취급됩니다. 따라서 아래와 같은 상황이 발생합니다.

```js
// function(){}방식으로 호출할 때
function objFunction() {
  console.log('Inside `objFunction`:', this.foo);
  return {
    foo: 25,
    bar: function() {
      console.log('Inside `bar`:', this.foo);
    },
  };
}

objFunction.call({foo: 13}).bar(); // objFunction의 `this`를 오버라이딩합니다.
```

위 결과는 아래와 같습니다.

```js
Inside `objFunction`: 13 // 처음에 인자로 전달한 값을 받음
Inside `bar`: 25 // 자신이 있는 Object를 this로 인지해서 25를 반환
```

우리가 기대한 그대로 나옵니다. 

하지만 `Arrow Function`을 실행하면 이야기가 약간 달라집니다.

```js
// Arrow Function방식으로 호출할 때
function objFunction() {
  console.log('Inside `objFunction`:', this.foo);
  return {
    foo: 25,
    bar: () => console.log('Inside `bar`:', this.foo),
  };
}

objFunction.call({foo: 13}).bar(); // objFunction의 `this`를 오버라이딩합니다.
```

위 코드의 결과는 아래와 같습니다.

```js
Inside `objFunction`: 13 // 처음에 인자로 전달한 값을 받음
Inside `bar`: 13 // Arrow Function에서 this는 일반 인자로 전달되었기 때문에 이미 값이 13로 지정됩니다.
```

즉, Arrow Function 안의 `this`는 `objFunction`의 `this`가 됩니다.

그리고 이 ArrowFunction은 `this`의 Scope를 바꾸고 싶지 않을 때 특히 유용합니다.

```js
// ES5 function에서는 `this` Scope가 function안에 들어가면 변하기 때문에 새로운 변수를 만들어 씁니다.
var someVar = this;
getData(function(data) {
  someVar.data = data;
});

// ES6 Arrow Function에서는 `this` Scope의 변화가 없기 때문에 `this`를 그대로 사용하면 됩니다.
getData(data => {
  this.data = data;
});
```

이와 같이 Arrow Function에서는 `.bind` method와 `.call` method를 사용할 수 없습니다.

즉, 비슷하게 보이지만 실제로 동작하는 것이 다르기 때문에 사용하는 때를 구별하는 것이 필요합니다.

## Arrow Function은 `new`로 호출할 수 없다

ES6에서 함수는 `callable`한 것과 `constructable`한 것의 차이를 두고 있습니다.

만약 어떤 함수가 constructable하다면 `new`로 만들어야 합니다. 반면 함수가 callable하다면 일반적인 함수처럼 `함수()`식으로 호출하는 것이 가능합니다.

`function newFunc() {}`와 `const newFunc = function() {}`와 같은 방식으로 만든 함수는 `callable`하며 동시에 `constructable`합니다. 하지만 Arrow Function(`() => {}`)은 `callable`하지만 `constructable`하지 **않기**때문에 호출만 가능합니다.

ps. ES6의 `class`는 `constructable`하지만 `callable`하지 않습니다.

## 정리

함수 정의 방식을 바꿔서 사용할 수 있는 경우는 다음과 같습니다.

- `this`나 `arguments`를 사용하지 않는 경우
- `.bind(this)`를 사용하는 경우

함수 정의 방식을 바꿔서 사용할 수 **없는** 경우는 다음과 같습니다.

- `new`등을 사용하는 constructable한 함수
- `prototype`에 덧붙여진 함수나 method들(보통 `this`를 사용합니다.)
- `arguments`를 함수의 인자로 사용한 경우
