# Input-Output Planning Model Simulation

A computational model simulating an input-output economy with planning mechanisms, capital accumulation, and demand dynamics. This code accompanies the research paper and provides a complete, reproducible simulation environment.

## Overview

This simulation models a multi-sector economy using input-output analysis with:
- 64 economic sectors (heavy industry, medium manufacturing, and light industry/services)
- Capital accumulation and depreciation
- Investment planning with forecasting
- Government expenditure
- Stochastic demand shocks
- Price adjustments based on excess demand

## Requirements

### Python Version
- Python 3.7 or higher

### Dependencies

Install required packages using:

```bash
pip install -r requirements.txt
```

Required packages:
- `numpy` (≥1.20.0) - Numerical computations
- `matplotlib` (≥3.3.0) - Plotting and visualization
- `pandas` (≥1.2.0) - Data handling
- `openpyxl` (≥3.0.0) - Excel file reading
- `pyyaml` (≥5.4.0) - Configuration file parsing

## Required Data Files

The simulation requires three Excel files containing Spanish economic data. These files must be in the same directory as the scripts:

1. **Spanish A-matrix.xlsx**
   - Contains the input-output coefficient matrix (A matrix)
   - Sheet name: "A Matrix"
   - Data range: Rows 4-67, Columns C-BN (64×64 matrix)

2. **Value added.xlsx**
   - Contains value added by sector
   - Data range: Row 1, Columns A-BM (1×64 vector)

3. **Consumption and total production.xlsx**
   - Contains multiple final demand components:
     - Column A: Household consumption
     - Column C: Investment
     - Column E: Government expenditure
     - Column G: Total production/output
   - Data range: Rows 3-67 for all columns

dynamic-leontief-planning/
├── README.md                  # Rename README_GITHUB.md to this
├── LICENSE
├── CITATION.cff
├── .gitignore
├── CONTRIBUTING.md
├── requirements.txt
│
├── code/
│   ├── main.py
│   ├── config.yaml
│   ├── data_loader.py
│   ├── model.py
│   ├── plotting.py
│   └── __init__.py           # Empty file
│
├── data/
│   ├── README.md             # Use DATA_README.md
│   ├── Spanish_A-matrix.xlsx
│   ├── Value_added.xlsx
│   └── Consumption_and_total_production.xlsx
│
├── examples/
│   ├── basic_simulation.py   # Use basic_example.py
│   └── README.md             # Create: "See basic_simulation.py for minimal example"
│
└── paper/
    └── manuscript.pdf        # Your PDF
## Quick Start

### Basic Usage

1. Ensure all data files are in the project directory
2. Run the simulation with default settings:

```bash
python main.py
```

### Custom Configuration

Run with a custom config file:

```bash
python main.py --config my_config.yaml
```

Specify a different output directory:

```bash
python main.py --output-dir my_results
```

## Configuration

All simulation parameters are defined in `config.yaml`. Key parameters include:

### Time Parameters
- `T_plan`: Planning horizon in months (default: 60)
- `W`: Window size for AR(1) estimation (default: 12)

### Economic Parameters
- `tau`: Tax rate (default: 0.025)
- `b`: Capacity buffer parameter (default: 0.0075)
- `g_a`: Annual growth rate (default: 0.05)
- `k`: Number of Neumann series iterations (default: 40)

### Sector Composition
- `n`: Total number of sectors (default: 64)
- `n_heavy`: Heavy industry sectors (default: 24)
- `n_medium`: Medium manufacturing sectors (default: 20)
- `n_light`: Light industry/services sectors (default: 20)

### Stochastic Parameters
- `shock_sigma`: Demand shock standard deviation (default: 0.0061)
- `shock_persist`: Shock persistence (default: 0.7)
- `mu_heavy`: Heavy industry trend (default: -0.0012)
- `mu_medium`: Medium manufacturing trend (default: -0.0003)
- `mu_light`: Services trend (default: 0.0015)

See `config.yaml` for complete parameter descriptions and default values.

## Output Files

### CSV Files

**aggregate_results.csv**
- Time series of aggregate economic variables
- Columns: Time, GDP_real, Capacity, Output_Gap, Capacity_Utilization, C_value, C_plan_value, I_value, G_value, AD_value

**summary_statistics.csv**
- Key summary metrics
- Includes: Excess Demand (%), Mean Absolute Output Gap (%), Annual Growth Rate (%), Debt to GDP Ratio (%)

### Plots

All plots are saved as high-resolution PNG files (300 DPI):

