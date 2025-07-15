import osmnx as ox
from typing import List

class Ant:
    """
    Represents a single ant in the Ant Colony Optimization algorithm.

    Each ant builds a path (tour) through the graph, node by node,
    making probabilistic decisions based on pheromone levels and heuristic
    information (distance).

    Attributes:
        graph (osmnx.graph): The graph on which the ant travels.
        start_node (int): The starting node for the ant's tour.
        path (List[int]): The sequence of nodes visited by the ant.
        path_distance (float): The total distance of the path traveled by the ant.
        visited (set[int]): A set of nodes visited by the ant to prevent cycles.
    """

    def __init__(self, graph: ox.graph, start_node: int):
        """
        Initializes an Ant.

        Args:
            graph (osmnx.graph): The graph on which the ant will travel.
            start_node (int): The starting node for the ant's tour.
        """
        self.graph = graph
        self.start_node = start_node
        self.path: List[int] = [start_node]
        self.path_distance: float = 0.0
        self.visited: set[int] = {start_node}

    def _select_next_node(self) -> int:
        """
        Selects the next node to visit based on pheromone levels and distance.

        Returns:
            int: The next node to visit.
        """
        pass

    def _update_path(self, next_node: int) -> None:
        """
        Updates the ant's path with the next node.

        Args:
            next_node (int): The next node to add to the path.
        """
        self.path.append(next_node)
        self.visited.add(next_node)
        # Assuming the graph has 'length' attribute for edges
        edge_data = self.graph.get_edge_data(self.path[-2], self.path[-1])
        if edge_data and 'length' in edge_data[0]:
            self.path_distance += edge_data[0]['length']

    def get_path_distance(self) -> float:
        """
        Calculates the total distance of the ant's completed tour.

        Returns:
            float: The total distance of the tour.
        """
        return self.path_distance
