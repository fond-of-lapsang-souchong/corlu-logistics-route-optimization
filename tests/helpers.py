import networkx as nx

def create_mock_graph():
    """
    Creates a small, predictable graph for testing purposes.
    The graph is now a MultiGraph to be fully compatible with OSMnx functions,
    and it includes node coordinates and a graph-level CRS attribute.
    """
    G = nx.MultiGraph() 
    
    G.graph['crs'] = 'epsg:4326'
    
    nodes_with_data = [
        (1, {'y': 41.0, 'x': 28.0}),  # Düğüm A
        (2, {'y': 41.0, 'x': 28.1}),  # Düğüm B
        (3, {'y': 41.1, 'x': 28.0}),  # Düğüm C
        (4, {'y': 41.1, 'x': 28.1})   # Düğüm D
    ]
    G.add_nodes_from(nodes_with_data)
    
    edges = [
        (1, 2, 0, {'length': 10}),  # A -> B
        (1, 3, 0, {'length': 10}),  # A -> C
        (1, 4, 0, {'length': 14}),  # A -> D
        (2, 4, 0, {'length': 10}),  # B -> D
        (3, 4, 0, {'length': 10}),  # C -> D
    ]
    G.add_edges_from(edges)
    
    return G