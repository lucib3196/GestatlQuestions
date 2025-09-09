from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ai_workspace.utils import save_graph_visualization
from typing import Optional

# Constants
FASTLLM = "gpt-4o-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"

# Define the vector store
# Load the vector Store and set up retriever
vector_store_path = r"ai_workspace\vectorstores\ME_course_catalog_index"
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = FAISS.load_local(
    vector_store_path, embeddings, allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


# Router will route between a websearch and a vectorstore with ucr information of classes
class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,
        description="Given the user question choose to route it to vector store or websearch",
    )


llm_router = ChatOpenAI(model=FASTLLM)
structured_router = llm_router.with_structured_output(RouteQuery)
route_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to engineering courses specifically mechanical engineering courses at the University of California Riverside
Use the vectorstore for questions on these topics. Otherwise, use web-search.""",
        ),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_router


## Query Generator
class Query(BaseModel):
    """A list of queries which will be used for the retrieval"""

    queries: List[str] = Field(..., description="A list of queries for searching")


llm_query = ChatOpenAI(model=FASTLLM)
structured_query = llm_query.with_structured_output(Query)
query_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at generating effective search queries for databases and web search.
Analyze the user's message carefully. The question may require multiple distinct queries, or just one.
Look at the input and try to reason about the underlying semantic intent

Your task is to generate up to **three concise and unique search queries** based on the user's question.
Each query should:
- Be to the point
- Avoid redundancy
- Target a different aspect or interpretation of the user's intent (if applicable)

Additionally also analyze wether they give a specific course code this is a valid search query
""",
        ),
        ("human", "{question}"),
    ]
)

query_generator = query_prompt | structured_query


## Retrieval grader
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: Literal["yes", "no"] = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


llm = ChatOpenAI(model=FASTLLM)
structured_llm_grader = llm.with_structured_output(GradeDocuments)

system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)
retrieval_grader = grade_prompt | structured_llm_grader

## Generate
system = """You are an assistant for academic question-answering tasks. Use the provided context to answer the user's question.

Your goal is to help students understand which courses are available at UCR. When answering:
- Only reference courses that are included in the context.
- Provide a detailed explanation of each relevant course.
- Describe what each course covers and what students can expect to learn or gain from it.

If the answer is not in the context, say: "I don't know based on the provided information."

Context:
{context}
"""
rag_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
llm = ChatOpenAI(model=FASTLLM)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = rag_prompt | llm | StrOutputParser()


## Hallucination Grader
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: Literal["yes", "no"] = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


llm = ChatOpenAI(model=FASTLLM)
structured_llm_grader = llm.with_structured_output(GradeHallucinations)
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)
hallucination_grader = hallucination_prompt | structured_llm_grader


### Answer Grader
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: Literal["yes", "no"] = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


llm = ChatOpenAI(model=FASTLLM)
structured_llm_grader = llm.with_structured_output(GradeAnswer)

# Prompt
system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)
answer_grader = answer_prompt | structured_llm_grader


# Define the graph
class State(BaseModel):
    question: str
    queries: Optional[List[str]] = None
    generation: Optional[str] = None
    documents: Optional[List[Document]] = None


def generate_queries(state: State):
    question = state.question
    results = query_generator.invoke({"question": question})
    return {"question": question, "queries": results.queries}  # type: ignore


def retrieve(state: State):
    queries = state.queries
    all_documents = []
    for q in queries:  # type: ignore
        document = retriever.invoke(q)
        all_documents.extend(document)
    return {"documents": all_documents}


def generate(state: State):
    question = state.question
    documents = state.documents
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}


def grade_documents(state: State):
    question = state.question
    documents = state.documents

    # Score each doc
    filtered_docs = []
    for d in documents:  # type: ignore
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score  # type: ignore
        if grade == "yes":
            filtered_docs.append(d)
        else:
            continue
    return {"documents": filtered_docs, "question": question}


def grade_generation_v_documents_and_questions(state: State):
    question = state.question
    documents = state.documents
    generation = state.generation

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score  # type: ignore
    if grade == "yes":
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score  # type: ignore
        if grade == "yes":
            return "useful"
        else:
            return "not useful"
    else:
        return "not supported"


from langgraph.graph import END, StateGraph, START

workflow = StateGraph(State)

workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("generate_queries", generate_queries)
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate

workflow.add_edge(START, "generate_queries")
workflow.add_edge("generate_queries", "retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("grade_documents", "generate")
workflow.add_edge("generate", END)


app = workflow.compile()
save_graph_visualization(app)  # type: ignore

if __name__ == "__main__":
    inputs = [
        {
            "question": "I am interested in the following courses being i like thermodynamics  what classes would i take."
        },
        {
            "question": "What classes at UCR offer robotics based courses, additionally I am also interested in fluid dynamics courses what courses can I take"
        },
        {"question": "What does the course ME118A cover in UCR"},
    ]
    all_text = ""
    for i in inputs:
        all_text += f"Input: {i['question']}\n"
        results = app.invoke(i)  # type: ignore
        all_text += f"Generated answer: {results.get('generation')} \n"
    print(all_text)
    filepath = "ai_workspace/agents/course_description_agent/example_output.txt"
    with open(filepath, "w") as f:
        f.write(all_text)
