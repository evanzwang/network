import pytest
import os
import json
from unittest.mock import patch, MagicMock
from tap.cli import parse_args, setup_environment, load_prompts, run_attack, analyze_results, resume_attack

@pytest.fixture
def mock_provider():
    """Create a mock provider for testing."""
    provider = MagicMock()
    provider.generate.return_value = MagicMock(
        content="test response",
        usage={"total_tokens": 10}
    )
    provider.evaluate.return_value = 0.8
    return provider

@pytest.fixture
def mock_attack_tree():
    """Create a mock attack tree for testing."""
    tree = MagicMock()
    tree.goal = "test goal"
    tree.target_str = "target"
    tree.root = MagicMock()
    tree.root.iter_subtree.return_value = []
    tree.get_statistics.return_value = {
        "total_nodes": 2,
        "successful_attacks": 1,
        "max_depth": 1,
        "avg_score": 0.6
    }
    
    def mock_save(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump({
                "goal": tree.goal,
                "target_str": tree.target_str,
                "nodes": []
            }, f)
    
    tree.save = mock_save
    return tree

def test_parse_args():
    """Test command line argument parsing."""
    # Test attack command
    with patch('sys.argv', ['tap', 'attack',
                          '--goal', 'test goal',
                          '--target', 'target',
                          '--prompts', 'prompts.txt',
                          '--provider', 'gpt-4',
                          '--max-attempts', '5']):
        args = parse_args()
        assert args.command == 'attack'
        assert args.goal == 'test goal'
        assert args.target == 'target'
        assert args.prompts == 'prompts.txt'
        assert args.provider == 'gpt-4'
        assert args.max_attempts == 5

    # Test analyze command
    with patch('sys.argv', ['tap', 'analyze',
                          'results.json',
                          '--format', 'json']):
        args = parse_args()
        assert args.command == 'analyze'
        assert args.results_file == 'results.json'
        assert args.format == 'json'

    # Test resume command
    with patch('sys.argv', ['tap', 'resume',
                          'state.json',
                          '--max-attempts', '5']):
        args = parse_args()
        assert args.command == 'resume'
        assert args.state_file == 'state.json'
        assert args.max_attempts == 5

def test_setup_environment(tmp_path):
    """Test environment setup."""
    output_dir = tmp_path / "output"
    args = MagicMock(
        debug=True,
        output=str(output_dir),
        config=None
    )
    
    setup_environment(args)
    assert os.path.exists(output_dir)

def test_load_prompts(tmp_path):
    """Test loading prompts from file."""
    prompts_file = tmp_path / "prompts.txt"
    prompts = ["prompt1", "prompt2", "prompt3"]
    
    with open(prompts_file, 'w') as f:
        f.write('\n'.join(prompts))
    
    loaded_prompts = load_prompts(str(prompts_file))
    assert loaded_prompts == prompts

@patch('tap.cli.create_provider')
def test_run_attack(mock_create_provider, mock_provider, tmp_path):
    """Test running attack command."""
    mock_create_provider.return_value = mock_provider
    
    # Create test prompts file
    prompts_file = tmp_path / "prompts.txt"
    with open(prompts_file, 'w') as f:
        f.write("test prompt")
    
    # Create args
    args = MagicMock(
        goal="test goal",
        target="target",
        prompts=str(prompts_file),
        provider="gpt-4",
        max_attempts=1,
        output=str(tmp_path),
        image=None
    )
    
    # Run attack
    run_attack(args, {})
    
    # Verify provider calls
    mock_provider.generate.assert_called_once()
    mock_provider.evaluate.assert_called_once()
    
    # Verify results file was created
    results_file = tmp_path / "attack_results.json"
    assert os.path.exists(results_file)

def test_analyze_results(mock_attack_tree, tmp_path):
    """Test analyzing results command."""
    # Create test results file
    results_file = tmp_path / "results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "goal": "test goal",
            "target_str": "target",
            "nodes": []
        }, f)
    
    # Test text format
    args = MagicMock(
        results_file=str(results_file),
        format="text"
    )
    
    with patch('tap.cli.AttackTree.load', return_value=mock_attack_tree):
        analyze_results(args)
        mock_attack_tree.get_statistics.assert_called_once()

    # Test JSON format
    args.format = "json"
    with patch('tap.cli.AttackTree.load', return_value=mock_attack_tree):
        analyze_results(args)
        mock_attack_tree.get_statistics.assert_called()

@patch('tap.cli.create_provider')
def test_resume_attack(mock_create_provider, mock_provider, mock_attack_tree, tmp_path):
    """Test resuming attack command."""
    mock_create_provider.return_value = mock_provider
    
    # Create test state file
    state_file = tmp_path / "state.json"
    with open(state_file, 'w') as f:
        json.dump({
            "goal": "test goal",
            "target_str": "target",
            "nodes": []
        }, f)
    
    # Create test prompts file
    prompts_file = tmp_path / "prompts.txt"
    with open(prompts_file, 'w') as f:
        f.write("test prompt")
    
    # Create args
    args = MagicMock(
        state_file=str(state_file),
        prompts=str(prompts_file),
        max_attempts=1,
        output=str(tmp_path)
    )
    
    with patch('tap.cli.AttackTree.load', return_value=mock_attack_tree):
        resume_attack(args, {})
        
        # Verify provider was created
        mock_create_provider.assert_called_once()
        
        # Verify results file was created
        results_file = tmp_path / "attack_results_resumed.json"
        assert os.path.exists(results_file) 