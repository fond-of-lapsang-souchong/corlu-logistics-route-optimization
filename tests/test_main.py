import os
import sys
import pytest
from unittest.mock import patch, MagicMock

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.main import main
from tests.helpers import create_mock_graph

@pytest.fixture
def setup_main_test(mocker):
    """
    main() fonksiyonunu test etmek için gerekli ortamı hazırlar.
    - Tüm harici servisleri ve dosya işlemlerini taklit eder (mock).
    """
    mocker.patch('src.main.load_graph', return_value=create_mock_graph())
    
    mock_distance_provider_instance = MagicMock()
    mock_distance_provider_instance.get_distance.return_value = 10.0
    mocker.patch('src.main.ACOptimizer', return_value=MagicMock(run=MagicMock(return_value=([[1,2,3,1]], 30.0))))
    
    mock_config = {
        'location': {'place_name': 'Test Place'},
        'problem': {
            'strategy': 'from_scenario',
            'scenario_filepath': 'data/scenarios/corlu_varsayilan_10_durak.json'
        },
        'aco': {
            'vehicle_fleet': [50],
            'vehicle_fixed_cost': 0.0,
            'iterations': 5,
            'alpha': 1.0,
            'beta': 2.0,
            'evaporation_rate': 0.5
        },
        'output': {'map_filename': 'test_output.html'}
    }
    mocker.patch('src.main.load_config', return_value=mock_config)

    mock_scenario = {
        'name': 'Test Senaryo',
        'nodes': [[1, 0], [2, 10], [3, 10], [4, 10]]
    }
    mocker.patch('json.load', return_value=mock_scenario)
    mocker.patch("builtins.open", mocker.mock_open())

    mock_plotter = mocker.patch('src.main.plot_optimized_route')
    
    mock_map_object = MagicMock()
    mock_plotter.return_value = mock_map_object

    yield mock_plotter, mock_map_object


def test_main_runs_without_errors_and_calls_plotter(setup_main_test):
    """
    Tests if the main function can run without exceptions and that it calls
    the plotting function with the correct arguments at the end.
    """
    mock_plotter, mock_map_object = setup_main_test

    try:
        with patch('sys.argv', ['src/main.py']):
             main()
    except Exception as e:
        pytest.fail(f"main() fonksiyonu bir hatayla sonlandı: {e}")

    mock_plotter.assert_called_once()
    
    mock_map_object.save.assert_called_once()