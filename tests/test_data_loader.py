import os
import sys
import pytest
import networkx as nx

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.data_loader import load_graph

TEST_PLACE_NAME = "Piedmont, California, USA"

@pytest.mark.slow
def test_load_graph_success():
    """
    Tests that load_graph successfully returns a NetworkX graph for a valid place.
    """
    G = load_graph(TEST_PLACE_NAME, verbose=False)
    
    assert isinstance(G, nx.Graph)
    
    assert len(G.nodes) > 0
    assert len(G.edges) > 0

@pytest.mark.slow
def test_load_graph_undirected_flag():
    """
    Tests the 'undirected' flag functionality.
    """
    G_undirected = load_graph(TEST_PLACE_NAME, undirected=True, verbose=False)
    assert not G_undirected.is_directed()
    
    G_directed = load_graph(TEST_PLACE_NAME, undirected=False, verbose=False)
    assert G_directed.is_directed()

def test_load_graph_invalid_place():
    """
    Tests that load_graph returns None for an invalid or nonexistent place name.
    """
    invalid_place = "Atlantis, The Lost City"
    G = load_graph(invalid_place, verbose=False)
    
    assert G is None

def test_load_graph_network_error(mocker):
    """
    Tests how load_graph handles a network error by mocking the ox.graph_from_place call.
    """
    # ox.graph_from_place fonksiyonunu, sanki bir internet hatası olmuş gibi
    # bir Exception fırlatacak şekilde "taklit et".
    mocker.patch('osmnx.graph_from_place', side_effect=Exception("Network error"))
    
    G = load_graph(TEST_PLACE_NAME, verbose=False)
    
    assert G is None