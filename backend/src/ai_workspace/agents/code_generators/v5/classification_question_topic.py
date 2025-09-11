# ======================
# Standard library
# ======================
from pathlib import Path
from typing import List, Literal

# ======================
# Third-party libraries
# ======================
from langchain_core.documents import Document
from langchain_core.vectorstores.base import VectorStoreRetriever
from langgraph.graph import END, START, StateGraph
from langsmith import Client
from pydantic import BaseModel, Field

# ======================
# Local application
# ======================
from .initializer import init_generation
from src.ai_workspace.core.config import LLMConfiguration
from src.ai_workspace.utils import save_graph_visualization, validate_llm_output


# ======================
# Initialization
# ======================
client = Client()

cfg = LLMConfiguration(
    vector_store_path=Path(r"src/ai_workspace/vectorstores/TOPIC_VS").resolve()
)
llm_config = init_generation(cfg, retriever_type="mmr")
llm_base = llm_config.base_llm
query_prompt = "query_question_topic"
query_grader_prompt = "query_grader_question_topic"

if isinstance(llm_config.q_retriver, VectorStoreRetriever):
    retriever = llm_config.q_retriver
else:
    raise ValueError("Expected VectorStoreRetriever")

NUMBER_SEARCH_QUERIES = 3


# ======================
# Schemas / State
# ======================
class QueryList(BaseModel):
    queries: List[str] = Field(..., description="Search queries")


class GradeDocuments(BaseModel):
    binary_score: Literal["yes", "no"]


class State(BaseModel):
    question: str
    queries: List[str] = []
    retrieved_documents: List[Document] = []
    relevant_documents: List[Document] = []
    topics: List[str] = []


# ======================
# Nodes
# ======================
def generate_queries(state: State) -> dict:
    base_prompt = client.pull_prompt(query_prompt)
    query_generator = base_prompt | llm_base.with_structured_output(QueryList)
    result: QueryList = validate_llm_output(
        query_generator.invoke(
            {"question": state.question, "N_SEARCH_QUERIES": NUMBER_SEARCH_QUERIES}
        ),
        QueryList,
    )
    return {"queries": result.queries}


def retrieve(state: State) -> dict:
    docs: list[Document] = []
    for q in state.queries or []:
        docs.extend(retriever.invoke(q))
    return {"retrieved_documents": docs}


def filter_docs(state: State) -> dict:
    base_prompt = client.pull_prompt(query_grader_prompt)
    grader_chain = base_prompt | llm_base.with_structured_output(GradeDocuments)
    relevant: list[Document] = []

    for doc in state.retrieved_documents or []:
        score = validate_llm_output(
            grader_chain.invoke(
                {"question": state.question, "document": doc.page_content}
            ),
            GradeDocuments,
        )
        if score.binary_score == "yes":
            relevant.append(doc)

    return {"relevant_documents": relevant}


def add_relevant_topics(state: State) -> dict[str, list[str]]:
    topics: set[str] = set()
    for t in state.relevant_documents:
        topic = t.metadata.get("topic_name")
        if topic is None:
            continue
        if isinstance(topic, (set, list, tuple)):
            topics.update(str(x) for x in topic if x)
        else:
            topics.add(str(topic))
    return {"topics": list(topics)}


# ======================
# Graph
# ======================
graph = StateGraph(State)
graph.add_node("generate_queries", generate_queries)
graph.add_node("retrieve", retrieve)
graph.add_node("filter_docs", filter_docs)
graph.add_node("add_relevant_topics", add_relevant_topics)

graph.add_edge(START, "generate_queries")
graph.add_edge("generate_queries", "retrieve")
graph.add_edge("retrieve", "filter_docs")
graph.add_edge("filter_docs", "add_relevant_topics")
graph.add_edge("add_relevant_topics", END)

app = graph.compile()


# ======================
# CLI / Manual test
# ======================
if __name__ == "__main__":
    save_graph_visualization(
        app,  # type: ignore
        "topic_classification.png",
        r"ai_workspace\agents\code_generators\v5\graphs",
    )

    test_questions = [
        {"question": "What is the derivative of sin(x) with respect to x?"},
        {
            "question": "Explain the photoelectric effect and how it supports the particle nature of light."
        },
        {
            "question": "How does Ohm’s Law relate voltage, current, and resistance in a simple circuit?"
        },
        {
            "question": "Calculate the torque produced by a 10 N force applied at a perpendicular distance of 0.5 m from the pivot."
        },
        {
            "question": "State Le Chatelier’s principle and describe how it predicts the shift in equilibrium when pressure is increased."
        },
    ]

    for idx, q in enumerate(test_questions, 1):
        print(f"\n{'=' * 20} Test #{idx} {'=' * 20}\nQuestion: {q['question']}\n")
        try:
            for update in app.stream(q, stream_mode="updates"):  # type: ignore
                print(update, "\n")
        except Exception as exc:
            print(f"❌ Error: {exc}")
