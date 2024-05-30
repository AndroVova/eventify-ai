from flask import request, jsonify
from app import app
from app.chatbot import handle_chatbot_message

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    message = data.get('message')
    response = handle_chatbot_message(message)
    return jsonify(response)
