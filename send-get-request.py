import requests
import threading
import time

load_balanced_url = 'http://34.102.162.102/get'  # Replace with the target URL
single_machine_url = 'http://34.72.219.170:8080/get'

import asyncio
import aiohttp

async def send_request(session, url):
    async with session.get(url) as response:
        pass

async def main(url, num_requests=1):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for x in range(num_requests):
            task = asyncio.create_task(send_request(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks)

for i in range(10):
    startTime = time.time()
    print(f'Started sending requests at {time.ctime(startTime)}')
    asyncio.run(main(load_balanced_url, 5000))
    endTime = time.time()
    print(f'Finished sending requests at {time.ctime(endTime)}')
    print(f'Total time: {endTime - startTime}')
    print()
    time.sleep(15)
