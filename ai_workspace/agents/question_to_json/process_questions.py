import pandas as pd
import os
import json
from .agent import app
from .agent import InputState as GraphInput
from ai_workspace.utils.general import to_serializable

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
]
df = df[columns_to_keep]
df.head()
print(df.head())

max_iter = 1

results = []
for cnt, (_, row) in enumerate(df.iterrows()):
    app_input = GraphInput(
        question=row["question.html"],
        info_json=json.loads(row["info.json"]),
        qmeta=None,
    )
    result = app.invoke(app_input)
    results.append(to_serializable(result))
    # for chunk in app.stream(app_input, stream_mode="updates"):
    #     print(chunk, "\n")
    if cnt > max_iter:
        break

    print("\nNew Input\n")

with open(r"ai_workspace\question_to_json/data.json", "w") as f:
    json.dump(results, f)
