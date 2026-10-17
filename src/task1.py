'''
    sync : 10.58s
    async: 0.71s
    Синхронный код выполняет запросы по очереди, суммируя время запросов
    Асинхронный код выполняет запросы параллельно, по времени получается только самый долгий
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

def sync_main():
    for url in URLS:
        requests.get(url) # по очереди, время складывается

async def fast_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks= [fetch(client,url) for url in URLS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    timed("sync ", sync_main)
    timed("async", lambda: asyncio.run(fast_main()))