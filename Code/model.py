import numpy as np
import logging

logger = logging.getLogger(__name__) 

def neumann(A, v, k):
    x = v.copy()
    term = v.copy()
    for _ in range(1, k):
        term = A @ term
        x += term
    return x

def update_alpha(alpha_prev, shock_prev, sigma, persist, mu):
    n = len(alpha_prev)
    eps = np.random.normal(0.0, sigma, size=n)
    shock = persist * shock_prev + eps

    alpha_tilde = alpha_prev * np.exp(mu + shock)
    alpha_tilde /= alpha_tilde.sum()

    return alpha_tilde, shock

def fit_ar1_gaussian(series):
    x = np.array(series[:-1])
    y = np.array(series[1:])
    
    Xmat = np.column_stack([x, np.ones(len(x))])
    beta = np.linalg.lstsq(Xmat, y, rcond=None)[0]
    
    phi = beta[0]
    c = beta[1]
    
    residuals = y - (phi * x + c)
    sigma = np.std(residuals, ddof=1)
    
    return phi, c, sigma

def test_neumann_convergence(A, test_vector, k_max, tolerance):
    logger.info("Testing Neumann series convergence...")
    
    d_norm = np.linalg.norm(test_vector)
    x = test_vector.copy()
    term = test_vector.copy()
    errors = []
    converged = False
    converged_k = None

    for k in range(1, k_max + 1):
        term = A @ term
        x += term
        error = np.linalg.norm(term) / d_norm * 100
        errors.append(error)
        
        if error < tolerance * 100 and not converged:
            logger.info(f"Converged at k = {k}, error = {error:.6f}%")
            converged = True
            converged_k = k
    
    if not converged:
        logger.warning(f"Did not converge within {k_max} iterations")
        logger.warning(f"Final error = {errors[-1]:.6f}%")
    
    return {
        'converged': converged,
        'converged_k': converged_k,
        'errors': errors,
        'final_error': errors[-1],
        'tolerance': tolerance * 100
    }

def initialize_state_arrays(T, n):
    return {
        'X': np.zeros((T, n)),      # Gross output
        'X_max': np.zeros((T, n)),   # Capacity (was 'C')
        'U': np.zeros((T, n)),      # Unutilized capacity
        'K': np.zeros((T, n)),      # Capital stock
        'K_e': np.zeros((T, n)),    # Expected capital requirement
        'I': np.zeros((T, n)),      # Investment
        'C_p': np.zeros((T, n)),    # Expected consumption demand (was 'd_ce')
        'C_0': np.zeros((T, n)),    # Initial consumption demand (was 'd_c_0')
        'C': np.zeros((T, n)),      # Actual consumption demand (was 'd_c')
        'F': np.zeros((T, n)),      # Final demand
        'ED': np.zeros((T, n)),     # Excess demand
        'K_u': np.zeros((T, n)),    # Unutilized capital
        'AD': np.zeros((T, n)),     # Aggregate demand
        'G': np.zeros((T, n)),      # Government expenditure
        'F_c': np.zeros((T, n))     # Capacity final demand
    }

def create_delta_matrix(config):
    n_heavy = config['n_heavy']
    n_medium = config['n_medium']
    n_light = config['n_light']
    
    # Annual depreciation rates
    delta_heavy_annual = (config['delta_heavy_min'], config['delta_heavy_max'])
    delta_medium_annual = (config['delta_medium_min'], config['delta_medium_max'])
    delta_light_annual = (config['delta_light_min'], config['delta_light_max'])
    
    # Convert to monthly
    delta_heavy = np.random.uniform(*delta_heavy_annual, n_heavy) / 12
    delta_medium = np.random.uniform(*delta_medium_annual, n_medium) / 12
    delta_light = np.random.uniform(*delta_light_annual, n_light) / 12
    
    # Concatenate and create diagonal matrix
    delta_vec = np.concatenate([delta_heavy, delta_medium, delta_light])
    Delta = np.diag(delta_vec)
    
    logger.info(f"Created depreciation matrix with rates: "
                f"heavy={np.mean(delta_heavy)*12:.3f}, "
                f"medium={np.mean(delta_medium)*12:.3f}, "
                f"light={np.mean(delta_light)*12:.3f} (annual)")
    
    return Delta

