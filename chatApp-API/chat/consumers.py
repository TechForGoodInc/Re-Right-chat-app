import asyncio
import json
import datetime
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from django.core.exceptions import ValidationError
from django.core import serializers
from channels.generic.websocket import WebsocketConsumer

from chat.apps import MessagingService as Ms
from chat.models import Message, ChatRoom
from serializers.chat_serializers import ConvMessageSerializer
from userApp.models import User
from .socket_request_types import *
from channels.consumer import SyncConsumer
from django.http import JsonResponse
import logging
logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    current_groups = []

    def websocket_connect(self, event):
        """event triggered when connection handshake is succesful"""
        self.send({'type': 'websocket.accept'})

    def websocket_receive(self, event):
        print('WEBSOCKET RECIEVE CALLED')
        """event triggered when a message is sent to the socket"""
        text_data = event.get('text', None)
        data_json = json.loads(text_data)
        logger.info('RECIEVED AN EVENT: ', data_json)
        _type = data_json.get('type')
        
        if _type == 'INITIAL_SETUP':
            print('INITIAL SETUP CALL')
            self.handleMultiGroupAdd(data_json.get('payload'))
            return
        
        data = data_json.get('payload')
        message, created = self.send_msg(data.get('uid1'), data.get('uid2'), data.get('message'))
        serialized_data = self.serialize(message)

        # hadle new conversation partners that do not have a conversation group
        groupname = f'chat_{message.room.id}'
        if groupname not in self.current_groups: self.handleUniGroupAdd(groupname)
        print('HERE')
        # Send message to room group (group represents the two chatting folks)
        async_to_sync(self.channel_layer.group_send)(
            groupname,
            {
                'type': 'chat_message',
                'message': serialized_data
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        print('CHAT MESSAGE CALLED')
        message = json.dumps(event.get('message'))
        self.send({
            "type": "websocket.send",
            "text": message
        })

    
    def send(self, message): 
        print('SEND CALLED')       
        self.base_send(message)

    def websocket_disconnect(self, close_code):
        pass


    def handleMultiGroupAdd(self, pk):
        """
        creates channel group for a user and all his/her conversation partners
        """
        partners = Ms.get_conversations(pk)
        for partner in partners:
            room = self.get_conv_room(pk, partner.pk)
            chat_room_name = f'chat_{room.id}'
            self.current_groups.append(chat_room_name)

            async_to_sync(self.channel_layer.group_add)(
                chat_room_name,
                self.channel_name
            )
    
    def handleUniGroupAdd(self, groupname):
        """
        creates channel group for a user and another user
        """
        self.current_groups.append(groupname)
        async_to_sync(self.channel_layer.group_add)(
            groupname,
            self.channel_name
        )


    def serialize(self, message):
        return ConvMessageSerializer(message).data

    def get_conv_room(self, pk1, pk2):
        return Ms.get_conversation_room(pk1, pk2)


    def send_msg(self, sender, recipient, message):
        return Ms.send_message(sender, recipient, message)