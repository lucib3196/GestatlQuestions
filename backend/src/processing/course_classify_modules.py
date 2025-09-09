"""
course_classify_modules.py

This script classifies questions by associating them with relevant engineering course codes.
It reads questions from a CSV file, uses an AI classification agent to determine the relevant courses,
and writes the results to a new CSV file with an added column for the course codes.
"""

import pandas as pd
import asyncio
from ai_workspace.agents.course_classification_agent.course_classification_agent import (
    app as classification_graph,
)


async def run_classifications(questions):
    """Run course classification asynchronously for a list of questions."""
    tasks = [classification_graph.ainvoke({"question": q}) for q in questions] # type: ignore
    return await asyncio.gather(*tasks)


async def main():
    """Main workflow: load data, classify questions, and save results."""
    input_path = r"src\data\QuestionDataV2_06122025.csv"
    output_path = r"src\data\QuestionDataV2_06122025_classified.csv"
    df = pd.read_csv(input_path)
    mask = (~df["question"].isna()) & (~df["isAdaptive"].isna())
    filtered_df = df[mask].copy()
    questions = filtered_df["question"].tolist()
    # print(filtered_df.head())
    # print(questions)

    results = await run_classifications(questions)

    for i, r in enumerate(results):
        generation = r.get("generation")
        if generation and hasattr(generation, "course_id"):
            course_ids = generation.course_id
            value = (
                ", ".join(course_ids)
                if isinstance(course_ids, list)
                else str(course_ids)
            )
        else:
            value = None
        filtered_df.at[filtered_df.index[i], "relevant_courses"] = value

    print(filtered_df)
    filtered_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    asyncio.run(main())
