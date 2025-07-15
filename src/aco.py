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

    def reset(self) -> None:
        """
        Resets the ant's path, distance, and visited nodes to the initial state.
        """
        self.path = [self.start_node]
        self.path_distance = 0.0
        self.visited = {self.start_node}

    def _select_next_node(self, pheromones: dict, nodes_to_visit: list, alpha: float, beta: float) -> int:
        """
        Selects the next node to visit from the list of required stops.
        """
        import numpy as np

        current_node = self.path[-1]
        candidate_nodes = [node for node in nodes_to_visit if node not in self.visited]

        if not candidate_nodes:
            return self.start_node

        probabilities = []
        for next_node in candidate_nodes:
            edge = (current_node, next_node)
            pheromone = pheromones.get(edge, 1.0)
            try:
                distance = ox.shortest_path_length(self.graph, current_node, next_node, weight='length')
            except:
                distance = float('inf') # Arada yol yoksa mesafe sonsuzdur

            heuristic = 1.0 / distance if distance != 0 else float('inf')

            probabilities.append((pheromone ** alpha) * (heuristic ** beta))

        probabilities = np.array(probabilities)
        if np.sum(probabilities) == 0 or np.isinf(np.sum(probabilities)):
            return np.random.choice(candidate_nodes)

        probabilities /= np.sum(probabilities)

        return np.random.choice(candidate_nodes, p=probabilities)

    def _update_path(self, next_node: int) -> None:
        """
        Updates the ant's path with the next node and calculates the
        REAL travel distance between the last node and the new node.
        """
        import networkx as nx
        
        last_node = self.path[-1]

        self.path.append(next_node)
        self.visited.add(next_node)

        try:
            distance = nx.shortest_path_length(self.graph, last_node, next_node, weight='length')
            self.path_distance += distance
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            self.path_distance += float('inf')

    def get_path_distance(self) -> float:
        """
        Calculates the total distance of the ant's completed tour.

        Returns:
            float: The total distance of the tour.
        """
        return self.path_distance

class ACOptimizer:
    """
    Manages the entire Ant Colony Optimization process.

    This class initializes the pheromone matrix, runs the main optimization
    loop, and manages the colony of ants to find the best path.

    Attributes:
        graph (osmnx.graph): The graph on which the optimization is performed.
        ants (List[Ant]): The list of ants in the colony.
        nodes_to_visit (List[int]): A list of all nodes that must be visited.
        alpha (float): The influence of the pheromone levels.
        beta (float): The influence of the heuristic information (distance).
        evaporation_rate (float): The rate at which pheromones evaporate.
        pheromones (dict): A dictionary representing the pheromone matrix.
    """

    def __init__(
        self,
        graph: ox.graph,
        ants: List[Ant],
        nodes_to_visit: List[int],
        alpha: float,
        beta: float,
        evaporation_rate: float,
    ):
        """
        Initializes the ACOptimizer.

        Args:
            graph (osmnx.graph): The graph for the optimization.
            ants (List[Ant]): The colony of ants.
            nodes_to_visit (List[int]): The list of nodes to be visited.
            alpha (float): The pheromone influence factor.
            beta (float): The heuristic influence factor.
            evaporation_rate (float): The pheromone evaporation rate.
        """
        self.graph = graph
        self.ants = ants
        self.nodes_to_visit = nodes_to_visit
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.pheromones = self._init_pheromones()

    def _init_pheromones(self) -> dict:
        """
        Initializes the pheromone matrix for all edges in the graph.

        Returns:
            dict: The initialized pheromone matrix.
        """
        pheromones = {}
        for u, v in self.graph.edges():
            pheromones[(u, v)] = 1.0
            pheromones[(v, u)] = 1.0
        return pheromones

    def run(self, iterations: int) -> tuple[List[int], float]:
        """
        Runs the main ACO optimization loop using the superior structure.
        """
        global_best_path = []
        global_best_distance = float('inf')

        all_possible_nodes = list(self.graph.nodes())

        for i in range(iterations):
            all_tours = [] 

            for ant in self.ants:
                ant.reset()

                while len(ant.visited) < len(self.nodes_to_visit):
                    next_node = ant._select_next_node(
                        self.pheromones, self.nodes_to_visit, self.alpha, self.beta
                    )
                    if next_node is None:
                        break
                    ant._update_path(next_node)
            
                ant._update_path(ant.start_node)
                all_tours.append(ant)

            self._update_pheromones(all_tours)

            for ant in all_tours:
                current_distance = ant.get_path_distance()
                if current_distance < global_best_distance:
                    global_best_distance = current_distance
                    global_best_path = ant.path

            print(f"İterasyon {i+1}: En İyi Mesafe = {global_best_distance:.2f} m")

        return global_best_path, global_best_distance

    def _update_pheromones(self, ants: List[Ant]) -> None:
        """
        Updates the pheromone matrix after each iteration.

        This involves two steps:
        1. Evaporation: All pheromone trails are reduced by a certain factor.
        2. Deposition: Ants deposit new pheromones on the paths they traveled,
           proportional to the quality of their tours.
        """
        # Evaporation
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.evaporation_rate)

        # Deposition
        for ant in self.ants:
            path_distance = ant.get_path_distance()
            if path_distance == 0:
                continue
            pheromone_deposit = 1.0 / path_distance
            for i in range(len(ant.path) - 1):
                edge = (ant.path[i], ant.path[i + 1])
                if edge in self.pheromones:
                    self.pheromones[edge] += pheromone_deposit