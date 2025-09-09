import pandas as pd
import json
from ai_workspace.agents.question_to_json.agent import FinalState
from ai_workspace.utils import to_serializable
import os
import re
from pathlib import Path


# Load in the data
qmeta_path = r"ai_workspace\agents\question_to_json\data.json"
csv_path = r"data\QuestionDataV2_06122025_classified.csv"

df = pd.read_csv(csv_path)
with open(qmeta_path, "r") as f:
    content = json.load(f)


def create_qmeta(q):
    # Main data for rendering
    data = {}
    data["rendering_data"] = q.payload.questionBase
    data["title"] = q.payload.title
    data["topic"] = q.payload.topic
    data["relevantCourses"] = q.payload.relevantCourses
    data["tags"] = q.payload.tags
    data["isAdaptive"] = q.payload.isAdaptive
    data["createdBy"] = q.payload.createdBy
    return data


def sanitize_name(name: str) -> str:
    """
    Trim whitespace and replace invalid filesystem chars with '_'.
    """
    name = name.strip()
    return re.sub(r'[<>:"/\\|?*]', "_", name)


project_root = Path(__file__).parent.parent
csv_path = project_root / "data" / "QuestionDataV2_06122025_classified.csv"
content_path = (
    project_root / "ai_workspace" / "agents" / "question_to_json" / "data.json"
)
output_root = project_root / "local_questions"


for cnt, (_, row) in enumerate(df.iterrows()):
    # Reconstruct your FinalState
    q: FinalState = FinalState(**content[cnt])

    # 1) Create a unique, sanitized folder
    clean_title = sanitize_name(q.payload.title)
    folder = output_root / clean_title

    num = 1
    while folder.exists():
        folder = output_root / f"{clean_title}_{num}"
        num += 1
        q.payload.title = f"{clean_title}_{num}"
    folder.mkdir(parents=True, exist_ok=True)

    # 2) Write qmeta.json
    q_meta = create_qmeta(q)
    with (folder / "qmeta.json").open("w", encoding="utf-8") as f:
        json.dump(to_serializable(q_meta), f, indent=4)

    # 3) Save any “images” (here string filenames) under clientFilesQuestion/
    q_with_image = [sq for sq in q.payload.questionBase if getattr(sq, "image", None)]
    if q_with_image:
        client_dir = folder / "clientFilesQuestion"
        client_dir.mkdir(exist_ok=True)

        for sq in q_with_image:
            fname = sanitize_name(str(sq.image))
            out_file = client_dir / fname
            # write the image string (or empty string if somehow None)
            out_file.write_text(sq.image or "", encoding="utf-8")

    # 4) Helper to write raw text files if non‐empty
    def write_text_if(key: str, filename: str):
        txt = row.get(key)
        if pd.notna(txt) and txt:
            (folder / filename).write_text(txt, encoding="utf-8")

    write_text_if("question.html", "question.html")
    write_text_if("solution.html", "solution.html")
    write_text_if("server.js", "server.js")
    write_text_if("server.py", "server.py")

    # 5) Parse & write info.json (stored as string in the CSV)
    info_str = row.get("info.json")
    if pd.notna(info_str) and info_str:
        try:
            info_data = json.loads(info_str)
        except json.JSONDecodeError:
            info_data = {}
        with (folder / "info.json").open("w", encoding="utf-8") as f:
            json.dump(info_data, f, indent=4)

print(f"All questions have been written to: {output_root}")
