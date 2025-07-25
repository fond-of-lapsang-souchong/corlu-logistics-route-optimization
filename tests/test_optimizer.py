import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.optimization import ACOptimizer
from src.utils import DistanceCache 
from tests.helpers import create_mock_graph

def test_vrp_optimizer_initialization(mocker):
    """
    Tests if the VRP-enabled ACOptimizer initializes correctly.
    """
    mocker.patch('src.optimization.optimizer.OSRMDistanceProvider', DistanceCache)

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
    assert isinstance(optimizer.distance_cache, DistanceCache)

def test_optimizer_run_produces_valid_solution(mocker):
    """
    Tests that a full run of the optimizer returns a solution
    with the expected structure and a valid cost.
    """
    mocker.patch('src.optimization.optimizer.OSRMDistanceProvider', DistanceCache)
    
    mock_graph = create_mock_graph()
    nodes_info = {1: 0, 2: 10, 4: 10} 
    start_node = 1
    vehicle_fleet = [25] 

    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_info=nodes_info,
        start_node=start_node,
        vehicle_fleet=vehicle_fleet,
        alpha=1.0,
        beta=2.0,
        evaporation_rate=0.5
    )

    best_solution, best_cost = optimizer.run(iterations=10)

    assert best_solution is not None
    assert best_cost != float('inf')
    assert best_cost > 0
    assert isinstance(best_solution, list)
    
    if best_solution:
        assert len(best_solution) >= 1
        first_tour = best_solution[0]
        assert isinstance(first_tour, list)
        assert first_tour[0] == start_node
        assert first_tour[-1] == start_node
        assert set(nodes_info.keys()) - {start_node} == set(first_tour) - {start_node}