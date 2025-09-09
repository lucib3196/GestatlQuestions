import json
from ai_workspace.agents.topic_creator.topic_creator_agent import app

filepath = r"src\ai_workspace\notebooks\data\unique_tags_topics_data.json"
try:
    with open(filepath, "r") as f:
        data = json.load(f)
        for k, v in data.items():
            input_question = (
                f"The new topic to be graded\n Topic Name: {k} "
                + "\nExample Questions\n"
            ) + "\n".join(v)
            print(input_question)
            for update in app.stream(
                {"question": input_question}, stream_mode="updates" # type: ignore
            ):
                print(update, "\n")
except:
    print("Could not load data")
