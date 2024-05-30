from flask import request, jsonify
from app import app
from app.chatbot import handle_chatbot_message, load_conversation

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    app.logger.info("Received POST request at /api/chatbot")
    data = request.json
    message = data.get('message')
    history = data.get('history', [])
    
    response = handle_chatbot_message(message, history)
    
    return jsonify({'response': response['response'], 'history': response['history']})

@app.route('/api/chatbot/history', methods=['GET'])
def get_conversation():
    app.logger.info("Received GET request at /api/chatbot/history")
    conversation = load_conversation()
    return jsonify({'conversation': conversation})

