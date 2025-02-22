# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, WebSocketException
# from typing import Dict
# import uuid 
# # Connection management with conversation IDs
# class ConnectionManager:
#     def __init__(self):
#         self.connections: Dict[str, WebSocket] = {}
        
#     def connect(self, conversation_id: str, websocket: WebSocket):
#         # Ensure no duplicate conversation ID is allowed
#         if conversation_id in self.connections:
#             raise WebSocketException(detail="Conversation ID already in use")
#         websocket.accept()
#         self.connections[conversation_id] = websocket

#     def disconnect(self, conversation_id: str):
#         connection = self.connections.pop(conversation_id, None)
#         if connection:
#              connection.close()

#     def send_message(self, conversation_id: str, message: str):
#         connection = self.connections.get(conversation_id)
#         print ("sennding data to websooocket")
#         if connection:
#             print ("sennding data to websooocket")
#             connection.send_text(message)
            
# ws_manager = ConnectionManager()







from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi import WebSocketException
import asyncio
from typing import Dict

# Connection management class
class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, conversation_id: str, websocket: WebSocket):
        if conversation_id in self.connections:
            raise WebSocketException(detail="Conversation ID already in use")
        await websocket.accept()  # Ensure we await the accept
        self.connections[conversation_id] = websocket

    async def disconnect(self, conversation_id: str):
        connection = self.connections.pop(conversation_id, None)
        if connection:
            await connection.close()  # Ensure we await the close

    async def send_message(self, conversation_id: str, message: str):
        connection = self.connections.get(conversation_id)
        print ("connections : ",connection)
        if connection:
            await connection.send_text(message)  # Ensure we await the send

ws_manager = ConnectionManager()