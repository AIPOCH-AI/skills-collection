#!/usr/bin/env python3
"""
Upset Plot Converter
Convert complex Venn diagrams (>4 sets) to clearer Upset Plots.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Set, Optional, Tuple


def _compute_intersections(sets: Dict[str, Set]) -> Dict[frozenset, Set]:
    """Compute all possible intersections between sets."""
    set_names = list(sets.keys())
    all_elements = set()
    for s in sets.values():
        all_elements.update(s)
    
    intersections = defaultdict(set)
    
    for elem in all_elements:
        # Find which sets contain this element
        containing_sets = frozenset(name for name, s in sets.items() if elem in s)
        if containing_sets:  # Only if element is in at least one set
            intersections[containing_sets].add(elem)
    
    return intersections


def _prepare_upset_data(
    intersections: Dict[frozenset, Set],
    set_names: List[str],
    min_subset_size: int = 1,
    max_intersections: int = 30
) -> Tuple[List[frozenset], List[int], np.ndarray]:
    """Prepare data for upset plot rendering."""
    # Filter by minimum subset size
    filtered = {k: v for k, v in intersections.items() if len(v) >= min_subset_size}
    
    # Sort by size (descending) and take top N
    sorted_items = sorted(filtered.items(), key=lambda x: len(x[1]), reverse=True)
    sorted_items = sorted_items[:max_intersections]
    
    if not sorted_items:
        return [], [], np.array([])
    
    intersection_sets = [item[0] for item in sorted_items]
    sizes = [len(item[1]) for item in sorted_items]
    
    # Create membership matrix
    n_sets = len(set_names)
    n_intersections = len(intersection_sets)
    membership = np.zeros((n_intersections, n_sets), dtype=int)
    
    for i, inter_set in enumerate(intersection_sets):
        for j, name in enumerate(set_names):
            if name in inter_set:
                membership[i, j] = 1
    
    return intersection_sets, sizes, membership


def _plot_upset(
    set_names: List[str],
    intersection_sets: List[frozenset],
    sizes: List[int],
    membership: np.ndarray,
    output_path: str,
    title: Optional[str] = None
) -> None:
    """Create the upset plot visualization."""
    n_sets = len(set_names)
    n_intersections = len(intersection_sets)
    
    if n_intersections == 0:
        print("No intersections to plot.")
        return
    
    # Figure dimensions
    bar_height = 0.6
    matrix_height = 0.4
    set_label_width = 0.15
    
    fig_width = max(10, n_intersections * 0.5 + 3)
    fig_height = max(6, n_sets * 0.5 + 2)
    
    fig = plt.figure(figsize=(fig_width, fig_height))
    gs = fig.add_gridspec(2, 2, 
                          width_ratios=[set_label_width, 1 - set_label_width],
                          height_ratios=[0.6, 0.4],
                          wspace=0.05, hspace=0.1)
    
    # Bar chart (top right)
    ax_bars = fig.add_subplot(gs[0, 1])
    ax_bars.bar(range(n_intersections), sizes, color='#4CAF50', edgecolor='black', linewidth=0.5)
    ax_bars.set_xticks(range(n_intersections))
    ax_bars.set_xticklabels([])
    ax_bars.set_ylabel('Intersection Size', fontsize=10)
    ax_bars.set_xlim(-0.5, n_intersections - 0.5)
    
    # Add value labels on bars
    for i, (size, inter_set) in enumerate(zip(sizes, intersection_sets)):
        ax_bars.text(i, size + max(sizes) * 0.02, str(size), 
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Set labels (bottom left)
    ax_set_labels = fig.add_subplot(gs[1, 0])
    ax_set_labels.set_xlim(0, 1)
    ax_set_labels.set_ylim(-0.5, n_sets - 0.5)
    for i, name in enumerate(reversed(set_names)):
        ax_set_labels.text(0.9, i, name, ha='right', va='center', fontsize=9)
    ax_set_labels.axis('off')
    
    # Matrix (bottom right)
    ax_matrix = fig.add_subplot(gs[1, 1])
    ax_matrix.set_xlim(-0.5, n_intersections - 0.5)
    ax_matrix.set_ylim(-0.5, n_sets - 0.5)
    
    # Draw grid lines
    for i in range(n_sets):
        ax_matrix.axhline(i - 0.5, color='gray', linewidth=0.5, alpha=0.3)
    for i in range(n_intersections + 1):
        ax_matrix.axvline(i - 0.5, color='gray', linewidth=0.5, alpha=0.3)
    
    # Draw dots and connecting lines
    colors = plt.cm.tab10(np.linspace(0, 1, n_sets))
    
    for col in range(n_intersections):
        active_rows = []
        for row in range(n_sets):
            if membership[col, row] == 1:
                # Draw circle
                circle = plt.Circle((col, n_sets - 1 - row), 0.15, 
                                   color=colors[row], ec='black', linewidth=1)
                ax_matrix.add_patch(circle)
                active_rows.append(n_sets - 1 - row)
        
        # Draw connecting line if multiple sets in intersection
        if len(active_rows) > 1:
            min_y, max_y = min(active_rows), max(active_rows)
            ax_matrix.plot([col, col], [min_y, max_y], 'k-', linewidth=2)
    
    ax_matrix.set_xticks(range(n_intersections))
    ax_matrix.set_xticklabels([])
    ax_matrix.set_yticks(range(n_sets))
    ax_matrix.set_yticklabels([])
    ax_matrix.set_aspect('equal')
    
    # Set total sizes on the left
    ax_totals = fig.add_subplot(gs[0, 0])
    ax_totals.set_xlim(0, 1)
    ax_totals.set_ylim(-0.5, n_sets - 0.5)
    
    # Hide the totals subplot (not needed for upset plot style)
    ax_totals.axis('off')
    
    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Upset plot saved to: {output_path}")


def convert_venn_to_upset(
    sets: Dict[str, Set],
    output_path: str = "upset_plot.png",
    title: Optional[str] = None,
    min_subset_size: int = 1,
    max_intersections: int = 30
) -> None:
    """
    Convert a dictionary of sets to an Upset Plot.
    
    Args:
        sets: Dictionary mapping set names to sets of elements
        output_path: Path to save the output figure
        title: Optional title for the plot
        min_subset_size: Minimum subset size to display
        max_intersections: Maximum number of intersections to show
    """
    if len(sets) <= 4:
        print(f"Warning: Only {len(sets)} sets provided. Venn diagrams work well for ≤4 sets.")
        print("Upset plot will still be generated for comparison.")
    
    if len(sets) > 10:
        print(f"Warning: {len(sets)} sets may produce a very large plot.")
    
    set_names = list(sets.keys())
    
    # Convert all values to sets
    sets_converted = {name: set(s) for name, s in sets.items()}
    
    # Compute intersections
    intersections = _compute_intersections(sets_converted)
    
    # Prepare data
    intersection_sets, sizes, membership = _prepare_upset_data(
        intersections, set_names, min_subset_size, max_intersections
    )
    
    # Generate plot
    _plot_upset(set_names, intersection_sets, sizes, membership, output_path, title)


def upset_from_lists(
    set_names: List[str],
    lists: List[List],
    output_path: str = "upset_plot.png",
    title: Optional[str] = None,
    min_subset_size: int = 1,
    max_intersections: int = 30
) -> None:
    """
    Create an Upset Plot from lists of elements.
    
    Args:
        set_names: List of names for each set
        lists: List of lists, each containing elements of a set
        output_path: Path to save the output figure
        title: Optional title for the plot
        min_subset_size: Minimum subset size to display
        max_intersections: Maximum number of intersections to show
    """
    if len(set_names) != len(lists):
        raise ValueError("set_names and lists must have the same length")
    
    sets = {name: set(lst) for name, lst in zip(set_names, lists)}
    
    convert_venn_to_upset(
        sets, output_path, title, min_subset_size, max_intersections
    )


def print_intersection_stats(sets: Dict[str, Set]) -> None:
    """Print statistics about set intersections."""
    intersections = _compute_intersections(sets)
    
    print("\n=== Set Intersection Statistics ===")
    print(f"Total unique elements: {len(set().union(*sets.values()))}")
    print(f"Number of sets: {len(sets)}")
    print(f"Number of unique intersections: {len(intersections)}")
    print("\nIntersections (sorted by size):")
    
    sorted_items = sorted(intersections.items(), key=lambda x: len(x[1]), reverse=True)
    
    for inter_set, elements in sorted_items:
        if len(inter_set) == 0:
            continue
        set_names = ', '.join(sorted(inter_set))
        print(f"  {set_names}: {len(elements)} elements")


# Example usage
if __name__ == "__main__":
    # Example with 5 sets
    sets = {
        'A': {1, 2, 3, 4, 5, 20, 21},
        'B': {4, 5, 6, 7, 8, 20, 22},
        'C': {3, 5, 7, 9, 10, 21, 22},
        'D': {2, 4, 6, 8, 10, 20, 23},
        'E': {1, 3, 5, 7, 9, 21, 23}
    }
    
    print_intersection_stats(sets)
    convert_venn_to_upset(sets, output_path="upset_plot.png", title="Example Upset Plot")
