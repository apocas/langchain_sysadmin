import json
from langchain.agents import AgentExecutor, AgentOutputParser, ConversationalAgent, ConversationalChatAgent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, HumanMessage

from langchain.agents.agent import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish

from brains.prompt import FORMAT_INSTRUCTIONS, PREFIX, SUFFIX

from brains.tools import ExecuteCommand

#https://github.com/hwchase17/langchain/blob/master/langchain/agents/conversational_chat/

class ConvoOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        cleaned_output = text.strip()
        if "```json" in cleaned_output:
            _, cleaned_output = cleaned_output.split("```json")
        if "```" in cleaned_output:
            cleaned_output, _ = cleaned_output.split("```")
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[len("```json") :]
        if cleaned_output.startswith("```"):
            cleaned_output = cleaned_output[len("```") :]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[: -len("```")]
        cleaned_output = cleaned_output.strip()
        response = json.loads(cleaned_output)
        action, action_input = response["action"], response["action_input"]
        if action == "Final Answer":
            return AgentFinish({"output": action_input}, text)
        else:
            return AgentAction(action, action_input, text)

class SysBrain:
    def __init__(self):
        tools = [
            ExecuteCommand()
        ]

        self.chat = ChatOpenAI(temperature=0, verbose=True,
                               model_name="gpt-3.5-turbo")

        lex_agent = ConversationalChatAgent.from_llm_and_tools(
            llm=self.chat,
            tools=tools,
            system_message = PREFIX,
            human_message = SUFFIX,
            output_parser = ConvoOutputParser()
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)

        self.agent = AgentExecutor.from_agent_and_tools(agent=lex_agent, tools=tools, verbose=True,
                                                        memory=self.memory)

    def addContext(self, message):
        self.memory.chat_memory.add_user_message(message)

    def run(self, message):
        self.agent.run(message)
