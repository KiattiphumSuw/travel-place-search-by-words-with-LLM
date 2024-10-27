from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from utils.file import read_txt_files
import os

class Chatbot:
    def __init__(self):
        load_dotenv()
        self.model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_APIKEY"))
        self.parser = StrOutputParser()

        # answer etc
        etc_answer_prompt = read_txt_files("prompt\etc_answer.txt")
        self.etc_answer_prompt_template = ChatPromptTemplate.from_messages(
            [("system", etc_answer_prompt), ("user", "{text}")]
        )

        self.chain_answer_etc = self.etc_answer_prompt_template | self.model | self.parser

        # intent classify
        intent_classify_prompt = read_txt_files("prompt\intent_classify.txt")
        self.intent_classify_prompt_template = ChatPromptTemplate.from_messages(
            [("system", intent_classify_prompt), ("user", "{text}")]
        )

        self.chain_classify_intent = self.intent_classify_prompt_template | self.model | self.parser

    def classify_intent(self, text):
        return self.chain_classify_intent.invoke({"text": text})

    def answer_etc(self, text):
        return self.chain_answer_etc.invoke({"text": text})