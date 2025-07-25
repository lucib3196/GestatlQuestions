import os
import json
import pandas as pd
from .agent import app
from .agent import InputState as GraphInput
from ai_workspace.utils.general import to_serializable
import asyncio

# Load the data
path = r".\data\QuestionDataV2_06122025_classified.csv"
df = pd.read_csv(path)

columns_to_keep = [
    "Question Title",
    "question.html",
    "server.js",
    "solution.html",
    "server.py",
    "properties.js",
    "info.json",
    "isAdaptive",
    "relevant_courses",
    "topics",
]
df = df[columns_to_keep]

print("Loaded DataFrame preview:")
print(df.head(), "\n")

max_iter = 1
results = []


async def process_question(row):
    data_dict = json.loads(row["info.json"])
    data_dict.pop("topic", None)
    data_dict["topics"] = row["topics"] if row["topics"] else []

    val = row["topics"]
    if pd.isna(val):
        data_dict["topics"] = []
    else:
        data_dict["topics"] = val

    val = row["relevant_courses"]
    if pd.isna(val):
        data_dict["relevant_courses"] = []
    else:
        data_dict["relevant_courses"] = val

    app_input = GraphInput(
        question=row["question.html"],
        info_json=data_dict,
        qmeta=None,
    )
    result = await app.ainvoke(app_input)
    return result


async def main():
    tasks = [process_question(row) for _, row in df.iterrows()]
    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    output_path = r"ai_workspace\agents\question_to_json\data.json"
    results = asyncio.run(main())
    print(results)
    with open(output_path, "w") as f:
        json.dump(to_serializable(results), f)


# for cnt, (_, row) in enumerate(df.iterrows(), start=1):
#     print(f"\nProcessing row {cnt}:")
#     print(f"Question HTML: {row['question.html'][:100]}...")  # Print first 100 chars

#     data_dict = json.loads(row["info.json"])
#     data_dict.pop("topic", None)
#     data_dict["topics"] = row["topics"] if row["topics"] else []

#     val = row["relevant_courses"]
#     if pd.isna(val):
#         data_dict["relevant_courses"] = []
#     else:
#         data_dict["relevant_courses"] = val

#     app_input = GraphInput(
#         question=row["question.html"],
#         info_json=data_dict,
#         qmeta=None,
#     )

#     print("Invoking app...")
#     result = app.invoke(app_input)
#     results.append(to_serializable(result))

#     print("Streaming updates:")
#     for chunk in app.stream(app_input, stream_mode="updates"):
#         print(f"  Update: {chunk}")

#     if cnt >= max_iter:
#         print("\nReached max_iter limit. Stopping.")
#         break

#     print("\nReady for next input.\n")

# output_path = r"ai_workspace\agents\question_to_json\data.json"
# with open(output_path, "w") as f:
#     json.dump(results, f)
# print(f"\nResults saved to {output_path}")
