import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Chat, People

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        result = []
        channel = data["channel"];
        
        messages = Chat.objects.filter(channel=channel).order_by("-timestamp")
        
        for message in messages:
            result.append({
                "channel": message.channel,
                "message": message.message,
                "user": message.people.name,
                "user_id": message.people.id,
                "timestamp": str(message.timestamp)
            })

        content = {
            "messages": result
        }
        
        self.send_message(content)

    def new_message(self, data):
        self.user = self.scope["user"]
        message = Chat.objects.create(
            channel_id=data["channel"],
            people=self.user.people,
            message=data["message"]
        )

        content = {
            "command": "new_message",
            "message": {
                "channel": message.channel.id,
                "message": message.message,
                "user": message.people.name,
                "user_id": message.people.id,
                "timestamp": str(message.timestamp)
            }
        }

        return self.send_chat_message(content)

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope["user"]

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data["command"]](self, data)

    def send_chat_message(self, message):

        #message = data['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
