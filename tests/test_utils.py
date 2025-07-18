import os
import sys
import json
import pytest
import networkx as nx

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.utils import DistanceCache
from tests.helpers import create_mock_graph

@pytest.fixture
def cache_setup():
    """
    Bu bir pytest "fixture"ıdır. Her test fonksiyonundan önce çalışır,
    gerekli nesneleri hazırlar ve test bittikten sonra ortalığı temizler.
    Bu, testlerimizin birbirinden etkilenmemesini sağlar.
    """
    mock_graph = create_mock_graph()
    temp_cache_file = "tests/temp_cache.json"
    cache = DistanceCache(mock_graph, cache_filepath=temp_cache_file)
    
    yield cache, temp_cache_file
    
    if os.path.exists(temp_cache_file):
        os.remove(temp_cache_file)

def test_distance_cache_initialization(cache_setup):
    """Tests if the DistanceCache initializes correctly."""
    cache, _ = cache_setup
    assert len(cache.memory_cache) == 0

def test_get_distance_direct_path(cache_setup):
    """Tests getting a direct path distance."""
    cache, _ = cache_setup
    distance = cache.get_distance(1, 2)
    assert distance == 10
    assert (1, 2) in cache.memory_cache

def test_get_distance_indirect_path(cache_setup):
    """Tests getting an indirect path distance."""
    cache, _ = cache_setup
    distance = cache.get_distance(2, 3)
    assert distance == 20
    assert (2, 3) in cache.memory_cache

def test_save_and_load_from_disk(cache_setup):
    """
    Tests the core functionality of saving the cache to a file and loading it back.
    """
    cache, temp_cache_file = cache_setup
    
    cache.get_distance(1, 2)  # Değer: 10
    cache.get_distance(2, 3)  # Değer: 20
    
    cache.save_to_disk()
    
    assert os.path.exists(temp_cache_file)
    
    new_cache = DistanceCache(cache.graph, cache_filepath=temp_cache_file)
    
    assert len(new_cache.memory_cache) == 2
    assert new_cache.get_distance(1, 2) == 10
    assert new_cache.get_distance(2, 3) == 20

def test_cache_hit_avoids_recalculation(mocker, cache_setup):
    """
    Tests that once a distance is cached, the expensive nx.shortest_path_length
    is NOT called again for the same pair of nodes.
    """
    cache, _ = cache_setup
    
    spy = mocker.spy(nx, 'shortest_path_length')
    
    distance1 = cache.get_distance(1, 4)
    assert distance1 == 14
    spy.assert_called_once_with(cache.graph, 1, 4, weight='length')
    
    distance2 = cache.get_distance(1, 4)
    assert distance2 == 14
    
    spy.assert_called_once()

def test_nonexistent_path_is_cached_as_inf(cache_setup):
    """
    Tests that if no path exists between two nodes, it is correctly
    cached as infinity.
    """
    cache, _ = cache_setup
    
    cache.graph.add_node(99)
    
    distance = cache.get_distance(1, 99)
    
    assert distance == float('inf')
    
    assert (1, 99) in cache.memory_cache
    assert cache.memory_cache[(1, 99)] == float('inf')

def test_cache_key_order_invariance(cache_setup):
    """
    Tests that the cache treats (u, v) and (v, u) as the same key.
    """
    cache, _ = cache_setup
    
    distance1 = cache.get_distance(1, 2)
    
    distance2 = cache.get_distance(2, 1)
    
    assert distance1 == distance2
    
    assert len(cache.memory_cache) == 1
    assert (1, 2) in cache.memory_cache
    assert (2, 1) not in cache.memory_cache