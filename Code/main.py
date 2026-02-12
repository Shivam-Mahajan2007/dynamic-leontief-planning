import numpy as np

import os
import argparse
import logging
import yaml
from datetime import datetime
import pandas as pd
import data_loader
import model
import plotting


def setup_logging(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    log_file = os.path.join(output_dir, 'simulation.log')
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    return logging.getLogger(__name__)


def load_config(config_file):
    if not os.path.exists(config_file):
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}\n"
            f"Please ensure config.yaml exists in the current directory."
        )
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def initialize_simulation(config, data):
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("INITIALIZING SIMULATION")
    logger.info("=" * 60)
    
    n = config['n']
    k = config['k']
    T_plan = config['T_plan']
    W = config['W']
    T = T_plan + W

    np.random.seed(None)
    logger.info(f"Random seed set to {config['random_seed']}")
    
    Delta = model.create_delta_matrix(config)
    B, B_inv = model.create_capital_intensity_matrix(config)
    mu = model.create_mu_vector(config)
    
    states = model.initialize_state_arrays(T, n)
    
    A = data['A']
    wL = data['va_per_unit']
    P0_real = model.neumann(A.T, wL, k)
    P0 = P0_real.copy()
    alpha = data['C_household'] / data['C_household'].sum()

    epsilon = -np.ones(n)
    epsilon_measured = epsilon
    
    alpha_shock = np.zeros(n)
    
    g_a = config['g_a']
    g = (1 + g_a)**(1/12) - 1
    
    states['C_0'][0] = data['C_household'] / P0
    states['C'][0] = states['C_0'][0]
    states['C_p'][0] = states['C'][0]
    states['G'][0] = data['G_government'] / P0
    
    states['K'][0] = config['initial_capacity_buffer'] * (B @ (data['total_output'] / P0))
    states['I'][0] = Delta @ states['K'][0]
    
    states['X'][0] = model.neumann(A, states['C'][0] + states['I'][0] + states['G'][0], k)
    states['K_e'][0] = B @ states['X'][0]
    states['X_max'][0] = config['initial_capacity_buffer'] * states['X'][0]
    states['AD'][0] = states['C'][0] + states['I'][0] + states['G'][0]
    states['F'][0] = states['AD'][0]
    states['F_c'][0] = (np.eye(n) - A) @ states['X_max'][0]
    states['K'][0] = B @ states['X_max'][0]
    states['U'][0] = states['X_max'][0] - states['X'][0]
    states['K_u'][0] = B @ states['U'][0]
    
    states['K'][1] = (np.eye(n) - Delta) @ states['K'][0] + states['I'][0]
    
    Delta_C_p_hist = []
    Delta2_C_p_hist = []
    Delta_P_last = 0
    Delta_K_e_last = np.zeros(n)
    
    Debt = 0
    Y_income_prev = data['C_household'].sum()
    
    Delta_C_p_forecaster = model.AR1Forecaster(W)
    Delta2_C_p_forecaster = model.AR1Forecaster(W)
    
    logger.info(f"Simulation initialized: T={T}, n={n}, k={k}")
    logger.info("=" * 60)
    logger.info("")
    
    return {
        'states': states,
        'Delta': Delta,
        'B': B,
        'B_inv': B_inv,
        'A': A,
        'P0': P0,
        'P0_real': P0_real,
        'wL': wL,
        'alpha': alpha,
        'alpha_shock': alpha_shock,
        'epsilon': epsilon,
        'epsilon_measured': epsilon_measured,
        'mu': mu,
        'g': g,
        'T': T,
        'W': W,
        'n': n,
        'k': k,
        'Delta_C_p_hist': Delta_C_p_hist,
        'Delta2_C_p_hist': Delta2_C_p_hist,
        'Delta_P_last': Delta_P_last,
        'Delta_K_e_last': Delta_K_e_last,
        'Debt': Debt,
        'Y_income_prev': Y_income_prev,
        'Delta_C_p_forecaster': Delta_C_p_forecaster,
        'Delta2_C_p_forecaster': Delta2_C_p_forecaster
    }


