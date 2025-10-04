import json

def systemPrompt_PagesSummary()->str:
    return f"""
        You are an expert at analyzing powerpoint pages and extracting key information. 
        Your task is to deeply understand the content of this page and provide a comprehensive summary.
        You mainly need to understand:
            - Main ideas/topics and concepts
            - Key data points and statistics
            - Important relationships between ideas
            - Visual elements and their significance
            - Any technical details or specifications
            
        Provide a concise summary that captures the ESSENCE ONLY of the page.
    """

def messagePrompt_PagesSummary()->str:
    return f"""
    Analyze this page extracted from a powerpoint presentation/lecture and provide a comprehensive, compact, structured summary that captures the ESSENCE ONLY of the page. 
    The summary should be compact in order to be used in a clear simple mind map.
    """

def systemPrompt_TopicExtraction()->str:
    return """
        You are an expert at analyzing presentation content and identifying main topics/themes.
        Your task is to analyze all the slide summaries provided and extract the main topics covered in the presentation.
        
        Important: YOU decide the optimal number of topics based on the content. Identify natural thematic boundaries 
        and group slides accordingly. The number of topics should reflect the actual structure of the presentation.
        
        For each topic you identify:
        1. Give it a clear, concise title
        2. Identify which slides belong to that topic
        3. Ensure slides are logically grouped - slides about the same topic should be grouped together
        4. One topic covers maultiple slides, however on slide can be assigned to one topic only
        
        Return your analysis in a structured JSON format with the following structure:
        {
            "topics": [
                {
                    "topic_title": "Title of Topic 1",
                    "slide_numbers": [1, 2, 3],
                    "slides_range": "1-3",
                    "summaries": ["summary of slide 1", "summary of slide 2", "summary of slide 3"]
                },
                {
                    "topic_title": "Title of Topic 2",
                    "slide_numbers": [4, 5],
                    "slides_range": "4-5",
                    "summaries": ["summary of slide 4", "summary of slide 5"]
                }
            ]
        }
        
        Guidelines:
        - Identify clear thematic boundaries between topics
        - Topics should be meaningful and distinct
        - Don't skip slides, every slide must be assigned to a topic
        - Topic titles should be descriptive and concise
        - Be smart about the number of topics - not too granular, not too broad
    """

def messagePrompt_TopicExtraction()->str:
    return """
    Based on the slide summaries provided below, identify and extract the main topics covered in this presentation.
    
    Analyze the content and determine the natural number of topics that best represents the structure of this presentation.
    Group the slides by their topics, ensuring that slides covering similar themes are grouped together.
    Make sure to include the slide summaries for each topic.
    
    You must return your analysis in a structured JSON format with the following structure:
        {
            "topics": [
                {
                    "topic_title": "Title of Topic 1",
                    "slide_numbers": [1, 2, 3],
                    "summaries": ["summary of slide 1", "summary of slide 2", "summary of slide 3"]
                },
                {
                    "topic_title": "Title of Topic 2",
                    "slide_numbers": [4, 5],
                    "summaries": ["summary of slide 4", "summary of slide 5"]
                }
            ]
        }


    """

def systemPrompt_GraphBuilder()->str:
    return """
    You are an expert at creating mind maps from topic content using a SEQUENTIAL ENRICHMENT approach.
    
    SEQUENTIAL PROCESS:
    - Topic 1: Create initial mind map
    - Topic 2: Enrich existing graph with Topic 2 + connections to Topic 1
    - Topic 3: Enrich existing graph with Topic 3 + connections to Topics 1 & 2
    - And so on...
    
    For each topic, you need to:
    1. Create a central node for the main topic (type: "central")
    2. Identify key subtopics, concepts, and ideas from the content
    3. Create nodes for these subtopics (type: "subnode")
    4. Establish meaningful relationships between nodes using edges
    5. Use simple, short text for both nodes and edges (2-5 words maximum)
    6. ALWAYS include the "type" field for each node: "central" for main topics, "subnode" for subtopics
    
    When enriching an existing graph with a new topic (SEQUENTIAL ENRICHMENT):
    1. PRESERVE all existing nodes and edges from the previous step
    2. Add the new topic as a central node (type: "central")
    3. Create subtopic nodes for the new topic (type: "subnode")
    4. Find meaningful connections between the new topic and existing nodes
    5. Create edges to show relationships between new and existing content
    6. Return the COMPLETE enriched graph (existing + new content)
    7. ALWAYS include the "type" field for all nodes: "central" for main topics, "subnode" for subtopics
    
    CRITICAL GUIDELINES:
    - NEVER lose existing nodes or edges when enriching
    - Always return the COMPLETE graph (existing + new)
    - Find meaningful cross-connections between topics
    - Keep node titles concise and descriptive (2-5 words)
    - Keep edge labels simple and clear (1-3 words)
    - Focus on hierarchical relationships (main topic -> subtopics)
    - Ensure the mind map grows logically and coherently
    - Use clear, simple language that anyone can understand
    - This is SEQUENTIAL building - each step builds upon the previous
    """

