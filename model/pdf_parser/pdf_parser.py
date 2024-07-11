import os
import pandas as pd
from pathlib import Path
from typing import Tuple, List
import fitz

import model.GC as GC

class PDF_Parser:
    def __init__(self, file_path:str, max_pages_ingestion:int):
        self.__method__ = "PURE-PDF"

        self.file_path, self.ext = os.path.splitext(file_path)
        self.file_path = Path(os.path.join(self.file_path + self.ext))

        self.removal_pattern = GC.PAGE_REMOVAL_PATTERNS
        self.max_pages_ingestion = max_pages_ingestion
        self.preview_pages = GC.DOC_PREVIEW_PAGES
        self.doc_min_length = GC.DOC_MINIMAL_LENGTH

        self.text_blocks, self.num_pages = self.extract_textboxes()
        self.overview = self.create_dataframe_overview()
        self.raw_text, self.preview = self.write_raw_text()

    def __str__(self) -> str:
        """Return the raw text parsed from the pdf file.

        Returns:
            str: Raw text from the PDF file.
        """
        return self.raw_text

    def __len__(self) -> int:
        """Return the amount of rows with content.

        Returns:
            int: Integer amount of rows with content.
        """
        return len(self.overview)

    def _output_accepted(self) -> bool:
        """Indicated whether the parsed amount of rows is above the threshold.

        Returns:
            bool: False if below the threshold (which triggers visual parser).
        """
        return len(self.overview) > self.doc_min_length

    def process_text_block(self, text_block:dict, page_nr:int) -> Tuple[dict, int]:
        """Process a single text box retrieved from the PDF. 

        Args:
            text_block (dict): Entire description of a given bounding box (bbox)
            page_nr (int): Index of the current page that is being processed.

        Returns:
            Tuple[dict, int]: Trimmed version of the bbox and its information and the highest y value found.
        """
        if text_block['type'] == 0:
            bbox, text = text_block['bbox'], ""
            for l in text_block['lines']:
                for s in l['spans']:
                    if 'bold' in s['font'].lower():
                        text += f"*{s['text'].lower()}* "
                    else:
                        text += f"{s['text'].lower()} "
                text += " "
            return ({'page': page_nr, 'bbox': bbox, 'text': text})

    def valid_block(self, text_block:dict) -> bool:
        """Evaluate whether the text box is valid.

        Args:
            text_block (dict): bounding box (bbox) and its content.

        Returns:
            bool: True if valid, False otherwise.
        """
        if text_block == None:
            return False
        else:
            return {'bbox', 'text'}.issubset(set(text_block.keys()))

    def clean_list_of_boxes(self, text_blocks:list) -> list:
        """Remove all invalid textboxes from the extracted list of textboxes.

        Args:
            text_blocks (list): collection of uncleaned bboxes and their content.

        Returns:
            list: collection of cleaned bboxes and their content.
        """
        return [text_block for text_block in text_blocks if self.valid_block(text_block)]

    def extract_textboxes(self) -> list:
        """Read the PDF file and extract the text boxes.

        Returns:
            list: collection of bboxes and their content.
        """
        text_boxes = []
        doc = fitz.open(self.file_path)
        for idx, page in enumerate(doc[:self.max_pages_ingestion]):
            blocks = page.get_text('dict')['blocks']

            for block in blocks:
                text_box = self.process_text_block(text_block=block, page_nr=idx+1)
                text_boxes.append(text_box)

        return self.clean_list_of_boxes(text_boxes), doc.page_count

    def clean_dataframe(self, df:pd.DataFrame) -> pd.DataFrame:
        """Remove the pages with a certain removal pattern present in bold.

        Args:
            df (pd.DataFrame): The dataframe to clean.

        Returns:
            pd.DataFrame: A cleaned dataframe, without pages with removal patterns as headers.
        """
        content_pages = [df[df['page'] == i]['content'].to_list() for i in range(1, 21)]
        pages_to_remove = []
        
        for idx, page in enumerate(content_pages):
            page_text = ' '.join(page)
            for pattern in self.removal_pattern:
                if f'*{pattern}*' in page_text:
                    pages_to_remove.append(idx + 1)
        
        return df[~df['page'].isin(pages_to_remove)]
        
    def create_dataframe_overview(self) -> pd.DataFrame:
        """Transform data into dataframe overview, converting lower-left and upper-right to upper-left and lower-right.

        Args:
            text_blocks (list): Data extracted from the pdf file.

        Returns:
            pd.DataFrame: Sorted overview of all content and their location.
        """
        page_nr, x_ul, y_ul, x_lr, y_lr, content = [], [], [], [], [], []
        for text_block in self.text_blocks:
            page_nr.append(text_block['page'])
            x_ul.append(round(text_block['bbox'][0],0))
            y_ul.append(round(text_block['bbox'][1],0))
            x_lr.append(round(text_block['bbox'][2],0))
            y_lr.append(round(text_block['bbox'][3],0))
            content.append(text_block['text'])
        
        df = pd.DataFrame(data={
            'page': page_nr,
            'x_ul': x_ul,
            'y_ul': y_ul,
            'x_lr': x_lr,
            'y_lr': y_lr,
            'content': content
        })

        cleaned_df = self.clean_dataframe(df)

        return cleaned_df.sort_values(by=['page', 'y_ul', 'x_ul'])

    def write_raw_text(self) -> Tuple[str, str]:
        """Transform the overview dataframe into raw text.

        Returns:
            Tuple[str, str]: Raw text and preview string describing the document.
        """
        text, preview = "", ""
        page, cur_y = 1, 0
        for _, row in self.overview.iterrows():
            if row['page'] > page:
                text += "\n\n --- \n"
                page = row['page']
                cur_y = 0

            if row['y_ul'] > cur_y:
                text += "\n"
                cur_y = row['y_ul']

            text += row['content']
            if row['page'] < self.preview_pages:
                preview += row['content']
        return text, preview

    def read_tables(self) -> List[pd.DataFrame]:
        """Read all tables from the document pages and return in the form of pandas dataframes.

        Returns:
            List[pd.DataFrame]: List of dataframes describing all content in the tables.
        """
        doc = fitz.open(self.file_path)
        table_dfs = {page_nr: [] for page_nr in range(self.max_pages_ingestion)}

        for idx, page in enumerate(doc[:self.max_pages_ingestion]):
            table_finder = page.find_tables()
            tables = table_finder.tables

            for table in tables:
                data = table.extract()
                data_dict = {
                    data[0][i]: [
                        data[r][i] for r in range(1, len(data))
                    ] for i in range(len(data[0]))
                }

                df = pd.DataFrame()
                for col in data_dict.keys():
                    df[col] = data_dict[col]
                
                table_dfs[idx].append(df)
        return table_dfs
