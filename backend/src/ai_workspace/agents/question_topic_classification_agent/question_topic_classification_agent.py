"""
Topic-classification workflow (LangGraph).

This pipeline:
1. Generates search queries for a user question.
2. Retrieves candidate topic descriptions from a FAISS vector store.
3. Filters them for relevance.
4. If none are relevant, proposes new topics and checks uniqueness.
5. Optionally stores new topics and updates the vector store.
"""

from __future__ import annotations

import json
from json.decoder import JSONDecodeError
from typing import List, Optional, Literal, Annotated

from pydantic import BaseModel, Field

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import START, END, StateGraph

from ai_workspace.utils import save_graph_visualization, to_serializable, keep_first
from ai_workspace.models import TopicDescription

# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
FASTLLM = "gpt-4o-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"

VECTOR_STORE_PATH = r"ai_workspace/vectorstores/TOPIC_VS"
TOPIC_JSON_PATH = r"./data\topic_data_description.json"
SAVED_INDEX_DIR = "ai_workspace/vectorstores/QTOPIC_VS"
N_SEARCH_QUERIES = 3

# ────────────────────────────────────────────────────────────────────────────────
# Vector store & retriever
# ────────────────────────────────────────────────────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = FAISS.load_local(
    VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2}, search_type="mmr")


# ────────────────────────────────────────────────────────────────────────────────
# Pydantic helper classes
# ────────────────────────────────────────────────────────────────────────────────
class QueryList(BaseModel):
    queries: List[str] = Field(..., description="Search queries")


class GradeDocuments(BaseModel):
    binary_score: Literal["yes", "no"]


class TopicClassification(BaseModel):
    topics: Optional[List[str]]


class GradeAnswer(BaseModel):
    binary_score: Literal["yes", "no"]


class Response(BaseModel):
    topics: List[TopicDescription]


# ────────────────────────────────────────────────────────────────────────────────
# Prompts & chains
# ────────────────────────────────────────────────────────────────────────────────
llm_fast = ChatOpenAI(model=FASTLLM)

# 1️⃣  Search-query generator
query_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""You are an expert at generating high-quality search queries for academic content classification and retrieval.

Your task is to analyze the user's question and generate up to **{N_SEARCH_QUERIES} concise and unique search queries**. These queries will be used to search a database of academic topics or subject descriptions.

### Guidelines:
- Focus on the **core academic intent** behind the question.
- Each query should:
  - Be short, specific, and non-redundant
  - Highlight a distinct aspect or interpretation of the question
  - Help retrieve relevant topics, concepts, or subject areas

### Context:
- The database contains topic names, brief descriptions, and relevant academic disciplines.
- A single question may relate to multiple topics or fields of study.
  - For example:
    - A question about **energy conservation** might relate to both **physics** and **engineering**.
    - A question about **global population trends** might relate to **geography**, **sociology**, and **economics**.

Think broadly and creatively. The goal is to maximize the chance of retrieving useful academic matches by covering different semantic angles of the user's question.
""",
        ),
        ("human", "{question}"),
    ]
)
query_generator = query_prompt | llm_fast.with_structured_output(QueryList)

# 2️⃣  Retrieval grader
retrieval_grade_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a grader evaluating whether a given academic question fits under a specified topic description.

### Task:
Determine if the topic accurately represents the subject matter of the question.

### Guidelines:
- A topic is considered **relevant** if its description includes:
  - Key concepts, terminology, or methods directly related to the question
  - A clear semantic connection to the question’s academic intent or scope
- The match does **not need to be exact**; reasonable academic overlap is acceptable.
- Ignore trivial keyword overlap if the core subject doesn't align.

### Instructions:
- Respond with a **binary score**: either `"yes"` (fits the topic) or `"no"` (does not fit the topic).
- Focus on **conceptual fit**: would a student expect this question to be covered under the given topic in a mechanical engineering course?

### Example Scenarios:
- A question about **heat conduction in rods** would fit under **heat transfer** → `"yes"`
- A question about **electrical circuit design** would not fit under **fluid mechanics** → `"no"`

Use academic reasoning to judge relevance. Don't be overly strict, but do filter out unrelated matches.
""",
        ),
        ("human", "Retrieved document:\n\n{document}\n\nQuestion: {question}"),
    ]
)
retrieval_grader = retrieval_grade_prompt | llm_fast.with_structured_output(
    GradeDocuments
)

# 3️⃣  RAG topic classification
rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an assistant for academic question classification tasks.

Your goal is to analyze the given question and classify it under one or more relevant **mechanical engineering topics** based on the provided topic descriptions.

### Task:
- Review the student's question.
- Identify the core academic concepts and intent.
- Match the question to one or more relevant topics from the provided list.

### Context:
- You will be provided with a list of topic descriptions. Each topic includes:
  - A topic name
  - A short description of what it covers
  - Related engineering disciplines