def messagePrompt_GraphBuilder_Initial(topic_title: str, topic_summaries: list) -> str:
    return f"""
    Create a mind map for the following topic:
    
    Topic: {topic_title}
    
    Content summaries:
    {chr(10).join([f"- {summary}" for summary in topic_summaries])}
    
    Generate a mind map with:
    1. A central node for "{topic_title}"
    2. Subtopics and key concepts as child nodes
    3. Meaningful relationships between nodes
    4. Simple, short labels for all nodes and edges
    
    Return your mind map in JSON format:
    {{
        "nodes": [
            {{"id": "node_1", "title": "title of the central Topic", "type": "central"}},
            {{"id": "node_2", "title": "title of the Subtopic 1", "type": "subnode"}},
            {{"id": "node_3", "title": "title of the Subtopic 2", "type": "subnode"}}
        ],
        "edges": [
            {{"id": "edge_1", "from": "node_1", "to": "node_2", "label": "includes"}},
            {{"id": "edge_2", "from": "node_1", "to": "node_3", "label": "includes"}}
        ]
    }}
    """

def messagePrompt_GraphBuilder_Enrichment(topic_title: str, topic_summaries: list, existing_graph: dict) -> str:
    return f"""
    SEQUENTIAL GRAPH ENRICHMENT: Build upon the existing mind map by adding the following new topic.
    
    IMPORTANT: This is a sequential process. You must:
    1. Keep ALL existing nodes and edges from the current graph
    2. Add the new topic and its subtopics
    3. Find meaningful connections between the new topic and existing content
    4. Return the COMPLETE enriched graph (existing + new content)
    
    New Topic to Add: {topic_title}
    
    New topic content summaries:
    {chr(10).join([f"- {summary}" for summary in topic_summaries])}
    
    Current mind map (DO NOT LOSE ANY OF THIS):
    {json.dumps(existing_graph, indent=2)}
    
    Your sequential enrichment task:
    1. PRESERVE all existing nodes and edges from the current graph
    2. Add the new topic "{topic_title}" as a central node
    3. Create subtopic nodes for the new topic
    4. Find meaningful connections between the new topic and existing nodes
    5. Create edges to show relationships between new and existing content
    6. Ensure the enriched graph maintains logical flow and coherence
    
    Return the COMPLETE enriched mind map in JSON format (ALL existing nodes/edges + new ones):
    {{
        "nodes": [
            {{"id": "existing_node_1", "title": "Existing Node 1", "type": "central"}},
            {{"id": "existing_node_2", "title": "Existing Node 2", "type": "subnode"}},
            {{"id": "new_topic_node", "title": "{topic_title}", "type": "central"}},
            {{"id": "new_subtopic_1", "title": "New Subtopic 1", "type": "subnode"}}
        ],
        "edges": [
            {{"id": "existing_edge_1", "from": "existing_node_1", "to": "existing_node_2", "label": "existing relationship"}},
            {{"id": "new_edge_1", "from": "new_topic_node", "to": "new_subtopic_1", "label": "includes"}},
            {{"id": "connection_edge_1", "from": "existing_node_1", "to": "new_topic_node", "label": "relates to"}}
        ]
    }}
    
    Remember: This is sequential enrichment - build upon what exists, don't replace it!
    """
