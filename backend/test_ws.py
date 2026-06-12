import asyncio
import websockets

async def test_ws():
    try:
        async with websockets.connect('ws://127.0.0.1:8000/ws') as ws:
            print('WebSocket connected')
    except Exception as e:
        print(f'WebSocket error: {e}')

asyncio.run(test_ws())
