from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
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

        # summarize
        summarize_prompt = read_txt_files("prompt\summarize.txt")
        self.summarize_prompt_template = PromptTemplate.from_template(
            summarize_prompt
        )

        # self.chain_summarize = self.summarize_prompt_template | self.model | self.parser

    def classify_intent(self, text):
        return self.chain_classify_intent.invoke({"text": text})

    def answer_etc(self, text):
        return self.chain_answer_etc.invoke({"text": text})
    
    def craft_prompt(result, user_input):
        full_template = read_txt_files("prompt\summarize.txt")

        full_prompt = PromptTemplate.from_template(full_template)

        result_prompt = full_prompt.format(
                ("result", result),
                ("user_input", user_input),
            )
        return result_prompt

    def summarization(self, result, user_input):
        full_text = self.summarize_prompt_template.format(result=result, user_input=user_input)
        # prompt = self.craft_prompt(result, user_input)
        # chain_summarize = prompt | self.model | self.parser
        return self.model.invoke([HumanMessage(content=full_text)])

    