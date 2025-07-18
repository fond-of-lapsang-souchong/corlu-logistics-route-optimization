import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.optimization import ACOptimizer
from tests.helpers import create_mock_graph

def test_optimizer_initialization():
    """
    Tests if the ACOptimizer class initializes correctly with the given parameters.
    """
    mock_graph = create_mock_graph()
    nodes = list(mock_graph.nodes())
    
    ANT_COUNT = 15
    ALPHA = 1.5
    BETA = 5.5
    EVAP_RATE = 0.55
    
    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_to_visit=nodes,
        start_node=nodes[0],
        ant_count=ANT_COUNT,
        alpha=ALPHA,
        beta=BETA,
        evaporation_rate=EVAP_RATE
    )
    
    assert optimizer.ant_count == ANT_COUNT
    assert optimizer.alpha == ALPHA
    assert optimizer.beta == BETA
    assert optimizer.evaporation_rate == EVAP_RATE
    assert optimizer.start_node == nodes[0]
    
    assert len(optimizer.ants) == ANT_COUNT
    
    assert len(optimizer.pheromones) > 0