1. **neumann_convergence.png** - Convergence test for the Neumann series
2. **Government.png** - Government expenditure over time
3. **Consumption.png** - Real consumption over time
4. **Investment.png** - Investment over time
5. **Output_gap.png** - Output gap percentage over time
6. **Utilization.png** - Capacity utilization over time
7. **Excess_demand.png** - Excess demand percentage over time
8. **GDP_Capacity_AD.png** - Comparison of GDP, potential GDP, and aggregate demand (monthly)
9. **GDP_Capacity_AD_quarterly.png** - Same comparison with quarterly averages

### Log File

**simulation.log**
- Detailed execution log with timestamps
- Includes parameter values, convergence information, and summary statistics
- Useful for debugging and validation

## Model Description

### Core Features

1. **Input-Output Structure**: Uses empirical Spanish IO matrix to capture inter-sectoral dependencies
2. **Capital Dynamics**: Capital stock evolves with depreciation and investment
3. **Investment Planning**: Forward-looking investment based on AR(1) forecasts of demand changes
4. **Demand Shocks**: Stochastic sector-specific demand shocks with persistence
5. **Price Mechanism**: Endogenous price adjustment based on excess demand
6. **Government Sector**: Exogenous government expenditure with trend growth

### Key Equations

The model uses a Neumann series approximation to solve the Leontief inverse:
```
X = (I - A)^(-1) * F ≈ (I + A + A² + ... + A^k) * F
```

Where:
- X = Gross output vector
- A = Input-output coefficient matrix
- F = Final demand vector
- k = Number of iterations (configurable)

### Simulation Flow

1. Initialize capital stock and demand structure
2. For each time period:
   - Update capital stock with depreciation
   - Forecast demand changes using AR(1) models
   - Plan investment to meet expected demand
   - Compute production given final demand
   - Calculate excess demand and adjust prices
   - Update consumption based on income and prices
   - Accumulate debt from government expenditure

## Customization

### Modifying Parameters

Edit `config.yaml` to change any parameter. For example, to increase the planning horizon:

```yaml
T_plan: 120  # Double the planning horizon to 120 months
```

### Adding New Outputs

To add new plots or CSV outputs:

1. Compute the desired variable in `main.py` (in the `compute_results` function)
2. Add plotting code to `plotting.py` (in the `generate_all_plots` function)
3. Add CSV export code to `main.py` (in the `save_results_csv` function)

### Using Different Data

To use data from a different country or time period:

1. Prepare Excel files in the same format as the Spanish data
2. Update the file names in `config.yaml`:
   ```yaml
   io_matrix_file: "Your_A-matrix.xlsx"
   value_added_file: "Your_value_added.xlsx"
   consumption_file: "Your_consumption.xlsx"
   ```
3. Ensure sector counts match (or update `n`, `n_heavy`, `n_medium`, `n_light`)

## Validation

### Neumann Convergence

The simulation automatically tests convergence of the Neumann series approximation. Check `neumann_convergence.png` to verify that:
- Error decreases monotonically
- Final error is below the tolerance threshold (default: 0.01%)

### Economic Consistency

Review the log file for:
- Excess demand levels (should be small if prices adjust well)
- Output gap magnitudes (indicates business cycle dynamics)
- Growth rate (should match intended calibration)
- Debt to GDP ratio (fiscal sustainability indicator)

## Troubleshooting

### Common Issues

**FileNotFoundError: Required file not found**
- Ensure all three Excel files are in the same directory as the scripts
- Check that file names in `config.yaml` match your actual file names

**Convergence Warning**
- The Neumann series did not converge within the specified iterations
- Increase `neumann_max_k` in the config file or reduce inter-sectoral dependencies in the A matrix

**Memory Error**
- Reduce `T_plan` (simulation length) or `n` (number of sectors)
- Close other applications to free memory

**Plotting Issues**
- Ensure matplotlib backend is set correctly (script uses 'Agg' for non-interactive environments)
- Check that `output_dir` has write permissions

### Getting Help

If you encounter issues:

1. Check the `simulation.log` file for detailed error messages
2. Verify your data files match the expected format
3. Test with default configuration before customizing
4. Ensure all dependencies are installed with correct versions

## Citation

If you use this code in your research, please cite the associated paper:

[Add your paper citation here]

## License

[Add your license information here]

## Contact

[Add contact information here]

## Version History

- **v1.0** (2024) - Initial release with refactored, modular structure
  - Improved documentation
  - Configuration file support
  - Comprehensive logging
  - CSV export functionality
  - Enhanced error handling

## Acknowledgments

[Add acknowledgments here if applicable]