- A single question may map to **multiple topics**, especially if it spans multiple concepts.
  - For example:
    - A question about **heat conduction in a metal bar** may belong to both **heat transfer** and **materials science**.
    - A question about **stress analysis in a beam** could apply to both **mechanics of materials** and **finite element analysis**.

### Requirements:
- Only return topic names that appear in the provided context.
- If you are unsure or the context does not contain sufficient information, respond with:
  **"I don't know based on the provided information. Return None"**

### Additional Notes:
- Be precise, and avoid making assumptions beyond what the topic descriptions support.
- Consider interdisciplinary overlap when a question logically fits more than one area.
- Think from a student's perspective: Under which topic(s) would this question most likely be taught?

Context:
{context}
""",
        ),
        ("human", "{question}"),
    ]
)
rag_chain = rag_prompt | llm_fast.with_structured_output(TopicClassification)

# 4️⃣  Answer grader (unchanged prompt text)
answer_grade_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a grader assessing whether an answer addresses / resolves a question 

Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question.""",
        ),
        ("human", "User question:\n\n{question}\n\nLLM generation:\n\n{generation}"),
    ]
)
answer_grader = answer_grade_prompt | llm_fast.with_structured_output(GradeAnswer)

# 5️⃣  New topic generator
new_topic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a classification model tasked with generating a new academic topic based on the provided question.

### Objective:
- Analyze the content and intent of the question.
- Generate:
  1. A **concise topic name** that broadly classifies the question.
  2. A **short description** explaining what the topic focuses on.
  3. A list of relevant **engineering disciplines** where this topic is commonly encountered.

### Guidelines:
- The topic should reflect the **core academic concept** behind the question (e.g., "Thermodynamics", "Control Systems").
- The description should be 1–2 sentences summarizing **what the topic covers** in an educational or practical context.
- The list of disciplines should include areas such as Mechanical Engineering, Electrical Engineering, Civil Engineering, etc., where this topic is relevant.
- Avoid overly specific or narrow terms—keep the topic name broad enough for classification purposes.
- If unsure, use academic reasoning to infer the best general category.

### Output Format:
Return a JSON object with the following fields:
- `"name"`: A concise topic name.
- `"description"`: A brief summary of what the topic covers.
- `"disciplines"`: A list of engineering disciplines where this topic is applicable.

### Example Output:
  "name": "Heat Transfer",
  "description": "Examines how thermal energy moves through conduction, convection, and radiation in various systems.",
  "disciplines": ["Mechanical Engineering", "Chemical Engineering", "Aerospace Engineering"]
""",
        ),
        ("human", "User question:\n\n{question}\n"),
    ]
)
new_topic_generator = new_topic_prompt | llm_fast.with_structured_output(Response)

# 6️⃣  Topic uniqueness grader
topic_grader_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a grader assessing whether a newly generated topic is sufficiently distinct from existing topics in a database.

### Task:
You are given:
- A **generated topic** intended to classify a question.
- A list of **closely related existing topics** from the database.

Your goal is to analyze whether the generated topic introduces a **unique and academically meaningful category**, or if it is too similar to existing topics.

### Instructions:
- If the generated topic is **significantly different** in scope, terminology, or conceptual focus from the provided similar topics, respond with `"yes"` (it is unique enough).
- If the generated topic is **too similar or redundant** with existing ones, respond with `"no"`.

### Binary Output:
- `"yes"` — The topic is sufficiently unique and justifies its own category.
- `"no"` — The topic overlaps too heavily with existing entries and should be merged or revised.

If there are no relevant docs given then it is an automatic yes

### Context:
{context}
""",
        ),
        (
            "human",
            "User question:\n\n{question}\n\nThe generated topic was {generation}",
        ),
    ]
)
topic_uniqueness_grader = topic_grader_prompt | llm_fast.with_structured_output(
    GradeDocuments
)


# ────────────────────────────────────────────────────────────────────────────────
# State object used in graph
# ────────────────────────────────────────────────────────────────────────────────
class PipelineState(BaseModel):
    question: Annotated[str, keep_first]
    search_queries: Optional[List[str]] = None
    candidate_topics: Optional[List[TopicDescription]] = None
    topic_classification_result: Optional[TopicClassification] = None
    retrieved_documents: Optional[List[Document]] = None
    relevant_documents: Optional[List[Document]] = None


# ────────────────────────────────────────────────────────────────────────────────
# Graph node functions
# ────────────────────────────────────────────────────────────────────────────────
def generate_queries(state: PipelineState):
    queries = query_generator.invoke({"question": state.question}).queries  # type: ignore
    return {"question": state.question, "search_queries": queries}


def retrieve(state: PipelineState):
    docs: list[Document] = []
    for q in state.search_queries or []:
        docs.extend(retriever.invoke(q))
    return {"retrieved_documents": docs}


def filter_docs(state: PipelineState):
    relevant = []
    for doc in state.retrieved_documents or []:
        score = retrieval_grader.invoke(
            {"question": state.question, "document": doc.page_content}
        )
        if score.binary_score == "yes":  # type: ignore
            relevant.append(doc)
    return {"question": state.question, "relevant_documents": relevant}


