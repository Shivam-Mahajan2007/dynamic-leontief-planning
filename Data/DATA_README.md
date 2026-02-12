# Data Directory

This directory contains Input–Output tables and related economic data used for calibrating and running the dynamic planning model.

## Included Data

### Spanish Economy (2022)

The default dataset is from Spain's 2022 Input–Output tables, obtained from the Instituto Nacional de Estadística (INE).

**Files:**
1. **Spanish A-matrix.xlsx**
   - Technical coefficients matrix (64×64)
   - Sheet: "A Matrix"
   - Rows 4-67, Columns C-BN
   - Each entry a_ij represents input from sector i needed per unit output of sector j

2. **Value added.xlsx**
   - Value added coefficients by sector (1×64 vector)
   - Row 1, Columns A-BM
   - Represents labor and profit share per unit output

3. **Consumption and total production.xlsx**
   - Final demand components (64×4 matrix)
   - Column A: Household consumption
   - Column C: Investment
   - Column E: Government expenditure  
   - Column G: Total production/output
   - Rows 3-67: Sector data

**Sector Classification:**
- Sectors 1-24: Heavy industry (steel, chemicals, machinery)
- Sectors 25-44: Medium manufacturing
- Sectors 45-64: Light industry and services

## Data Source

**Source:** Instituto Nacional de Estadística (INE), Spain  
**Year:** 2022  
**URL:** https://www.ine.es/dyngs/INEbase/en/operacion.htm?c=Estadistica_C&cid=1254736177058&menu=ultiDatos&idp=1254735576581  
**License:** Public domain (government statistical data)

**Citation:**
> Instituto Nacional de Estadística (2022). Contabilidad nacional anual de España: Tablas input–output (TIO). Online statistical database. Available at: https://www.ine.es

## File Format Requirements

If you want to use your own IO data, files must follow this structure:

### A-matrix File
- Excel file (.xlsx)
- Contains sheet with technical coefficients
- n×n matrix starting at specified row/column
- All values should be non-negative
- Row sums should be < 1 (productive economy assumption)

### Value Added File
- Excel file (.xlsx)
- 1×n row vector of value-added coefficients
- Values between 0 and 1
- Represents labor + profit per unit output

### Final Demand File
- Excel file (.xlsx)
- At least 3 columns: consumption, investment, government
- n rows (one per sector)
- All values in same units (e.g., millions of euros)

## Using Your Own Data

1. **Prepare your files** in the format described above

2. **Update config.yaml:**
```yaml
io_matrix_file: "Your_A-matrix.xlsx"
io_sheet_name: "Your_Sheet_Name"  # If different
value_added_file: "Your_value_added.xlsx"
consumption_file: "Your_final_demand.xlsx"
n: [your number of sectors]
```

3. **Adjust sector composition** if needed:
```yaml
n_heavy: [number of heavy industry sectors]
n_medium: [number of medium manufacturing sectors]
n_light: [number of light industry/services sectors]
# Note: n_heavy + n_medium + n_light must equal n
```

4. **Run the simulation:**
```bash
python code/main.py
```

## Data Validation

The code automatically validates:
- ✓ Matrix dimensions match config
- ✓ A-matrix row sums < 1 (productivity)
- ✓ Non-negative entries
- ✓ File exists and is readable

Validation errors will show clear messages about what needs to be fixed.

## Additional Data Sources

### International IO Tables

**OECD:**
- URL: https://www.oecd.org/sti/ind/input-outputtables.htm
- Coverage: 60+ countries
- Format: Usually 36-45 sectors

**Eurostat:**
- URL: https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables
- Coverage: EU countries
- Format: Various levels of aggregation

**WIOD (World Input-Output Database):**
- URL: https://www.rug.nl/ggdc/valuechain/wiod/
- Coverage: 40+ countries, international linkages
- Format: Standardized 56 sectors

**UN Statistics:**
- URL: https://unstats.un.org/unsd/snaama/Index
- Coverage: Global
- Format: Various

### Converting Other Formats

Most IO tables follow the Supply-Use Table (SUT) framework. To convert:

1. **Extract A-matrix:** Technical coefficients matrix
2. **Extract value added:** Labor/profit vector
3. **Extract final demand:** Consumption, investment, government columns
4. **Save in Excel format** following the structure above

See `examples/data_conversion.py` for helper functions.

## Data License

The Spanish IO data is public domain as official government statistics. 

If you contribute data from other sources, please:
- Verify license permits redistribution
- Include attribution
- Document source and year clearly

## Questions?

If you have issues with data formatting or need help converting your IO tables, please open an issue on GitHub.
