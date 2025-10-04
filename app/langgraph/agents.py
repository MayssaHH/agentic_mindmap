from app.langgraph.user_state import userState
from langchain_core.messages import HumanMessage,  SystemMessage
from langgraph.graph import StateGraph
from app.langgraph.prompts import systemPrompt_PagesSummary, messagePrompt_PagesSummary
from langsmith import trace
import logging
from langchain_openai import ChatOpenAI
from app.langgraph.functions import pdf_page_to_base64, number_of_pages_in_pdf
import asyncio


model_4o = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=4095,
    tags=["mindmap"]
)

logger = logging.getLogger(__name__)

builder = StateGraph(userState)

# Helper function for processing individual pages asynchronously
async def process_single_page(pdf_path: str, page_num: int) -> dict:
    """
    Process a single page asynchronously.
    Returns a dictionary with page_number and summary.
    """
    try:
        logger.info(f"Processing page {page_num}")
        
        # Convert page to base64
        base64_image = pdf_page_to_base64(pdf_path, page_num)
        
        # Prepare content for the model
        content = []
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
        
        # Create messages
        messages = [
            SystemMessage(content=systemPrompt_PagesSummary()),
            HumanMessage(content=content), 
            HumanMessage(content=messagePrompt_PagesSummary())
        ]
        
        # Get model response asynchronously
        response = await model_4o.ainvoke(messages)
        
        page_summary = {
            "page_number": page_num,
            "summary": response.content
        }
        
        logger.info(f"Successfully processed page {page_num}")
        return page_summary
        
    except Exception as e:
        logger.error(f"Error processing page {page_num}: {str(e)}")
        return {
            "page_number": page_num,
            "summary": f"Error processing page: {str(e)}"
        }

# Nodes Definitions
async def get_Pages_Summary(state:userState)->userState: 
    with trace(name="get_PagesPdf"):
        logger.info("Node: get_PagesPdf")
        '''
        Modify based on the pdf file: 
            # - name_topics 
            # - pages_topics 
            # - nb_topics
            # - nb_pages
        '''
        state['nb_pages'] = number_of_pages_in_pdf(state['path'])

        if state['nb_pages'] <= 0: 
            logger.error("Error: The ppt file is empty or does not exist.")
            raise ValueError("The ppt file is empty or does not exist.")

        if state['nb_topics'] <= 0:
            logger.error("Error: The number of topics must be greater than 0.")
            raise ValueError("The number of topics must be greater than 0.")
        
        pages = state['nb_pages']
        logger.info(f"Starting parallel processing of {pages} pages")
        
        # Create tasks for all pages to process them in parallel
        tasks = []
        for page_num in range(1, pages + 1):
            task = process_single_page(state['path'], page_num)
            tasks.append(task)
        
        # Process all pages in parallel using asyncio.gather
        try:
            page_summaries = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out any exceptions and ensure we have valid results
            valid_summaries = []
            for i, result in enumerate(page_summaries):
                if isinstance(result, Exception):
                    logger.error(f"Page {i+1} failed with exception: {str(result)}")
                    valid_summaries.append({
                        "page_number": i + 1,
                        "summary": f"Error processing page: {str(result)}"
                    })
                else:
                    valid_summaries.append(result)
            
            # Sort by page number to maintain order
            valid_summaries.sort(key=lambda x: x['page_number'])
            
        except Exception as e:
            logger.error(f"Error in parallel processing: {str(e)}")
            # Fallback to empty summaries if everything fails
            valid_summaries = []
        
        state['page_summaries'] = valid_summaries
        logger.info(f"Processed {len(valid_summaries)} pages successfully")   
    return state

# Add the agent to the StateGraph
builder.add_node("get_pages_summary", get_Pages_Summary)

# Set the entry point
builder.set_entry_point("get_pages_summary")

# Compile the graph
graph = builder.compile()