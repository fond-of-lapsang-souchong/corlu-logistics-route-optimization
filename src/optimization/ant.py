import random
from typing import List, Dict, Set, Tuple, Any, Optional
from ..utils import OSRMDistanceProvider
import networkx as nx

Graph = nx.MultiDiGraph

class Ant:
    """
    Represents a single vehicle (or ant) in a CVRP or VRPTW problem.
    It builds a series of tours respecting capacity and time window constraints.
    """
    def __init__(self, graph: Graph, start_node: int, capacity: int, distance_provider: OSRMDistanceProvider):
        self.graph = graph
        self.start_node = start_node
        self.capacity = capacity
        self.distance_provider = distance_provider
        self.tours: List[List[int]] = []
        self.total_distance: float = 0.0
        self.current_tour: List[int] = []
        self.current_load: int = 0
        self.visited_nodes: Set[int] = set()
        self.current_time: float = 0.0
        self.total_wait_time: float = 0.0
        self.time_window_violated: bool = False
        self.reset()

    def reset(self):
        """Resets the ant for a new optimization iteration."""
        self.tours = []
        self.total_distance = 0.0
        self.current_tour = [self.start_node]
        self.current_load = 0
        self.visited_nodes = {self.start_node}
        self.current_time = 0.0
        self.total_wait_time = 0.0
        self.time_window_violated = False

    def _select_next_node(self, pheromones: Dict, all_nodes_info: Dict[int, Any], alpha: float, beta: float) -> Optional[int]:
        """
        Selects the next node to visit. Returns None if no valid node can be visited.
        """
        current_node = self.current_tour[-1]
        candidate_nodes = []
        for node_id, info in all_nodes_info.items():
            if node_id not in self.visited_nodes:
                if self.current_load + info['demand'] > self.capacity:
                    continue
                _, travel_time = self.distance_provider.get_travel_info(current_node, node_id)
                arrival_time = self.current_time + travel_time
                if arrival_time > info['time_window'][1]:
                    continue
                candidate_nodes.append(node_id)
        
        if not candidate_nodes:
            return None

        probabilities = []
        for next_node in candidate_nodes:
            edge = tuple(sorted((current_node, next_node)))
            pheromone = pheromones.get(edge, 1.0)
            distance, travel_time = self.distance_provider.get_travel_info(current_node, next_node)
            arrival_time = self.current_time + travel_time
            wait_time = max(0, all_nodes_info[next_node]['time_window'][0] - arrival_time)
            urgency = all_nodes_info[next_node]['time_window'][1]
            heuristic = 1.0 / (distance + travel_time + wait_time + urgency + 1e-10)
            probabilities.append((pheromone ** alpha) * (heuristic ** beta))

        total_prob = sum(probabilities)
        if total_prob == 0:
            return random.choice(candidate_nodes) if candidate_nodes else None
            
        normalized_probs = [p / total_prob for p in probabilities]
        return random.choices(candidate_nodes, weights=normalized_probs, k=1)[0]

    def move_to_node(self, next_node: int, all_nodes_info: Dict[int, Any]):
        """
        Moves the ant to the next node, updating its state including current time
        and considering service time at the node.
        """
        last_node = self.current_tour[-1]
        distance_traveled, time_traveled = self.distance_provider.get_travel_info(last_node, next_node)

        arrival_time = self.current_time + time_traveled

        if next_node == self.start_node:
            self.current_tour.append(self.start_node)
            self.tours.append(self.current_tour)
            self.total_distance += distance_traveled
            self.current_time = arrival_time
            self.current_tour = [self.start_node]
            self.current_load = 0
        else:
            node_info = all_nodes_info[next_node]
            
            earliest_arrival = node_info['time_window'][0]
            latest_arrival = node_info['time_window'][1]

            if arrival_time > latest_arrival:
                self.time_window_violated = True
            
            wait_time = max(0, earliest_arrival - arrival_time)
            self.total_wait_time += wait_time

            service_start_time = arrival_time + wait_time
            service_time = node_info.get('service_time', 0)
            self.current_time = service_start_time + service_time

            self.current_tour.append(next_node)
            self.visited_nodes.add(next_node)
            self.current_load += node_info['demand']
            self.total_distance += distance_traveled

    def finalize_solution(self):
        """
        Ensures the last tour is properly finished by returning to the depot.
        """
        if self.current_tour and self.current_tour[-1] != self.start_node:
            distance_to_depot, time_to_depot = self.distance_provider.get_travel_info(self.current_tour[-1], self.start_node)
            self.current_tour.append(self.start_node)
            self.tours.append(self.current_tour)
            self.total_distance += distance_to_depot
            self.current_time += time_to_depot