from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from ai_workspace.utils import save_graph_visualization, parse_structured
from typing import Optional
from ai_workspace.retrievers import SemanticExamplesCSV
from langgraph.graph import END, StateGraph, START
from itertools import chain
from collections.abc import Iterable
from langchain import hub
from ai_workspace.models import CodeResponse
from langsmith import Client
from langchain_core.messages import SystemMessage

client = Client()
# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
FASTLLM = "gpt-5-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"
TAG_VECTOR_STORE_PATH = r"ai_workspace\vectorstores\QUESTIONTAG_VS"
QUESTION_VECTOR_STORE_PATH = r"ai_workspace\vectorstores\QUESTIONMOD_VS"
N_SEARCH_QUERIES = 3
CSV_PATH = r"data\QuestionDataV2_06122025_classified.csv"

fast_llm = ChatOpenAI(model=FASTLLM)
long_context_llm = ChatOpenAI(model=LONGCONTEXTLLM)

# ────────────────────────────────────────────────────────────────────────────────
# Vector store & retriever
# ────────────────────────────────────────────────────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
tag_vectorstore = FAISS.load_local(
    TAG_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
)
tag_retriever = tag_vectorstore.as_retriever(
    search_type="mmr", search_kwargs={"k": N_SEARCH_QUERIES}
)

q_vectorstore = FAISS.load_local(
    QUESTION_VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
)

# Question retriever and formatter
q_retriever = SemanticExamplesCSV(
    column_names=["question.html", "solution.html"],
    csv_path=CSV_PATH,
    vector_store=q_vectorstore,
)


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
            f"""
You are an expert at generating effective search queries for academic databases of custom HTML tags used to generate academic content (quizzes, tests, homework, etc.).

Your task is to carefully analyze the user's question and generate up to **{N_SEARCH_QUERIES}concise and unique search queries**. These queries will be used to search a database of HTML tags relevant for rendering the question as an interactive HTML file.

When analyzing the question, focus on identifying key structural and functional aspects, such as:
- Is the question multiple choice, single choice, or open-ended?
- Does the question require a specific input type (e.g., checkbox, radio button, number input, text area)?
- Is the question multipart or does it contain sub-questions?
- Are there any special requirements (e.g., code input, mathematical expressions, file upload)?
- Any other relevant features that would influence the choice of HTML tags.

Guidelines:
- Focus on the **semantic intent** and structure of the question.
- Each query should:
    - Be direct, non-redundant, and reflect a different possible interpretation or aspect of the question.
    - Help identify the most relevant HTML tags for rendering the question appropriately.
    - Include keywords related to the input type, question structure, and any special requirements.
- The query should be focused on html tags you should be thinking as a developer who is trying to create 
a html file that will display these questions
""",
        ),
        (
            "human",
            "This is the input question to be converted to a html document \n Question: {question}",
        ),
    ]
)

query_generator = query_prompt | structured_query


## Retrieval grader
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: Literal["yes", "no"] = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


grade_documents_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert in educational technology and HTML development. Your task is to analyze the provided tag information (which describes custom HTML tags and their usage) and the given question (which needs to be converted into an interactive HTML format).

