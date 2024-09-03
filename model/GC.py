"""
Defines constants used throughout the application.

Constants:
- VALID_DOC_TYPES: List of document file extensions that can be processed.
- PDF_PARSE_THRESHOLD: Minimum token count threshold for Pure-PDF parsing.
- MAX_PAGES_INGESTION: Maximum number of pages to process.
- PAGE_REMOVAL_PATTERNS: Patterns for page removal.
- DOC_PREVIEW_PAGES: Number of pages used to create a preview.
- DOC_MINIMAL_LENGTH: Minimum row length for Pure-PDF parsing.
- CLF_MODEL_PATH: Path to the classification model file.
- CLF_DEFAULT_CLASS: Default classification when unknown.
- CLF_DEFAULT_CERTAINTY: Default certainty level.
- DECIMALS_CERTAINTY: Number of decimal places for certainty rounding.
- SIMILARITY_THRESHOLD: The minimum similarity score to be accepted as an example.
"""

VALID_DOC_TYPES = ['.pdf']

PDF_PARSE_THRESHOLD = 0
MAX_PAGES_INGESTION = 15
PAGE_REMOVAL_PATTERNS = ["inhoudsopgave", "gebruikte afkortingen"]

DOC_PREVIEW_PAGES = 2
DOC_MINIMAL_LENGTH = 5

CLF_MODEL_PATH = 'embeddings/saved_models/QDR-CLF_25-06-2024.h5'
CLF_DEFAULT_CLASS = 'UNKNOWN'
CLF_DEFAULT_CERTAINTY = 0.0
DECIMALS_CERTAINTY = 3

SIMILARITY_THRESHOLD = 0.9
