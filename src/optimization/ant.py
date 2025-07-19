import random
from typing import List, Dict, Set, Tuple

from ..utils import DistanceCache
import networkx as nx
Graph = nx.MultiDiGraph

class Ant:
    """
    Represents a single vehicle (or ant) in a Vehicle Routing Problem.
    It builds a series of tours, returning to the depot when its capacity is full.
    """
    def __init__(self, graph: Graph, start_node: int, capacity: int, distance_cache: DistanceCache):
        self.graph = graph
        self.start_node = start_node
        self.capacity = capacity
        self.distance_cache = distance_cache

        self.tours: List[List[int]] = []
        self.total_distance: float = 0.0
        
        self.current_tour: List[int] = []
        self.current_load: int = 0
        self.visited_nodes: Set[int] = set()

        self.reset()

    def reset(self):
        """Resets the ant for a new optimization iteration."""
        self.tours = []
        self.total_distance = 0.0
        self.current_tour = [self.start_node]
        self.current_load = 0
        self.visited_nodes = {self.start_node}

    def _select_next_node(self, pheromones: Dict, all_nodes_info: Dict[int, int], alpha: float, beta: float) -> int:
        """
        Selects the next node to visit based on pheromones, distance, and capacity constraints.
        """
        current_node = self.current_tour[-1]
        
        candidate_nodes = []
        for node_id, demand in all_nodes_info.items():
            if node_id not in self.visited_nodes and self.current_load + demand <= self.capacity:
                candidate_nodes.append(node_id)
        
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

    def move_to_node(self, next_node: int, all_nodes_info: Dict[int, int]):
        """
        Moves the ant to the next node, updating its tour, load, and distance.
        Handles the logic for returning to the depot.
        """
        last_node = self.current_tour[-1]
        distance_traveled = self.distance_cache.get_distance(last_node, next_node)

        if next_node == self.start_node:
            self.current_tour.append(self.start_node)
            self.tours.append(self.current_tour) # Tamamlanan turu listeye ekle
            self.total_distance += distance_traveled
            
            self.current_tour = [self.start_node]
            self.current_load = 0
        else: 
            self.current_tour.append(next_node)
            self.visited_nodes.add(next_node)
            self.current_load += all_nodes_info[next_node]
            self.total_distance += distance_traveled

    def finalize_solution(self):
        """
        Called after all nodes have been visited. Ensures the last tour is properly
        finished by returning to the depot.
        """
        if self.current_tour[-1] != self.start_node:
            distance_to_depot = self.distance_cache.get_distance(self.current_tour[-1], self.start_node)
            self.current_tour.append(self.start_node)
            self.tours.append(self.current_tour)
            self.total_distance += distance_to_depot