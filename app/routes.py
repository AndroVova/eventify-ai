from flask import request, jsonify
from app import app
from app.chatbot import handle_chatbot_message, load_conversation

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    message = data.get('message')
    history = data.get('history', [])
    
    # Обработка сообщения чат-ботом
    response = handle_chatbot_message(message, history)
    
    return jsonify({'response': response['response'], 'history': response['history']})

@app.route('/api/chatbot/history', methods=['GET'])
def get_conversation():
    conversation = load_conversation()
    return jsonify({'conversation': conversation})
