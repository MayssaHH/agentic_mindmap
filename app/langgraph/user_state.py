from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage

class userState(TypedDict):  
    thread_id: str #thread id
    path: str #path to the ppt file
    nb_pages: int #number of pages in the ppt
    page_summaries: list[dict[str, str]] # m pages each page number -> summary

    nb_topics: int #number of sections in the ppt based on main ideas/topics
    name_topics: list[str] # assume size n: topic title
    pages_topics: list[dict[str, str]] # n topics each topic title -> page numbers

    contextWindow_topics: dict[str,list[AnyMessage]] # str: topic title, list: messages in the context window

    graph: dict[str, list[dict[str,str]]] # str: nodes, edges, the list is a dict with keys id, title, .... and values their corresponding values
    graph_building_complete: bool # Flag to indicate if all topics have been processed
    export_file_path: str # Path to the exported JSON file containing the complete system output