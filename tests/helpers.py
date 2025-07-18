import networkx as nx

def create_mock_graph():
    """
    Creates a small, predictable graph for testing purposes.
    
    The graph structure is a simple square with a diagonal:
    A --10-- B
    | \\     |
    10  14  10
    |     \\ |
    C --10-- D
    """
    G = nx.Graph() 
    
    nodes = [1, 2, 3, 4]
    G.add_nodes_from(nodes)
    
    edges = [
        (1, 2, {'length': 10}),  # A -> B
        (1, 3, {'length': 10}),  # A -> C
        (1, 4, {'length': 14}),  # A -> D (diagonal)
        (2, 4, {'length': 10}),  # B -> D
        (3, 4, {'length': 10}),  # C -> D
    ]
    G.add_edges_from(edges)
    
    return G