def generate_rag_answer(state: PipelineState):
    if not state.relevant_documents:
        return
    generation = rag_chain.invoke(
        {"context": state.relevant_documents, "question": state.question}
    )
    return {
        "topic_classification_result": generation,
        "relevant_documents": state.relevant_documents,
    }


def generate_new_topics(state: PipelineState):
    resp = new_topic_generator.invoke({"question": state.question})
    return {"question": state.question, "candidate_topics": resp.topics}  # type: ignore


def grade_and_store_topics(state: PipelineState):
    print("Insidfe here")
    valid, new_docs = [], []
    for topic in state.candidate_topics or []:
        score = topic_uniqueness_grader.invoke(
            {
                "question": state.question,
                "generation": f"{topic.name}{topic.description}",
                "context": (
                    "\n".join(d.page_content for d in state.retrieved_documents)
                    if state.retrieved_documents
                    else "No supporting documents available."
                ),
            }
        )
        if score.binary_score == "yes":  # type: ignore
            valid.append(topic)
            new_docs.append(
                Document(
                    page_content=f"Topic Name: {topic.name}\nDisciplines: {', '.join(topic.discipline)}\nDescription: {topic.description}",
                    metadata={"source": "topic list", "topic_name": topic.name},
                )
            )

    if valid:
        try:
            with open(TOPIC_JSON_PATH, "r+", encoding="utf-8") as fp:
                data = json.load(fp)
                data["topics"].extend(to_serializable(t) for t in valid)
                fp.seek(0)
                json.dump(data, fp, indent=2)
                fp.truncate()
        except JSONDecodeError as err:
            print(f"❌ JSON error: {err}")

        vectorstore.add_documents(new_docs)
        vectorstore.save_local(SAVED_INDEX_DIR)
    valid = [
        v.name for v in valid
    ]  # Convert to a list of string with just the topic names cant put in topics directly as its a different structure
    return {"question": state.question, "topic_classification_result": valid}


# ────────────────────────────────────────────────────────────────────────────────
# Routing utilities
# ────────────────────────────────────────────────────────────────────────────────
def route_after_filter(state: PipelineState):
    return "generate_rag_answer" if state.relevant_documents else "generate_new_topics"


def route_after_answer(state: PipelineState):
    return END if state.topic_classification_result else "generate_new_topics"


# ────────────────────────────────────────────────────────────────────────────────
# Graph construction
# ────────────────────────────────────────────────────────────────────────────────
graph = StateGraph(PipelineState)

graph.add_node("generate_queries", generate_queries)
graph.add_node("retrieve_docs", retrieve)
graph.add_node("filter_docs", filter_docs)
graph.add_node("generate_rag_answer", generate_rag_answer)
graph.add_node("generate_new_topics", generate_new_topics)
graph.add_node("grade_and_store_topics", grade_and_store_topics)

graph.add_edge(START, "generate_queries")
graph.add_edge("generate_queries", "retrieve_docs")
graph.add_edge("retrieve_docs", "filter_docs")
graph.add_conditional_edges(
    "filter_docs", route_after_filter, ["generate_rag_answer", "generate_new_topics"]
)
graph.add_conditional_edges(
    "generate_rag_answer", route_after_answer, [END, "generate_new_topics"]
)
graph.add_edge("generate_new_topics", "grade_and_store_topics")
graph.add_edge("grade_and_store_topics", END)

app = graph.compile()


if __name__ == "__main__":
    save_graph_visualization(
        app,  # type: ignore
        "topic_classification.png",
        r"ai_workspace/agents/question_topic_classification_agent",
    )

    test_questions = [
        # Mathematics
        {"question": "What is the derivative of sin(x) with respect to x?"},
        # Physics
        {
            "question": "Explain the photoelectric effect and how it supports the particle nature of light."
        },
        # Electrical Engineering / Electronics
        {
            "question": "How does Ohm’s Law relate voltage, current, and resistance in a simple circuit?"
        },
        # Mechanical Engineering
        {
            "question": "Calculate the torque produced by a 10 N force applied at a perpendicular distance of 0.5 m from the pivot."
        },
        # Chemistry
        {
            "question": "State Le Chatelier’s principle and describe how it predicts the shift in equilibrium when pressure is increased."
        },
    ]

    for idx, q in enumerate(test_questions, 1):
        print(f"\n{'='*20} Test #{idx} {'='*20}\nQuestion: {q['question']}\n")
        try:
            for update in app.stream(q, stream_mode="updates"):  # type: ignore
                print(update, "\n")
                if update.get("generate_rag_answer", {}):
                    print(
                        "Generated Classification: ",
                        update.get("generate_rag_answer").get(  # type: ignore
                            "topic_classification_result"
                        ),
                    )
        except Exception as exc:
            print(f"❌ Error: {exc}")
