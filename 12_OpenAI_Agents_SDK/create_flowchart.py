import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(20, 24))
ax.set_xlim(0, 12)
ax.set_ylim(0, 24)
ax.axis('off')

# Colors
header_color = '#2E86AB'
manager_color = '#A23B72'
planner_color = '#F18F01'
search_color = '#C73E1D'
writer_color = '#7209B7'
output_color = '#2D5016'

# Title
title_box = FancyBboxPatch((1, 22), 10, 1.5, 
                          boxstyle="round,pad=0.1", 
                          facecolor=header_color, 
                          edgecolor='black', 
                          linewidth=2)
ax.add_patch(title_box)
ax.text(6, 22.75, 'FOOTBALL RECRUITING AGENT SYSTEM', 
        ha='center', va='center', fontsize=18, fontweight='bold', color='white')

# User Input
input_box = FancyBboxPatch((4, 20), 4, 1, 
                          boxstyle="round,pad=0.1", 
                          facecolor='lightblue', 
                          edgecolor='black', 
                          linewidth=2)
ax.add_patch(input_box)
ax.text(6, 20.5, 'USER INPUT\n"Research QB John Smith"', 
        ha='center', va='center', fontsize=14, fontweight='bold')

# Arrow 1
ax.arrow(6, 20, 0, -0.5, head_width=0.2, head_length=0.1, fc='black', ec='black')

# Research Manager
manager_box = FancyBboxPatch((1, 18), 10, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=manager_color, 
                            edgecolor='black', 
                            linewidth=2)
ax.add_patch(manager_box)
ax.text(6, 18.75, 'RESEARCH MANAGER\n• Orchestrates the entire process\n• Manages progress tracking with Printer class\n• Handles error management and retries', 
        ha='center', va='center', fontsize=13, fontweight='bold', color='white')

# Arrow 2
ax.arrow(6, 18, 0, -0.5, head_width=0.2, head_length=0.1, fc='black', ec='black')

# Planner Agent
planner_box = FancyBboxPatch((1, 15.5), 10, 2, 
                           boxstyle="round,pad=0.1", 
                           facecolor=planner_color, 
                           edgecolor='black', 
                           linewidth=2)
ax.add_patch(planner_box)
planner_text = """PLANNER AGENT
• Role: College Football Recruiting Assistant
• Input: Recruiting query about prospective student-athlete
• Output: 5-20 search terms focused on:
  - Player stats & performance
  - Game highlights & film
  - Academic performance
  - Character references
  - Recruiting rankings
  - Program fit assessment
• Model: GPT-4.1 with structured output (WebSearchPlan)"""
ax.text(6, 16.5, planner_text, ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Arrow 3
ax.arrow(6, 15.5, 0, -0.5, head_width=0.2, head_length=0.1, fc='black', ec='black')

# Search Agent
search_box = FancyBboxPatch((1, 13), 10, 2, 
                          boxstyle="round,pad=0.1", 
                          facecolor=search_color, 
                          edgecolor='black', 
                          linewidth=2)
ax.add_patch(search_box)
search_text = """SEARCH AGENT
• Role: College Football Recruiting Assistant
• Tools: WebSearchTool (OpenAI Responses API)
• Process: Parallel execution (max 5 concurrent searches)
• Output: Concise summaries (2-3 paragraphs, <300 words)
• Focus: Actionable recruiting intelligence
• Model: GPT-4 with tool_choice="required" """
ax.text(6, 14, search_text, ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Arrow 4
ax.arrow(6, 13, 0, -0.5, head_width=0.2, head_length=0.1, fc='black', ec='black')

# Writer Agent
writer_box = FancyBboxPatch((1, 9.5), 10, 3, 
                           boxstyle="round,pad=0.1", 
                           facecolor=writer_color, 
                           edgecolor='black', 
                           linewidth=2)
ax.add_patch(writer_box)
writer_text = """WRITER AGENT
• Role: Senior College Football Recruiting Coordinator
• Input: Original query + search summaries
• Process: Creates outline → Generates comprehensive report
• Output: Professional scouting report (5-10 pages, 1000+ words)
• Sections:
  - Player background
  - Athletic performance
  - Academic standing
  - Character assessment
  - Potential fit with program
  - Recruiting recommendations
• Model: o3-mini (reasoning model)"""
ax.text(6, 11, writer_text, ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Arrow 5
ax.arrow(6, 9.5, 0, -0.5, head_width=0.2, head_length=0.1, fc='black', ec='black')

# Final Output
output_box = FancyBboxPatch((1, 6), 10, 2.5, 
                           boxstyle="round,pad=0.1", 
                           facecolor=output_color, 
                           edgecolor='black', 
                           linewidth=2)
ax.add_patch(output_box)
output_text = """FINAL OUTPUT
• Short Summary (2-3 sentences)
• Detailed Markdown Report
• 5 Unique Follow-up Questions:
  - Additional game film analysis
  - Academic transcripts review
  - Character references
  - Competitive offers assessment
  - Program-specific fit analysis"""
ax.text(6, 7.25, output_text, ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Add some styling
plt.title('Football Recruiting Agent System Workflow', fontsize=18, fontweight='bold', pad=20)

# Save the figure
plt.tight_layout()
plt.savefig('/Users/fmt116/Desktop/AI_Makerspace/AIE8/12_OpenAI_Agents_SDK/football_recruiting_flowchart.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print("Flowchart saved as 'football_recruiting_flowchart.png'")
