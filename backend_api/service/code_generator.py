from ai_workspace.agents.code_generators.v4.qmeta import (
    CodeGenInput,
    Question,
    OutputState as CodeGenOutputState,
    compiled_graph as codegenv4,
)
from pathlib import Path
from ai_workspace.utils import to_serializable
from typing import Union
from backend_api.model.users import User



local_questions = Path.cwd() / "./local_questions"

filemap = {
    "question_html": "question.html",
    "server_js": "server.js",
    "server_py": "server.py",
    "solution_html": "solution.html",
    "metadata": "info.json",
}


async def generate_question_text(question: str):
    qinput = CodeGenInput(question_payload=Question(question=question), initial_metadata=None)  # type: ignore
    return await codegenv4.ainvoke(input=qinput)


filemap = {
    "question_html": "question.html",
    "server_js": "server.js",
    "server_py": "server.py",
    "solution_html": "solution.html",
    "metadata": "info.json",
}


def process_output_local(data: Union[CodeGenOutputState, dict]):
    """
    Saves the generated files from CodeGenOutputState to a local folder structure.
    """
    if not isinstance(data, CodeGenOutputState):
        data = CodeGenOutputState(**data)

    qtitle = data.qmeta.title
    save_path = local_questions / qtitle
    save_path.mkdir(parents=True, exist_ok=True)

    for file_key, content in data.files:
        mapped_name = filemap.get(file_key)
        if not mapped_name:
            print(f"⚠️ Unknown file key '{file_key}' — skipping.")
            continue

        file_path = save_path / mapped_name
        with file_path.open("w", encoding="utf-8") as f:
            if isinstance(content, dict):
                json.dump(content, f, indent=2)
            else:
                f.write(content)

    qmeta_path = save_path / "qmeta.json"
    with qmeta_path.open("w", encoding="utf-8") as f:
        json.dump(to_serializable(data.qmeta), f, indent=2)
        
        
        



if __name__ == "__main__":
    import json

    with open(r"backend_api\service\response_1753816385150.json", "r", encoding="utf-8") as f:
        content = json.load(f)
    process_output_local(content)
