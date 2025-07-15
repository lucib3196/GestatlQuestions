import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Optional, List
from langchain_core.documents import Document
from ai_workspace.utils import validate_columns


class SemanticExamplesCSV:
    """
    A class for retrieving semantically similar input-output example pairs from a CSV file using a vector store.
    This class loads a CSV file containing example pairs (e.g., question-answer, input-output), and allows
    retrieval of the most relevant examples to a given query using semantic similarity or max marginal relevance (MMR)
    search via a provided FAISS vector store.
    Args:
        column_names (list[str]): A list of two column names in the CSV, specifying the input and output columns.
        csv_path (str): Path to the CSV file containing the examples.
        vector_store (FAISS): A FAISS vector store instance used for semantic search.
        search_type (str, optional): The type of search to use. Either "similarity" (default) or "mmr".
        filter_kwargs (Optional[dict], optional): Optional filter arguments to pass to the vector store search.
        **search_kwargs: Additional keyword arguments to pass to the vector store search methods.
    Raises:
        ValueError: If column_names does not contain exactly two columns, or if the specified columns are not present in the CSV.
    Methods:
        validate():
            Validates that the specified columns exist in the loaded DataFrame.
        retrieve(query: str, k: int = 2) -> List[Document]:
            Retrieves the top-k most relevant documents from the vector store for the given query.
        extract_examples(query: str, k: int = 2) -> list[tuple[str, str, int]]:
            Retrieves and returns the top-k example pairs (input, output, index) from the CSV corresponding to the query.
        pretty_print_ex(query: str, k: int = 2) -> None:
            Prints the extracted examples for the given query in a human-readable format.
    """

    def __init__(
        self,
        column_names: list[str],
        csv_path: str,
        vector_store: FAISS,
        search_type: str = "similarity",
        filter_kwargs: Optional[dict] = None,
        **search_kwargs,
    ):
        if len(column_names) != 2:
            raise ValueError(
                "column_names must be a list of two columns: [input_column, output_column]"
            )
        self.df = pd.read_csv(csv_path)
        self.vector_store = vector_store
        self.column_names = column_names
        self.filter = filter_kwargs or {}
        self.search_type = search_type
        self.search_kwargs = search_kwargs or {}

        self.validate()

    def set_filter(self, filter_kwargs: dict):
        self.filter = filter_kwargs or {}

    def set_search_kwargs(self, **kwargs):
        self.search_kwargs.update(kwargs)

    def validate(self) -> None:
        """
        Validates that the specified columns exist in the loaded DataFrame.
        Raises:
            ValueError: If column_names does not contain exactly two columns or if the columns are not present.
        """
        if len(self.column_names) != 2:
            raise ValueError(
                "column_names must be a list of two columns: [input_column, output_column]"
            )
        if not validate_columns(self.df, self.column_names):
            raise ValueError(
                f"column_names are not present in dataframe {self.column_names}"
            )

    def retrieve(self, query: str, k: int = 2) -> List[Document]:
        """
        Retrieves the top-k most relevant documents from the vector store for the given query.
        Args:
            query (str): The input query string.
            k (int, optional): Number of top results to retrieve. Defaults to 2.
        Returns:
            List[Document]: List of retrieved Document objects.
        Raises:
            ValueError: If an unknown search_type is specified.
        """
        if self.search_type == "similarity":
            self.results = self.vector_store.similarity_search(
                query,
                filter=self.filter,
                k=k,
                **self.search_kwargs,
            )
            return self.results
        elif self.search_type == "mmr":
            self.results = self.vector_store.max_marginal_relevance_search(
                query,
                filter=self.filter,
                k=k,
                **self.search_kwargs,
            )
            return self.results
        else:
            raise ValueError(f"Unknown search_type: {self.search_type}")

    def extract_examples(self, query: str, k: int = 2) -> list[tuple[str, str, int]]:
        """
        Retrieves and returns the top-k example pairs (input, output, index) from the CSV corresponding to the query.
        Args:
            query (str): The input query string.
            k (int, optional): Number of top examples to extract. Defaults to 2.
        Returns:
            list[tuple[str, str, int]]: List of tuples containing (input, output, index).
        """
        retrieved_d: List[Document] = self.retrieve(query, k)
        indexes = [r.metadata["index"] for r in retrieved_d]
        self.examples = [
            (
                str(self.df.loc[idx, self.column_names[0]]),
                str(self.df.loc[idx, self.column_names[1]]),
                idx,
            )
            for idx in indexes
        ]
        return self.examples

    def pretty_print_ex(self, query: str, k: int = 2) -> None:
        """
        Prints the extracted examples for the given query in a human-readable format.
        Args:
            query (str): The input query string.
            k (int, optional): Number of examples to print. Defaults to 2.
        """
        examples = self.extract_examples(query, k)
        print(f"Extracted Examples for: '{query}'\n")
        print("-" * 120)
        for input_ex, output_ex, idx in examples:
            print(f"CSV Index {idx}")
            print(f"Input:  {input_ex}\nOutput: {output_ex}")
            print("-" * 120)

    def format_template(self, query: str, k: int = 2, base_template: str = "") -> str:
        """
        Formats the extracted examples for the given query and returns them as a string,
        delimited for clarity.
        Args:
            query (str): The input query string.
            k (int, optional): Number of examples to format. Defaults to 2.
            base_template (str, optional): A base template string to prepend. Defaults to "".
        Returns:
            str: The formatted string containing the base template and examples.
        """

        # Replacement is meant to escape code like latex or braces in js code etc probably
        # needs a better implemenation this is always an issue and needs to be worked on
        examples = self.extract_examples(query, k)
        formatted_examples = "\n".join(
            [
                f"--- Example {i+1} ---\nInput Example: {ex[0]}\nExample Output: {ex[1]}\n"
                for i, ex in enumerate(examples)
            ]
        )
        template = (
            base_template
            + "\n"
            + formatted_examples.replace(r"{", r"{{").replace(r"}", r"}}")
            + f"\n: The new input: {query.replace(r"{", r"{{").replace(r"}", r"}}")}"
        )

        return template

    def remove_empty_values(self):
        self.df = self.df.dropna(subset=self.column_names)


if __name__ == "__main__":

    vector_store_path = r"ai_workspace\vectorstores\QUESTIONMOD_VS"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = FAISS.load_local(
        vector_store_path, embeddings, allow_dangerous_deserialization=True
    )
    columns_names = ["question", "question.html"]
    filter = {"isAdaptive": True}

    retriever = SemanticExamplesCSV(
        column_names=columns_names,
        csv_path=r"data\QuestionDataV2_06122025_classified.csv",
        vector_store=vectorstore,
        filter_kwargs=filter,
    )

    query = (
        "A car travels a total distance of 100 miles in 5 hours. Calculate its speed"
    )
    result = retriever.pretty_print_ex(query, 2)

    result = retriever.format_template(query, 2, "This is an example template")

    print(result)
