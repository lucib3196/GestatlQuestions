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


@dataclass(frozen=True)
class JSGenResources:
    base_llm: BaseChatModel
    fast_llm: BaseChatModel
    long_context_llm: BaseChatModel
    embeddings: object
    q_vectorstore: object
    q_retriever_js: SemanticExamplesCSV


@lru_cache(maxsize=1)
def init_js_generation() -> JSGenResources:
    """
    Initialize JS generation resources once (cached).
    Raises InitError on any failure with a helpful message.
    """
    try:
        cfg = LLMConfiguration()  # BaseSettings: allows env overrides
        validate_paths(cfg)

        logger.debug("Initializing JS server models…")
        fast_llm = init_chat_model(cfg.fast_model, model_provider=cfg.model_provider)
        base_llm = init_chat_model(cfg.base_model, model_provider=cfg.model_provider)
        long_context_llm = init_chat_model(
            cfg.long_context_model, model_provider=cfg.model_provider
        )

        logger.debug("Creating embeddings with model=%s", cfg.embedding_model)
        embeddings = OpenAIEmbeddings(model=cfg.embedding_model)

        logger.debug("Loading vectorstore from %s", cfg.question_vs)
        q_vectorstore = load_vectorstore(Path(cfg.question_vs), embeddings)

        logger.debug("Building retriever using CSV=%s", cfg.question_csv_path)
        q_retriever_js = SemanticExamplesCSV(
            column_names=["question.html", "server.js"],
            csv_path=str(cfg.question_csv_path),
            vector_store=q_vectorstore,
        )

        logger.info("JS generation resources initialized successfully.")
        return JSGenResources(
            base_llm=base_llm,
            fast_llm=fast_llm,
            long_context_llm=long_context_llm,
            embeddings=embeddings,
            q_vectorstore=q_vectorstore,
            q_retriever_js=q_retriever_js,
        )

    except InitError:
        # already specific; just propagate
        logger.exception("Configuration validation failed.")
        raise
    except Exception as e:
        # keep stack trace + add context
        logger.exception("Failed to initialize JS generation resources.")
        raise InitError(f"Initialization failed: {e}") from e


@dataclass(frozen=True)
class PyGenResources:
    base_llm: BaseChatModel
    fast_llm: BaseChatModel
    long_context_llm: BaseChatModel
    embeddings: object
    q_vectorstore: object
    q_retriever_py: SemanticExamplesCSV


@lru_cache(maxsize=1)
def init_py_generation() -> PyGenResources:
    """
    Initialize Python code generation resources once (cached).
    Raises InitError on any failure with helpful context.
    """
    try:
        # Load configuration from env or defaults
        cfg = LLMConfiguration()
        validate_paths(cfg)

        logger.debug("Initializing Python generation LLMs…")

        # Use init_chat_model to automatically infer model provider
        fast_llm = init_chat_model(cfg.fast_model, model_provider=cfg.model_provider)
        base_llm = init_chat_model(cfg.base_model, model_provider=cfg.model_provider)
        long_context_llm = init_chat_model(
            cfg.long_context_model, model_provider=cfg.model_provider
        )

        logger.debug("Initializing embeddings (model=%s)", cfg.embedding_model)
        embeddings = OpenAIEmbeddings(model=cfg.embedding_model)

        logger.debug("Loading vectorstore from %s", cfg.question_vs)
        q_vectorstore = load_vectorstore(Path(cfg.question_vs), embeddings)

        logger.debug("Initializing retriever with CSV at %s", cfg.question_csv_path)
        q_retriever_py = SemanticExamplesCSV(
            column_names=["question.html", "server.py"],
            csv_path=str(cfg.question_csv_path),
            vector_store=q_vectorstore,
        )

        logger.info("Python generation resources initialized successfully.")
        return PyGenResources(
            base_llm=base_llm,
            fast_llm=fast_llm,
            long_context_llm=long_context_llm,
            embeddings=embeddings,
            q_vectorstore=q_vectorstore,
            q_retriever_py=q_retriever_py,
        )

    except InitError:
        # Already specific, just log and re-raise
        logger.exception("Configuration validation failed.")
        raise
    except Exception as e:
        logger.exception("Failed to initialize Python generation resources.")
        raise InitError(f"Initialization failed: {e}") from e
