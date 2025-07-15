from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field
from typing import List, Literal, Annotated, Optional
from langchain_core.documents import Document
from ai_workspace.utils import save_graph_visualization, to_serializable
from ai_workspace.utils import keep_first
from ai_workspace.models import TopicDescription
from langgraph.graph import START, END, StateGraph
from collections.abc import Iterable
from itertools import chain
import json

# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
FASTLLM = "gpt-4o-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"

VECTOR_STORE_PATH = r"ai_workspace\vectorstores\TOPIC_VS"
TOPIC_JSON_PATH = r".\data\topic_data_description.json"
SAVED_INDEX_DIR = r"ai_workspace\vectorstores\TOPIC_VS"
N_SEARCH_QUERIES = 3

# ────────────────────────────────────────────────────────────────────────────────
# Vector store & retriever
# ────────────────────────────────────────────────────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = FAISS.load_local(
    VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 1, "fetch_k": 3, "lambda_mult": 0.5},
    search_type="mmr",
)

# ────────────────────────────────────────────────────────────────────────────────
# Prompts & chains
# ────────────────────────────────────────────────────────────────────────────────
llm_fast = ChatOpenAI(model=FASTLLM)

from ai_workspace.chains import (
    generate_academic_query_chain,
    grade_topic,
    new_topic_chain,
)

# Chain focused on quering the database
query_topic_chain = generate_academic_query_chain(FASTLLM, N_SEARCH_QUERIES)
# Chain focused on gradin  the documents
grade_topic_chain = grade_topic(FASTLLM)
# Chain focused on generating the description
new_topic_gen = new_topic_chain(FASTLLM)


class State(BaseModel):
    question: Annotated[str, keep_first]
    topic_name: Optional[str] = None
    search_queries: Optional[List[str]] = None
    retrieved_documents: Optional[List[Document]] = None
    isgenerated: Optional[bool] = None
    generated_topic: Optional[TopicDescription] = None


# ────────────────────────────────────────────────────────────────────────────────
# Graph node functions
# ────────────────────────────────────────────────────────────────────────────────
def generate_queries(state: State):
    queries = query_topic_chain.invoke({"question": state.question}).queries  # type: ignore
    return {"question": state.question, "search_queries": queries}


def retrieve(state: State) -> dict[str, list[Document]]:
    """
    For each query in `state.search_queries`:
    ▸ call `retriever.invoke(query)` → iterable[Document]
    ▸ keep the first document for every *new* topic_name
    Returns {"retrieved_documents": unique_docs}
    """
    if not state.search_queries:
        return {"retrieved_documents": []}

    seen: set[str] = set()  # topic names we've already accepted
    unique_docs: list[Document] = []

    # flatten the doc lists
    for doc in chain.from_iterable(retriever.invoke(q) for q in state.search_queries):
        raw_topic = doc.metadata.get("topic_name")

        # normalise: allow str or any iterable of strs
        if isinstance(raw_topic, str):
            topics = {raw_topic}
        elif isinstance(raw_topic, Iterable):
            topics = {str(t) for t in raw_topic}
        else:
            topics = {str(raw_topic)}

        # skip if we've already seen ANY of these topics
        if topics.isdisjoint(seen):
            seen.update(topics)
            unique_docs.append(doc)

    return {"retrieved_documents": unique_docs}


def route_retriever(state: State):
    if state.retrieved_documents:
        return "grade_topic_uniqueness"
    else:
        return "generate_new_topic"


def grade_topic_uniqueness(state: State):
    docs = state.retrieved_documents
    parsed_docs = "\n".join(f"Topic From DataBase {d.page_content}" for d in docs)  # type: ignore

    input_q = (
        "You are grading whether the proposed topic "
        "The topic to grade is:\n"
        f"{state.question}\n\n"
    )
    score = grade_topic_chain.invoke({"input": input_q, "context": parsed_docs})
    if score.binary_score == "yes":  # type: ignore
        return {"isgenerated": True}
    elif score.binary_score == "no":  # type: ignore
        return {"isgenerated": False}


def route_retriever2(state: State):
    if state.isgenerated:
        return "generate_new_topic"
    else:
        return END


def generate_new_topic(state: State):
    print("Generating new topic")
    resp = new_topic_gen.invoke({"input": state.question})
    return {"generated_topic": resp.topics[0]}  # type: ignore


# Helper function for adding document of type topic description
def create_topic_document(topic: TopicDescription):
    return Document(
        page_content=f"Topic Name: {topic.name}\nDisciplines: {', '.join(topic.discipline)}\nDescription: {topic.description}",
        metadata={"source": "topic list", "topic_name": topic.name},
    )


def add_topic_database(state: State):
    topic = state.generated_topic
    if not topic:
        return
    doc = create_topic_document(topic)
    try:
        with open(TOPIC_JSON_PATH, "r+", encoding="utf-8") as fp:
            data = json.load(fp)
            data["topics"].extend([to_serializable(topic)])
            fp.seek(0)
            json.dump(data, fp, indent=2)
            fp.truncate()
    except json.JSONDecodeError as err:
        print(f"❌ JSON error: {err}")
    vectorstore.add_documents([doc])
    vectorstore.save_local(SAVED_INDEX_DIR)

    return {"generated_topic": topic}


graph = StateGraph(State)
graph.add_node("generate_queries", generate_queries)
graph.add_node("retrieve_docs", retrieve)
graph.add_node("generate_new_topic", generate_new_topic)
graph.add_node("grade_topic_uniqueness", grade_topic_uniqueness)
graph.add_node("add_topic_database", add_topic_database)

graph.add_edge(START, "generate_queries")
graph.add_edge("generate_queries", "retrieve_docs")
graph.add_conditional_edges(
    "retrieve_docs", route_retriever, ["grade_topic_uniqueness", "generate_new_topic"]
)
graph.add_conditional_edges(
    "grade_topic_uniqueness", route_retriever2, [END, "generate_new_topic"]
)
graph.add_edge("generate_new_topic", "add_topic_database")
graph.add_edge("add_topic_database", END)
app = graph.compile()
save_graph_visualization(
    app, "topic_creator.png", r"ai_workspace/agents/topic_creator"  # type: ignore
)

if __name__ == "__main__":
    print("running")
    test = {
        "topic": "Moment",
        "questions": [
            "Determine the moment about point O produced by a 50 N force acting at the beam tip.",
            "Refer to the diagram ‘3dMoment2.png’; compute the moment components M₀ᵢ, M₀ⱼ, M₀ₖ caused by force F.",
            "Find the resultant moment of forces Fᵣ = 10 N and F𝓰 = −5 N about point O.",
        ],
    }

    questions = test.get("questions") or []
    input_question = (
        f"The new topic to be graded\n Topic Name: "
        + (test.get("topic") or "")
        + "\nExample Questions\n"
        + "\n".join(questions)
    )

    for update in app.stream({"question": input_question}, stream_mode="updates"):  # type: ignore
        print(update, "\n")