def run_simulation(config, sim):
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("RUNNING SIMULATION")
    logger.info("=" * 60)
    
    states = sim['states']
    T = sim['T']
    W = sim['W']
    n = sim['n']
    k = sim['k']
    A = sim['A']
    B = sim['B']
    Delta = sim['Delta']
    P0 = sim['P0']
    g = sim['g']
    tau = config['tau']
    b = config['b']
    
    shock_sigma = config['shock_sigma']
    shock_persist = config['shock_persist']
    
    for t in range(1, T):
        if t % 12 == 0:
            logger.info(f"Progress: Year {t//12}/{(T-W)//12}")
        
        K_e_last = B @ states['X'][t-1]
        
        K_e_hat = K_e_last + sim['Delta_K_e_last']
        
        states['K'][t] = (np.eye(n) - Delta) @ states['K'][t-1] + states['I'][t-1]
        
        states['K_u'][t] = (1-b)*states['K'][t] - K_e_hat
        
        Delta_C_p_last = -states['C_p'][t-1] * ((sim['epsilon_measured'] * sim['Delta_P_last']) / (P0))
        
        states['C_p'][t] = states['C_p'][t-1] + Delta_C_p_last
        
        states['G'][t] = (1+g)*states['G'][t-1]
        
        sim['alpha'], sim['alpha_shock'] = model.update_alpha(
            sim['alpha'], sim['alpha_shock'], shock_sigma, shock_persist, sim['mu']
        )
        
        sim['Delta_C_p_hist'].append(Delta_C_p_last.copy())
        
        if len(sim['Delta_C_p_hist']) > 1:
            sim['Delta2_C_p_hist'].append(sim['Delta_C_p_hist'][-1] - sim['Delta_C_p_hist'][-2])
        
        sim['Delta_C_p_forecaster'].add_observation(Delta_C_p_last)
        if len(sim['Delta2_C_p_hist']) > 0:
            sim['Delta2_C_p_forecaster'].add_observation(sim['Delta2_C_p_hist'][-1])
        
        if len(sim['Delta_C_p_hist']) < W:
            Delta_C_p_hat = Delta_C_p_last.copy()
            Delta2_C_p_hat = np.zeros(n)
        else:
            sim['Delta_C_p_forecaster'].fit()
            sim['Delta2_C_p_forecaster'].fit()
            
            Delta_C_p_hat = sim['Delta_C_p_forecaster'].predict(Delta_C_p_last)
            
            if len(sim['Delta2_C_p_hist']) >= 2:
                last_delta2 = sim['Delta2_C_p_hist'][-1]
                Delta2_C_p_hat = sim['Delta2_C_p_forecaster'].predict(last_delta2)
            else:
                Delta2_C_p_hat = np.zeros(n)
        
        Delta_K_e = B @ model.neumann(A, Delta_C_p_hat + g*states['G'][t] + B @ model.neumann(A, Delta2_C_p_hat + (g**2)*states['G'][t], k), k)
        
        Delta_K_u = -np.minimum(Delta_K_e, states['K_u'][t])
        
        states['I'][t] = Delta @ states['K'][t] + (Delta_K_e + Delta_K_u)
        
        states['F'][t] = states['C_p'][t] + states['I'][t] + states['G'][t]
        
        states['X'][t] = model.neumann(A, states['F'][t], k)
        
        Taxes = (1 - tau)*P0 @ (states['I'][t] + states['G'][t])
        
        Y_income = sim['wL'] @ states['X'][t] - Taxes
        
        states['C_0'][t] = sim['alpha'] * Y_income / P0
        
        states['ED'][t] = states['C_0'][t] - states['C_p'][t]
        
        Delta_P = P0 * (-states['ED'][t] / (sim['epsilon'] * states['C_0'][t]))
        
        P = P0 + Delta_P
        
        states['C'][t] = sim['alpha'] * Y_income / P
        
        states['AD'][t] = states['C'][t] + states['I'][t] + states['G'][t]
        
        states['X_max'][t] = sim['B_inv'] @ states['K'][t]
        
        states['F_c'][t] = (np.eye(n) - A) @ states['X_max'][t]
        
        sim['Debt'] += P0 @ (states['G'][t] + states['I'][t]) - Taxes
        
        sim['Delta_K_e_last'] = Delta_K_e.copy()
        
        sim['Delta_P_last'] = Delta_P.copy()
    
    logger.info("Simulation loop complete")
    logger.info("=" * 60)
    logger.info("")
    
    return sim


