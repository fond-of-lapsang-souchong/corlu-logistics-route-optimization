import osmnx as ox
import networkx as nx
from typing import Optional

def load_graph(place_name: str, network_type: str = 'drive', undirected: bool = True, verbose: bool = True) -> Optional[nx.MultiDiGraph]:
    """
    Belirtilen yer için OSMnx kullanarak bir yol ağı grafiği indirir ve hazırlar.

    Args:
        place_name (str): İndirilecek yerin adı (örn. 'Çorlu, Tekirdağ, Türkiye').
        network_type (str, optional): Çekilecek ağ türü. Varsayılan: 'drive'.
        undirected (bool, optional): Grafiğin yönsüz olup olmayacağını belirtir. 
                                     ACO için genellikle True olması tercih edilir. Varsayılan: True.
        verbose (bool, optional): İşlem sırasında bilgi mesajları yazdırılıp yazdırılmayacağı. 
                                  Varsayılan: True.

    Returns:
        Optional[nx.MultiDiGraph]: Başarılı olursa OSMnx graf nesnesini, 
                                   aksi takdirde None döndürür.
    """
    try:
        if verbose:
            print(f"'{place_name}' için '{network_type}' yol ağı indiriliyor...")
        
        graph = ox.graph_from_place(place_name, network_type=network_type)
        
        if undirected:
            graph = graph.to_undirected()
            if verbose:
                print("Graf başarıyla YÖNSÜZ hale getirildi.")
        
        if verbose:
            print(f"Graf başarıyla oluşturuldu. Düğüm Sayısı: {len(graph.nodes())}, Kenar Sayısı: {len(graph.edges())}")
            
        return graph

    except Exception as e:
        print(f"Graf yüklenirken bir hata oluştu: {e}")
        return None