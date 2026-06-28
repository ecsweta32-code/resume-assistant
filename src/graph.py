# src/graph.py
import os
import sys

# Add the project root directory to the Python path if running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, START, END
from src.state import ScreeningState  # 👈 This fixes your NameError!
from src.node import (
    extract_and_retrieve_node,
    scoring_node,
    summary_node,
    questions_node,
    compile_report_node
)

# Initialize graph with our state definition
workflow = StateGraph(ScreeningState)

# 1. Add all nodes
workflow.add_node("extract_and_retrieve", extract_and_retrieve_node)
workflow.add_node("calculate_score", scoring_node)
workflow.add_node("generate_summary", summary_node)
workflow.add_node("generate_questions", questions_node)
workflow.add_node("compile_report", compile_report_node)

# 2. Build the edges (Control Flow)
workflow.add_edge(START, "extract_and_retrieve")

# LangGraph automatically runs these 3 nodes in parallel 
# because they share the exact same source node
workflow.add_edge("extract_and_retrieve", "calculate_score")
workflow.add_edge("extract_and_retrieve", "generate_summary")
workflow.add_edge("extract_and_retrieve", "generate_questions")

# Merge parallel branches back into the final compiler node
workflow.add_edge("calculate_score", "compile_report")
workflow.add_edge("generate_summary", "compile_report")
workflow.add_edge("generate_questions", "compile_report")

workflow.add_edge("compile_report", END)

# 3. Compile the graph so it's ready to execute
app = workflow.compile()