import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ClientCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.client_id = self.scope['url_route']['kwargs']['client_id']
        self.lawyer_id = self.scope['url_route']['kwargs']['lawyer_id']
        self.room_group_name = f"call_{self.client_id}_{self.lawyer_id}"

        # Join the room group for the client
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        if action == 'call':
            target = text_data_json['target']
            # Send incoming call to client
            await self.channel_layer.group_send(
                f"call_{self.client_id}_{self.lawyer_id}",
                {
                    'type': 'incoming_call',
                    'from': self.lawyer_id,
                    'message': 'You have an incoming call from the lawyer!'
                }
            )
        elif action == 'accept_call':
            # Notify the lawyer that the client accepted the call
            await self.channel_layer.group_send(
                f"call_{self.client_id}_{self.lawyer_id}",
                {
                    'type': 'call_accepted',
                    'message': 'The client accepted the call!'
                }
            )
        elif action == 'reject_call':
            # Notify the lawyer that the client rejected the call
            await self.channel_layer.group_send(
                f"call_{self.client_id}_{self.lawyer_id}",
                {
                    'type': 'call_rejected',
                    'message': 'The client has rejected the call.'
                }
            )

    # Handle sending messages to the WebSocket
    async def incoming_call(self, event):
        # Send incoming call to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'incoming_call',
            'from': event['from'],
            'message': event['message']
        }))

    async def call_accepted(self, event):
        await self.send(text_data=json.dumps({
            'action': 'call_accepted',
            'message': event['message']
        }))

    async def call_rejected(self, event):
        await self.send(text_data=json.dumps({
            'action': 'call_rejected',
            'message': event['message']
        }))