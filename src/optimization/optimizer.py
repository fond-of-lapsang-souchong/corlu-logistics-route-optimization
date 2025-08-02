import logging
import networkx as nx
from tqdm import tqdm
from typing import List, Tuple, Dict, Set

from .ant import Ant
from ..utils import OSRMDistanceProvider

Graph = nx.MultiDiGraph

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ACOptimizer:
    """
    Karınca Kolonisi Optimizasyonu (ACO) kullanarak Araç Rotalama Problemini (VRP)
    çözmek için tasarlanmış sınıf.

    Elitist Ant System (EAS) ve Max-Min Ant System (MMAS) gibi farklı ACO
    stratejilerini destekler.
    """
    
    _TIME_PENALTY = 1_000_000_000
    _WAIT_PENALTY_MULTIPLIER = 100

    def __init__(
        self,
        graph: Graph,
        nodes_info: Dict[int, int],
        start_node: int,
        vehicle_fleet: List[int],
        osrm_host: str,
        aco_strategy: str = "eas",
        vehicle_fixed_cost: float = 0.0,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.5,
        eas_elitism_factor: float = 1.0,
        mmas_rho: float = 0.2
    ):
        """
        ACOptimizer sınıfını başlatır.

        Args:
            graph (Graph): Rotalama için kullanılacak NetworkX grafiği.
            nodes_info (Dict[int, int]): Düğüm ID'lerini ve bilgilerini (örn. talep) içeren sözlük.
            start_node (int): Başlangıç ve bitiş düğümü (depo).
            vehicle_fleet (List[int]): Her bir aracın kapasitesini içeren liste.
            osrm_host (str): OSRM sunucusunun adresi.
            aco_strategy (str): Kullanılacak ACO stratejisi ("eas" veya "mmas").
            vehicle_fixed_cost (float): Her bir tur için eklenen sabit araç maliyeti.
            alpha (float): Feromonun etkisini belirleyen parametre.
            beta (float): Sezgisel bilginin (uzaklık) etkisini belirleyen parametre.
            evaporation_rate (float): Feromon buharlaşma oranı (EAS için).
            eas_elitism_factor (float): EAS'de global en iyi çözümün feromonunu güçlendirme faktörü.
            mmas_rho (float): MMAS için feromon buharlaşma oranı.
        """
        self.graph = graph
        self.nodes_info = nodes_info
        self.start_node = start_node
        self.vehicle_fleet = vehicle_fleet
        self.osrm_host = osrm_host
        self.vehicle_fixed_cost = vehicle_fixed_cost
        
        self.strategy = aco_strategy.lower()
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.eas_elitism_factor = eas_elitism_factor
        self.mmas_rho = mmas_rho
        
        self.pheromone_min = 0.0
        self.pheromone_max = float('inf')
        self.mmas_initialized = False

        self.distance_cache = OSRMDistanceProvider(self.graph, host=self.osrm_host)
        self.pheromones = self._init_pheromones()
        
        self.ants = [Ant(self.graph, self.start_node, capacity, self.distance_cache) for capacity in self.vehicle_fleet]
        self.num_ants = len(self.vehicle_fleet)

        self.global_best_solution: List[List[int]] = []
        self.global_best_cost: float = float('inf')

    def _init_pheromones(self) -> Dict[Tuple[int, int], float]:
        """Tüm kenarlar için başlangıç feromon seviyesini ayarlar."""
        pheromones = {}
        all_nodes = list(self.nodes_info.keys())
        logging.info("Pheromonlar ön-başlatılıyor...")
        for i in range(len(all_nodes)):
            for j in range(i + 1, len(all_nodes)):
                edge = tuple(sorted((all_nodes[i], all_nodes[j])))
                pheromones[edge] = 1.0
        return pheromones

    def _apply_pheromone_deposit(self, tours: List[List[int]], deposit_amount: float):
        """Verilen turlar üzerine belirtilen miktarda feromon bırakır."""
        for tour in tours:
            for i in range(len(tour) - 1):
                edge = tuple(sorted((tour[i], tour[i+1])))
                if edge in self.pheromones:
                    self.pheromones[edge] += deposit_amount

    def _update_pheromones_eas(self, iteration_best_solution: Tuple[List[List[int]], float]):
        """Elitist Ant System (EAS) stratejisine göre feromonları günceller."""
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.evaporation_rate)

        tours, cost = iteration_best_solution
        if cost != float('inf') and cost > 0:
            pheromone_deposit = 1.0 / cost
            self._apply_pheromone_deposit(tours, pheromone_deposit)

        if self.global_best_cost != float('inf'):
            elitist_deposit = self.eas_elitism_factor * (1.0 / self.global_best_cost)
            self._apply_pheromone_deposit(self.global_best_solution, elitist_deposit)
            
    def _update_mmas_pheromone_limits(self):
        """MMAS için feromon alt ve üst limitlerini global en iyi maliyete göre günceller."""
        if self.global_best_cost == float('inf'):
            return

        self.pheromone_max = 1 / (self.mmas_rho * self.global_best_cost)
        n = len(self.nodes_info)
        p_best = 0.05
        denominator = (n / 2 - 1) * (p_best ** (1 / n))
        if denominator > 0:
            self.pheromone_min = self.pheromone_max * (1 - (p_best ** (1 / n))) / denominator
        else:
            self.pheromone_min = self.pheromone_max * 0.05
            
        if not self.mmas_initialized:
            logging.info("İlk çözüm bulundu. MMAS feromonları τ_max'a ayarlanıyor...")
            for edge in self.pheromones:
                self.pheromones[edge] = self.pheromone_max
            self.mmas_initialized = True

    def _update_pheromones_mmas(self, best_solution_of_iteration: Tuple[List[List[int]], float]):
        """Max-Min Ant System (MMAS) stratejisine göre feromonları günceller."""
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.mmas_rho)

        tours, cost = best_solution_of_iteration
        if cost != float('inf') and cost > 0:
            pheromone_deposit = 1.0 / cost
            self._apply_pheromone_deposit(tours, pheromone_deposit)
        
        for edge in self.pheromones:
            self.pheromones[edge] = max(self.pheromone_min, min(self.pheromones[edge], self.pheromone_max))
    
    def _update_pheromones(self, iteration_best_solution: Tuple[List[List[int]], float]):
        """Seçilen stratejiye göre uygun feromon güncelleme metodunu çağırır."""
        if self.strategy == "eas":
            self._update_pheromones_eas(iteration_best_solution) 
        elif self.strategy == "mmas":
            if iteration_best_solution[1] != float('inf'):
                self._update_pheromones_mmas(iteration_best_solution)

    def _calculate_cost(self, ant: Ant) -> float:
        """Bir karıncanın oluşturduğu çözümün toplam maliyetini hesaplar."""
        num_tours = len([tour for tour in ant.tours if len(tour) > 2])
        base_cost = ant.total_distance
        time_penalty = self._TIME_PENALTY if ant.time_window_violated else 0
        wait_penalty = ant.total_wait_time * self._WAIT_PENALTY_MULTIPLIER
        fixed_cost = num_tours * self.vehicle_fixed_cost

        return base_cost + fixed_cost + time_penalty + wait_penalty

    def run(self, iterations: int) -> Tuple[List[List[int]], float, List[float]]:
        """
        ACO optimizasyonunu belirtilen iterasyon sayısı kadar çalıştırır.
        Bu versiyon, çoklu karıncaların (araçların) tek bir çözümü
        işbirliği içinde oluşturduğu bir VRP mantığı kullanır.
        """ 
        cost_history = []
        progress_bar = tqdm(range(iterations), desc=f"ACO Optimizasyonu ({self.strategy.upper()})")

        for i in progress_bar:
            colony_solution_tours = []
            colony_total_distance = 0.0
            colony_total_wait_time = 0.0
            colony_time_window_violated = False

            iteration_unvisited_nodes = {
                node_id: info 
                for node_id, info in self.nodes_info.items() 
                if node_id != self.start_node
            }

            for ant in self.ants:
                if not iteration_unvisited_nodes:
                    break

                ant.reset()

                while True:
                    next_node = ant._select_next_node(
                        self.pheromones,
                        iteration_unvisited_nodes,
                        self.alpha,
                        self.beta
                    )

                    if next_node is None:
                        break

                    ant.move_to_node(next_node, self.nodes_info)
                
                    del iteration_unvisited_nodes[next_node]

                ant.finalize_solution()

                colony_solution_tours.extend(ant.tours)
                colony_total_distance += ant.total_distance
                colony_total_wait_time += ant.total_wait_time
                if ant.time_window_violated:
                    colony_time_window_violated = True
        
            if iteration_unvisited_nodes:
                total_cost = float('inf')
                logging.warning(f"İterasyon {i+1}, filonun kapasitesi/zamanı yetmediği için {len(iteration_unvisited_nodes)} durağı ziyaret edemedi.")
            else:
                num_tours = len([tour for tour in colony_solution_tours if len(tour) > 2])
                base_cost = colony_total_distance
                time_penalty = self._TIME_PENALTY if colony_time_window_violated else 0
                wait_penalty = colony_total_wait_time * self._WAIT_PENALTY_MULTIPLIER
                fixed_cost = num_tours * self.vehicle_fixed_cost
                total_cost = base_cost + fixed_cost + time_penalty + wait_penalty

            iteration_best_solution = (colony_solution_tours, total_cost)

            if total_cost < self.global_best_cost:
                self.global_best_cost = total_cost
                self.global_best_solution = colony_solution_tours
            
                if self.strategy == "mmas":
                    self._update_mmas_pheromone_limits()
        
            self._update_pheromones(iteration_best_solution)

            cost_history.append(self.global_best_cost)
            display_cost = f"{self.global_best_cost/1000:.2f}k" if self.global_best_cost != float('inf') else 'GEÇERSİZ'
            progress_bar.set_postfix({"En İyi Maliyet": display_cost})
    
        self.distance_cache.save_to_disk()
        logging.info(f"Optimizasyon tamamlandı. En iyi maliyet: {self.global_best_cost}")
        return self.global_best_solution, self.global_best_cost, cost_history