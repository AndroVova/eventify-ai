from flask import request, jsonify
from app import app
from app.chatbot import handle_chatbot_message, load_conversation

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    app.logger.info("Received POST request at /api/chatbot")
    try:
        data = request.json
        app.logger.info(f"Received data: {data}")
        message = data.get('message')
        history = data.get('history', [])
        
        response = handle_chatbot_message(message, history)
        app.logger.info(f"Chatbot response: {response}")
        
        return jsonify({'response': response['response'], 'history': response['history']})
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/chatbot/history', methods=['GET'])
def get_conversation():
    app.logger.info("Received GET request at /api/chatbot/history")
    try:
        conversation = load_conversation()
        app.logger.info(f"Conversation history: {conversation}")
        return jsonify({'conversation': conversation})
    except Exception as e:
        app.logger.error(f"Error loading conversation history: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
