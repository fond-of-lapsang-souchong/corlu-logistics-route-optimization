import os
import sys
import pytest
from unittest.mock import MagicMock

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.optimization import ACOptimizer
from src.utils import DistanceCache 
from tests.helpers import create_mock_graph

@pytest.fixture
def mock_distance_provider(mocker):
    """
    OSRMDistanceProvider'ı mock'lar ve her get_distance çağrısına
    sabit bir değer döndürmesini sağlar.
    """
    mock_provider_instance = MagicMock()
    mock_provider_instance.get_distance.return_value = 10.0
    mocker.patch('src.optimization.optimizer.OSRMDistanceProvider', return_value=mock_provider_instance)

@pytest.mark.parametrize("strategy", ["eas", "mmas"])
def test_optimizer_initialization(mock_distance_provider, strategy):
    """
    ACOptimizer'ın farklı stratejiler için doğru başlatıldığını test eder.
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
        osrm_host="mock_host",
        aco_strategy=strategy,
        alpha=1.0, 
        beta=2.0, 
        evaporation_rate=0.5
    )
    
    assert optimizer.strategy == strategy
    assert len(optimizer.ants) == len(vehicle_fleet)

@pytest.mark.parametrize("strategy", ["eas", "mmas"])
def test_optimizer_run_produces_valid_solution(mock_distance_provider, strategy):
    """
    Optimizer'ın tam bir çalıştırmasının geçerli bir çözüm ürettiğini test eder.
    """
    mock_graph = create_mock_graph()
    nodes_info = {1: 0, 2: 10, 4: 10} 
    start_node = 1
    vehicle_fleet = [25] 

    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_info=nodes_info,
        start_node=start_node,
        vehicle_fleet=vehicle_fleet,
        osrm_host="mock_host",
        aco_strategy=strategy,
        alpha=1.0,
        beta=2.0,
        evaporation_rate=0.5
    )
    
    best_solution, best_cost, cost_history = optimizer.run(iterations=10)

    assert best_solution is not None
    assert best_cost != float('inf')
    assert cost_history is not None
    assert len(cost_history) == 10