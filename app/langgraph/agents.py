from app.langgraph.user_state import userState
from langchain_core.messages import HumanMessage,  SystemMessage
from langgraph.graph import StateGraph, END
from app.langgraph.prompts import systemPrompt_PagesSummary, messagePrompt_PagesSummary, systemPrompt_TopicExtraction, messagePrompt_TopicExtraction, systemPrompt_GraphBuilder, messagePrompt_GraphBuilder_Initial, messagePrompt_GraphBuilder_Enrichment
from langsmith import trace
import logging
from langchain_openai import ChatOpenAI
from app.langgraph.functions import pdf_page_to_base64, number_of_pages_in_pdf
import asyncio
import json
import os
from datetime import datetime


model_4o = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=4095,
    tags=["mindmap"]
)

logger = logging.getLogger(__name__)

def save_final_system_output(state: dict, output_dir: str = "output") -> str:
    """
    Save the complete final output of the system to a JSON file.
    This includes all processing results: page summaries, topics, and the final graph.
    
    Args:
        state: Complete user state with all processing results
        output_dir: Directory to save the file (default: "output")
    
    Returns:
        str: Path to the saved file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        thread_id = state.get('thread_id', 'unknown')
        filename = f"system_output_{thread_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Prepare the complete system output
        system_output = {
            "metadata": {
                "thread_id": thread_id,
                "created_at": datetime.now().isoformat(),
                "source_file": state.get('path', 'unknown'),
                "total_pages": state.get('nb_pages', 0),
                "total_topics": state.get('nb_topics', 0),
                "graph_nodes": len(state.get('graph', {}).get('nodes', [])),
                "graph_edges": len(state.get('graph', {}).get('edges', []))
            },
            "processing_results": {
                "page_summaries": state.get('page_summaries', []),
                "topics": {
                    "topic_names": state.get('name_topics', []),
                    "topic_details": state.get('pages_topics', [])
                },
                "final_graph": state.get('graph', {}),
                "graph_building_complete": state.get('graph_building_complete', False)
            }
        }
        
        # Save to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(system_output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Complete system output saved to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving system output to JSON: {str(e)}")
        return None

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
        Process all pages from the PDF and generate summaries.
        Updates state:
            # - nb_pages: number of pages in the PDF
            # - page_summaries: list of page summaries with page numbers
        '''
        state['nb_pages'] = number_of_pages_in_pdf(state['path'])

        if state['nb_pages'] <= 0: 
            logger.error("Error: The ppt file is empty or does not exist.")
            raise ValueError("The ppt file is empty or does not exist.")
        
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

# New Node: Extract Topics from All Summaries
async def extract_Topics_From_Summaries(state: userState) -> userState:
    with trace(name="extract_Topics"):
        logger.info("Node: extract_Topics_From_Summaries")
        
        try:
            # Get all page summaries
            page_summaries = state.get('page_summaries', [])
            
            if not page_summaries:
                logger.error("No page summaries available for topic extraction")
                raise ValueError("No page summaries available")
            
            # Build the input message with all summaries
            summaries_text = ""
            for page_summary in page_summaries:
                page_num = page_summary.get('page_number', 'Unknown')
                summary = page_summary.get('summary', '')
                summaries_text += f"\n\nSlide {page_num}:\n{summary}"
            
            # Create messages for the LLM (LLM will determine optimal number of topics)
            messages = [
                SystemMessage(content=systemPrompt_TopicExtraction()),
                HumanMessage(content=summaries_text),
                HumanMessage(content=messagePrompt_TopicExtraction())
            ]
            
            # Get LLM response
            logger.info(f"Sending {len(page_summaries)} summaries to LLM for topic extraction")
            response = await model_4o.ainvoke(messages)
            
            # Parse the JSON response
            try:
                # Extract JSON from response (handle potential markdown code blocks)
                response_text = response.content.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(response_text)
                topics_data = result.get('topics', [])
                
                # Extract topic names
                name_topics = [topic['topic_title'] for topic in topics_data]
                
                # Build pages_topics - mapping topic title to slide information with summaries
                pages_topics = []
                for topic in topics_data:
                    topic_entry = {
                        'topic_title': topic['topic_title'],
                        'slide_numbers': topic['slide_numbers'],
                        'slides_range': topic['slides_range'],
                        'summaries': topic['summaries']  # This contains the summaries for this topic
                    }
                    pages_topics.append(topic_entry)
                
                logger.info(f"Extracted {len(topics_data)} topics with their summaries:")
                for i, topic in enumerate(topics_data, 1):
                    logger.info(f"  Topic {i}: {topic['topic_title']} ({len(topic['summaries'])} summaries)")
                
                # Update state
                state['name_topics'] = name_topics
                state['pages_topics'] = pages_topics
                state['nb_topics'] = len(name_topics)
                
                logger.info(f"Successfully extracted {len(name_topics)} topics: {name_topics}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response was: {response.content}")
                # Fallback: create a single topic with all slides
                state['name_topics'] = ["Main Content"]
                state['pages_topics'] = [{
                    'topic_title': "Main Content",
                    'slide_numbers': [ps['page_number'] for ps in page_summaries],
                    'slides_range': f"1-{len(page_summaries)}",
                    'summaries': [ps['summary'] for ps in page_summaries]
                }]
                state['nb_topics'] = 1
                
        except Exception as e:
            logger.error(f"Error in topic extraction: {str(e)}")
            raise
            
    return state

# Graph Builder Agent - Processes ALL topics sequentially in n iterations
async def build_mind_map_graph(state: userState) -> userState:
    with trace(name="build_mind_map_graph"):
        logger.info("Node: build_mind_map_graph - Processing ALL topics sequentially")
        
        try:
            # Get topics data
            pages_topics = state.get('pages_topics', [])
            nb_topics = len(pages_topics)
            
            if nb_topics == 0:
                logger.warning("No topics found for graph building")
                state['graph'] = {"nodes": [], "edges": []}
                state['graph_building_complete'] = True
                return state
            
            # Initialize empty graph
            state['graph'] = {"nodes": [], "edges": []}
            logger.info(f"Starting sequential graph building with {nb_topics} topics")
            
            # Process each topic sequentially (n iterations)
            for i, topic in enumerate(pages_topics):
                topic_title = topic['topic_title']
                topic_summaries = topic['summaries']
                
                logger.info(f"Processing topic {i + 1}/{nb_topics}: {topic_title}")
                logger.info(f"Current graph has {len(state['graph'].get('nodes', []))} nodes and {len(state['graph'].get('edges', []))} edges")
                
                # Prepare messages for the LLM
                if i == 0:
                    # First topic - create initial graph
                    logger.info("Creating initial graph for first topic")
                    messages = [
                        SystemMessage(content=systemPrompt_GraphBuilder()),
                        HumanMessage(content=messagePrompt_GraphBuilder_Initial(topic_title, topic_summaries))
                    ]
                else:
                    # Subsequent topics - enrich existing graph
                    logger.info(f"Enriching existing graph with topic: {topic_title}")
                    messages = [
                        SystemMessage(content=systemPrompt_GraphBuilder()),
                        HumanMessage(content=messagePrompt_GraphBuilder_Enrichment(topic_title, topic_summaries, state['graph']))
                    ]
                
                # Get LLM response
                response = await model_4o.ainvoke(messages)
                
                # Parse the JSON response
                try:
                    response_text = response.content.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif response_text.startswith("```"):
                        response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                    updated_graph = json.loads(response_text)
                    
                    # Update the graph with the new enriched version
                    state['graph'] = updated_graph
                    
                    logger.info(f"Successfully processed topic {i + 1}: {topic_title}")
                    logger.info(f"Updated graph now has {len(updated_graph.get('nodes', []))} nodes and {len(updated_graph.get('edges', []))} edges")
                    
                    # Log the sequential progress
                    if i == 0:
                        logger.info("✅ Initial graph created")
                    else:
                        logger.info(f"✅ Graph enriched with topic {i + 1}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response for topic {topic_title}: {str(e)}")
                    logger.error(f"Response was: {response.content}")
                    # Continue with next topic even if this one failed
                    continue
            
            # Mark graph building as complete
            state['graph_building_complete'] = True
            logger.info(f"✅ Sequential graph building completed! Final graph has {len(state['graph'].get('nodes', []))} nodes and {len(state['graph'].get('edges', []))} edges")
                
        except Exception as e:
            logger.error(f"Error in sequential graph building: {str(e)}")
            state['graph_building_complete'] = True  # Mark as complete even if there was an error
            
    return state

# Note: Removed should_continue_graph_building function since we now use fixed n iterations

# Export final system output
async def export_final_output(state: userState) -> userState:
    """
    Export and save the complete final output of the system to a JSON file.
    This includes all processing results: page summaries, topics, and the final graph.
    """
    with trace(name="export_final_output"):
        logger.info("Node: export_final_output")
        
        try:
            # Save the complete system output
            saved_path = save_final_system_output(state)
            
            if saved_path:
                state['export_file_path'] = saved_path
                logger.info(f"Final system output exported to: {saved_path}")
            else:
                logger.warning("Failed to export final system output")
                
        except Exception as e:
            logger.error(f"Error in export_final_output: {str(e)}")
            
    return state

# Add the agents to the StateGraph
builder.add_node("get_pages_summary", get_Pages_Summary)
builder.add_node("extract_topics", extract_Topics_From_Summaries)
builder.add_node("build_graph", build_mind_map_graph)
builder.add_node("export_output", export_final_output)

# Set the entry point
builder.set_entry_point("get_pages_summary")

# Add edges to create the flow (no conditional logic needed - fixed n iterations)
builder.add_edge("get_pages_summary", "extract_topics")
builder.add_edge("extract_topics", "build_graph")
builder.add_edge("build_graph", "export_output")
builder.add_edge("export_output", END)

# Compile the graph
graph = builder.compile()