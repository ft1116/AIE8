import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Define colors
start_end_color = '#90EE90'  # Light green
supervisor_color = '#87CEEB'  # Sky blue
agent_color = '#FFB6C1'  # Light pink
finish_color = '#DDA0DD'  # Plum

# Define node positions
positions = {
    'start': (5, 11),
    'supervisor': (5, 8),
    'rag_agent': (2, 5),
    'search_agent': (8, 5),
    'finish': (7, 3),
    'end': (7, 1)
}

# Create nodes
def create_node(x, y, text, color, width=1.5, height=0.8, style='rectangle'):
    if style == 'oval':
        # Create oval shape
        ellipse = patches.Ellipse((x, y), width, height, 
                                facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(ellipse)
    else:
        # Create rectangle
        rect = FancyBboxPatch((x-width/2, y-height/2), width, height,
                             boxstyle="round,pad=0.1",
                             facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
    
    # Add text
    ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')

# Create all nodes
create_node(positions['start'][0], positions['start'][1], '__start__', start_end_color, style='oval')
create_node(positions['supervisor'][0], positions['supervisor'][1], 'ResearchSupervisor', supervisor_color)
create_node(positions['rag_agent'][0], positions['rag_agent'][1], 'HowPeopleUseAIRetriever', agent_color)
create_node(positions['search_agent'][0], positions['search_agent'][1], 'Search', agent_color)
create_node(positions['finish'][0], positions['finish'][1], 'FINISH', finish_color)
create_node(positions['end'][0], positions['end'][1], '__end__', start_end_color, style='oval')

# Create arrows
def create_arrow(start, end, style='solid', color='black', linewidth=2):
    if style == 'dotted':
        linestyle = '--'
    else:
        linestyle = '-'
    
    # Calculate arrow direction and adjust start/end points
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = np.sqrt(dx**2 + dy**2)
    
    # Normalize and scale
    dx_norm = dx / length
    dy_norm = dy / length
    
    # Adjust start and end points to avoid overlapping with nodes
    start_adj = (start[0] + dx_norm * 0.4, start[1] + dy_norm * 0.4)
    end_adj = (end[0] - dx_norm * 0.4, end[1] - dy_norm * 0.4)
    
    # Create arrow
    arrow = patches.FancyArrowPatch(start_adj, end_adj,
                                   arrowstyle='->', mutation_scale=20,
                                   color=color, linewidth=linewidth, linestyle=linestyle)
    ax.add_patch(arrow)

# Create all arrows
# Start to Supervisor (solid)
create_arrow(positions['start'], positions['supervisor'], 'solid')

# Supervisor to agents (dotted - routing decisions)
create_arrow(positions['supervisor'], positions['rag_agent'], 'dotted')
create_arrow(positions['supervisor'], positions['search_agent'], 'dotted')

# Supervisor to FINISH (dotted - completion decision)
create_arrow(positions['supervisor'], positions['finish'], 'dotted')

# Agents back to Supervisor (solid - task completion)
create_arrow(positions['rag_agent'], positions['supervisor'], 'solid')
create_arrow(positions['search_agent'], positions['supervisor'], 'solid')

# FINISH to END (solid)
create_arrow(positions['finish'], positions['end'], 'solid')

# Add title
ax.text(5, 11.5, 'Multi-Agent RAG System Flow', ha='center', va='center', 
        fontsize=16, fontweight='bold')

# Add legend
legend_elements = [
    patches.Patch(color=start_end_color, label='Start/End Nodes'),
    patches.Patch(color=supervisor_color, label='Supervisor (Decision Maker)'),
    patches.Patch(color=agent_color, label='Specialized Agents'),
    patches.Patch(color=finish_color, label='Completion State')
]

ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))

# Add arrow type explanations
ax.text(0.5, 2, 'Solid arrows: Task completion/flow', fontsize=9, style='italic')
ax.text(0.5, 1.5, 'Dotted arrows: Routing decisions', fontsize=9, style='italic')

# Save the diagram
plt.tight_layout()
plt.savefig('multi_agent_flow_diagram.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print("Flow diagram saved as 'multi_agent_flow_diagram.png'")

