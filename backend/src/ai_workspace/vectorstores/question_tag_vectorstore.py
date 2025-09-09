from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from ai_workspace.document_loaders import QuestionTagLoader
# For documentation for working with the database see https://python.langchain.com/docs/integrations/vectorstores/faiss/#add-items-to-vector-store

def main(path_to_save:str):
    filepath = r"./data/question_element_tags.json"
    loader = QuestionTagLoader(filepath)
    docs = loader.load()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = FAISS.from_documents(docs, embeddings)

    vectorstore.save_local(path_to_save)
    
if __name__ == "__main__":
    print("Generating Vector Store")
    main(path_to_save="ai_workspace/vectorstores/QUESTIONTAG_VS")