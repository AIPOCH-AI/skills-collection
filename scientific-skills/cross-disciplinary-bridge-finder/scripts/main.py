#!/usr/bin/env python3
"""
Cross-Disciplinary Bridge Finder
Identifies potential connections between seemingly unrelated disciplines
and predicts cross-disciplinary innovation opportunities.

Usage:
    python main.py --source "biology" --target "computer science" --depth 3
    python main.py --domains "physics,biology,economics" --mode complete-graph
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import uuid
from datetime import datetime

import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity


# Constants
DEFAULT_CONFIG = {
    "novelty_weight": 0.5,
    "feasibility_weight": 0.3,
    "impact_weight": 0.2,
    "min_bridge_score": 0.5,
    "max_path_depth": 4,
}

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


@dataclass
class Domain:
    """Represents a knowledge domain/discipline."""
    name: str
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    parent_domains: List[str] = field(default_factory=list)
    core_concepts: List[str] = field(default_factory=list)
    methodologies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConceptualAnalogy:
    """Represents an analogy between two concepts."""
    source_concept: str
    target_concept: str
    analogy_description: str
    strength: float  # 0-1
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Bridge:
    """Represents a bridge between two domains."""
    id: str
    source: str
    target: str
    path: List[str]  # Intermediate domains/concepts
    bridge_score: float
    novelty_score: float
    feasibility_score: float
    conceptual_mappings: Dict[str, str] = field(default_factory=dict)
    analogies: List[ConceptualAnalogy] = field(default_factory=list)
    innovation_opportunities: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "path": self.path,
            "bridge_score": round(self.bridge_score, 3),
            "novelty_score": round(self.novelty_score, 3),
            "feasibility_score": round(self.feasibility_score, 3),
            "conceptual_mappings": self.conceptual_mappings,
            "analogies": [a.to_dict() for a in self.analogies],
            "innovation_opportunities": self.innovation_opportunities
        }


@dataclass
class InnovationHypothesis:
    """Represents a research/innovation hypothesis."""
    title: str
    description: str
    rationale: str
    potential_impact: str  # high/medium/low
    timeline: str
    required_expertise: List[str]
    key_challenges: List[str]
    success_metrics: List[str]
    
    def to_dict(self) -> dict:
        return asdict(self)


class KnowledgeGraph:
    """Manages the conceptual knowledge graph."""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.domains: Dict[str, Domain] = {}
        self._initialize_core_domains()
    
    def _initialize_core_domains(self):
        """Initialize core knowledge domains."""
        core_domains = [
            Domain(
                name="biology",
                description="Study of living organisms",
                keywords=["cell", "organism", "evolution", "genetics", "ecology"],
                core_concepts=["evolution", "homeostasis", "emergence", "adaptation"],
                methodologies=["experimentation", "observation", "modeling"]
            ),
            Domain(
                name="immunology",
                description="Study of immune systems",
                keywords=["antibody", "cytokine", "t-cell", "immune response"],
                core_concepts=["self-nonself discrimination", "immune memory", "inflammation"],
                methodologies=["flow cytometry", "ELISA", "sequencing"],
                parent_domains=["biology"]
            ),
            Domain(
                name="computer science",
                description="Study of computation and information",
                keywords=["algorithm", "data structure", "complexity", "computation"],
                core_concepts=["abstraction", "modularity", "recursion", "parallelism"],
                methodologies=["analysis", "implementation", "verification"]
            ),
            Domain(
                name="machine learning",
                description="Algorithms that learn from data",
                keywords=["neural network", "training", "inference", "optimization"],
                core_concepts=["generalization", "overfitting", "representation learning"],
                methodologies=["supervised learning", "unsupervised learning", "reinforcement learning"],
                parent_domains=["computer science", "statistics"]
            ),
            Domain(
                name="physics",
                description="Study of matter and energy",
                keywords=["force", "energy", "particle", "field", "wave"],
                core_concepts=["conservation", "symmetry", "uncertainty", "entropy"],
                methodologies=["mathematical modeling", "experiment", "simulation"]
            ),
            Domain(
                name="economics",
                description="Study of resource allocation",
                keywords=["market", "supply", "demand", "price", "incentive"],
                core_concepts=["equilibrium", "optimization", "game theory", "externalities"],
                methodologies=["econometrics", "modeling", "behavioral experiments"]
            ),
            Domain(
                name="psychology",
                description="Study of mind and behavior",
                keywords=["cognition", "emotion", "perception", "memory"],
                core_concepts=["attention", "learning", "decision making", "bias"],
                methodologies=["experiments", "surveys", "neuroimaging"]
            ),
            Domain(
                name="neuroscience",
                description="Study of nervous systems",
                keywords=["neuron", "synapse", "brain", "circuit", "plasticity"],
                core_concepts=["information processing", "plasticity", "oscillation", "encoding"],
                methodologies=["electrophysiology", "imaging", "optogenetics"],
                parent_domains=["biology", "psychology"]
            ),
            Domain(
                name="chemistry",
                description="Study of matter and reactions",
                keywords=["molecule", "reaction", "catalyst", "bond"],
                core_concepts=["equilibrium", "kinetics", "thermodynamics", "structure"],
                methodologies=["synthesis", "spectroscopy", "chromatography"]
            ),
            Domain(
                name="materials science",
                description="Study of material properties",
                keywords=["crystal", "polymer", "composite", "nanomaterial"],
                core_concepts=["structure-property relationship", "phase transition", "defect"],
                methodologies=["characterization", "synthesis", "simulation"],
                parent_domains=["physics", "chemistry"]
            ),
            Domain(
                name="sociology",
                description="Study of social behavior",
                keywords=["social structure", "institution", "culture", "interaction"],
                core_concepts=["social networks", "collective behavior", "stratification"],
                methodologies=["surveys", "ethnography", "network analysis"]
            ),
            Domain(
                name="mathematics",
                description="Study of abstract structures",
                keywords=["number", "function", "proof", "topology", "algebra"],
                core_concepts=["abstraction", "generality", "elegance", "rigor"],
                methodologies=["proof", "construction", "computation"]
            ),
            Domain(
                name="medicine",
                description="Study of disease and treatment",
                keywords=["diagnosis", "therapy", "pathology", "patient"],
                core_concepts=["evidence-based practice", "precision medicine", "holistic care"],
                methodologies=["clinical trial", "case study", "systematic review"],
                parent_domains=["biology"]
            ),
            Domain(
                name="game theory",
                description="Study of strategic interaction",
                keywords=["strategy", "equilibrium", "payoff", "incentive"],
                core_concepts=["Nash equilibrium", "dominant strategy", "cooperation"],
                methodologies=["mathematical analysis", "simulation"],
                parent_domains=["mathematics", "economics"]
            ),
            Domain(
                name="network science",
                description="Study of complex networks",
                keywords=["node", "edge", "centrality", "clustering"],
                core_concepts=["small world", "scale-free", "community structure"],
                methodologies=["graph analysis", "statistical mechanics"],
                parent_domains=["mathematics", "physics", "computer science"]
            ),
            Domain(
                name="optimization",
                description="Finding best solutions under constraints",
                keywords=["objective function", "constraint", "gradient", "convergence"],
                core_concepts=["local vs global optimum", "convexity", "trade-offs"],
                methodologies=["gradient descent", "evolutionary algorithms", "linear programming"],
                parent_domains=["mathematics", "computer science"]
            ),
            Domain(
                name="complex systems",
                description="Study of emergent collective behavior",
                keywords=["emergence", "self-organization", "nonlinearity", "feedback"],
                core_concepts=["phase transition", "criticality", "robustness"],
                methodologies=["agent-based modeling", "network analysis"],
                parent_domains=["physics", "mathematics"]
            ),
            Domain(
                name="cryptography",
                description="Secure communication techniques",
                keywords=["encryption", "key", "hash", "protocol"],
                core_concepts=["confidentiality", "integrity", "authentication", "zero-knowledge"],
                methodologies=["symmetric encryption", "public-key", "protocol design"],
                parent_domains=["computer science", "mathematics"]
            ),
            Domain(
                name="blockchain",
                description="Distributed ledger technology",
                keywords=["distributed ledger", "consensus", "smart contract", "decentralization"],
                core_concepts=["immutability", "consensus", "decentralization", "transparency"],
                methodologies=["proof of work", "proof of stake", "Byzantine fault tolerance"],
                parent_domains=["computer science", "cryptography"]
            ),
            Domain(
                name="genetics",
                description="Study of heredity and variation",
                keywords=["gene", "allele", "chromosome", "mutation", "inheritance"],
                core_concepts=["Mendelian inheritance", "gene expression", "epigenetics"],
                methodologies=["sequencing", "genotyping", "GWAS"],
                parent_domains=["biology"]
            ),
        ]
        
        for domain in core_domains:
            self.add_domain(domain)
        
        # Add intermediate concepts and edges
        self._add_concept_edges()
    
    def add_domain(self, domain: Domain):
        """Add a domain to the graph."""
        self.domains[domain.name.lower()] = domain
        self.graph.add_node(
            domain.name.lower(),
            type="domain",
            data=domain
        )
    
    def _add_concept_edges(self):
        """Add conceptual edges between domains."""
        # Define cross-domain analogies and relationships
        edges = [
            # Network science bridges
            ("network science", "sociology", 0.8, "social network analysis"),
            ("network science", "neuroscience", 0.75, "neural networks"),
            ("network science", "immunology", 0.7, "immune network theory"),
            ("network science", "computer science", 0.9, "graph algorithms"),
            
            # Optimization bridges
            ("optimization", "economics", 0.8, "resource allocation"),
            ("optimization", "biology", 0.7, "evolutionary optimization"),
            ("optimization", "machine learning", 0.9, "training algorithms"),
            ("optimization", "physics", 0.75, "energy minimization"),
            
            # Complex systems bridges
            ("complex systems", "biology", 0.85, "ecosystems"),
            ("complex systems", "economics", 0.8, "market dynamics"),
            ("complex systems", "physics", 0.9, "statistical mechanics"),
            ("complex systems", "sociology", 0.75, "collective behavior"),
            
            # Game theory bridges
            ("game theory", "economics", 0.95, "strategic interaction"),
            ("game theory", "biology", 0.8, "evolutionary game theory"),
            ("game theory", "computer science", 0.75, "algorithmic game theory"),
            ("game theory", "psychology", 0.7, "decision making"),
            
            # Machine learning bridges
            ("machine learning", "neuroscience", 0.85, "neural networks"),
            ("machine learning", "statistics", 0.9, "statistical learning"),
            ("machine learning", "optimization", 0.85, "gradient descent"),
            
            # Physics bridges
            ("physics", "materials science", 0.9, "condensed matter"),
            ("physics", "neuroscience", 0.65, "neural dynamics"),
            
            # Biology bridges
            ("biology", "medicine", 0.95, "pathophysiology"),
            ("biology", "chemistry", 0.85, "biochemistry"),
            ("biology", "materials science", 0.7, "biomaterials"),
            
            # Cryptography bridges
            ("cryptography", "blockchain", 0.9, "secure protocols"),
            ("cryptography", "game theory", 0.65, "mechanism design"),
            
            # Additional novel bridges
            ("immunology", "blockchain", 0.6, "consensus mechanisms"),
            ("genetics", "cryptography", 0.55, "DNA encryption"),
            ("neuroscience", "machine learning", 0.85, "deep learning inspiration"),
        ]
        
        for source, target, weight, description in edges:
            if source in self.domains and target in self.domains:
                self.graph.add_edge(
                    source, target,
                    weight=weight,
                    description=description,
                    type="conceptual_bridge"
                )
    
    def find_paths(
        self,
        source: str,
        target: str,
        max_depth: int = 4
    ) -> List[Tuple[List[str], float]]:
        """Find paths between two domains with scores."""
        source = source.lower()
        target = target.lower()
        
        paths = []
        try:
            # Find simple paths up to max_depth
            for path in nx.all_simple_paths(
                self.graph, source, target, cutoff=max_depth
            ):
                if len(path) <= max_depth + 1:
                    # Calculate path score
                    score = self._calculate_path_score(path)
                    paths.append((path, score))
        except nx.NetworkXNoPath:
            pass
        
        # Sort by score
        paths.sort(key=lambda x: x[1], reverse=True)
        return paths
    
    def _calculate_path_score(self, path: List[str]) -> float:
        """Calculate a score for a path based on edge weights."""
        if len(path) < 2:
            return 0.0
        
        scores = []
        for i in range(len(path) - 1):
            edge_data = self.graph.get_edge_data(path[i], path[i + 1])
            if edge_data:
                scores.append(edge_data.get("weight", 0.5))
            else:
                scores.append(0.3)  # Default for implicit connections
        
        # Path score is product of edge weights, normalized
        if not scores:
            return 0.0
        
        import math
        # Geometric mean of edge weights
        return math.exp(sum(math.log(max(s, 0.01)) for s in scores) / len(scores))
    
    def get_domain(self, name: str) -> Optional[Domain]:
        """Get a domain by name."""
        return self.domains.get(name.lower())
    
    def get_neighbors(self, name: str) -> List[str]:
        """Get neighboring domains."""
        name = name.lower()
        if name in self.graph:
            return list(self.graph.neighbors(name))
        return []


class BridgeAnalyzer:
    """Analyzes and generates bridges between domains."""
    
    def __init__(self, knowledge_graph: KnowledgeGraph, config: Optional[Dict] = None):
        self.kg = knowledge_graph
        self.config = config or DEFAULT_CONFIG.copy()
    
    def discover_bridges(
        self,
        source: str,
        target: str,
        max_bridges: int = 10,
        depth: int = 3
    ) -> List[Bridge]:
        """Discover bridges between two domains."""
        paths = self.kg.find_paths(source, target, max_depth=depth)
        
        bridges = []
        for i, (path, path_score) in enumerate(paths[:max_bridges * 2]):
            if len(path) < 2:
                continue
            
            bridge_id = f"bridge_{i+1:03d}"
            
            # Calculate component scores
            novelty = self._calculate_novelty(path)
            feasibility = self._calculate_feasibility(path)
            
            # Overall bridge score
            bridge_score = (
                path_score * 0.4 +
                novelty * self.config["novelty_weight"] +
                feasibility * self.config["feasibility_weight"]
            )
            
            if bridge_score < self.config["min_bridge_score"]:
                continue
            
            # Generate conceptual mappings
            mappings = self._generate_conceptual_mappings(path[0], path[-1])
            
            # Generate analogies
            analogies = self._generate_analogies(path)
            
            # Generate innovation opportunities
            opportunities = self._generate_opportunities(path, bridge_score)
            
            bridge = Bridge(
                id=bridge_id,
                source=source,
                target=target,
                path=path,
                bridge_score=bridge_score,
                novelty_score=novelty,
                feasibility_score=feasibility,
                conceptual_mappings=mappings,
                analogies=analogies,
                innovation_opportunities=opportunities
            )
            bridges.append(bridge)
        
        # Sort and limit
        bridges.sort(key=lambda b: b.bridge_score, reverse=True)
        return bridges[:max_bridges]
    
    def _calculate_novelty(self, path: List[str]) -> float:
        """Calculate novelty score for a path."""
        # Novelty is higher for longer, less common paths
        length_factor = min((len(path) - 1) / 4, 1.0)  # 0-1
        
        # Check if this is a well-trodden path
        common_pairs = [
            ("machine learning", "neuroscience"),
            ("biology", "chemistry"),
            ("physics", "mathematics"),
        ]
        
        path_pairs = set(zip(path[:-1], path[1:]))
        common_count = sum(1 for pair in common_pairs if pair in path_pairs)
        familiarity = common_count / max(len(path_pairs), 1)
        
        novelty = 0.5 + (length_factor * 0.3) - (familiarity * 0.3)
        return max(0.0, min(1.0, novelty))
    
    def _calculate_feasibility(self, path: List[str]) -> float:
        """Calculate feasibility score for a path."""
        # Feasibility decreases with path length but increases with edge weights
        path_length_penalty = (len(path) - 2) * 0.1
        
        # Average edge weight
        edge_weights = []
        for i in range(len(path) - 1):
            edge_data = self.kg.graph.get_edge_data(path[i], path[i + 1])
            if edge_data:
                edge_weights.append(edge_data.get("weight", 0.5))
        
        avg_weight = sum(edge_weights) / len(edge_weights) if edge_weights else 0.5
        
        feasibility = avg_weight - path_length_penalty
        return max(0.0, min(1.0, feasibility))
    
    def _generate_conceptual_mappings(
        self,
        source: str,
        target: str
    ) -> Dict[str, str]:
        """Generate conceptual mappings between source and target."""
        # This is a simplified version - in production, use LLM for richer mappings
        mappings = {}
        
        source_domain = self.kg.get_domain(source)
        target_domain = self.kg.get_domain(target)
        
        if source_domain and target_domain:
            # Map core concepts based on structural similarity
            for s_concept in source_domain.core_concepts[:3]:
                for t_concept in target_domain.core_concepts[:3]:
                    if self._concept_similarity(s_concept, t_concept) > 0.5:
                        mappings[s_concept] = t_concept
        
        # If no mappings found, create generic ones
        if not mappings:
            mappings[f"{source}_structure"] = f"{target}_structure"
            mappings[f"{source}_dynamics"] = f"{target}_dynamics"
        
        return mappings
    
    def _concept_similarity(self, c1: str, c2: str) -> float:
        """Calculate semantic similarity between two concepts."""
        # Simplified similarity based on word overlap
        words1 = set(c1.lower().split())
        words2 = set(c2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _generate_analogies(self, path: List[str]) -> List[ConceptualAnalogy]:
        """Generate analogies along the path."""
        analogies = []
        
        # Generate analogies for adjacent nodes
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            source_domain = self.kg.get_domain(source)
            target_domain = self.kg.get_domain(target)
            
            if source_domain and target_domain:
                s_concept = source_domain.core_concepts[0] if source_domain.core_concepts else source
                t_concept = target_domain.core_concepts[0] if target_domain.core_concepts else target
                
                analogy = ConceptualAnalogy(
                    source_concept=s_concept,
                    target_concept=t_concept,
                    analogy_description=f"Both involve {s_concept} and {t_concept} in their respective domains",
                    strength=0.7
                )
                analogies.append(analogy)
        
        return analogies
    
    def _generate_opportunities(
        self,
        path: List[str],
        bridge_score: float
    ) -> List[dict]:
        """Generate innovation opportunities."""
        opportunities = []
        
        # Determine impact level
        if bridge_score > 0.8:
            impact = "high"
            timeline = "2-4 years"
        elif bridge_score > 0.6:
            impact = "medium"
            timeline = "3-5 years"
        else:
            impact = "speculative"
            timeline = "5-10 years"
        
        # Create opportunity based on path
        source = path[0]
        target = path[-1]
        intermediates = path[1:-1] if len(path) > 2 else []
        
        title = f"Cross-disciplinary Innovation: {source.title()} × {target.title()}"
        if intermediates:
            title += f" via {intermediates[0].title()}"
        
        description = (
            f"Leverage conceptual bridges between {source} and {target} "
            f"to develop novel methodologies and insights."
        )
        
        opportunity = {
            "title": title,
            "description": description,
            "potential_impact": impact,
            "timeline": timeline,
            "key_collaborators": [f"{d} experts" for d in path]
        }
        opportunities.append(opportunity)
        
        return opportunities
    
    def generate_hypotheses(
        self,
        source: str,
        target: str,
        n_hypotheses: int = 5
    ) -> List[InnovationHypothesis]:
        """Generate research hypotheses at the intersection."""
        hypotheses = []
        
        template_types = [
            "methodology_transfer",
            "analogical_insight",
            "hybrid_approach",
            "problem_reframing",
            "tool_adaptation"
        ]
        
        for i in range(n_hypotheses):
            template = template_types[i % len(template_types)]
            
            if template == "methodology_transfer":
                title = f"Applying {target.title()} Methods to {source.title()} Problems"
                description = f"Transfer successful methodologies from {target} to address open questions in {source}."
                expertise = [source, target, "methods development"]
            elif template == "analogical_insight":
                title = f"{source.title()} Insights from {target.title()} Perspective"
                description = f"Use {target} concepts as analogy generators for understanding {source} phenomena."
                expertise = [source, target, "theory development"]
            elif template == "hybrid_approach":
                title = f"Hybrid {source.title()}-{target.title()} Framework"
                description = f"Integrate theoretical frameworks from both domains for synergistic understanding."
                expertise = [source, target, "systems thinking"]
            elif template == "problem_reframing":
                title = f"Reframing {source.title()} Through {target.title()} Lens"
                description = f"Recast classical {source} problems using {target} formalisms."
                expertise = [source, target, "formal methods"]
            else:
                title = f"Adapting {target.title()} Tools for {source.title()}"
                description = f"Modify existing {target} tools to suit {source} data and questions."
                expertise = [source, target, "tool development"]
            
            hypothesis = InnovationHypothesis(
                title=title,
                description=description,
                rationale=f"Strong conceptual bridge identified between {source} and {target}",
                potential_impact="medium" if i < 3 else "speculative",
                timeline="3-5 years" if i < 3 else "5-10 years",
                required_expertise=expertise,
                key_challenges=["terminology alignment", "methodology integration", "validation"],
                success_metrics=["publications", "tools developed", "collaborations formed"]
            )
            hypotheses.append(hypothesis)
        
        return hypotheses


class OutputFormatter:
    """Formats output in various formats."""
    
    def format_json(self, data: dict) -> str:
        """Format as JSON."""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def format_markdown_bridge(self, source: str, target: str, bridges: List[Bridge]) -> str:
        """Format bridge analysis as Markdown."""
        lines = [
            "# Cross-Disciplinary Bridge Analysis",
            "",
            f"## {source.title()} ↔ {target.title()}",
            "",
            f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Bridges Found:** {len(bridges)}",
            "",
            "---",
            ""
        ]
        
        if not bridges:
            lines.append("*No significant bridges found. Try adjusting depth or domains.*")
            return "\n".join(lines)
        
        for i, bridge in enumerate(bridges, 1):
            lines.extend(self._format_single_bridge(bridge, i))
        
        # Summary
        avg_novelty = sum(b.novelty_score for b in bridges) / len(bridges)
        avg_feasibility = sum(b.feasibility_score for b in bridges) / len(bridges)
        
        lines.extend([
            "## Summary",
            "",
            f"- **Total Bridges:** {len(bridges)}",
            f"- **Average Novelty:** {avg_novelty:.2f}",
            f"- **Average Feasibility:** {avg_feasibility:.2f}",
            f"- **Top Bridge:** {bridges[0].id if bridges else 'N/A'}",
            ""
        ])
        
        return "\n".join(lines)
    
    def _format_single_bridge(self, bridge: Bridge, index: int) -> List[str]:
        """Format a single bridge."""
        score_emoji = "🔥" if bridge.bridge_score > 0.8 else "🔗" if bridge.bridge_score > 0.6 else "💡"
        
        lines = [
            f"### {score_emoji} Bridge #{index}: {bridge.id}",
            "",
            f"**Bridge Score:** {bridge.bridge_score:.3f}",
            f"**Novelty:** {bridge.novelty_score:.3f} | **Feasibility:** {bridge.feasibility_score:.3f}",
            "",
            "**Conceptual Path:**",
            " → ".join([p.title() for p in bridge.path]),
            ""
        ]
        
        if bridge.analogies:
            lines.extend(["**Key Analogies:**", ""])
            for analogy in bridge.analogies[:3]:
                lines.append(f"- *{analogy.source_concept}* ↔ *{analogy.target_concept}*: {analogy.analogy_description}")
            lines.append("")
        
        if bridge.innovation_opportunities:
            lines.extend(["**💡 Innovation Opportunities:**", ""])
            for opp in bridge.innovation_opportunities[:2]:
                lines.extend([
                    f"**{opp['title']}**",
                    f"- Impact: {opp['potential_impact'].title()}",
                    f"- Timeline: {opp['timeline']}",
                    f"- Description: {opp['description']}",
                    ""
                ])
        
        lines.append("---")
        lines.append("")
        
        return lines
    
    def format_markdown_hypotheses(
        self,
        source: str,
        target: str,
        hypotheses: List[InnovationHypothesis]
    ) -> str:
        """Format hypotheses as Markdown."""
        lines = [
            "# Innovation Hypotheses",
            "",
            f"## {source.title()} × {target.title()}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Hypotheses:** {len(hypotheses)}",
            "",
            "---",
            ""
        ]
        
        for i, h in enumerate(hypotheses, 1):
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "speculative": "⚪"}.get(
                h.potential_impact, "⚪"
            )
            
            lines.extend([
                f"### {impact_emoji} Hypothesis #{i}: {h.title}",
                "",
                f"**Description:** {h.description}",
                "",
                f"**Rationale:** {h.rationale}",
                "",
                f"**Impact:** {h.potential_impact.title()} | **Timeline:** {h.timeline}",
                "",
                "**Required Expertise:**",
                "" + "\n".join(f"- {e}" for e in h.required_expertise) + "",
                "",
                "**Key Challenges:**",
                "" + "\n".join(f"- {c}" for c in h.key_challenges) + "",
                "",
                "---",
                ""
            ])
        
        return "\n".join(lines)
    
    def format_markdown_complete_graph(
        self,
        domains: List[str],
        bridges: List[Bridge]
    ) -> str:
        """Format complete graph analysis as Markdown."""
        lines = [
            "# Multi-Domain Bridge Analysis",
            "",
            f"**Domains:** {', '.join(d.title() for d in domains)}",
            f"**Total Bridges:** {len(bridges)}",
            f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "---",
            ""
        ]
        
        # Group bridges by source-target pair
        bridge_groups = {}
        for bridge in bridges:
            key = (bridge.source, bridge.target)
            if key not in bridge_groups:
                bridge_groups[key] = []
            bridge_groups[key].append(bridge)
        
        for (source, target), group_bridges in sorted(
            bridge_groups.items(),
            key=lambda x: max(b.bridge_score for b in x[1]),
            reverse=True
        ):
            best_bridge = max(group_bridges, key=lambda b: b.bridge_score)
            lines.extend([
                f"## {source.title()} ↔ {target.title()}",
                "",
                f"**Best Bridge Score:** {best_bridge.bridge_score:.3f}",
                f"**Path:** {' → '.join(p.title() for p in best_bridge.path)}",
                ""
            ])
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Disciplinary Bridge Finder - Discover connections between distant fields"
    )
    
    # Input parameters
    parser.add_argument(
        "--source",
        type=str,
        help="Source discipline/field"
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Target discipline/field"
    )
    parser.add_argument(
        "--domains",
        type=str,
        help="Comma-separated list of domains for complete-graph mode"
    )
    
    # Mode selection
    parser.add_argument(
        "--mode",
        choices=["bridge", "complete-graph", "hypothesis", "landscape"],
        default="bridge",
        help="Analysis mode"
    )
    
    # Analysis parameters
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        help="Maximum bridge path depth"
    )
    parser.add_argument(
        "--max-bridges",
        type=int,
        default=10,
        help="Maximum bridges to return"
    )
    parser.add_argument(
        "--n-hypotheses",
        type=int,
        default=5,
        help="Number of hypotheses to generate"
    )
    parser.add_argument(
        "--novelty-weight",
        type=float,
        default=0.5,
        help="Weight for novelty (0-1)"
    )
    
    # Output
    parser.add_argument(
        "--output",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format"
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save output to file"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == "bridge" and (not args.source or not args.target):
        parser.error("--source and --target required for bridge mode")
    
    if args.mode == "complete-graph" and not args.domains:
        parser.error("--domains required for complete-graph mode")
    
    print("🔬 Cross-Disciplinary Bridge Finder")
    print("-" * 40)
    
    # Initialize
    kg = KnowledgeGraph()
    config = DEFAULT_CONFIG.copy()
    config["novelty_weight"] = args.novelty_weight
    analyzer = BridgeAnalyzer(kg, config)
    formatter = OutputFormatter()
    
    # Execute based on mode
    if args.mode == "bridge":
        print(f"Finding bridges between '{args.source}' and '{args.target}'...")
        
        bridges = analyzer.discover_bridges(
            args.source,
            args.target,
            max_bridges=args.max_bridges,
            depth=args.depth
        )
        
        print(f"Found {len(bridges)} bridges")
        
        output_data = {
            "analysis_id": f"bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "source": args.source,
            "target": args.target,
            "mode": args.mode,
            "bridges": [b.to_dict() for b in bridges],
            "summary": {
                "total_bridges": len(bridges),
                "average_novelty": round(sum(b.novelty_score for b in bridges) / max(len(bridges), 1), 3),
                "average_feasibility": round(sum(b.feasibility_score for b in bridges) / max(len(bridges), 1), 3)
            }
        }
        
        if args.output == "json":
            output = formatter.format_json(output_data)
        else:
            output = formatter.format_markdown_bridge(args.source, args.target, bridges)
    
    elif args.mode == "hypothesis":
        print(f"Generating hypotheses for '{args.source}' × '{args.target}'...")
        
        hypotheses = analyzer.generate_hypotheses(
            args.source,
            args.target,
            n_hypotheses=args.n_hypotheses
        )
        
        print(f"Generated {len(hypotheses)} hypotheses")
        
        output_data = {
            "analysis_id": f"hypothesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "source": args.source,
            "target": args.target,
            "mode": args.mode,
            "hypotheses": [h.to_dict() for h in hypotheses]
        }
        
        if args.output == "json":
            output = formatter.format_json(output_data)
        else:
            output = formatter.format_markdown_hypotheses(
                args.source, args.target, hypotheses
            )
    
    elif args.mode == "complete-graph":
        domains = [d.strip() for d in args.domains.split(",")]
        print(f"Analyzing bridges between {len(domains)} domains...")
        
        all_bridges = []
        for i, source in enumerate(domains):
            for target in domains[i+1:]:
                bridges = analyzer.discover_bridges(
                    source, target,
                    max_bridges=3,
                    depth=args.depth
                )
                all_bridges.extend(bridges)
        
        all_bridges.sort(key=lambda b: b.bridge_score, reverse=True)
        all_bridges = all_bridges[:args.max_bridges]
        
        print(f"Found {len(all_bridges)} bridges across all domain pairs")
        
        output_data = {
            "analysis_id": f"complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "domains": domains,
            "mode": args.mode,
            "bridges": [b.to_dict() for b in all_bridges],
            "summary": {
                "total_bridges": len(all_bridges),
                "domain_pairs": len(domains) * (len(domains) - 1) // 2
            }
        }
        
        if args.output == "json":
            output = formatter.format_json(output_data)
        else:
            output = formatter.format_markdown_complete_graph(domains, all_bridges)
    
    else:  # landscape mode
        print(f"Mapping landscape around '{args.source}'...")
        
        # Find all domains within radius
        neighbors = kg.get_neighbors(args.source)
        all_bridges = []
        
        for neighbor in neighbors:
            bridges = analyzer.discover_bridges(
                args.source, neighbor,
                max_bridges=2,
                depth=2
            )
            all_bridges.extend(bridges)
        
        print(f"Found {len(all_bridges)} connections in local landscape")
        
        output_data = {
            "analysis_id": f"landscape_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "center_domain": args.source,
            "mode": args.mode,
            "neighboring_domains": neighbors,
            "bridges": [b.to_dict() for b in all_bridges]
        }
        
        if args.output == "json":
            output = formatter.format_json(output_data)
        else:
            output = formatter.format_markdown_complete_graph(
                [args.source] + neighbors, all_bridges
            )
    
    # Output
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nOutput saved to: {args.save}")
    else:
        print("\n" + "=" * 60)
        print(output)
    
    print(f"\n{'=' * 60}")
    print("Analysis complete!")


if __name__ == "__main__":
    main()
