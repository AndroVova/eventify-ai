from dotenv import load_dotenv, find_dotenv
import openai

import os
import pickle

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from app.utils.file_reader import get_prompt_from_source
import app.constants as constants

load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

def message_to_dict(message):
    if isinstance(message, HumanMessage):
        return {'role': 'user', 'content': message.content}
    elif isinstance(message, AIMessage):
        return {'role': 'bot', 'content': message.content}
    return {}

def dict_to_message(msg_dict):
    if 'role' not in msg_dict:
        raise KeyError("Missing 'role' in message dictionary")
    if msg_dict['role'] == 'user':
        return HumanMessage(content=msg_dict['content'])
    elif msg_dict['role'] == 'bot':
        return AIMessage(content=msg_dict['content'])
    return None

def set_chat_environment(history=[]):
    system_instructions = get_prompt_from_source(constants.SYSTEM_INSTRUCTION)

    template = system_instructions
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(template),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    model = "gpt-3.5-turbo-0125"
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm = ChatOpenAI(
        temperature=0.3, model=model, callback_manager=callback_manager, streaming=True
    )
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    
    # Загрузим историю сообщений в память
    memory.chat_memory.messages = [dict_to_message(msg) for msg in history]

    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    return conversation

def start_chat(message, history=[]):
    conversation = set_chat_environment(history)
    
    userInput = message
    answer = conversation.predict(
        input=userInput
    )
    
    # Обновление истории сообщений
    updated_history = [message_to_dict(msg) for msg in conversation.memory.chat_memory.messages]

    return answer, updated_history

def handle_chatbot_message(message, history=[]):
    result, updated_history = start_chat(message, history)
    return {"response": result, "history": updated_history}

def load_conversation():
    if os.path.exists('conversation_history.pkl'):
        with open('conversation_history.pkl', 'rb') as f:
            return pickle.load(f)
    return []