# Dynamic Input–Output Planning Model

**Computational implementation of the dynamic Leontief framework for large-scale production planning**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

## Overview

This repository contains the complete implementation of the dynamic input–output planning model described in:

> **Mahajan, S., & Singh, A.** (2025). "On a Dynamic Input–Output Framework for Price-Feedback-Based Production Planning." *[Journal Name]*, [Volume]([Issue]), [pages].

The model extends the classical Leontief input–output framework to incorporate:
- **Demand feedback** through price-based adjustment mechanisms
- **Capital dynamics** with sector-specific depreciation and investment
- **Computational tractability** via Neumann series approximations
- **Stochastic demand** with AR(1) extrapolation

### Key Features

- ✅ Scales to 64+ sectors (tested; theoretically up to 10⁶ sectors)
- ✅ Monthly planning frequency with annual recalibration
- ✅ Mean absolute output gap: **1.56%** (below US benchmark of 1.78%)
- ✅ Convergence in ~40 iterations with exponential error decay
- ✅ Fully reproducible with provided Spanish IO data (2022)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dynamic-leontief-planning.git
cd dynamic-leontief-planning

# Install dependencies
pip install -r requirements.txt
```

### Run Basic Simulation

```bash
# Run with default parameters (Spanish economy, 64 sectors, 60 months)
python code/main.py

# View results
ls simulation_outputs/
# → GDP_Capacity_AD.png, Output_gap.png, summary_statistics.csv, etc.
```

### Customize Parameters

```bash
# Edit config.yaml to change:
# - Planning horizon (T_plan)
# - Growth rate (g_a)
# - Sector composition (n_heavy, n_medium, n_light)
# - Shock parameters (shock_sigma, shock_persist)

python code/main.py --config custom_config.yaml
```

## Repository Contents

### Core Code (`code/`)
- **`main.py`** - Orchestrates the full simulation pipeline
- **`model.py`** - Core economic functions (Neumann series, AR(1), dynamics)
- **`data_loader.py`** - Loads and validates IO data from Excel
- **`plotting.py`** - Generates all figures from the paper
- **`config.yaml`** - All model parameters in one file

### Data (`data/`)
Spanish Input–Output tables (2022) from Instituto Nacional de Estadística:
- **A-matrix** (64×64): Technical coefficients
- **Value added** (1×64): Labor/profit shares by sector
- **Final demand** (64×3): Consumption, investment, government spending

### Examples (`examples/`)
- `basic_simulation.py` - Minimal working example
- `sensitivity_analysis.py` - Parameter sweep demonstrations
- `custom_sectors.py` - How to use your own IO data

## Results from Paper

All figures and tables in the published paper are reproducible using this code:

| Figure | File | Command |
|--------|------|---------|
| Figure 1 | `neumann_convergence.png` | Default run |
| Figure 5 | `GDP_Capacity_AD.png` | Default run |
| Figure 6 | `Output_gap.png` | Default run |
| Figure 7 | `Excess_demand.png` | Default run |
| Table 1 | `summary_statistics.csv` | Default run |

**Runtime**: ~2 minutes on a standard laptop (Intel i5, 8GB RAM)

## Model Description

### Mathematical Framework

The core planning problem is a **viability-preserving tracking system**:

```
Material balance:    (I - A)X(t) = F(t) = C_p(t) + I(t) + G(t)
Capital dynamics:    K(t+1) = (I - Δ)K(t) + I(t)
Capacity constraint: BX(t) ≤ K(t)
Price feedback:      ΔC_p(t) ≈ -C_p(t-1) · (ϵ · ΔP(t-1)/P₀)
```

### Investment Planning

Investment is determined by forecasted demand changes using AR(1) extrapolation:

```
ΔK_e(t) = B · Neumann(A, ΔC_p,E(t) + g·G(t) + 
                       B·Neumann(A, Δ²C_p,E(t) + g²·G(t)))
I(t) = ΔK_e(t) + ΔK_u(t) + δK(t)
```

### Computational Efficiency

The Neumann series approximation avoids repeated matrix inversion:

```
(I - A)⁻¹·d ≈ (I + A + A² + ... + Aᵏ)·d
```

- **Time complexity**: O(n²) per iteration
- **Convergence**: Exponential error decay δ(k) = δ(0)e^(-αk) with α ≈ 0.48
- **Typical iterations needed**: k = 30-40 for 0.01% error

## Citation

If you use this code in your research, please cite:

```bibtex
@article{mahajan2025dynamic,
  title={On a Dynamic Input–Output Framework for Price-Feedback-Based Production Planning},
  author={Mahajan, Shivam and Singh, Arjunveer},
  journal={[Journal Name]},
  volume={[Volume]},
  number={[Issue]},
  pages={[Pages]},
  year={2025},
  publisher={[Publisher]},
  doi={[DOI]}
}
```

For the software implementation specifically:

```bibtex
@software{mahajan2025code,
  author={Mahajan, Shivam and Singh, Arjunveer},
  title={Dynamic Input–Output Planning Model: Python Implementation},
  year={2025},
  publisher={GitHub},
  url={https://github.com/yourusername/dynamic-leontief-planning},
  doi={10.5281/zenodo.XXXXXXX}
}
```

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Methodology](docs/METHODOLOGY.md)** - Mathematical details
- **[API Reference](docs/API.md)** - Function documentation
- **[FAQ](docs/FAQ.md)** - Common questions

## Using Your Own Data

To run the model with your own Input–Output tables:

1. Prepare three Excel files:
   - **A-matrix**: Technical coefficients (n×n matrix)
   - **Value added**: Labor coefficients (1×n vector)
   - **Final demand**: Consumption, investment, government (n×3 matrix)

2. Update `config.yaml`:
```yaml
io_matrix_file: "Your_A-matrix.xlsx"
value_added_file: "Your_value_added.xlsx"
consumption_file: "Your_final_demand.xlsx"
n: [your number of sectors]
```

3. Run: `python code/main.py`

See `examples/custom_sectors.py` for a complete example.

## Validation

### Neumann Series Convergence
- Tested on matrices up to 1000×1000
- Error decays exponentially: δ(k) = 4.2e^(-0.48k) for Spanish data
- Tolerance (0.01%) reached at k ≈ 30

### Economic Consistency
- Mean absolute output gap: **1.56%** (vs. 1.78% US benchmark)
- Mean excess demand: **0.0017%** of GDP
- Capacity utilization: **98.44%** (stable over 60 months)
- Growth rate: **5.0%** annual (as calibrated)

## Extensions and Future Work

This codebase provides a foundation for:
- **International trade**: Add import/export optimization (see paper Section 8.3)
- **Multi-tier planning**: Different time scales for different sectors
- **Cybernetic control**: Optimal control formulations
- **Non-linear feedback**: Neural network demand forecasting

See `docs/EXTENSIONS.md` for detailed suggestions.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Contact

- **Shivam Mahajan** - [email]
- **Arjunveer Singh** - [email]

## Acknowledgments

- Spanish Instituto Nacional de Estadística for IO data
- Giovanni Paiela for error calculation contributions
- [Add any other acknowledgments]

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where contributions would be particularly valuable:
- Additional country IO data adapters
- Performance optimizations for large-scale systems
- Extended visualization tools
- Integration with other economic models

## Version History

- **v1.0.0** (2025-02) - Initial release accompanying paper publication
  - Full implementation of dynamic planning model
  - Spanish IO data (2022) included
  - Complete reproducibility of paper results

---

**Note**: This is an academic research tool. For production economic planning applications, please consult domain experts and validate against your specific institutional context.
