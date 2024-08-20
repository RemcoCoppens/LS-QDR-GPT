"""
Module for document classification using TF-IDF vectorization and SGD Classifier.

This module includes classes and methods to:
- Initialize and load models
- Parse PDF files
- Train and evaluate models
- Classify documents
"""

from abc import ABC

import os
from typing import Tuple
import numpy as np
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from scipy.sparse import vstack

from model.GC import (
    CLF_DEFAULT_CLASS, CLF_DEFAULT_CERTAINTY, DECIMALS_CERTAINTY
)

class ModelInitializer(ABC):
    """
    Base class for initializing the model and vectorizer, and handling model loading.

    Args:
        model_path (str): Path where the model files are stored.
        load_existing_model (bool): Whether to load existing model files or not.
    """

    def __init__(self, model_path:str='model/classifier/saved_models', load_existing_model:bool=True):
        """
        Initialize the ModelInitializer with vectorizer, model, and label encoder.
        
        Args:
            model_path (str): Path where the model files are stored.
            load_existing_model (bool): Whether to load existing model files or not.
        """
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.model = SGDClassifier(loss='modified_huber')
        self.label_encoder = LabelEncoder()

        self.model_path = model_path
        self.load_existing_model = load_existing_model
        if self.load_existing_model:
            self.load_model()

    def check_model_presence(self, model_paths:list) -> None:
        """
        Loop over model paths and check their existence.

        Args:
            model_paths (list): Paths towards the models to be loaded.

        Raises:
            FileNotFoundError: Raised when one or more files are not found.
        """
        missing_files=[]

        for model_path in model_paths:
            if not os.path.isfile(model_path):
                missing_files.append(model_path)

        if missing_files:
            missing_files_text = ', '.join(missing_files)
            raise FileNotFoundError(f"Missing files: {missing_files_text}")

    def load_model(self) -> None:
        """
        Load the trained models from file.
        """
        vectorizer_file = os.path.join(self.model_path, 'tfidf_vectorizer.joblib')
        model_file = os.path.join(self.model_path, 'sgd_classifier_model.joblib')
        label_encoder_file = os.path.join(self.model_path, 'label_encoder.joblib')

        self.check_model_presence(
            model_paths=[vectorizer_file, model_file, label_encoder_file]
        )

        self.vectorizer = joblib.load(vectorizer_file)
        self.model = joblib.load(model_file)
        self.label_encoder = joblib.load(label_encoder_file)

class Classifier(ModelInitializer):
    """
    Document classification model.

    Initialized and used per document, utilizing the ModelInitializer class.

    Args:
        raw_text (str): Raw text of the document to classify.
        file_name (str): Name of the file being classified.
    """

    def __init__(self, raw_text:str, file_name:str):
        """
        Initialize the Classifier with the given document text and file name.

        Args:
            raw_text (str): Raw text of the document to classify.
            file_name (str): Name of the file being classified.
        """
        super().__init__()
        self.file_name = file_name

        try:
            self.doctype, self.certainty = self.classify(raw_text)

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.doctype, self.certainty = CLF_DEFAULT_CLASS, CLF_DEFAULT_CERTAINTY

    def classify(self, raw_text:str) -> Tuple[str, float]:
        """
        Classify a document based on the given inputs.

        Args:
            raw_text (str): Raw text parsed from the PDF document.

        Returns:
            Tuple[str, float]: The predicted label and the certainty of the prediction.
        """
        if not isinstance(raw_text, str):
            raise ValueError(f"Expected string but got {type(raw_text)}")

        x = self.vectorizer.transform([raw_text])
        prediction = self.model.predict(x)
        predicted_label = self.label_encoder.inverse_transform(prediction)

        if hasattr(self.model, 'predict_proba'):
            certainty = round(np.max(self.model.predict_proba(x), axis=1)[0], DECIMALS_CERTAINTY)
        else:
            decision = self.model.decision_function(x)
            certainty = round(np.max(decision), DECIMALS_CERTAINTY)

        return predicted_label[0], certainty
