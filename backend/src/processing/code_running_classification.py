from pathlib import Path
import json

local_qs = Path.cwd() / "local_questions"


metafile = "qmeta.json"
js_path = "server.js"
py_path = "server.py"
for q in local_qs.iterdir():
    meta = q / metafile
    if meta.exists():
        with open(meta, "r") as f:
            data = json.load(f)

        data["language"] = []
        js = q / js_path
        if js.exists():
            data["language"].append("JavaScript")
        py = q / py_path
        if py.exists():
            data["language"].append("Python")

        # Assuming all local questions are human made
        ## comment or uncomment based on needs

        data["ai_generated"] = False

        with open(meta, "w") as f:
            f.write(json.dumps(data, indent=4))
