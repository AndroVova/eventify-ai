from dotenv import load_dotenv, find_dotenv
import openai
import requests
import json
import os
import pickle
import re

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


def get_tag_names():
    url = "https://eventify-backend.azurewebsites.net/api/Ai/get-tag-names"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"ERROR: ERROE CODE: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"ERROR: {e}"


def message_to_dict(message):
    if isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        return {"role": "bot", "content": message.content}
    return {}


def dict_to_message(msg_dict):
    if "role" not in msg_dict:
        raise KeyError("Missing 'role' in message dictionary")
    if msg_dict["role"] == "user":
        return HumanMessage(content=msg_dict["content"])
    elif msg_dict["role"] == "bot":
        return AIMessage(content=msg_dict["content"])
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

    model = "gpt-4o-2024-05-13"
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm = ChatOpenAI(
        temperature=0.3, model=model, callback_manager=callback_manager, streaming=True
    )
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    memory.chat_memory.messages = [dict_to_message(msg) for msg in history]

    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    return conversation


def start_chat(message, history=[]):
    conversation = set_chat_environment(history)

    userInput = message
    answer = conversation.predict(input=userInput)

    updated_history = [
        message_to_dict(msg) for msg in conversation.memory.chat_memory.messages
    ]

    return answer, updated_history, conversation


def get_tag_info(name):
    url = f"https://eventify-backend.azurewebsites.net/api/Tag/get-by-name?name={name}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Failed to decode JSON for tag '{name}'. Response text: {response.text}")
            return None
    else:
        print(f"Failed to fetch info for tag '{name}'. Status code: {response.status_code}")
        return None

def fetch_events(conversation):
    tagsNames = get_tag_names()
    print("\n\n\nTags:", tagsNames)
    prompt = get_prompt_from_source(constants.TAG_FINDER)
    prompt = prompt.format(tagsNames=tagsNames)
    
    answer = conversation.predict(input=prompt)
    print("\n\n\nAnswer:", answer)

    try:
        match = re.search(r"\{.*\}", answer, re.DOTALL)
        if match:
            json_string = match.group(0)
            extracted_info = json.loads(json_string)
        else:
            raise ValueError("JSON object not found in answer.")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to decode JSON from conversation.predict response: {e}")
        return None
    
    if 'tags' in extracted_info:
        new_tags_structure = []
        for tag_name in extracted_info['tags']:
            tag_info = get_tag_info(tag_name)
            if tag_info:
                new_tags_structure.append({
                    "name": tag_info["name"],
                    "color": tag_info["color"],
                    "id": tag_info["id"]
                })
            else:
                print(f"Tag '{tag_name}' not found or failed to decode.")
        
        extracted_info['tags'] = new_tags_structure

    extracted_info['radius'] = 1.5
    
    post_url = "https://eventify-backend.azurewebsites.net/api/Ai/get-locations"
    headers = {'Content-Type': 'application/json'}
    try:
        post_response = requests.post(post_url, json=extracted_info, headers=headers)
        post_response.raise_for_status()
        post_result = post_response.json()
    except requests.RequestException as e:
        print(f"Failed to send POST request: {e}")
        return None
    
    return post_result



def handle_chatbot_message(message, history=[]):
    result, updated_history, conversation = start_chat(message, history)
    final_response = result

    if "PROCESSING EVENTS" in result or "ПРОЦЕСС ОБРАБОТКИ СОБЫТИЙ" in result:
        events = fetch_events(conversation)
        if not events:
            apology_message = conversation.predict(
                input="""write a very short message that you are sorry for not finding the event for the user. Ask user to give you new date or tag. answer in language the user firstly have spoken."""
            )
            try:
                latest_message = AIMessage(content=apology_message)
                if latest_message.content != "PROCESSING EVENTS":
                    updated_history.append(message_to_dict(latest_message))
            except Exception as e:
                print(f"Error appending message to history: {e}")
            final_response = apology_message
        else:
            success_message = conversation.predict(
                input="""write a very short message that you have found an event. Answer in language the user firstly have spoken."""
            )
            print('\n')
            final_response += success_message + "\n" + json.dumps(events)

    updated_history = [
        message for message in updated_history 
        if message.get('content') != "PROCESSING EVENTS"
    ]
    print(final_response)

    return {"response": final_response, "history": updated_history}


def load_conversation():
    if os.path.exists("conversation_history.pkl"):
        with open("conversation_history.pkl", "rb") as f:
            return pickle.load(f)
    return []
