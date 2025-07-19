import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.optimization import ACOptimizer
from tests.helpers import create_mock_graph

def test_vrp_optimizer_initialization():
    """
    Tests if the VRP-enabled ACOptimizer initializes correctly.
    """
    mock_graph = create_mock_graph()
    nodes_info = {1: 0, 2: 5, 3: 7, 4: 8}
    start_node = 1
    vehicle_fleet = [15, 10]
    
    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_info=nodes_info,
        start_node=start_node,
        vehicle_fleet=vehicle_fleet,
        alpha=1.0, beta=2.0, evaporation_rate=0.5
    )
    
    assert len(optimizer.ants) == len(vehicle_fleet)
    assert optimizer.num_ants == 2
    assert optimizer.ants[0].capacity == 15
    assert optimizer.ants[1].capacity == 10
    assert optimizer.nodes_to_visit == {2, 3, 4}