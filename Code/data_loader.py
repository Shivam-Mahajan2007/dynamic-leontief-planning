import numpy as np
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)


def validate_file_exists(filepath, description):
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Required file not found: {description}\n"
            f"Expected location: {filepath}\n"
            f"Please ensure this file is in the correct directory."
        )
    logger.info(f"Found {description}: {os.path.basename(filepath)}")


def load_io_matrix(script_dir, filename, sheet_name, n):
    filepath = os.path.join(script_dir, filename)
    validate_file_exists(filepath, "IO matrix file")
    
    logger.info(f"Loading IO matrix from {filename}, sheet '{sheet_name}'")
    
    try:
        io_df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
        A = io_df.iloc[3:67, 2:66].to_numpy(dtype=float)
        
        if A.shape != (n, n):
            raise ValueError(
                f"IO matrix has shape {A.shape}, expected ({n}, {n})"
            )
        
        logger.info(f"Successfully loaded {n}x{n} IO matrix")
        return A
        
    except Exception as e:
        raise RuntimeError(
            f"Error loading IO matrix from {filename}: {str(e)}"
        )


def load_value_added(script_dir, filename, n):
    # Load value added
    va_filepath = os.path.join(script_dir, filename)
    validate_file_exists(va_filepath, "Value added file")
    
    logger.info(f"Loading value added data from {filename}")
    
    try:
        va_df = pd.read_excel(va_filepath, header=None)
        value_added = va_df.iloc[0, 0:n].to_numpy(dtype=float)
        
        if len(value_added) != n:
            raise ValueError(
                f"Value added has {len(value_added)} sectors, expected {n}"
            )
        
        logger.info(f"Successfully loaded value added for {n} sectors")
        return value_added
        
    except Exception as e:
        raise RuntimeError(
            f"Error loading value added from {filename}: {str(e)}"
        )


def load_consumption_and_output(script_dir, filename, n):
    filepath = os.path.join(script_dir, filename)
    validate_file_exists(filepath, "Consumption and production file")
    
    logger.info(f"Loading consumption and output data from {filename}")
    
    try:
        df = pd.read_excel(filepath, header=None)
        
        # Total output from column G (index 6), rows 3-67
        total_output = 1e+6 * df.iloc[2:66, 6].to_numpy(dtype=float)
        
        # Final demand components
        C_household = 1e+6 * df.iloc[2:66, 0].to_numpy(dtype=float)
        I_investment = 1e+6 * df.iloc[2:66, 2].to_numpy(dtype=float)
        G_government = 1e+6 * df.iloc[2:66, 4].to_numpy(dtype=float)
        
        # Validate dimensions
        for name, data in [
            ('total_output', total_output),
            ('C_household', C_household),
            ('I_investment', I_investment),
            ('G_government', G_government)
        ]:
            if len(data) != n:
                raise ValueError(f"{name} has {len(data)} sectors, expected {n}")
        
        logger.info(f"Successfully loaded consumption and output data for {n} sectors")
        
        return {
            'total_output': total_output,
            'C_household': C_household,
            'I_investment': I_investment,
            'G_government': G_government
        }
        
    except Exception as e:
        raise RuntimeError(
            f"Error loading consumption and output from {filename}: {str(e)}"
        )


def compute_value_added_per_unit(value_added, total_output):
    va_per_unit = value_added / total_output
    va_per_unit = np.nan_to_num(va_per_unit, nan=0.0, posinf=0.0, neginf=0.0)
    
    logger.info("Computed value added per unit of output")
    return va_per_unit


def load_all_data(config, script_dir):
    logger.info("=" * 60)
    logger.info("LOADING DATA FILES")
    logger.info("=" * 60)
    
    n = config['n']
    
    # Load IO matrix
    A = load_io_matrix(
        script_dir,
        config['io_matrix_file'],
        config['io_sheet_name'],
        n
    )
    
    # Load value added
    value_added = load_value_added(
        script_dir,
        config['value_added_file'],
        n
    )
    
    # Load consumption and output data
    cons_data = load_consumption_and_output(
        script_dir,
        config['consumption_file'],
        n
    )
    
    # Compute value added per unit
    va_per_unit = compute_value_added_per_unit(
        value_added,
        cons_data['total_output']
    )
    
    logger.info("=" * 60)
    logger.info("DATA LOADING COMPLETE")
    logger.info("=" * 60)
    logger.info("")
    
    return {
        'A': A,
        'value_added': value_added,
        'va_per_unit': va_per_unit,
        'total_output': cons_data['total_output'],
        'C_household': cons_data['C_household'],
        'I_investment': cons_data['I_investment'],
        'G_government': cons_data['G_government']
    }
