import json
import os
from typing import Dict, List, Optional
from datetime import datetime

def load_exported_output(file_path: str) -> Optional[Dict]:
    """
    Load an exported system output from a JSON file.
    
    Args:
        file_path: Path to the exported JSON file
    
    Returns:
        Dict containing the complete system output, or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading exported output from {file_path}: {e}")
        return None

def display_export_summary(exported_data: Dict) -> None:
    """
    Display a summary of the exported system output.
    
    Args:
        exported_data: Exported data loaded from JSON file
    """
    if not exported_data:
        print("No exported data to display")
        return
    
    metadata = exported_data.get('metadata', {})
    processing_results = exported_data.get('processing_results', {})
    
    print("=" * 60)
    print("EXPORTED SYSTEM OUTPUT SUMMARY")
    print("=" * 60)
    print(f"Thread ID: {metadata.get('thread_id', 'Unknown')}")
    print(f"Created: {metadata.get('created_at', 'Unknown')}")
    print(f"Source File: {metadata.get('source_file', 'Unknown')}")
    print(f"Total Pages: {metadata.get('total_pages', 0)}")
    print(f"Total Topics: {metadata.get('total_topics', 0)}")
    print(f"Graph Nodes: {metadata.get('graph_nodes', 0)}")
    print(f"Graph Edges: {metadata.get('graph_edges', 0)}")
    
    # Display page summaries
    page_summaries = processing_results.get('page_summaries', [])
    print(f"\n📄 PAGE SUMMARIES ({len(page_summaries)} pages):")
    for i, page in enumerate(page_summaries, 1):
        summary = page.get('summary', 'No summary')
        # Truncate long summaries
        if len(summary) > 100:
            summary = summary[:100] + "..."
        print(f"  {i}. Page {page.get('page_number', '?')}: {summary}")
    
    # Display topics
    topics = processing_results.get('topics', {})
    topic_names = topics.get('topic_names', [])
    topic_details = topics.get('topic_details', [])
    
    print(f"\n📚 TOPICS ({len(topic_names)} topics):")
    for i, topic_name in enumerate(topic_names, 1):
        print(f"  {i}. {topic_name}")
    
    print(f"\n📋 TOPIC DETAILS:")
    for i, topic in enumerate(topic_details, 1):
        print(f"  {i}. {topic.get('topic_title', 'Unknown')}")
        print(f"     - Slides: {topic.get('slides_range', 'Unknown')}")
        print(f"     - Slide Numbers: {topic.get('slide_numbers', [])}")
        summaries = topic.get('summaries', [])
        if summaries:
            print(f"     - Summaries: {len(summaries)} summaries")
    
    # Display final graph
    final_graph = processing_results.get('final_graph', {})
    nodes = final_graph.get('nodes', [])
    edges = final_graph.get('edges', [])
    
    print(f"\n🗺️  FINAL MIND MAP:")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Graph Building Complete: {processing_results.get('graph_building_complete', False)}")
    
    if nodes:
        print(f"\n  NODES:")
        for i, node in enumerate(nodes, 1):
            print(f"    {i}. {node.get('id', 'unknown')}: {node.get('title', 'untitled')}")
    
    if edges:
        print(f"\n  EDGES:")
        for i, edge in enumerate(edges, 1):
            from_node = edge.get('from', 'unknown')
            to_node = edge.get('to', 'unknown')
            label = edge.get('label', '')
            print(f"    {i}. {from_node} --[{label}]--> {to_node}")

def list_exported_files(output_dir: str = "output") -> List[str]:
    """
    List all exported system output files in the output directory.
    
    Args:
        output_dir: Directory containing exported files
    
    Returns:
        List of file paths to exported files
    """
    if not os.path.exists(output_dir):
        return []
    
    exported_files = []
    for filename in os.listdir(output_dir):
        if filename.startswith("system_output_") and filename.endswith(".json"):
            exported_files.append(os.path.join(output_dir, filename))
    
    return sorted(exported_files, key=os.path.getmtime, reverse=True)

def get_latest_export(output_dir: str = "output") -> Optional[str]:
    """
    Get the path to the most recently exported system output.
    
    Args:
        output_dir: Directory containing exported files
    
    Returns:
        Path to the latest exported file, or None if no files found
    """
    exported_files = list_exported_files(output_dir)
    return exported_files[0] if exported_files else None

def export_graph_only(exported_data: Dict, output_file: str) -> bool:
    """
    Export only the graph portion from the complete system output.
    
    Args:
        exported_data: Complete exported system output
        output_file: Path where to save the graph-only file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        final_graph = exported_data.get('processing_results', {}).get('final_graph', {})
        
        if not final_graph:
            print("No graph data found in exported file")
            return False
        
        # Create graph-only export with metadata
        graph_export = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "source_thread": exported_data.get('metadata', {}).get('thread_id', 'unknown'),
                "total_nodes": len(final_graph.get('nodes', [])),
                "total_edges": len(final_graph.get('edges', []))
            },
            "graph": final_graph
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_export, f, indent=2, ensure_ascii=False)
        
        print(f"Graph exported to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error exporting graph: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    latest_export = get_latest_export()
    if latest_export:
        print(f"Loading latest export: {latest_export}")
        exported_data = load_exported_output(latest_export)
        if exported_data:
            display_export_summary(exported_data)
            
            # Export graph only
            graph_output = latest_export.replace("system_output_", "graph_only_")
            export_graph_only(exported_data, graph_output)
    else:
        print("No exported files found in output directory")
