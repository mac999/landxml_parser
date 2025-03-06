# title: open api client call example
# author: kang taewook
# email: laputa99999@gmail.com
# 
import json, traceback, asyncio, websockets, aiohttp # import httpx
from aiohttp import ClientSession, ClientTimeout

async def call_calc_align():
    params = {"length": "10"}
    t = ClientTimeout(total=60*2)  # 2 minutes
    async with aiohttp.ClientSession(timeout=t) as session:
        async with session.post('http://localhost:8001/v1/calc/align', params=params) as resp:
            results = await resp.text()
            print(results)

async def connect():
    async with websockets.connect('ws://localhost:8001/ws/align') as websocket:
        CHUNK_SIZE = 64 * 1024  # 64KB
        full_data = None
        received_count = 0
        try:
            while True:
                chunk = await asyncio.wait_for(websocket.recv(), timeout=5) # adjust timeout value considering internet speed
                if full_data is None:
                    full_data = chunk
                else:
                    full_data += chunk
                received_count += len(chunk) 
                print('Received data: ', received_count)
        except asyncio.TimeoutError:
            print("Timeout error: The server didn't respond within 5 seconds")
        except Exception as e:
            print(e)
            pass
        
        print('Received data: ', received_count)
        data = json.loads(full_data)
        try:
            os.remove('download_output_landxml.json')
        except:
            pass
        with open('download_output_landxml.json', 'w') as json_file:
            json.dump(data, json_file)
            print('JSON data saved to file.')

def main():
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(call_calc_align())
        loop.run_until_complete(connect())
    except Exception as e:
        print(traceback.format_exc())

if __name__ == '__main__':
    main()