import uuid
import json
import os

from typing import List, TypedDict, Tuple, Union
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)

from model.pdf_parser.parser import PdfParser
from model.extractor.schemas import SchemaLookup

class Example(TypedDict):
    """A representation of an example consisting of text input and expected tool calls.

    For extraction, the tool calls are represented as instances of pydantic model.
    """
    input: str  
    tool_calls: List[BaseModel] 

class ExampleSet():
    def __init__(self, document_type:str, example_fnames:list):
        self.doctype = document_type
        self.examples_path = "./examples"
        self.selected_schema = SchemaLookup.get_schema(doctype=document_type)
        self.schema_vals = self.selected_schema.get_attribute_names_and_dtypes()
        
        self.examples = self.load_examples(fnames=example_fnames)
        self.messages = self.create_example_set()

    def ensure_dtype(self, dtype: str, var: Union[list, dict, set, tuple], within_function_call:bool=False) -> Union[str, list[str]]:
        """Transform the given variable into the given dtype. (Work iteratively through multiple calls)

        Args:
            dtype (str): The desired data type for the data to be transformed towards.
            var (Union[list, dict, set, tuple]): The variable containing the data.
            within_function_call (bool, optional): If True it is a non-primary call, which adjusts the list[str] behavior. Defaults to False.

        Raises:
            ValueError: Raised whenever a dtype is requested that is not 'list' nor 'str'.

        Returns:
            Union[str, list[str]]: Formatted output in either a string or list of strings.
        """
        if var == None:
            return None
        
        elif dtype == 'list':
            if isinstance(var, dict):
                return [f"{key}: {self.ensure_dtype(dtype, val, True)}" for key, val in var.items()]
            elif isinstance(var, (list, tuple, set)):
                return [self.ensure_dtype(dtype, val, True) for val in var]
            elif within_function_call:
                return str(var)
            else:
                return [str(var)]
        
        elif dtype == 'str':
            if isinstance(var, dict):
                return ", ".join([f"{key}: {self.ensure_dtype(dtype, val)}" for key, val in var.items()])
            else:
                return str(var)
        
        else:
            raise ValueError(f"Requested dtype: '{dtype}' is currently not supported. Only 'str' and 'list' are supported. ")

    def transform_example(self, data:dict) -> Tuple[str, Example]:
        """Transform the textual example into a workable format.

        Args:
            data (dict): Data of a single example, described by text and attribute values.

        Returns:
            Tuple[str, object]: The text and a filled schema for the attributes.
        """
        example = {}
        attributes = data['attributes']
        for name, dtype in self.schema_vals:
            try:
                example[name] = self.ensure_dtype(dtype=dtype, var=attributes[name])
            except KeyError:
                example[name] = None

        return (
            data['text'],
            self.selected_schema(**example)
        )

    def load_examples(self, fnames:list) -> list:
        """Load and transform the examples from the JSON example file.

        Args:
            fnames (list): A list of one or more filenames to be included as examples.

        Returns:
            list: A list of all examples corresponding to the specific document type.
        """
        examples = []
        for fname in fnames:
            text = PdfParser(file_name=fname.replace('.json', '.pdf')).raw_text
            with open(os.path.join(self.examples_path, f"{fname}")) as file:
                attributes = json.load(file)

            examples.append({'text':text, 'attributes':attributes})
        
        return [self.transform_example(example) for example in examples]

    def tool_example_to_messages(self, example:dict) -> List[BaseMessage]:
        """Adapter that converts our example into a list of messages.
        These messages are compatible with the chat model and consist of three parts:
        1) HumanMessage: contains the content from which content should be extracted.
        2) AIMessage: contains the extracted information from the model
        3) ToolMessage: contains confirmation to the model that the model requested a tool correctly.
        
        Args:
            example (dict): Input text and tool-call, formatted as the Example class.

        Returns:
            List[BaseMessage]: Conversational messages explaining the example to the chat model.
        """
        messages: List[BaseMessage] = [HumanMessage(content=example["input"])]
        openai_tool_calls = []
        for tool_call in example["tool_calls"]:
            openai_tool_calls.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "function",
                    "function": {
                        # The name of the function right now corresponds
                        # to the name of the pydantic model
                        # This is implicit in the API right now,
                        # and will be improved over time.
                        "name": tool_call.__class__.__name__,
                        "arguments": tool_call.json(),
                    },
                }
            )
        
        messages.append(
            AIMessage(content="", additional_kwargs={"tool_calls": openai_tool_calls})
        )

        tool_outputs = example.get("tool_outputs") or [
            "You have correctly called this tool."
        ] * len(openai_tool_calls)

        for output, tool_call in zip(tool_outputs, openai_tool_calls):
            messages.append(ToolMessage(content=output, tool_call_id=tool_call["id"]))
            
        return messages

    def create_example_set(self) -> list:
        """Transform all examples into a readable format for the model.

        Args:
            examples (list): Collection of examples in human readable format.

        Returns:
            list: Examples in model readable format.
        """
        messages = []
        for text, tool_call in self.examples:
            messages.extend(
                self.tool_example_to_messages({"input": text, "tool_calls": [tool_call]})
            )
        return messages
    
    def add_example(self, example:dict) -> None:
        """Add a single example to the example set in messages.

        Args:
            example (dict): Input text and atteribute descriptions.
        """
        text, tool_call = self.transform_example(example)
        self.messages.extend(
            self.tool_example_to_messages({"input": text, "tool_calls": [tool_call]})
        )


if __name__ == "__main__":
    examples = ExampleSet(doctype='werkbon')

