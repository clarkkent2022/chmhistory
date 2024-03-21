# -*- coding: utf-8 -*-
"""

**Computer History Bot - Richard Sawey**

A chatbot for research on computing history, a RAG implementation on selections from the archives at the Computer History Museum, 
Mountain View, https://www.computerhistory.org

This script expects a parameter to indicate the LLM to use, a parameter to indidate if the vector stores should be recreated, else
the stores in the vectorpersist and summarypersist directories will be used. Finally there is a parameter to either run this in
command line mode or to run this as a web page with streamlit

"""

# load up with stuff we'll need
#pip install openai
#pip install sentence-transformers
#pip install langchain pypdf langchain-openai #tiktoken chromadb
#pip install llama-index-vector-stores-chroma
#pip install llama-index --upgrade
#pip install streamlit

#
# Let's get to work now all the riff raff has been loaded
#
from openai import OpenAI
import os, sys


if len(sys.argv) != 4:
    sys.exit("""
        Thank you for trying HistoryBot, a prototype chat bot designed to provide an interactive
        experience for those researching or interested in computer history. In History Bot's current
        experimental configuration the only source document used is a Computer History Museum docent's
        script. The author wrote this script as part of his responsibilities as a museum docent and the
        script includes details on a range of important computers from history such as ENIAC and the 
        IBM 360.

        With funding I'd look to expand the History Bot to include the many personal histories collected
        by the museum and currently archived in either PDF or video format. 

        This script can be used stand alone from the command line or with streamlit. 

        This script needs three input arguments, first the LLM to use (right now
        this is ignored, I always use gpt-4-turbo-preview). Next a 0 or 1 is required
        to indicate if we should use the existing vector stores. A '1' says use the persisted vector store 
        and '0' tells History Bot to rebuild the vector indexes. The third input parameter
        tells History Bot if you want to run in command line or web browser mode?
        
        This script also assumes the existence of an environment variable OPENAI_API_KEY
        that obviously contains your OpenAI key for the LLM.
        
        And if you want web browser mode you need to invoke streamlit so the command becomes:
        streamlit run chmbotv6routsl.py chatgpt 1 web

        In command line script mode just enter:
        python3 chmbotv6routsl.py chatgpt 1 line

        Richard Sawey TECH16 March 2024
        """)


llm_name = sys.argv[1]
USE_STORE = sys.argv[2]
# 
if not (USE_STORE == "0" or USE_STORE == "1"):
    sys.exit('Ending, USE_STORE input variable, the second one, must be set and must be either a 0 or 1')

run_mode = sys.argv[3]
if not (run_mode == "line" or run_mode == "web"):
    sys.exit("Ending, run mode, the third input parameter, must be set and must be either 'line' or 'web' ")

#
# setup OpenAI keys
#
open_ai_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=open_ai_key)


from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader, SummaryIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.openai import OpenAIEmbedding


#
# Change to chatgpt 4 from LlamaIndex default of 3.5
#
Settings.llm = OpenAI(temperature=0, model_name='gpt-4-turbo-preview', api_key=open_ai_key)
llm = OpenAI(temperature=0, model_name='gpt-4-turbo-preview', api_key=open_ai_key)

#
#  index the supplied documents using llama_index and create a persistent index store
#
#
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.openai import OpenAIEmbedding

# USE_STORE=os.environ["BOT_USE_STORE"]

if USE_STORE == "1":
  storage_context = StorageContext.from_defaults(persist_dir="./vectorpersist")
  vector_index = load_index_from_storage(storage_context)
  storage_summary_context = StorageContext.from_defaults(persist_dir="./summarypersist")
  summary_index = load_index_from_storage(storage_summary_context)
else:
#    vector_storage = StorageContext.from_defaults(persist_dir="./vectorpersist")
#    vector_index = load_index_from_storage(vector_storage)

    #documents = SimpleDirectoryReader("./History").load_data()
    documents = SimpleDirectoryReader(input_files=["./Tourv5.pdf"]).load_data()
    embed_model = OpenAIEmbedding()
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )
    nodes = splitter.get_nodes_from_documents(documents, show_progress=False)
    print(nodes[5].get_content())

    summary_index = SummaryIndex(nodes)
    summary_index.storage_context.persist(persist_dir="./summarypersist")
    
    vector_index = VectorStoreIndex(nodes)
    vector_index.storage_context.persist(persist_dir="./vectorpersist")


summary_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True, llm=llm
)
vector_query_engine = vector_index.as_query_engine(llm=llm)


from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.tools import QueryEngineTool


summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description="Useful for summarization questions related to the source documents",
)
vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description="Useful for retrieving specific context and answers related to the source documents",
)

query_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[
        summary_tool,
        vector_tool,
    ],
)

#response = query_engine.query("Summarize the tour in bullet points, one per computer")
#print(response)

if run_mode == "line":
    while True:  # Initiates an infinite loop, emulating an ever-ready assistant.
        user_input = input("Please enter your question for HistoryBot or press enter to exit: ")
        if user_input == "":  
            sys.exit("Goodbye! Thanks for using History Bot.")
        else:
            # Process the user's question.
            response = query_engine.query(user_input)
            print(response)
else:
    import streamlit as st
    st.title("The History Bot")
    with st.form('history_bot_form'):
    #    print("Press return or type exit to quit the HistoryBot question loop")
        bot_question = st.text_area("Ask HistoryBot a question: ", value=" ")
        submitted = st.form_submit_button('Submit')
        response = query_engine.query(bot_question)
        st.info(response)
