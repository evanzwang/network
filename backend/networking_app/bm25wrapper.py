from typing import Optional, List, Dict
import bm25s
import os
import numpy as np


class BM25SWrapper:
    """
    A wrapper class for BM25S functionality that handles document indexing,
    persistence, and retrieval.

    This class provides an interface to:
    - Index documents with unique IDs
    - Save/load the index and document mappings to/from disk
    - Query documents using BM25 scoring
    - Retrieve original document text by ID

    Attributes:
        retriever (bm25s.BM25): The underlying BM25 search engine
        num_to_id (Optional[np.ndarray]): Mapping of document numbers to IDs
        id_to_text (Optional[Dict[str, str]]): Mapping of document IDs to text content
    """

    NAMES_FILE = "names.npy"

    def __init__(self) -> None:
        """Initialize an empty BM25S wrapper."""
        self.retriever = bm25s.BM25()
        self.names: Optional[List[str]] = None

    def init_bm25(self, name_to_text: Dict[str, str]) -> None:
        """
        Initialize the BM25 index with documents.

        """
        corpus = list(name_to_text.values())
        corpus_tokens = bm25s.tokenize(corpus)

        self.retriever.index(corpus_tokens)
        self.names = list(name_to_text.keys())

    def save(self, location: str) -> None:
        """
        Save the BM25 index and document mappings to disk.

        Args:
            location: Directory path where files should be saved
        Raises:
            AssertionError: If the wrapper hasn't been initialized
        """
        assert self.names is not None

        self.retriever.save(location)
        np.save(os.path.join(location, self.NAMES_FILE), self.names)

    def load(self, location: str) -> None:
        """
        Load the BM25 index and document mappings from disk.

        Args:
            location: Directory path where files are stored
        """
        self.retriever = bm25s.BM25.load(location, load_corpus=False)
        self.names = np.load(os.path.join(location, self.NAMES_FILE)).tolist()

    def query(self, texts: List[str], k: int) -> List[List[str]]:
        """
        Query the index for similar documents.

        Args:
            texts: List of query texts to search for
            k: Number of results to return per query
        Returns:
            List of lists of names for each query
        Raises:
            AssertionError: If texts is not a list or if wrapper hasn't been initialized
        """
        assert isinstance(texts, list)
        query_tokens = bm25s.tokenize(texts)
        doc_nums = self.retriever.retrieve(query_tokens, corpus=self.names, k=k, return_as="documents")
        return doc_nums.tolist()
