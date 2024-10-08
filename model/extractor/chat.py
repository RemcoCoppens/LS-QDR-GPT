from dotenv import load_dotenv
from datetime import datetime




import tiktoken




from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

import warnings
from langchain_core._api.beta_decorator import LangChainBetaWarning

warnings.filterwarnings("ignore", category=LangChainBetaWarning)

from model.extractor.schemas import SchemaLookup

class ExtractAttributes:
    def __init__(self, document_type:str, raw_text:str):
        self.setup_environment()

        self.document_type = document_type.upper()
        self.selected_schema = SchemaLookup.get_schema(doctype=document_type)

        self.prompt = self.create_chat_prompts()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0
        )

        self.runnable = self.prompt | self.llm.with_structured_output(
            schema=self.selected_schema,
            method="function_calling",
            include_raw=False,
        )

        self.buffer_tokens = 1000
        self.validation_tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.prompt_token_length = self.get_prompt_token_length(str(self.runnable))
        self.raw_text = self.truncate_text(text=raw_text, token_limit=16384)

        self.attributes = self._EXTRACT(input=self.raw_text)

    def get_prompt_token_length(self, prompt_text:str) -> int:
        tokens = self.validation_tokenizer.encode(prompt_text)
        return len(tokens)

    def truncate_text(self, text: str, token_limit: int) -> str:
        available_tokens = token_limit - self.prompt_token_length

        tokens = self.validation_tokenizer.encode(text)

        if len(tokens) > available_tokens:

            tokens = tokens[:available_tokens]
            truncated_text = self.validation_tokenizer.decode(tokens)
            return truncated_text
        else:
            return text
        
    def setup_environment(self) -> None:
        """Load and set the environmental variables.
        """
        _ = load_dotenv()
        # print('Successfully setup the environment.')

    def create_chat_prompts(self) -> ChatPromptTemplate:
        """Create a chat prompt to guide the LLM to accurately extract the desired schema.

        Returns:
            ChatPromptTemplate: A basic template prompt that can be supplemented with examples.
        """
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Je bent een expert in het extractie-algoritme voor facilitaire diensten. "
                    "Je krijgt voorverwerkte Nederlandse teksten en jouw taak is om alleen relevante informatie te extraheren die overeenkomt met de attributen in de bijbehorende schema's. "
                    "Zorg ervoor dat verschillende attributen nooit dezelfde waarde hebben en alle waarden in stringformaat worden geretourneerd. "
                    "Geef alleen waarden terug waarvan je zeker weet dat ze correct zijn. "
                    "Als je twijfelt over een bepaalde waarde, retourneer dan de aangegeven default waarde."
                ),
                MessagesPlaceholder("examples"),
                ("human", "{text}"),
            ]
        )

    def log_API_call(self, n_tokens:int, cost:float) -> None:
        """Log the size and cost information of the API call made.

        Args:
            n_tokens (int): The total amount of tokens comprising the API call.
            cost (float): The cost associated with this API call.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"Timestamp: {timestamp}, Tokens Used: {n_tokens}, Cost:{round(cost,6)}"

        with open("logs/api_usage_log.txt", "a") as log_file:
            log_file.write(log_entry + "\n")

    def _EXTRACT(self, input:str) -> dict:
        """CAUTION: Cost involved!!
        Extract the information from the given input.

        Args:
            input (str): Raw text from which the attributes need to be extracted.

        Returns:
            dict: An overview of the found attributes.
        """
        attributes = self.runnable.invoke({"text": input, "examples": []})

        return attributes