def compute_results(sim):
    logger = logging.getLogger(__name__)
    logger.info("Computing results...")
    
    states = sim['states']
    P0_real = sim['P0_real']
    T = sim['T']
    W = sim['W']
    
    GDP_real = np.sum(P0_real * states['F'], axis=1)
    Capacity = np.sum(P0_real * states['F_c'], axis=1)
    C_plan_value = np.sum(P0_real * states['C_p'], axis=1)
    C_value = np.sum(P0_real * states['C'], axis=1)
    G_value = np.sum(P0_real * states['G'], axis=1)
    AD_value = np.sum(P0_real * states['AD'], axis=1)
    I_value = np.sum(P0_real * states['I'], axis=1)
    
    Output_Gap = 100 * ((GDP_real - Capacity) / Capacity)
    Capacity_Utilization = 100 * GDP_real / Capacity
    
    excess_demand = 100 * np.mean((C_value - C_plan_value) / C_value)
    mean_abs_output_gap = np.mean(np.abs(Output_Gap[12:72]))
    
    Final = P0_real @ states['F'][T-1]
    Initial = P0_real @ states['F'][0]
    Growth = (Final / Initial)**(12/T) - 1
    
    Debt_to_GDP_ratio = (sim['Debt'] * 100) / Final
    
    logger.info(f"Excess demand: {excess_demand:.4f}%")
    logger.info(f"Mean absolute output gap: {mean_abs_output_gap:.4f}%")
    logger.info(f"Annual growth rate: {Growth*100:.4f}%")
    logger.info(f"Debt to GDP ratio: {Debt_to_GDP_ratio:.4f}%")
    
    return {
        'GDP_real': GDP_real,
        'Capacity': Capacity,
        'C_plan_value': C_plan_value,
        'C_value': C_value,
        'G_value': G_value,
        'AD_value': AD_value,
        'I_value': I_value,
        'Output_Gap': Output_Gap,
        'Capacity_Utilization': Capacity_Utilization,
        'excess_demand': excess_demand,
        'mean_abs_output_gap': mean_abs_output_gap,
        'Growth': Growth,
        'Debt_to_GDP_ratio': Debt_to_GDP_ratio,
        'T': T,
        'W': W
    }


def save_results_csv(results, states, outdir):
    logger = logging.getLogger(__name__)
    logger.info("Saving results to CSV...")
    
    W = results['W']
    T = results['T']
    
    aggregate_df = pd.DataFrame({
        'Time': range(W, T),
        'GDP_real': results['GDP_real'][W:T],
        'Capacity': results['Capacity'][W:T],
        'Output_Gap': results['Output_Gap'][W:T],
        'Capacity_Utilization': results['Capacity_Utilization'][W:T],
        'C_value': results['C_value'][W:T],
        'C_plan_value': results['C_plan_value'][W:T],
        'I_value': results['I_value'][W:T],
        'G_value': results['G_value'][W:T],
        'AD_value': results['AD_value'][W:T]
    })
    aggregate_df.to_csv(os.path.join(outdir, 'aggregate_results.csv'), index=False)
    
    summary_df = pd.DataFrame({
        'Metric': [
            'Excess Demand (%)',
            'Mean Absolute Output Gap (%)',
            'Annual Growth Rate (%)',
            'Debt to GDP Ratio (%)'
        ],
        'Value': [
            results['excess_demand'],
            results['mean_abs_output_gap'],
            results['Growth'] * 100,
            results['Debt_to_GDP_ratio']
        ]
    })
    summary_df.to_csv(os.path.join(outdir, 'summary_statistics.csv'), index=False)
    
    logger.info(f"CSV files saved to {outdir}")


def main():
    parser = argparse.ArgumentParser(
        description='Input-Output Planning Model Simulation'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory (overrides config file)'
    )
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    if args.output_dir:
        config['output_dir'] = args.output_dir
    outdir = config.get('output_dir', 'simulation_outputs')
    
    logger = setup_logging(outdir)
    
    logger.info("=" * 60)
    logger.info("IO PLANNING MODEL SIMULATION")
    logger.info("=" * 60)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Configuration file: {args.config}")
    logger.info(f"Output directory: {outdir}")
    logger.info("")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        plotting.setup_plot_style(config)

        data = data_loader.load_all_data(config, script_dir)

        convergence_results = model.test_neumann_convergence(
            data['A'],
            data['C_household'] / (model.neumann(data['A'].T, data['va_per_unit'], config['k'])),
            config['neumann_max_k'],
            config['neumann_tolerance']
        )
        plotting.plot_neumann_convergence(convergence_results, outdir, config.get('plot_dpi', 300))
        
        sim = initialize_simulation(config, data)
        
        sim = run_simulation(config, sim)

        results = compute_results(sim)
        
        if config.get('save_csv', True):
            save_results_csv(results, sim['states'], outdir)
        
        if config.get('save_plots', True):
            plotting.generate_all_plots(results, config, outdir)
        
        logger.info("=" * 60)
        logger.info("SIMULATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"All outputs saved to: {outdir}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Simulation failed with error: {str(e)}", exc_info=True)
        raise
if __name__ == "__main__":
    main()