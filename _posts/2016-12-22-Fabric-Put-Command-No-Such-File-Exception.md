---
title: 'Fabric Put 커맨드가 No Such File Exception을 반환할 때 해결법'
date: 2016-12-22 01:00:00+09:00
layout: post
categories:
- Python
- Fabric
image: https://upload.wikimedia.org/wikipedia/en/f/fc/CKEditor_logo.png
---

# 환경

```
Python 3.5+
Fabric3
```

# 문제 발생 상황

```py
def _put_envs():
    put('envs.json', '~/{}/envs.json'.format(PROJECT_NAME))
```

이와 같이 로컬에는 `envs.json`파일이 명확히 존재하고 있었다.
그러나 Fabric에서는 

```sh
Fatal error: put() encountered an exception while uploading 'envs.json'
```

위와 같은 에러를 여전히 뿜고 있었다.

하지만 [StackOverflow:Fabric put command gives fatal error: 'No such file' exception](http://stackoverflow.com/questions/6351370/fabric-put-command-gives-fatal-error-no-such-file-exception) 게시글을 살펴보면 이 문제는 Fabirc의 에러 창이 잘못되었다는 것을 말해준다.

즉, 위 에러에서는 로컬 위치에 `envs.json`이 없다고 말하지만 실제로는 서버, 그러니까 `'~/{}/envs.json'.format(PROJECT_NAME)`에 해당하는 위치가 원격 서버 상에 존재하지 않아서 에러를 내는 것이다.

그래서 Fabric코드의 순서를 바꾸어 주었다.

기존 순서가

```py
def _put_envs():
    put(os.path.join(PROJECT_DIR, 'envs.json'), '~/{}/envs.json'.format(PROJECT_NAME))

def _get_latest_source():
    if exists(project_folder + '/.git'):
        run('cd %s && git fetch' % (project_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, project_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (project_folder, current_commit))
```

와 같이 envs를 업로드 후 github소스를 받아오는 것이었다면, 이제는 소스를 먼저 가져온 후 (`_get_latest_source`를 먼저 실행 후) envs를 업로드 하도록 바꾸었다.

이 경우 정상적으로 실행 되었다.


