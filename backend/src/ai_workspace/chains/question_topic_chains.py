from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pydantic import BaseModel
from typing import List
from ai_workspace.models import QueryList, BinaryScore,TopicDescription



def generate_academic_query_chain(model="gpt-4o-mini", num_queries: int = 3):
    """
    Creates a LangChain chain for generating high-quality academic search queries from a user's question.
    This function constructs a prompt for an LLM (Large Language Model) to analyze an academic question and generate up to `num_queries` concise, unique search queries. The queries are designed to maximize retrieval of relevant academic topics or subject areas from a database containing topic names, descriptions, and disciplines.
    Args:
        model (str): The name of the OpenAI model to use (default: "gpt-4o-mini").
        num_queries (int): The maximum number of search queries to generate (default: 3).
    Returns:
        langchain_core.runnables.base.Runnable:
            A LangChain chain that takes a question as input and outputs a structured list of search queries (QueryList).

    When running the chain the
    chain = query_chain()
    chain.invoke({"question": Input })

    """
    llm = ChatOpenAI(model=model)

    query_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You are an expert at generating high-quality search queries for academic content classification and retrieval.

    Your task is to analyze the user's question and generate up to **{num_queries} concise and unique search queries**. These queries will be used to search a database of academic topics or subject descriptions.

    ### Guidelines:
    - Focus on the **core academic intent** behind the question.
    - Each query should:
    - Be short, specific, and non-redundant
    - Highlight a distinct aspect or interpretation of the question
    - Help retrieve relevant topics, concepts, or subject areas

    ### Context:
    - The database contains topic names, brief descriptions, and relevant academic disciplines.

    Think broadly and creatively. The goal is to maximize the chance of retrieving useful academic matches by covering different semantic angles of the user's question.
    """,
            ),
            ("human", "{question}"),
        ]
    )
    return query_prompt | llm.with_structured_output(QueryList)


def grade_topic(model="gpt-4o-mini"):
    """
    Creates a LangChain chain for grading whether a newly generated academic topic is sufficiently distinct from existing topics.

    This function constructs a prompt for an LLM (Large Language Model) to analyze a generated topic and a list of closely related existing topics, and then determine if the new topic is unique enough to justify its own category.

    Args:
        model (str): The name of the OpenAI model to use (default: "gpt-4o-mini").

    Returns:
        langchain_core.runnables.base.Runnable:
            A LangChain chain that takes a dictionary with "input" (the generated topic) and "context" (the list of related topics) as input, and outputs a structured binary score (BinaryScore) indicating uniqueness.

    Note:
        When running the chain, initialize and return the runnable:
            chain = grade_topic()
        To run it, use:
            chain.invoke({"input": input, "context": context})
        where `input` is the human message (the generated topic) and `context` is the context used to answer the question (the related topics).
    """
    llm = ChatOpenAI(model=model)
    system = """
    You are a grader assessing whether a newly generated topic is sufficiently distinct from existing topics in a database.

    ### Task:
        Decide whether a newly-proposed topic should be **accepted** as a distinct label
    or **rejected** as merely a re-wording / duplicate of topics already in the
    database.

    🔹  You receive  
    1. **new_topic** – the candidate topic string.  
    2. **nearby_topics[]** – a short list of existing topics judged most similar.

     What counts as “unique enough”  
    
   | Situation | Return |
    |-----------|--------|
    | The new topic introduces a **new sub-area or sub-topic** (e.g. “Shear Force Diagrams” vs. existing “Bending Moment Diagrams”). | `"yes"` |
    | It focuses on a **different concept, method, or application**, even if nested under the same broad field. | `"yes"` |
    | The only difference is superficial wording, plural/singular, punctuation, or synonym (e.g. “Vector Addition” vs. “Addition of Vectors”). | `"no"` |
    | It simply adds a qualifier that doesn’t change scope (e.g. “Basic Statics” vs. “Statics”). | `"no"` |
    | **No nearby_topics are supplied** (the list is empty). | `"yes"` (assume unique) |

    > *Rule of thumb:* If a subject-matter expert would create a **separate section** for it in a syllabus or textbook, mark **yes**; otherwise **no**.

    - **"yes"**  – keep the topic as a distinct entry.  
    - **"no"**   – too similar; merge or revise.
    
    Context (for the grader’s eyes only – do not echo):

    ### Context:
    {context}
    """
    topic_grader_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Input: {input}",
            ),
        ]
    )
    return topic_grader_prompt | llm.with_structured_output(BinaryScore)


class Response(BaseModel):
    topics: List[TopicDescription]


def new_topic_chain(model: str = "gpt-4o-mini"):
    """
    Creates a chain for generating a new academic topic classification based on a provided question.
    This function constructs a prompt for an LLM to analyze a question and return a structured JSON object containing:
        - A concise topic name that broadly classifies the question.
        - A short description summarizing the topic's focus.
        - A list of relevant engineering disciplines where the topic is commonly encountered.
    The prompt guides the model to use academic reasoning, avoid overly specific terms, and ensure the topic is suitable for broad classification. The output is parsed into a structured Response object.
    Args:
        model (str): The name of the language model to use (default: "gpt-4o-mini").
    Returns:
        Runnable: A chain that takes an input question and returns a structured Response with topic name, description, and disciplines.
    """
    llm = ChatOpenAI(model=model)
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
            ("human", "{input}"),
        ]
    )
    return new_topic_prompt | llm.with_structured_output(Response)