def create_capital_intensity_matrix(config):
    n_heavy = config['n_heavy']
    n_medium = config['n_medium']
    n_light = config['n_light']
    
    heavy_diag = np.random.uniform(
        config['heavy_diag_min'],
        config['heavy_diag_max'],
        n_heavy
    )
    medium_diag = np.random.uniform(
        config['medium_diag_min'],
        config['medium_diag_max'],
        n_medium
    )
    light_diag = np.random.uniform(
        config['light_diag_min'],
        config['light_diag_max'],
        n_light
    )
    
    all_diag = np.concatenate([heavy_diag, medium_diag, light_diag])
    B = np.diag(all_diag)
    B_inv = np.linalg.inv(B)
    
    logger.info(f"Created capital intensity matrix with means: "
                f"heavy={np.mean(heavy_diag):.3f}, "
                f"medium={np.mean(medium_diag):.3f}, "
                f"light={np.mean(light_diag):.3f}")
    
    return B, B_inv

def create_mu_vector(config):
    n = config['n']
    n_heavy = config['n_heavy']
    n_medium = config['n_medium']
    
    mu = np.zeros(n)
    mu[:n_heavy] = config['mu_heavy']
    mu[n_heavy:n_heavy+n_medium] = config['mu_medium']
    mu[n_heavy+n_medium:] = config['mu_light']
    
    return mu


class AR1Forecaster:
    """
    AR(1) forecasting system that fits V(t+1) = phi*V(t) + c + epsilon
    where epsilon ~ N(0, sigma)
    """
    def __init__(self, window_size):
        self.window_size = window_size
        self.history = []
        self.phi = None
        self.c = None
        self.sigma = None
        self.is_fitted = False
    
    def add_observation(self, value):
        """Add a new observation to history"""
        self.history.append(value.copy() if hasattr(value, 'copy') else value)
        
        # Keep only the last window_size observations
        if len(self.history) > self.window_size:
            self.history.pop(0)
    
    def fit(self):
        """Fit AR(1) model to current history"""
        if len(self.history) < 2:
            self.is_fitted = False
            return
        
        n_vars = len(self.history[0]) if hasattr(self.history[0], '__len__') else 1
        
        if n_vars == 1:
            # Univariate case
            x = np.array(self.history[:-1])
            y = np.array(self.history[1:])
            
            X = np.column_stack([x, np.ones(len(x))])
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            
            self.phi = beta[0]
            self.c = beta[1]
            self.sigma = np.std(y - (self.phi * x + self.c), ddof=1)
            
        else:
            # Multivariate case - fit independent AR(1) for each variable
            self.phi = np.zeros(n_vars)
            self.c = np.zeros(n_vars)
            self.sigma = np.zeros(n_vars)
            
            hist_array = np.array(self.history)
            
            for i in range(n_vars):
                x = hist_array[:-1, i]
                y = hist_array[1:, i]
                
                X = np.column_stack([x, np.ones(len(x))])
                beta = np.linalg.lstsq(X, y, rcond=None)[0]
                
                self.phi[i] = beta[0]
                self.c[i] = beta[1]
                self.sigma[i] = np.std(y - (self.phi[i] * x + self.c[i]), ddof=1)
        
        self.is_fitted = True
    
    def predict(self, last_value, n_steps=1):
        """
        Predict future values using the fitted AR(1) model
        V(t+1) = phi * V(t) + c
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        
        predictions = []
        current = last_value.copy() if hasattr(last_value, 'copy') else last_value
        
        for _ in range(n_steps):
            if hasattr(self.phi, '__len__'):
                # Multivariate case
                next_val = self.phi * current + self.c
            else:
                # Univariate case
                next_val = self.phi * current + self.c
            
            predictions.append(next_val)
            current = next_val
        
        return predictions[0] if n_steps == 1 else predictions
    
    def predict_with_uncertainty(self, last_value, n_steps=1, n_simulations=1000):
        """
        Predict with uncertainty intervals using Monte Carlo simulation
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        
        predictions = []
        for _ in range(n_simulations):
            sim_pred = []
            current = last_value.copy() if hasattr(last_value, 'copy') else last_value
            
            for _ in range(n_steps):
                if hasattr(self.phi, '__len__'):
                    noise = np.random.normal(0, self.sigma, len(self.phi))
                    next_val = self.phi * current + self.c + noise
                else:
                    noise = np.random.normal(0, self.sigma)
                    next_val = self.phi * current + self.c + noise
                
                sim_pred.append(next_val)
                current = next_val
            
            predictions.append(sim_pred)
        
        predictions = np.array(predictions)
        
        if n_steps == 1:
            mean_pred = np.mean(predictions[:, 0], axis=0)
            lower_pred = np.percentile(predictions[:, 0], 5, axis=0)
            upper_pred = np.percentile(predictions[:, 0], 95, axis=0)
        else:
            mean_pred = np.mean(predictions, axis=0)
            lower_pred = np.percentile(predictions, 5, axis=0)
            upper_pred = np.percentile(predictions, 95, axis=0)
        
        return {
            'mean': mean_pred,
            'lower_5': lower_pred,
            'upper_95': upper_pred,
            'simulations': predictions
        }