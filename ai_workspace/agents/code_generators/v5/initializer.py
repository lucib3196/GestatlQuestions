from ai_workspace.core import (
    LLMConfiguration,
    load_vectorstore,
    validate_paths,
    InitError,
)
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from backend_api.core.logging import logger
from ai_workspace.retrievers import SemanticExamplesCSV
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever
from typing import Union, Optional, Tuple, List, Mapping, Any, Literal


@dataclass(frozen=True)
class GenResources:
    base_llm: BaseChatModel
    fast_llm: BaseChatModel
    long_context_llm: BaseChatModel
    embeddings: object
    q_vectorstore: object
    q_retriver: Union[SemanticExamplesCSV, BaseRetriever]


_ALLOWED_RETRIEVERS = ("csv_semantic_example", "mmr", "similarity")


def _search_kwargs_key(
    search_kwargs: Optional[Mapping[str, Any]],
) -> Tuple[Tuple[str, Any], ...]:
    """Normalize mapping to a stable, hashable key for caching."""
    if not search_kwargs:
        return ()
    # Convert nested unhashables cautiously; here we assume values are hashable or str-repr them.
    # If you expect nested dicts/lists, implement a recursive _freeze().
    return tuple(sorted((k, search_kwargs[k]) for k in search_kwargs))


def _validate_column_names(column_names: Optional[Tuple[str, ...]]) -> None:
    if column_names is None:
        return
    if len(column_names) != 2:
        raise InitError(
            f"Exactly 2 column names are required, got {len(column_names)}."
        )
    if not all(isinstance(c, str) and c for c in column_names):
        raise InitError("column_names must be a tuple of two non-empty strings.")


@lru_cache(maxsize=1)
def init_generation(
    llm_configuration: Optional[type[LLMConfiguration]] = None,
    name: str = "",
    column_names: Optional[Tuple[str, ...]] = None,
    retriever_type: Literal[
        "csv_semantic_example", "mmr", "similarity"
    ] = "csv_semantic_example",
    search_kwargs: Optional[Mapping[str, Any]] = None,
) -> GenResources:
    # Validation
    if retriever_type not in _ALLOWED_RETRIEVERS:
        raise InitError(
            f"Unsupported retriever_type: {retriever_type!r}. Allowed: {_ALLOWED_RETRIEVERS}."
        )
    _validate_column_names(column_names)
    # Removed unused variable 'search_key'

    try:
        # Base
        if llm_configuration:
            cfg = llm_configuration
        else:
            cfg = LLMConfiguration()
        validate_paths(cfg) # type: ignore
        logger.debug("Intializing the %s models")

        def _init(m: str) -> BaseChatModel:
            return init_chat_model(m, model_provider=cfg.model_provider)

        base_llm = _init(cfg.base_model)
        fast_llm = _init(cfg.fast_model)
        long_context_llm = _init(cfg.long_context_model)

        # --- Embeddings & VectorStore ---
        logger.debug("Creating embeddings with model=%s", cfg.embedding_model)
        embeddings = OpenAIEmbeddings(model=cfg.embedding_model)

        logger.debug("Loading vectorstore from %s", cfg.vector_store_path)
        q_vectorstore = load_vectorstore(Path(cfg.vector_store_path), embeddings)

        if column_names and retriever_type != "csv_semantic_example":
            logger.warning(
                "column_names provided but retriever_type=%s; column_names will be ignored.",
                retriever_type,
            )

        if retriever_type == "csv_semantic_example":
            if not column_names:
                raise InitError(
                    "column_names is required when using 'csv_semantic_example' retriever."
                )
            logger.debug(
                "Building CSV semantic retriever from %s with columns=%s",
                cfg.question_csv_path,
                column_names,
            )
            q_retriever = SemanticExamplesCSV(
                column_names=[column_names[0], column_names[1]],
                csv_path=str(cfg.question_csv_path),
                vector_store=q_vectorstore,
            )
        else:
            logger.debug(
                "Building vectorstore retriever type=%s, kwargs=%s",
                retriever_type,
                dict(search_kwargs or {}),
            )
            q_retriever = q_vectorstore.as_retriever(
                search_kwargs=dict(search_kwargs or {}),
                search_type=retriever_type,
            )

        return GenResources(
            base_llm=base_llm,
            fast_llm=fast_llm,
            long_context_llm=long_context_llm,
            embeddings=embeddings,
            q_vectorstore=q_vectorstore,
            q_retriver=q_retriever,
        )

    except InitError:
        # already specific; just propagate
        logger.exception("Configuration validation failed.")
        raise
    except Exception as e:
        # keep stack trace + add context
        logger.exception("Failed to initialize %s generation resources.", name)
        raise InitError(f"Initialization failed: {e}") from e
