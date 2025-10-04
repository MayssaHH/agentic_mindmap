def systemPrompt_PagesSummary()->str:
    return f"""
        You are an expert at analyzing powerpoint pages and extracting key information. 
        Your task is to deeply understand the content of this page and provide a comprehensive summary.
        Focus on:
            - Main ideas/topics and concepts
            - Key data points and statistics
            - Important relationships between ideas
            - Visual elements and their significance
            - Any technical details or specifications
            
        Provide a detailed, structured summary that captures the essence of the page.
    """

def messagePrompt_PagesSummary()->str:
    return f"""
    Analyze this page extracted from a powerpoint presentation/lecture and provide a comprehensive summary. 
    Look for main topics, key information, data points, and any important details that would be relevant for creating a mind map.
    """