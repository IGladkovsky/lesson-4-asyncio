'''
    slow : 2.52s
    fixed : 0.64s
    async не дал ускорения потому что await внутри цикла for
    ждал завершения операции а не переходил сразу к следующей,
    в итоге выполнение кода был последовательным
'''


import asyncio
import time

import httpx
import requests

# 20 разных картинок (у каждой свой номер в адресе) — ответы достаточно
# «тяжёлые», чтобы разница между sync и async была хорошо видна
URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]
def timed(label, fn, *args):
    """Запускает fn(*args) и печатает, сколько секунд она работала."""
    start = time.perf_counter()
    fn(*args)
    print(f"{label}: {time.perf_counter() - start:.2f}s")

async def fetch(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url)
    return resp.status_code


async def slow_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in URLS:
            await fetch(client, url) # <-- разобраться и починить

async def fixed_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = []
        for url in URLS:
            task = asyncio.create_task(fetch(client, url))
            tasks.append(task)
        for task in tasks:
            await task

# Запуск и замер — добавь в конец файла:
timed("slow ", lambda: asyncio.run(slow_main()))
# lambda нужна, чтобы запуск произошёл ВНУТРИ timed: если написать
# timed("slow ", asyncio.run(slow_main())), корутина выполнится ещё
# до начала замера, и timed получит уже готовый результат.
timed("fixed ", lambda: asyncio.run(fixed_main()))

