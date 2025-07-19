import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.optimization.ant import Ant
from src.utils import DistanceCache
from tests.helpers import create_mock_graph

@pytest.fixture
def vrp_ant_setup():
    mock_graph = create_mock_graph()
    cache = DistanceCache(mock_graph, cache_filepath="tests/temp_cache_ant.json")
    ant = Ant(mock_graph, start_node=1, capacity=15, distance_cache=cache)
    nodes_info = {1: 0, 2: 8, 3: 10, 4: 6}
    yield ant, nodes_info
    if os.path.exists("tests/temp_cache_ant.json"):
        os.remove("tests/temp_cache_ant.json")

def test_ant_selects_visitable_node(vrp_ant_setup):
    ant, nodes_info = vrp_ant_setup
    ant.current_load = 5
    unvisited = {2, 3, 4}
    next_node = ant._select_next_node({}, {n: nodes_info[n] for n in unvisited}, 1.0, 2.0)
    assert next_node in [2, 4]

def test_ant_returns_to_depot_when_full(vrp_ant_setup):
    ant, nodes_info = vrp_ant_setup
    ant.current_load = 10
    unvisited = {2, 3, 4}
    next_node = ant._select_next_node({}, {n: nodes_info[n] for n in unvisited}, 1.0, 2.0)
    assert next_node == ant.start_node

def test_ant_move_to_node_updates_state(vrp_ant_setup):
    ant, nodes_info = vrp_ant_setup
    ant.move_to_node(2, nodes_info)
    assert ant.current_load == 8
    assert ant.current_tour == [1, 2]
    assert ant.total_distance == 10

def test_ant_move_to_depot_finalizes_tour(vrp_ant_setup):
    ant, nodes_info = vrp_ant_setup
    ant.current_tour = [1, 2, 4]
    ant.move_to_node(1, nodes_info)
    assert ant.current_load == 0
    assert ant.current_tour == [1]
    assert ant.tours == [[1, 2, 4, 1]]