"""LLM and agent definitions for the assistant's graph."""
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent
from src.backend.chatbot.prompts_builder import answer_agent_builder, tool_agent_builder
from src.backend.config.config import Config
from src.backend.tools.project_tools import PROJECT_TOOLS
from src.backend.tools.task_tools import TASK_TOOLS
from src.backend.tools.workflow_tools import WORKFLOW_TOOLS
from src.backend.schemas.context import Context

_tool_llm = ChatOllama(model=Config.LLM_MODEL, temperature=0, num_predict=6256)
_answer_llm = ChatOllama(model=Config.LLM_MODEL, temperature=0)

tool_agent = create_agent(
        model=_tool_llm,
        tools=[*PROJECT_TOOLS, *TASK_TOOLS, *WORKFLOW_TOOLS],
        context_schema=Context,
        system_prompt=tool_agent_builder()
    )

_answer_prompt = ChatPromptTemplate.from_messages([
    ("system", answer_agent_builder()),
    MessagesPlaceholder("messages"),
    ("human", "Internal report from the operations agent:\n{tool_report}\n\nWrite the final reply to the user based on the conversation above and this report.")
])

answer_chain = _answer_prompt | _answer_llm | StrOutputParser()