Determine if the tag information is directly useful and relevant for creating the HTML representation of the question. Consider whether the tag's functionality, input type, and features match the requirements of the question. If the tag information would help a developer implement the question as HTML, respond "yes". If it is not relevant or would not help, respond "no".
""",
        ),
        (
            "human",
            "Question to convert: {question}\nTag information: {documents}",
        ),
    ]
)

structured_grader = llm_query.with_structured_output(GradeDocuments)
grader = grade_documents_prompt | structured_grader


# Define the state
class State(BaseModel):
    question: str
    solution: Optional[str] = None
    isAdaptive: bool = True
    queries: List[str] = Field(default_factory=list)
    tag_documents: List[Document] = Field(default=[])
    filtered_docs: List[Document] = Field(default=[])
    qfile: str = ""


# Nodees
def generate_queries(state: State):
    question = state.question
    question += q_retriever.format_template(
        query=question,
        k=2,
        base_template="\nAdditionally here are some examples of question formatted in html, these can aid in your search",
    )
    results = query_generator.invoke({"question": question})

    return {"queries": results.queries}  # type: ignore


def retrieve_tag_info(state: State):
    seen: set[str] = set()
    unique_docs: List[Document] = []
    for doc in chain.from_iterable(
        tag_retriever.invoke(q, filter={"type": "solution"}) for q in state.queries
    ):
        t_name = doc.metadata.get("tag_name")

        if isinstance(t_name, str):
            tags = {t_name}
        elif isinstance(t_name, Iterable):
            tags = {str(t) for t in t_name}
        else:
            tags = {str(t_name)}
        # skip if we've already seen ANY of these tags
        if tags.isdisjoint(seen):
            seen.update(tags)
            unique_docs.append(doc)
    return {"tag_documents": unique_docs}


def generate_question_file(state: State):
    # Retrieve the base prompt template from the hub
    base_prompt = client.pull_prompt("solution_html_template")

    # Prepare tag documentation string
    tag_docs = "\n\n".join(
        f"- {doc.page_content}" for doc in (state.filtered_docs or state.tag_documents)
    )
    tag_info_section = (
        f"\n\nAdditionally, here is documentation for available tags you may reference:\n{tag_docs}"
        if tag_docs
        else ""
    )

    # Format the prompt with the question and base template
    prompt = q_retriever.format_template(
        query=state.question, k=2, base_template=base_prompt
    )
    messages = prompt.format_messages(question=state.question)  # type: ignore

    # Insert tag info section after the last SystemMessage
    last_sys_idx = max(
        (i for i, m in enumerate(messages) if isinstance(m, SystemMessage)), default=-1
    )
    if tag_info_section:
        tag_msg = SystemMessage(content=tag_info_section)
        insert_idx = last_sys_idx + 1
        messages = messages[:insert_idx] + [tag_msg] + messages[insert_idx:]

    # Set retriever filter
    q_retriever.set_filter({"isAdaptive": state.isAdaptive})

    # If a solution is provided, add it as a SystemMessage
    if state.solution:
        solution_prompt = (
            "\n\nAdditionally, you are provided with the following solution guide. "
            "This solution guide outlines the intended approach and logic for solving the question. "
            "You must use the reasoning, steps, and methodology from this guide as the primary reference for how the question should be implemented and transformed into the HTML file. "
            "Expand on the steps where necessary for clarity, but ensure that the structure and logic of the HTML output closely follow the solution guide's approach."
            f"\n\nSolution Guide:\n{state.solution.replace('{', '{{').replace('}', '}}')}\n"
        )
        solution_msg = SystemMessage(content=solution_prompt)
        insert_idx = (
            max(
                (i for i, m in enumerate(messages) if isinstance(m, SystemMessage)),
                default=-1,
            )
            + 1
        )
        messages = messages[:insert_idx] + [solution_msg] + messages[insert_idx:]

    # Generate the code response
    chain = fast_llm.with_structured_output(CodeResponse, include_raw=True)
    result = chain.invoke(messages)
    ai_message = result["raw"]
    structured = parse_structured(CodeResponse, ai_message)
    return {"qfile": structured.code}


clean_file_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert developer specializing in code formatting and "
                "template processing. Your task is to review, verify, and modify "
                "the provided code so it complies with our **new placeholder "
                "standard**."
            ),
        ),
        (
            "human",
            """Here is a code snippet that will be processed on our backend. Please apply **all** of the following changes:

1. **Placeholder Migration**  
   • Every template reference written as `params.value`, `params.correct_answers`, or similar **must** be wrapped in the new double-square-bracket syntax:  
     • `[[params.value]]`  
     • `[[params.correct_answers]]`  

2. **LaTeX Delimiters**  
   • Ensure all LaTeX is correctly enclosed—use `$ ... $` for inline math and `$$ ... $$` for display math.  
   • Fix any formatting issues so each expression renders cleanly.

3. **Integrity Check**  
   • After updating, **verify** that no deprecated `{{ … }}` placeholders remain.  
   • Do **not** alter any other program logic or structure.

Return **only** the cleaned code with these requirements satisfied.

Code to convert:
{question}""",
        ),
    ]
)

clean_file = clean_file_prompt | fast_llm.with_structured_output(
    CodeResponse, include_raw=True
)


def clean_up_file(state: State):
    result = clean_file.invoke({"question": state.qfile})
    ai_message = result["raw"]
    structured = parse_structured(CodeResponse, ai_message)
    return {"qfile": structured.code}


workflow = StateGraph(State)
workflow.add_node("generate_search_queries", generate_queries)
workflow.add_node("retrieve_tag_info", retrieve_tag_info)
workflow.add_node("generate_solution_file", generate_question_file)
workflow.add_node("clean_up_file", clean_up_file)

workflow.add_edge(START, "generate_search_queries")
workflow.add_edge("generate_search_queries", "retrieve_tag_info")
workflow.add_edge("retrieve_tag_info", "generate_solution_file")
workflow.add_edge("generate_solution_file", END)
# workflow.add_edge("clean_up_file", END)

app = workflow.compile()


if __name__ == "__main__":
    save_graph_visualization(
        app,  # type: ignore
        "solution_graph.png",
        base_path=r"ai_workspace/agentsv2/code_generator/ver3/graphs",
    )  #

    t_inputs = [
        {
            "question": """<pl-question-panel>\n  
            <p>A car is traveling along a straight road at a speed of {{params.initialSpeed}} {{params.unitsSpeed}}. 
            It sees a stop sign {{params.distanceToSign}} {{params.unitsDistance}} ahead and applies the brakes, coming to a complete stop just as it reaches the sign.</p>\n  <p>What is the car\'s constant acceleration during this process? Show your calculations.</p>\n</pl-question-panel>\n\n<pl-input-container>\n  
            <pl-number-input answers-name="initialSpeed" label="Initial Speed ({{params.unitsSpeed}})" />\n  <pl-number-input answers-name="distanceToSign" label="Distance to Stop Sign ({{params.unitsDistance}})" />\n</pl-input-container>\n\n<pl-number-input answers-name="acceleration" comparison="sigfig" digits="3" label="Acceleration (in {{params.unitsAcceleration}})"/>"""
        },
    ]

    for t in t_inputs:
        for chunk in app.stream(t, stream_mode="updates"):  # type: ignore
            print(chunk)
