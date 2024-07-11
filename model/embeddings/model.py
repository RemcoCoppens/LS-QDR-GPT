import tensorflow as tf
from transformers import TFDistilBertModel
import warnings
import logging

tf.get_logger().setLevel('ERROR')
warnings.filterwarnings('ignore', category=FutureWarning, module='huggingface_hub.file_download')
logging.getLogger("transformers").setLevel(logging.ERROR)

class BertCLF(tf.keras.Model):
    def __init__(self, output_dim, max_length=128):
        super(BertCLF, self).__init__()
        self.labels = {0: "KEURINGSRAPPORT", 1: "INSPECTIE_ONDERHOUDSRAPPORT"}
        self.max_length = max_length
        self.bert = TFDistilBertModel.from_pretrained("distilbert-base-uncased")
        self.out = tf.keras.layers.Dense(output_dim, activation='softmax')
        
    def call(self, input_ids, attention_mask, training=False):
        bert_output = self.bert(input_ids=input_ids, attention_mask=attention_mask, training=training)
        embedded = bert_output.last_hidden_state[:, 0, :]
        return self.out(embedded)

    def embed(self, input_ids, attention_mask, training=False):
        input_ids = tf.keras.Input(shape=(self.max_length,), dtype=tf.int32)
        attention_mask = tf.keras.Input(shape=(self.max_length,), dtype=tf.int32)
        
        bert_output = self.bert(input_ids=input_ids, attention_mask=attention_mask, training=training)
        return bert_output.last_hidden_state[:, 0, :]
    