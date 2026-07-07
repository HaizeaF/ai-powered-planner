"""LLM chain definitions for the chatbot's agents."""

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from src.backend.prompts.prompts import ANSWER_PROMPT
from src.backend.config.config import Config

_llm = ChatOllama(model=Config.LLM_MODEL, temperature=0)

answer_chain = (
    PromptTemplate(template=ANSWER_PROMPT, input_variables=["context", "question"])
    | _llm
    | StrOutputParser()
)