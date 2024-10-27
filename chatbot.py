from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from utils import read_txt_file
from dotenv import load_dotenv
import os

load_dotenv()


class Intent_Model:
    def __init__(sel, file_path):
        prompt = read_txt_file(file_path)
        self.system_template = prompt

        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.system_template), ("user", "{text}")]
        )

        self.model = ChatOpenAI(openai_api_key=os.getenv("GPT_KEY1"))
        self.parser = StrOutputParser()
        self.chain = self.prompt_template | self.model | self.parser

    def invoke(self, text):
        # Here, implement the logic to process the input text through the chain
        return self.chain.invoke({"text": text})
