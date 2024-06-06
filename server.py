import asyncio
import websockets
import logging

logging.basicConfig(level=logging.DEBUG)

async def handler(websocket, path):
    logging.info(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            logging.info(f"Received message from {websocket.remote_address}: {message}")
            if message.startswith("broadcast:"):
                await websocket.send("Broadcast received")
            # Handle other message types
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed with error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info(f"Client disconnected: {websocket.remote_address}")

start_server = websockets.serve(handler, "localhost", 11005)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
