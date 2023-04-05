# Тестовое Задание Сервис с Одним Запросом
В данном репозитории представлено решение тестового задания на FastAPI сервиса с одним запросом.
## Задача
Сделать сервис на FastAPI, предоставляющий один метод: GET /test 

В качестве полезной работы метод спит 3 секунды. 

Метод считается успешным, если при одновременном вызове каждый возвращающийся
 ответ содержит elapsed, отличающийся от предыдущего не менее чем на 3 секунды

## Реализация
Для того, чтобы написать асинхронный GET запрос на FastAPI, который не может обрабатывать несколько вызовов асинхронной функции одновременно, можно использовать механизм блокировки — Lock.

```python script
# Создание объекта блокировки
lock = asyncio.Lock()


async def work() -> None:
    await asyncio.sleep(3)


@router.get("/test", response_model=schemas.TestResponse)
async def handler() -> schemas.TestResponse:
    ts1 = monotonic()

    async with lock:
        # Если блокировка не активна, то вызываем функцию work()
        await work()

    ts2 = monotonic()
    return schemas.TestResponse(elapsed=ts2 - ts1)
```

В этом коде создается глобальный объект блокировки `lock` и передается в контекстный менеджер `async with`, гарантируя, что функция `work` не будет выполняться одновременно более 1 раза. 

Если блокировка активна, то последующие вызовы функции `work` будут ждать ее освобождения. После того, как блокировка перестанет быть активной, то первая вызванная функция `work` начнет свою работу и вернет результат.

## Тесты

Для проверки работы данной функции был написан асинхронный тест на pytest, который отправит несколько одновременных запросов к приложению FastAPI и проверит время полученных ответов между каждыми двумя соседними запросами. Оно должно быть не меньше 3 секунд.
```python script
@pytest.mark.asyncio
@pytest.mark.parametrize("num_requests", [2, 4, 8])
async def test_concurrent_requests(num_requests: int, event_loop) -> None:
    url = f"http://{env.HOSTNAME}:{env.PORT}/test"
    
    async with httpx.AsyncClient(app=app) as client:
        # Отправка num_requests одновременных запросов
        tasks = [asyncio.ensure_future(client.get(url), loop=event_loop) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)

    for response in responses:
        assert response.status_code == 200
    
    # Проверка пройденного времени между каждыми двумя соседними запросами
    for i in range(len(responses)-1):
        time_i = responses[i].json()['elapsed']
        time_j = responses[i+1].json()['elapsed']
        assert time_j - time_i >= 3
```
Данный тест последовательно отправит сначала 2, потом 4, потом 8 одновременных запросов и сравнит время для каждых двух запросов по значению `'elapsed'`, который возвращается из ответа, полученного от сервера.
## Setup
Следуйте шагам описанными ниже, чтобы поднять окружение на локальной машине.

### Dependencies
- python 3.6+
- FastAPI
- pydantic
- uvicorn
- httpx
- pytest-asyncio
- Все python зависимости содержатся в [`requirements.txt`](https://github.com/0105artem/test-balance/blob/main/app/requirements.txt)
         
### Установка
1. В терминале откройте директорию с репозиторием
2. Создайте виртуальное окружение, используя следующую команду
    ```shell script
    $ python3 -m venv venv
    ```
3. Активируйте виртуальное окружение
    Linux:
    ```shell script
    $ source /venv/bin/active
    ```
    Windows:
    ```shell script
    > ./venv/bin/active
    ```
4. Убедитесь что ваше виртуальное окружение активно и установите все необходимые зависимости из файла requirements.txt или вручную:
    ```shell script
    $ pip install -r requirements.txt
    ```
   Или
    ```shell script
    $ pip install fastapi "uvicorn[standard]" pytest-asyncio httpx
    ```
5. *(Опционально)*. Создайте `.env` файл, скопировав в него содержимое файла `.env.sample`. Измените переменные `HOSTNAME` и `PORT` при необходимости. Без создания `.env` файла их значения будут равными `localhost` и `8000` соответственно.
6. Запустите тесты:
    ```shell script
    $ pytest -v
    ```
7. Чтобы запустить API выполните команду
    ```shell script
    $ uvicorn main:app --host localhost --port 8000
    ```

## Обратная связь
- 0105artem@gmail.com
- https://t.me/artemk0rn1lov
