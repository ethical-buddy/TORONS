import aiohttp
import asyncio
from aiohttp_socks import ProxyType, ProxyConnector

async def fetch(url, session):
    async with session.get(url) as response:
        return await response.text()

async def main():
    test_url = "http://torch2cjfpa4gwrzsghfd2g6nebckghjkx3bn6xyw6capgj2nqemveqd.onion/"
    url = test_url
    proxy_url = 'socks5://127.0.0.1:9050'

    connector = ProxyConnector.from_url(proxy_url)

    async with aiohttp.ClientSession(connector=connector) as session:
        # You can make multiple requests concurrently by creating multiple tasks
        tasks = [fetch(url, session) for _ in range(5)]

        # Gather all tasks and wait for them to complete
        responses = await asyncio.gather(*tasks)

        for i, response in enumerate(responses, 1):
            print(f'Response {i}: {response[:100]}...')

if __name__ == '__main__':
    asyncio.run(main())
