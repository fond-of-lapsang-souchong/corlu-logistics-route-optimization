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
    """
    mocker.patch('src.main.load_graph', return_value=create_mock_graph())
    
    mock_run_instance = mocker.patch(
        'src.main.run_optimization_instance', 
        return_value=(
            [[1, 2, 1]],     
            20.0,           
            [30.0, 20.0],    
            0.1             
        )
    )
    
    mock_config = {
        'location': {'place_name': 'Test Place'},
        'problem': { 'strategy': 'from_scenario', 'scenario_filepath': 'path/to/scenario.json' },
        'aco': { 'vehicle_fleet': [50], 'iterations': 5 },
        'output': {'map_filename': 'test_output.html'},
    }
    mocker.patch('src.main.load_config', return_value=mock_config)
    
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch('json.load', return_value={'nodes': [[1,0], [2,10]]})
    
    mock_plotter = mocker.patch('src.main.plot_optimized_route')
    mock_convergence_plotter = mocker.patch('src.main.plot_convergence')
    
    mock_map_object = MagicMock()
    mock_plotter.return_value = mock_map_object

    yield mock_plotter, mock_map_object, mock_convergence_plotter

def test_main_runs_without_errors_and_calls_plotters(setup_main_test):
    """
    main() fonksiyonunun baştan sona hatasız çalıştığını ve
    görselleştirme fonksiyonlarını çağırdığını test eder.
    """
    mock_plotter, mock_map_object, mock_convergence_plotter = setup_main_test

    try:
        with patch('sys.argv', ['src/main.py']):
             main()
    except Exception as e:
        pytest.fail(f"main() fonksiyonu bir hatayla sonlandı: {e}")

    mock_plotter.assert_called_once()
    mock_map_object.save.assert_called_once()
    mock_convergence_plotter.assert_called_once()