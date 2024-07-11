from typing import Tuple
import numpy as np
import tensorflow as tf
from transformers import DistilBertTokenizer

from model.embeddings.model import BertCLF

class EmbeddingClassifier:
    def __init__(self, model_path:str, raw_text:str):
        self.tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

        self.model = BertCLF(output_dim=2)
        self.initialize_model(model_weights=model_path)

        self.doctype, self.certainty = self.classify(raw_text)
    
    def initialize_model(self, model_weights:str) -> None:
        _ = self.model(
            input_ids=tf.ones((1, self.model.max_length), dtype=tf.int32), 
            attention_mask=tf.ones((1, self.model.max_length), dtype=tf.int32)
        )
        self.model.load_weights(model_weights)
    
    def classify(self, raw_text:str) -> Tuple[str, np.float32]:
        inputs = self.tokenizer(
            text=raw_text,
            padding='max_length',
            truncation=True,
            max_length=self.model.max_length,
            return_tensors='tf'
        )

        output = self.model(
            input_ids=inputs['input_ids'], 
            attention_mask=inputs['attention_mask']
        )

        return self.model.labels[np.argmax(output)], np.max(output)