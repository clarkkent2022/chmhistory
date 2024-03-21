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
