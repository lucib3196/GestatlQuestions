from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from ai_workspace.utils import save_graph_visualization
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional, List
from langchain_core.output_parsers import StrOutputParser

# Constants
FASTLLM = "gpt-4o-mini"
LONGCONTEXTLLM = "o3-mini-2025-01-31"


# Would be replaced with database search functions
def get_available_tags():
    available_tags = {
        "conduction": "Heat transfer within solids or stationary fluids via particle interactions",
        "convection": "Heat transfer via fluid motion combined with molecular movement",
        "mass_transfer": "Transport of mass driven by concentration differences in multiphase systems",
    }
    return available_tags


def get_available_topics():
    available_topics = {
        "thermodynamics": "Study of energy, heat, work, and entropy governed by thermodynamic laws",
    }
    return available_topics


## Retrieval


## Retrieval grader
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: Literal["yes", "no"] = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


llm = ChatOpenAI(model=FASTLLM)
structured_llm_grader = llm.with_structured_output(GradeDocuments)
system = """
You are an evaluator tasked with assessing the relevance of a proposed **tag or topic** for a given academic question.

### Task:
Determine whether the suggested tag/topic is an appropriate classification for the question.

### Guidelines:
- A tag/topic is considered **relevant** if it:
  - Accurately reflects the subject, concept, or skills required to solve the question
  - Matches common academic categorization for similar questions
  - Would be a reasonable label used in a course, textbook, or study resource

- Tags do **not** need to match the question word-for-word, but they should:
  - Capture the core concept or domain (e.g., “thermodynamics”, “statics”, “circuit analysis”)
  - Be something a student or instructor would expect when organizing or searching for similar problems

- Discard tags that are:
  - Off-topic, overly broad, or too vague
  - Clearly unrelated to the question’s academic domain

### Instructions:
- Respond with a **binary judgment**: `"yes"` (relevant) or `"no"` (not relevant)
- Use academic judgment: **would this tag help group or retrieve similar questions?**

### Example Scenarios:
- A question about **fluid flow in pipes** and the tag **“fluid mechanics”** → `"yes"`
- A question about **AC circuit analysis** and the tag **“thermodynamics”** → `"no"`
- A question involving **moment of inertia** and the tag **“dynamics”** → `"yes"` (reasonable overlap)

Be practical, not overly strict. Prioritize functional classification that would make sense in an academic setting.

"""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n  question: {question}"),
    ]
)
retrieval_grader = grade_prompt | structured_llm_grader

# Generate
system = """
You are an assistant for academic question analysis and topic classification.
Your goal is to analyze the given question and generate one or more relevant **academic tags or topics** that accurately describe its content.

### Task:
- Review the input question.
- Identify the core academic **concepts**, **skills**, and **subject areas** involved.

### Context:
- You will be provided with a list of topics and their  descriptions that include:
  - Topic Name
  - Topic Description
  
A single question may map to multiple topics especially if it spans multiple disciplines or academic levels.


### Examples:
- Question: *"A block slides down a frictionless incline. What is its acceleration?"*  
  Tags: `"classical mechanics"`, `"kinematics"`, `"Newton's laws"`

- Question: *"Calculate the entropy change in an ideal gas during an isothermal expansion."*  
  Tags: `"thermodynamics"`, `"entropy"`, `"ideal gas"`

### Uncertainty Handling:
- Only return topics that appear in the provided context.
- If the question is too vague or outside the academic scope, respond with:  
  `"I don't know based on the provided information. Return None"`
  
### Additional Notes:
- Be precise, and avoid making assumptions beyond what the context allows.
- Think like an educator or course organizer: which topics would you use to group this question for study or review?
- Do **not** return course codes—only topical tags or academic concepts.


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


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


class TopicsClassification(BaseModel):
    topic: Optional[List[str]] = Field(
        ..., description="A list of the relevan topics based on the question "
    )


rag_chain = (
    rag_prompt | llm.with_structured_output(TopicsClassification) | StrOutputParser()
)


# Tools that will generate the data will ideally add to a vector database
def create_tag(tag_name: str, description: str):
    """Creates a tag to classify a question

    Args:
        tag_name (str): the name of the tag to create
        description (str): _description_

    Returns:
        str: A message of the comp
    """
    msg = f"Created tag {tag_name}: {description}"
    return msg


def create_topic(topic_name: str, description: str):
    """
    Creates a topic with the given name and description.

    Args:
        topic_name (str): The name of the topic to create.
        description (str): A brief description of the topic.

    Returns:
        str: A message confirming the creation of the topic with its description.
    """
    msg = f"Created topic {topic_name}: {description}"
    return msg


tools = [create_tag, create_topic]
llm = ChatOpenAI(model=FASTLLM)
llm_with_tools = llm.bind_tools(tools)


class State(BaseModel):
    question: str
    available_tags: Optional[dict] = None
    available_topics: Optional[dict] = None
    generated_topics: Optional[List[str]] = None


def retrieve_topics(state: State):
    # replace with retriever
    available_topics = get_available_topics()
    return {"available_topics": available_topics}


def retrieve_tags(state: State):
    # replace with retriever
    available_topics = get_available_topics()
    return {"available_tags": available_topics}



def generate(state: State):
    question = state.question
    context = state.available_topics
    if context:
        generation = rag_chain.invoke({"context": context, "question": question})
        return {"generated_topics": generation}
    else:
        return






builder = StateGraph(State)
builder.add_node("get_available_topics", retrieve_topics)
builder.add_node("get_available_topics", generate)

builder.add_edge(START, "assistant")


# sys_msg = SystemMessage(
#     content="You are a helpful assistant tasked with analyzing the following question and classifying them by giving them a topic and tag"
# )
# def assistant(state: State):
#     return {"question": [llm_with_tools.invoke(state.question)]}

# # Define nodes: these do the work
# builder.add_node("get_available_tags", get_available_tags)
# builder.add_node("get_available_topics", get_available_topics)


# builder.add_node("assistant", assistant)
# builder.add_node("tools", ToolNode(tools))

# # Define edges: these determine the control flow
# builder.add_edge(START, "assistant")
# builder.add_conditional_edges(
#     "assistant",
#     # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
#     # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
#     tools_condition,
# )
# builder.add_edge("tools", "assistant")

# memory = MemorySaver()
# graph = builder.compile(interrupt_before=["tools"], checkpointer=memory)
# save_graph_visualization(graph, r"src/ai_workspace/agentsv2/question_metadata_agent")  # type: ignore
