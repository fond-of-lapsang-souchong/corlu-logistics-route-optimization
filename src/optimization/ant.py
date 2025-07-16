import random
import networkx as nx
from typing import List, Dict, Set

from ..utils import DistanceCache

Graph = nx.MultiDiGraph

class Ant:
    """
    Represents a single ant that uses a DistanceCache to make decisions
    and calculate path distances efficiently.
    """
    def __init__(self, graph: Graph, start_node: int, distance_cache: DistanceCache):
        """
        Initializes an Ant with a reference to the shared distance cache.
        """
        self.graph = graph
        self.start_node = start_node
        self.distance_cache = distance_cache
        
        self.path: List[int] = []
        self.path_distance: float = 0.0
        self.visited: Set[int] = set()
        self.reset()

    def reset(self) -> None:
        """Resets the ant to its starting state."""
        self.path = [self.start_node]
        self.path_distance = 0.0
        self.visited = {self.start_node}

    def _select_next_node(self, pheromones: Dict, nodes_to_visit: Set[int], alpha: float, beta: float) -> int:
        """
        Selects the next node to visit using the pre-computed or cached distances.
        """
        current_node = self.path[-1]
        candidate_nodes = list(nodes_to_visit - self.visited)

        if not candidate_nodes:
            return self.start_node

        probabilities = []
        for next_node in candidate_nodes:
            edge = tuple(sorted((current_node, next_node)))
            pheromone = pheromones.get(edge, 1.0)
            
            distance = self.distance_cache.get_distance(current_node, next_node)

            heuristic = 1.0 / (distance + 1e-10) 
            probabilities.append((pheromone ** alpha) * (heuristic ** beta))

        total_prob = sum(probabilities)
        if total_prob == 0:
            return random.choice(candidate_nodes)
            
        normalized_probs = [p / total_prob for p in probabilities]
        return random.choices(candidate_nodes, weights=normalized_probs, k=1)[0]

    def _update_path(self, next_node: int) -> None:
        """
        Updates the ant's path using the pre-computed or cached distances.
        """
        last_node = self.path[-1]
        self.path.append(next_node)
        self.visited.add(next_node)

        distance = self.distance_cache.get_distance(last_node, next_node)
        
        if self.path_distance == float('inf') or distance == float('inf'):
            self.path_distance = float('inf')
        else:
            self.path_distance += distance