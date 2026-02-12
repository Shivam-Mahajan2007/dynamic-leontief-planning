"""
Basic Example: Running the Dynamic IO Planning Model

This minimal example demonstrates how to run the simulation
with default parameters and view key results.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import yaml
import numpy as np
from pathlib import Path

# Import our modules
import data_loader
import model
import plotting


def main():
    """Run a basic simulation with default parameters."""
    
    print("=" * 60)
    print("BASIC DYNAMIC IO PLANNING SIMULATION")
    print("=" * 60)
    
    # Load default configuration
    config_path = Path(__file__).parent.parent / 'code' / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Set random seed for reproducibility
    np.random.seed(config['random_seed'])
    
    print(f"\nConfiguration:")
    print(f"  Sectors: {config['n']}")
    print(f"  Planning horizon: {config['T_plan']} months")
    print(f"  Annual growth rate: {config['g_a']*100:.1f}%")
    print(f"  Random seed: {config['random_seed']}")
    
    # Get data directory
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Load data
    print("\nLoading IO data...")
    data = data_loader.load_all_data(config, str(data_dir))
    
    print(f"  Loaded {config['n']}x{config['n']} IO matrix")
    print(f"  Spectral radius of A: {np.max(np.abs(np.linalg.eigvals(data['A']))):.4f}")
    
    # Test Neumann convergence
    print("\nTesting Neumann series convergence...")
    test_vector = data['C_household'] / model.neumann(
        data['A'].T, data['va_per_unit'], config['k']
    )
    
    convergence = model.test_neumann_convergence(
        data['A'],
        test_vector,
        config['neumann_max_k'],
        config['neumann_tolerance']
    )
    
    if convergence['converged']:
        print(f"  ✓ Converged at k = {convergence['converged_k']}")
        print(f"    Final error: {convergence['final_error']:.6f}%")
    else:
        print(f"  ✗ Did not converge within {config['neumann_max_k']} iterations")
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print(f"\nFor full simulation with outputs, run:")
    print(f"  python code/main.py")
    print(f"\nThis will generate plots and CSV files in simulation_outputs/")


if __name__ == "__main__":
    main()
