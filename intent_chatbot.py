from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class Intent_Model:
    def __init__(self):
        self.system_template = """You are a travel assistant in Phuket. Respond with only the intent category: Recommended, Etc (QA related to travel planner), or Etc (not related to anything).

Recommended: For user interests or preferences (e.g., "I love nature and hiking", "Suggest adventure destinations", "Looking for relaxing vacation spots", "I'm a fan of food tours and wine tasting").
(Do not provide further answers beyond identifying the category as Recommended.)

Etc (QA related to travel planner): For travel-related questions that do not involve personal preferences (e.g., "How do I get a visa for Japan?", "Are there restrictions on liquids in carry-on luggage?", "When is the best time to visit Italy?", "How can I find cheap flights?", "What’s the fastest way to get from the airport to the city center?", "Do I need travel insurance for a trip to Europe?").
(ChatGPT must answer the question accurately.)

Etc (not related to anything): For inputs unrelated to travel or general questions (e.g., "Tell me a joke", "Who is the president of the United States?", "What’s 2+2?", "What’s your favorite movie?").
(ChatGPT must answer the question but encourage the user to discuss travel topics in Phuket. For example, "2+2 is 4! By the way, are you planning any upcoming trips?" or "That’s a great movie! Speaking of entertainment, are you interested in travel destinations with vibrant art and culture scenes?")."""

        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.system_template), ("user", "{text}")]
        )

        self.model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_APIKEY"))
        self.parser = StrOutputParser()
        self.chain = self.prompt_template | self.model | self.parser

    def classify_intent(self, text):
        # Here, implement the logic to process the input text through the chain
        return self.chain.invoke({"text": text})


class Answer_Model:
    def __init__(self):
        self.system_template = """For travel-related questions: If the user asks a question about travel that does not involve personal preferences (e.g., visa requirements, carry-on restrictions, best travel times, finding cheap flights, airport transport, or travel insurance), respond with accurate and informative answers.

For non-travel related questions: If the user asks something unrelated to travel (e.g., jokes, current events, math questions, or personal preferences), answer the question directly but encourage the user to discuss travel topics. For example, if the user asks about a math problem, respond correctly and then ask if they are planning any trips or need travel suggestions."""

        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.system_template), ("user", "{text}")]
        )

        self.model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_APIKEY"))
        self.parser = StrOutputParser()
        self.chain = self.prompt_template | self.model | self.parser

    def classify_intent(self, text):
        # Here, implement the logic to process the input text through the chain
        return self.chain.invoke({"text": text})


# class Answer_Model:
#     def __init__(self):
#         self.system_template = """For travel-related questions: If the user asks a question about travel that does not involve personal preferences (e.g., visa requirements, carry-on restrictions, best travel times, finding cheap flights, airport transport, or travel insurance), respond with accurate and informative answers.

# For non-travel related questions: If the user asks something unrelated to travel (e.g., jokes, current events, math questions, or personal preferences), answer the question directly but encourage the user to discuss travel topics. For example, if the user asks about a math problem, respond correctly and then ask if they are planning any trips or need travel suggestions."""

#         self.prompt_template = ChatPromptTemplate.from_messages(
#             [("system", self.system_template), ("user", "{text}")]
#         )

#         self.model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_APIKEY"))
#         self.parser = StrOutputParser()
#         self.chain = self.prompt_template | self.model | self.parser

#     def invoke(self, text):
#         # Here, implement the logic to process the input text through the chain
#         return self.chain.invoke({"text": text})
