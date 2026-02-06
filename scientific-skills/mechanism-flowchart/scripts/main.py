#!/usr/bin/env python3
"""
Mechanism Flowchart Generator
Generates Mermaid diagrams for medical mechanisms and pathophysiology.
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DiagramType(Enum):
    FLOWCHART = "flowchart"
    SEQUENCE = "sequenceDiagram"
    STATE = "stateDiagram"


class FlowDirection(Enum):
    TOP_BOTTOM = "TB"
    LEFT_RIGHT = "LR"
    RIGHT_LEFT = "RL"
    BOTTOM_TOP = "BT"


@dataclass
class FlowNode:
    """Represents a node in the flowchart."""
    id: str
    label: str
    node_type: str = "default"  # default, process, decision, start, end
    
    def to_mermaid(self) -> str:
        """Convert to Mermaid syntax."""
        # Escape special characters
        label = self.label.replace('"', '"')
        return f'    {self.id}["{label}"]'


@dataclass
class FlowEdge:
    """Represents an edge/connection between nodes."""
    from_node: str
    to_node: str
    label: Optional[str] = None
    
    def to_mermaid(self) -> str:
        """Convert to Mermaid syntax."""
        if self.label:
            return f'    {self.from_node} -->|"{self.label}"| {self.to_node}'
        return f'    {self.from_node} --> {self.to_node}'


class MechanismDiagram:
    """Generates Mermaid flowcharts from medical mechanism descriptions."""
    
    # Medical keywords for node extraction
    MEDICAL_KEYWORDS = {
        "processes": [
            "activation", "inhibition", "secretion", "synthesis", "degradation",
            "phosphorylation", "transcription", "translation", "binding",
            "release", "uptake", "transport", "conversion", "metabolism"
        ],
        "causal": [
            "leads to", "causes", "results in", "triggers", "induces",
            "promotes", "stimulates", "enhances", "upregulates"
        ],
        "inhibitory": [
            "inhibits", "blocks", "prevents", "reduces", "decreases",
            "downregulates", "suppresses", "antagonizes"
        ]
    }
    
    def __init__(self, direction: str = "TB", style: str = "medical"):
        self.direction = FlowDirection(direction) if direction in [d.value for d in FlowDirection] else FlowDirection.TOP_BOTTOM
        self.style = style
        self.nodes: List[FlowNode] = []
        self.edges: List[FlowEdge] = []
        self.node_counter = 0
        
    def _generate_node_id(self) -> str:
        """Generate unique node ID."""
        self.node_counter += 1
        return f"N{self.node_counter}"
    
    def _extract_nodes_from_text(self, text: str) -> List[str]:
        """Extract potential nodes from text description."""
        # Split by common delimiters
        delimiters = r'[;,.]|\band\b|\bthen\b|\bwhich\b'
        parts = re.split(delimiters, text, flags=re.IGNORECASE)
        
        nodes = []
        for part in parts:
            part = part.strip()
            # Clean up the text
            part = re.sub(r'\s+', ' ', part)
            # Remove leading connecting words
            part = re.sub(r'^(leads? to|causes?|results? in|triggers?|and|or)\s+', '', part, flags=re.IGNORECASE)
            
            if len(part) > 3:  # Minimum meaningful length
                nodes.append(part)
        
        return nodes
    
    def _identify_relationships(self, text: str, nodes: List[str]) -> List[Tuple[int, int, str]]:
        """Identify relationships between nodes."""
        relationships = []
        
        # Simple sequential relationship for now
        for i in range(len(nodes) - 1):
            # Look for relationship indicators between nodes
            segment = text.lower()
            label = ""
            
            # Check for causal keywords
            for keyword in self.MEDICAL_KEYWORDS["causal"]:
                if keyword in segment:
                    label = keyword
                    break
            
            # Check for inhibitory keywords
            for keyword in self.MEDICAL_KEYWORDS["inhibitory"]:
                if keyword in segment:
                    label = keyword
                    break
            
            relationships.append((i, i + 1, label))
        
        return relationships
    
    def generate(self, mechanism_description: str, diagram_type: str = "flowchart") -> Dict:
        """
        Generate Mermaid flowchart from mechanism description.
        
        Args:
            mechanism_description: Text description of the mechanism
            diagram_type: Type of diagram (flowchart, sequence, state)
            
        Returns:
            Dictionary with Mermaid code and metadata
        """
        self.nodes = []
        self.edges = []
        self.node_counter = 0
        
        # Extract nodes
        node_labels = self._extract_nodes_from_text(mechanism_description)
        
        # Create nodes
        for label in node_labels[:10]:  # Limit to 10 nodes for readability
            node_id = self._generate_node_id()
            node = FlowNode(id=node_id, label=label)
            self.nodes.append(node)
        
        # Create edges
        relationships = self._identify_relationships(mechanism_description, node_labels)
        for from_idx, to_idx, label in relationships:
            if from_idx < len(self.nodes) and to_idx < len(self.nodes):
                edge = FlowEdge(
                    from_node=self.nodes[from_idx].id,
                    to_node=self.nodes[to_idx].id,
                    label=label if label else None
                )
                self.edges.append(edge)
        
        # Generate Mermaid code
        mermaid_code = self._generate_mermaid_code(diagram_type)
        
        return {
            "mermaid_code": mermaid_code,
            "diagram_type": diagram_type,
            "direction": self.direction.value,
            "nodes": [n.label for n in self.nodes],
            "edges": len(self.edges),
            "style": self.style
        }
    
    def _generate_mermaid_code(self, diagram_type: str) -> str:
        """Generate complete Mermaid code."""
        lines = []
        
        # Header
        if diagram_type == "flowchart":
            lines.append(f"flowchart {self.direction.value}")
        elif diagram_type == "sequence":
            lines.append("sequenceDiagram")
        elif diagram_type == "state":
            lines.append("stateDiagram-v2")
        
        # Add style definitions
        if self.style == "medical":
            lines.extend([
                "    classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
                "    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px",
                "    classDef start fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px"
            ])
        
        # Add nodes
        for node in self.nodes:
            lines.append(node.to_mermaid())
        
        # Add edges
        for edge in self.edges:
            lines.append(edge.to_mermaid())
        
        return "\n".join(lines)
    
    def generate_from_template(self, template_name: str) -> Dict:
        """Generate diagram from predefined template."""
        templates = {
            "diabetes_t2": {
                "nodes": [
                    "Insulin Resistance in Muscle/Fat",
                    "Compensatory Hyperinsulinemia",
                    "Beta Cell Stress",
                    "Progressive Beta Cell Failure",
                    "Hyperglycemia",
                    "Microvascular Complications"
                ],
                "edges": [(0, 1, "causes"), (1, 2, "leads to"), (2, 3, "results in"), 
                         (3, 4, "produces"), (4, 5, "leads to")]
            },
            "hypertension_raas": {
                "nodes": [
                    "Decreased Renal Perfusion",
                    "Renin Release from JG Cells",
                    "Angiotensinogen → Angiotensin I",
                    "ACE converts AT-I to AT-II",
                    "Vasoconstriction",
                    "Aldosterone Release",
                    "Sodium/Water Retention"
                ],
                "edges": [(0, 1, "triggers"), (1, 2, "catalyzes"), (2, 3, ""), 
                         (3, 4, "causes"), (3, 5, "stimulates"), (5, 6, "promotes")]
            },
            "coagulation_cascade": {
                "nodes": [
                    "Vascular Injury",
                    "TF Release",
                    "Factor VII Activation",
                    "TF-FVIIa Complex",
                    "Factor X Activation",
                    "Thrombin Generation",
                    "Fibrin Clot Formation"
                ],
                "edges": [(0, 1, ""), (1, 2, "activates"), (2, 3, "forms"), 
                         (3, 4, "activates"), (4, 5, "leads to"), (5, 6, "catalyzes")]
            }
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(templates.keys())}")
        
        template = templates[template_name]
        
        # Create nodes
        self.nodes = []
        self.edges = []
        self.node_counter = 0
        
        for label in template["nodes"]:
            node_id = self._generate_node_id()
            self.nodes.append(FlowNode(id=node_id, label=label))
        
        # Create edges
        for from_idx, to_idx, label in template["edges"]:
            self.edges.append(FlowEdge(
                from_node=self.nodes[from_idx].id,
                to_node=self.nodes[to_idx].id,
                label=label if label else None
            ))
        
        mermaid_code = self._generate_mermaid_code("flowchart")
        
        return {
            "mermaid_code": mermaid_code,
            "template": template_name,
            "nodes": template["nodes"],
            "edges": len(template["edges"])
        }


def main():
    """CLI interface for testing."""
    import sys
    
    generator = MechanismDiagram()
    
    if len(sys.argv) > 1:
        # Check if it's a template
        if sys.argv[1] in ["diabetes_t2", "hypertension_raas", "coagulation_cascade"]:
            result = generator.generate_from_template(sys.argv[1])
        else:
            description = " ".join(sys.argv[1:])
            result = generator.generate(description)
    else:
        # Demo
        description = ("Type 2 Diabetes pathophysiology: Insulin resistance in peripheral tissues "
                      "leads to compensatory hyperinsulinemia, which causes beta cell stress, "
                      "resulting in progressive beta cell failure and hyperglycemia")
        result = generator.generate(description)
    
    print("Generated Mermaid Code:")
    print("=" * 50)
    print(result['mermaid_code'])
    print("\nMetadata:")
    print(json.dumps({k: v for k, v in result.items() if k != 'mermaid_code'}, indent=2))


if __name__ == "__main__":
    main()
