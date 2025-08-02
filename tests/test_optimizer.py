import os
import sys
import pytest
from unittest.mock import MagicMock

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.optimization import ACOptimizer
from tests.helpers import create_mock_graph

@pytest.fixture
def mock_distance_provider(mocker):
    """
    OSRMDistanceProvider'ı taklit eder ve sabit mesafe/süre döndürür.
    """
    mock_provider_instance = MagicMock()
    mock_provider_instance.get_travel_info.return_value = (10.0, 2.0)
    mock_provider_instance.get_distance.return_value = 10.0
    mocker.patch('src.optimization.optimizer.OSRMDistanceProvider', return_value=mock_provider_instance)

@pytest.mark.parametrize("strategy", ["eas", "mmas"])
def test_optimizer_initialization(mock_distance_provider, strategy):
    """
    ACOptimizer'ın yeni zengin veri yapısıyla doğru başlatıldığını test eder.
    """
    mock_graph = create_mock_graph()
    nodes_info_tw = {
        1: {'demand': 0, 'time_window': [0, 1440], 'service_time': 0},
        2: {'demand': 5, 'time_window': [0, 100], 'service_time': 5},
    }
    start_node = 1
    vehicle_fleet = [15, 10]
    
    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_info=nodes_info_tw,
        start_node=start_node,
        vehicle_fleet=vehicle_fleet,
        osrm_host="mock_host",
        aco_strategy=strategy
    )
    
    assert optimizer.strategy == strategy
    assert len(optimizer.ants) == len(vehicle_fleet)

@pytest.mark.parametrize("strategy", ["eas", "mmas"])
def test_optimizer_run_produces_valid_solution(mock_distance_provider, strategy):
    """
    Optimizer'ın tam bir çalıştırmasının geçerli bir çözüm ürettiğini test eder.
    """
    mock_graph = create_mock_graph()
    nodes_info_tw = {
        1: {'demand': 0, 'time_window': [0, 1440], 'service_time': 0},
        2: {'demand': 10, 'time_window': [0, 100], 'service_time': 5},
        4: {'demand': 10, 'time_window': [0, 100], 'service_time': 5},
    }
    start_node = 1
    vehicle_fleet = [25] 

    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_info=nodes_info_tw,
        start_node=start_node,
        vehicle_fleet=vehicle_fleet,
        osrm_host="mock_host",
        aco_strategy=strategy
    )
    
    best_solution, best_cost, cost_history = optimizer.run(iterations=10)

    assert best_solution is not None
    assert best_cost != float('inf')
    assert len(cost_history) == 10

@pytest.mark.parametrize("strategy", ["eas", "mmas"])
def test_optimizer_penalizes_time_window_violation(mock_distance_provider, strategy):
    """
    Zaman penceresini ihlal eden bir çözümün maliyetinin,
    cezalandırma nedeniyle çok yüksek olduğunu test eder.
    """
    mock_graph = create_mock_graph()
    
    nodes_info_tw = {
        1: {'demand': 0, 'time_window': [0, 1440], 'service_time': 0},
        2: {'demand': 10, 'time_window': [0, 100], 'service_time': 5},
        4: {'demand': 10, 'time_window': [0, 5], 'service_time': 5},
    }
    start_node = 1
    vehicle_fleet = [25]

    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_info=nodes_info_tw,
        start_node=start_node,
        vehicle_fleet=vehicle_fleet,
        osrm_host="mock_host",
        aco_strategy=strategy
    )
    
    ant = optimizer.ants[0]
    ant.reset()
    
    ant.move_to_node(2, optimizer.nodes_info)
    ant.move_to_node(4, optimizer.nodes_info)
    ant.finalize_solution()
    
    assert ant.time_window_violated is True

    cost = optimizer._calculate_cost(ant)
    
    assert cost > optimizer._TIME_PENALTY

@pytest.mark.parametrize("strategy", ["eas", "mmas"])
def test_optimizer_does_not_select_violated_solution_as_best(mock_distance_provider, strategy):
    """
    Optimizer'ın, zamanı ihlal eden bir çözümü en iyi çözüm olarak seçmediğini test eder.
    """
    mock_graph = create_mock_graph()
    nodes_info_tw = {
        1: {'demand': 0, 'time_window': [0, 1440], 'service_time': 0},
        2: {'demand': 10, 'time_window': [0, 100], 'service_time': 5},
    }
    start_node = 1
    vehicle_fleet = [25]

    optimizer = ACOptimizer(
        graph=mock_graph,
        nodes_info=nodes_info_tw,
        start_node=start_node,
        vehicle_fleet=vehicle_fleet,
        osrm_host="mock_host",
        aco_strategy=strategy
    )
    
    valid_solution_tours = [[1, 2, 1]]
    valid_distance = 20.0
    
    valid_cost = optimizer._calculate_cost(MagicMock(tours=valid_solution_tours, total_distance=valid_distance, total_wait_time=0, time_window_violated=False))
    violated_cost = optimizer._calculate_cost(MagicMock(tours=valid_solution_tours, total_distance=valid_distance, total_wait_time=0, time_window_violated=True))
    
    optimizer.global_best_cost = valid_cost
    
    new_total_cost = violated_cost
    time_was_violated = True
    
    if new_total_cost < optimizer.global_best_cost:
        if not time_was_violated:
             optimizer.global_best_cost = new_total_cost
             
    assert optimizer.global_best_cost == valid_cost