from dotenv import load_dotenv, find_dotenv
import openai
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
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

# Ensure 'constants.py' exists and is in the correct directory
import app.constants as constants

def set_chat_environment():
    load_dotenv(find_dotenv())
    openai.api_key = os.getenv("OPENAI_API_KEY")

    system_instructions = get_prompt_from_source(constants.SYSTEM_INSTRUCTION)

    template = system_instructions
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(template),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    model = "gpt-3.5-turbo-0125"#fallback_model("gpt-4-1106-preview")
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm = ChatOpenAI(
        temperature=0.3, model=model, callback_manager=callback_manager, streaming=True
    )
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    return conversation

def fallback_model(model: str) -> str:
    try:
        openai.Model.retrieve(model)
        # return "gpt-4o-2024-05-13"
        return "gpt-3.5-turbo-0125"
    except openai.BadRequestError:
        print(
            f"Model {model} not available for provided API key. Reverting "
            "to gpt-3.5-turbo-16k. Sign up for the GPT-4 wait list here: "
            "https://openai.com/waitlist/gpt-4-api\n"
        )
        return "gpt-3.5-turbo-0125"
    
def start_chat(message):
    conversation = set_chat_environment()
    userInput = message
    result = conversation.predict(
        input=userInput
    )
    return result


def handle_chatbot_message(message):
    
    result = start_chat(message)

    return {"response": result}


