import os
import re
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
# This will suppress TensorFlow CUDA related warnings
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

import warnings
from tqdm import TqdmWarning

warnings.filterwarnings("ignore", category=TqdmWarning)

from model.pdf_parser.parser import PdfParser
from model.classifier import Classifier
from model.extractor.chat import ExtractAttributes

class UnknownType(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ProcessDocument:
    def __init__(self, file_path:str):
        self.file_path = file_path
        self.path = os.path.dirname(file_path)
        self.file_name, self.file_ext = os.path.splitext(
            os.path.basename(file_path)
        )
        self.check_document_validity()

        self.clf_model_path = 'model/embeddings/saved_models/QDR-CLF_25-06-2024.h5'

    def check_document_validity(self):
        if self.file_ext.lower() != '.pdf':
            raise UnknownType(
                f"The retrieved document type {self.file_ext.lower()} cannot be processed yet."
            )

    def _PARSE(self):
        self.pdf = PdfParser(
            file_path=self.file_path
        )

    def _CLASSIFY(self):
        self.pdf = PdfParser(
            file_path=self.file_path
        )
        
        self.clf = Classifier(
            raw_text=self.pdf.raw_text,
            file_name=self.file_name
        )

        print(f"The document is classified as: {self.clf.doctype}")
        print(f"with an certainty of: {self.clf.certainty}")

    def _EXTRACT(self):
        self.pdf = PdfParser(
            file_path=self.file_path
        )
        
        self.clf = Classifier(
            raw_text=self.pdf.raw_text,
            file_name=self.file_name
        )

        self.extractor = ExtractAttributes(
            document_type=self.clf.doctype,
            raw_text=self.pdf.raw_text
        )

        self.attributes = self.extractor.attributes.to_dict()

    def add_chat_generated_content(self, text:str, labels:dict) -> str:
        """Add text that chat generated instead of looked up to answer extraction query.

        Args:
            text (str): Raw text extracted from file.
            labels (dict): Attribute labels extracted from file.

        Returns:
            str: Updated string, with prefix of chat generated content.
        """

        generated_labels = []
        for label, values in labels.items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                if value is not None:
                    pattern = re.escape(value)
                    if re.findall(pattern, text) == []:
                        generated_labels.append(
                            f'- {label}: {value}'
                        )

        prefix = "*Chat generated text:* \n"
        postfix = '-' * 20 + '\n\n'
        return prefix + '\n'.join(generated_labels) + postfix + text

    def get_LS_output(self):
        self._EXTRACT()
        adjusted_raw_text = self.add_chat_generated_content(
            text=self.pdf.raw_text, labels=self.attributes
        )
        self.attributes['doctype'] = self.clf.doctype
        adjusted_raw_text = 'KEURINGSRAPPORT || INSPECTIE_ONDERHOUDSRAPPORT' + '\n\n' + adjusted_raw_text
        return adjusted_raw_text, self.attributes
