import asyncio
import websockets
import json

async def send_message(chat_id, token):
    uri = f"ws://localhost:8000/v1/chat/ws/{chat_id}?token={token}"
    async with websockets.connect(uri) as websocket:
        while True:
            message_to_send = input("Enter message to send: ")
            if message_to_send.lower() == 'exit':
                break
            await websocket.send(message_to_send)
            response = await websocket.recv()
            print(f"Received from server: {response}")

async def receive_messages(chat_id, token):
    uri = f"ws://localhost:8000/v1/chat/ws/{chat_id}?token={token}"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            print(f"Received from server: {response}")

async def main():
    chat_id = 7
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcl93c18xIiwiZW1haWwiOiJ0ZXN0dXNlcl93c18xQGV4YW1wbGUuY29tIiwiZXhwIjoxNzU0NTk2MDM3fQ.KLYmpJL9FDqpIvn4bXHt_fOZ0iLAcpEWmOUATM9HhKc"

    # To test sending and receiving in parallel, you can run two instances of this script.
    # In one instance, run send_message, and in the other, run receive_messages.
    # Or, you can use asyncio.gather to run them concurrently in the same script.

    # Example of running both sender and receiver for the same user
    # This will show messages sent by this user being broadcast back to them.
    send_task = asyncio.create_task(send_message(chat_id, token))
    receive_task = asyncio.create_task(receive_messages(chat_id, token))

    await asyncio.gather(send_task, receive_task)


if __name__ == "__main__":
    asyncio.run(main())
