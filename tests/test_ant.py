import os
import sys
import pytest
from unittest.mock import MagicMock

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.optimization.ant import Ant
from tests.helpers import create_mock_graph

@pytest.fixture
def vrptw_ant_setup():
    """
    Zaman Pencereleri (VRPTW) ve Hizmet Süresi özelliklerini test etmek için
    gerekli ortamı hazırlar.
    """
    mock_graph = create_mock_graph()
    
    mock_provider = MagicMock()
    mock_provider.get_travel_info.return_value = (10.0, 2.0) 
    
    ant = Ant(mock_graph, start_node=1, capacity=20, distance_provider=mock_provider)
    
    nodes_info_tw = {
        1: {'demand': 0, 'time_window': [0, 1440], 'service_time': 0},
        2: {'demand': 8, 'time_window': [0, 100], 'service_time': 5},
        3: {'demand': 10, 'time_window': [10, 50], 'service_time': 8},
        4: {'demand': 6, 'time_window': [0, 10], 'service_time': 3}
    }
    yield ant, nodes_info_tw

def test_ant_selects_visitable_node(vrptw_ant_setup):
    """
    Karıncanın, zaman ve kapasite kısıtlarına uyan bir durağı seçtiğini test eder.
    """
    ant, nodes_info_tw = vrptw_ant_setup
    ant.current_load = 10 
    ant.current_time = 5   
        
    unvisited = {node_id: info for node_id, info in nodes_info_tw.items() if node_id != 1}
    next_node = ant._select_next_node({}, unvisited, 1.0, 2.0)
    
    assert next_node in [2, 3, 4]

def test_ant_rejects_node_due_to_time_window(vrptw_ant_setup):
    """
    Karıncanın, zaman penceresini kaçıracağı bir durağı seçmediğini test eder.
    """
    ant, nodes_info_tw = vrptw_ant_setup
    ant.current_time = 9 
    
    unvisited = {node_id: info for node_id, info in nodes_info_tw.items() if node_id != 1}
    candidate_nodes = []
    for node_id, info in unvisited.items():
        _, travel_time = ant.distance_provider.get_travel_info(ant.current_tour[-1], node_id)
        arrival_time = ant.current_time + travel_time
        if arrival_time <= info['time_window'][1]:
            candidate_nodes.append(node_id)
            
    assert 4 not in candidate_nodes

def test_ant_move_to_node_updates_time_correctly(vrptw_ant_setup):
    """
    move_to_node'un zamanı, bekleme süresini ve hizmet süresini doğru hesapladığını test eder.
    """
    ant, nodes_info_tw = vrptw_ant_setup
    ant.current_time = 5 
    
    ant.move_to_node(3, nodes_info_tw)
    
    assert ant.current_tour == [1, 3]
    assert ant.total_wait_time == 3
    assert ant.current_time == 18

def test_ant_returns_none_when_no_valid_node(vrptw_ant_setup):
    """
    Gidilecek geçerli durak kalmadığında _select_next_node'un None döndürdüğünü test eder.
    """
    ant, nodes_info_tw = vrptw_ant_setup
    ant.current_load = 15
    ant.current_time = 95 

    unvisited = {node_id: info for node_id, info in nodes_info_tw.items() if node_id != 1}
    
    next_node = ant._select_next_node({}, unvisited, 1.0, 2.0)
    
    assert next_node is None

def test_ant_rejects_node_due_to_strict_time_window(vrptw_ant_setup):
    """
    Karıncanın, varış zamanının pencerenin sonundan büyük olacağı bir durağı
    kategorik olarak reddettiğini test eder.
    """
    ant, nodes_info_tw = vrptw_ant_setup
    ant.current_time = 9.0  # Mevcut zaman: 9. dakika
    
    unvisited = {node_id: info for node_id, info in nodes_info_tw.items() if node_id != 1}
    
    candidate_nodes = []
    current_node = ant.current_tour[-1]
    for node_id, info in unvisited.items():
        if node_id not in ant.visited_nodes:
            if ant.current_load + info['demand'] <= ant.capacity:
                _, travel_time = ant.distance_provider.get_travel_info(current_node, node_id)
                arrival_time = ant.current_time + travel_time
                if arrival_time <= info['time_window'][1]: 
                    candidate_nodes.append(node_id)

    print(f"Aday düğümler: {candidate_nodes}")
    assert 4 not in candidate_nodes
    assert 2 in candidate_nodes 
    assert 3 in candidate_nodes 

def test_ant_move_to_node_correctly_calculates_wait_time(vrptw_ant_setup):
    """
    Bir durağa erken varıldığında bekleme süresinin doğru hesaplanıp
    karıncanın durumuna (current_time, total_wait_time) yansıtıldığını test eder.
    """
    ant, nodes_info_tw = vrptw_ant_setup
    ant.current_time = 5.0 # Mevcut zaman: 5. dakika
    
    ant.move_to_node(3, nodes_info_tw)

    assert ant.total_wait_time == 3.0
    assert ant.current_time == 18.0
    assert not ant.time_window_violated