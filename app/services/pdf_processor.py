import logging
from pathlib import Path
from typing import Dict, Any
import uuid

from app.langgraph.agents import graph
from app.langgraph.user_state import userState

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    PDF Processor that uses LangGraph agents to:
    1. Extract summaries from PDF pages
    2. Identify topics from summaries
    3. Build a mind map graph
    """
    
    async def process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a PDF file and generate a mind map graph.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing the graph with nodes and edges
        """
        try:
            logger.info(f"Starting PDF processing for: {file_path}")
            
            # Verify file exists
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            # Create initial state with unique thread ID
            thread_id = f"session_{uuid.uuid4().hex[:8]}"
            
            initial_state: userState = {
                'thread_id': thread_id,
                'path': str(file_path),
                'nb_pages': 0,
                'page_summaries': [],
                'nb_topics': 0,
                'name_topics': [],
                'pages_topics': [],
                'contextWindow_topics': {},
                'graph': {},
                'graph_building_complete': False,
                'export_file_path': ''
            }
            
            # Execute the graph workflow
            logger.info("Invoking LangGraph workflow...")
            result = await graph.ainvoke(initial_state)
            
            logger.info("Graph execution completed successfully!")
            
            # Extract the graph data
            graph_data = result.get('graph', {'nodes': [], 'edges': []})
            
            # Return the processing result
            processing_result = {
                'graph': graph_data,
                'metadata': {
                    'thread_id': thread_id,
                    'total_pages': result.get('nb_pages', 0),
                    'total_topics': result.get('nb_topics', 0),
                    'total_nodes': len(graph_data.get('nodes', [])),
                    'total_edges': len(graph_data.get('edges', [])),
                    'export_file_path': result.get('export_file_path', '')
                },
                'topics': result.get('pages_topics', [])
            }
            
            logger.info(f"Processing complete: {processing_result['metadata']['total_nodes']} nodes, {processing_result['metadata']['total_edges']} edges")
            
            return processing_result
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            raise
