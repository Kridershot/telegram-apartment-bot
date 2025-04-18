import json
import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
RECEIVER_CHAT_ID = os.getenv('RECEIVER_CHAT_ID')

user_states = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, data=payload)
    return response.json()

def handler(event, context):
    try:
        body = json.loads(event['body'])
        chat_id = body['message']['chat']['id']
        message_text = body['message']['text']
        user_first_name = body['message']['from']['first_name']
        user_username = body['message']['from'].get('username', 'пользователь без имени пользователя') 

        if message_text.strip() == '/start':
            greeting_message = f"Здравствуйте, {user_first_name}!\n\nНапишите цель визита и я ее передам владельцу квартиры, даже если его нет дома."
            send_message(chat_id, greeting_message)
            user_states[chat_id] = 'waiting_for_message'
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'greeting sent'}),
                'isBase64Encoded': False
            }

        if chat_id in user_states and user_states[chat_id] == 'waiting_for_message':
            # Формируем сообщение для RECEIVER_CHAT_ID
            formatted_message = (f"Пользователь {user_first_name} оставил сообщение.\n\n"
                                 f"Цель визита: {message_text}\n\n"
                                 f"Ссылка на пользователя: https://t.me/{user_username}")
            send_message(RECEIVER_CHAT_ID, formatted_message)
            send_message(chat_id, "Хорошо, я передам это сообщение. Хорошего дня!")
            del user_states[chat_id]
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'message sent'}),
                'isBase64Encoded': False
            }

        # Если команда или сообщение не распознаны
        send_message(chat_id, "Пожалуйста, введите /start, прежде чем отправлять сообщения.")
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'waiting for command'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }