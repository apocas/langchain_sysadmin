from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage
)


class GeneralBrain:
    def __init__(self):
        self.chat = ChatOpenAI(temperature=0, verbose=True, model_name="gpt-3.5-turbo")

        self.system = SystemMessage(content="Your job is to identify if each message is an instruction or not. Do not invent output. Your output can only be 'instruction' if the message was an instruction or 'context' otherwise.")

    def run(self, message):
        messages = [self.system, HumanMessage(content=message)]
        return self.chat(messages).content
