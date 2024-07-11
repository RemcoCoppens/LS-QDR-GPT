import os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
# This will suppress TensorFlow CUDA related warnings
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

import warnings
from tqdm import TqdmWarning

warnings.filterwarnings("ignore", category=TqdmWarning)

from model.pdf_parser.parser import PdfParser
from model.embeddings.classifier import EmbeddingClassifier
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
            raise UnknownType(f"The retrieved document type {self.file_ext.lower()} cannot be processed yet.")
    
    def _PARSE(self):
        self.pdf = PdfParser(
            file_path=self.file_path
        )

    def _CLASSIFY(self):
        self.pdf = PdfParser(
            file_path=self.file_path
        )
        
        self.clf = EmbeddingClassifier(
            model_path=self.clf_model_path,
            raw_text=self.pdf.raw_text
        )

        print(f"The document is classified as: {self.clf.doctype}")
        print(f"with an certainty of: {self.clf.certainty}")

    def _EXTRACT(self):
        self.pdf = PdfParser(
            file_path=self.file_path
        )
        
        self.clf = EmbeddingClassifier(
            model_path=self.clf_model_path,
            raw_text=self.pdf.raw_text
        )

        self.extractor = ExtractAttributes(
            document_type=self.clf.doctype, 
            raw_text=self.pdf.raw_text
        )

        self.attributes = self.extractor.attributes.to_dict()

    def get_LS_output(self):
        self._EXTRACT()
        self.attributes['doctype'] = self.clf.doctype
        raw_text = 'KEURINGSRAPPORT || INSPECTIE_ONDERHOUDSRAPPORT' + '\n\n' + self.pdf.raw_text
        return raw_text, self.attributes

if __name__ == "__main__":
    import pandas as pd

    data_dir = "Bonnen Isala"

    output = {
        'fname': [],
        'doctype': [],
        'certainty': []
    }

    for fname in os.listdir(f'data/{data_dir}'):
        doc = ProcessDocument(file_path=f"data/{data_dir}/{fname}")
        doc._CLASSIFY()

        output['fname'].append(fname)
        output['doctype'].append(doc.clf.doctype)
        output['certainty'].append(doc.clf.certainty)

    df = pd.DataFrame(data=output)







