import asyncio
import time

import httpx
import requests

# 20 разных картинок (у каждой свой номер в адресе) — ответы достаточно
# «тяжёлые», чтобы разница между sync и async была хорошо видна
URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]
URLS.append("https://httpbin.org/delay/10")
URLS.append("https://no-such-site.invalid")
def timed(label, fn, *args):
    """Запускает fn(*args) и печатает, сколько секунд она работала."""
    start = time.perf_counter()
    fn(*args)
    print(f"{label}: {time.perf_counter() - start:.2f}s")

async def robust_fetch(client: httpx.AsyncClient, url: str) -> int:
    RETRIES = 3
    for i in range(RETRIES):
        try:
            resp = await client.get(url,timeout=5.0)
            resp.raise_for_status()
            return resp.status_code
        except httpx.HTTPError:
            if i == RETRIES-1:
                raise
            backoff = 2 ** i
            await asyncio.sleep(0,backoff)

async def robust_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks= [robust_fetch(client,url) for url in URLS]
        responses = await asyncio.gather(*tasks,return_exceptions=True)
        errors = []
        successful_respones = []
        for response in responses:
            if isinstance(response,Exception):
                errors.append(response)
            else:
                successful_respones.append(response)
        return [errors,successful_respones]

if __name__ == "__main__":
    print(asyncio.run(robust_main()))