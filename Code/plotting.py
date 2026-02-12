"""
Plotting and visualization functions for IO Planning Model.

This module handles all plot generation and styling.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import logging

logger = logging.getLogger(__name__)


def setup_plot_style(config):
    """
    Configure matplotlib style parameters.
    
    Parameters
    ----------
    config : dict
        Configuration dictionary containing plotting parameters
    """
    mpl.rcParams.update({
        # Font
        "font.family": "serif",
        "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        # Sizes
        "font.size": config.get('font_size', 11),
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        # Lines & markers
        "lines.linewidth": config.get('line_width', 1.2),
        "lines.markersize": config.get('marker_size', 4),
        # Figure
        "figure.figsize": (config.get('figure_width', 6.5), 
                          config.get('figure_height', 4)),
        "figure.dpi": config.get('figure_dpi', 150),
        # Axes
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False
    })
    logger.info("Plot style configured")


def save_plot(data, title, filename, outdir, zero_line=False, ylim=None, 
              marker="o", linestyle="-", markevery=1, skip_points=1, dpi=300):
    """
    Create and save a single-series plot.
    
    Parameters
    ----------
    data : ndarray
        Data to plot
    title : str
        Plot title
    filename : str
        Output filename
    outdir : str
        Output directory
    zero_line : bool, optional
        Whether to add a horizontal line at y=0
    ylim : tuple, optional
        Y-axis limits (min, max)
    marker : str, optional
        Marker style
    linestyle : str, optional
        Line style
    markevery : int, optional
        Marker frequency
    skip_points : int, optional
        Show every (skip_points+1)th point
    dpi : int, optional
        Resolution for saved figure
    """
    fig, ax = plt.subplots()
    
    # Reduce data density if requested
    if skip_points > 0:
        indices = np.arange(0, len(data), skip_points + 1)
        plot_data = data[indices]
        x_vals = np.arange(len(data))[indices]
        ax.plot(x_vals, plot_data, marker=marker, linestyle=linestyle, 
                markevery=1)
    else:
        ax.plot(data, marker=marker, linestyle=linestyle, markevery=markevery)
    
    if zero_line:
        ax.axhline(0, linestyle="--", linewidth=0.8, alpha=0.6)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.set_xlabel("Time")
    ax.set_title(title)
    fig.tight_layout()
    
    filepath = os.path.join(outdir, filename)
    fig.savefig(filepath, dpi=dpi)
    plt.close(fig)
    logger.info(f"Saved plot: {filename}")


def save_plot_three(series1, series2, series3, label1, label2, label3, 
                   title, filename, outdir, zero_line=False, skip_points=1, 
                   dpi=300):
    """
    Create and save a three-series comparison plot.
    
    Parameters
    ----------
    series1, series2, series3 : ndarray
        Data series to plot
    label1, label2, label3 : str
        Labels for each series
    title : str
        Plot title
    filename : str
        Output filename
    outdir : str
        Output directory
    zero_line : bool, optional
        Whether to add a horizontal line at y=0
    skip_points : int, optional
        Show every (skip_points+1)th point
    dpi : int, optional
        Resolution for saved figure
    """
    fig, ax = plt.subplots()
    
    # Helper function to apply skipping
    def skip_data(data, skip):
        if skip > 0:
            indices = np.arange(0, len(data), skip + 1)
            plot_data = data[indices]
            x_vals = np.arange(len(data))[indices]
            return x_vals, plot_data
        return np.arange(len(data)), data
    
    x1, y1 = skip_data(series1, skip_points)
    x2, y2 = skip_data(series2, skip_points)
    x3, y3 = skip_data(series3, skip_points)
    
    ax.plot(x1, y1, label=label1, marker="o", linestyle="-", markevery=1)
    ax.plot(x2, y2, label=label2, marker="s", linestyle="--", markevery=1)
    ax.plot(x3, y3, label=label3, marker="^", linestyle=":", markevery=1)
    
    if zero_line:
        ax.axhline(0, linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_xlabel("Time")
    ax.set_ylabel("Euros (constant prices)")
    ax.set_title(title)
    ax.legend(frameon=False, loc="best")
    
    from matplotlib.ticker import ScalarFormatter
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0, 0))
    ax.yaxis.set_major_formatter(formatter)
    
    fig.tight_layout()
    
    filepath = os.path.join(outdir, filename)
    fig.savefig(filepath, dpi=dpi)
    plt.close(fig)
    logger.info(f"Saved plot: {filename}")


def plot_neumann_convergence(convergence_results, outdir, dpi=300):
    """
    Plot Neumann series convergence test results.
    
    Parameters
    ----------
    convergence_results : dict
        Results from test_neumann_convergence()
    outdir : str
        Output directory
    dpi : int, optional
        Resolution for saved figure
    """
    errors = convergence_results['errors']
    tolerance = convergence_results['tolerance']
    
    fig, ax = plt.subplots(figsize=(7, 4))
    iterations = list(range(1, len(errors) + 1))
    ax.plot(iterations, errors, 'b-o', linewidth=2, markersize=4)
    ax.axhline(y=tolerance, color='r', linestyle='--', 
               label=f'Tolerance = {tolerance:.1f}%')
    ax.set_xlabel('Iteration (k)')
    ax.set_ylabel('Relative Error (%)')
    ax.set_title(f'Neumann Convergence (tolerance = {tolerance/100})')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    
    filepath = os.path.join(outdir, "neumann_convergence.png")
    plt.savefig(filepath, dpi=dpi)
    plt.close()
    logger.info(f"Saved convergence plot: neumann_convergence.png")


def quarterly_average(series, start=0):
    """
    Convert monthly series to quarterly averages.
    
    Parameters
    ----------
    series : ndarray
        Monthly time series
    start : int, optional
        Starting index
        
    Returns
    -------
    ndarray
        Quarterly averaged series
    """
    trimmed = series[start:]
    n_quarters = len(trimmed) // 3
    return trimmed[:3*n_quarters].reshape(n_quarters, 3).mean(axis=1)


def generate_all_plots(results, config, outdir):
    """
    Generate all simulation output plots.
    
    Parameters
    ----------
    results : dict
        Dictionary containing simulation results
    config : dict
        Configuration dictionary
    outdir : str
        Output directory
    """
    if not config.get('save_plots', True):
        logger.info("Plot generation disabled in config")
        return
    
    logger.info("Generating plots...")
    
    W = config['W']
    T = results['T']
    dpi = config.get('plot_dpi', 300)
    skip = config.get('plot_skip_points', 1)
    
    # Extract results
    G_value = results['G_value']
    C_value = results['C_value']
    C_plan_value = results['C_plan_value']
    I_value = results['I_value']
    Output_Gap = results['Output_Gap']
    Capacity_Utilization = results['Capacity_Utilization']
    GDP_real = results['GDP_real']
    Capacity = results['Capacity']
    AD_value = results['AD_value']
    
    # Individual plots
    save_plot(G_value[W:T], "Government Expenditure (real value)", 
              "Government.png", outdir, zero_line=True, skip_points=skip, dpi=dpi)
    
    save_plot(C_value[W:T], "Consumption (real value)", 
              "Consumption.png", outdir, zero_line=True, skip_points=skip, dpi=dpi)
    
    save_plot(100*(C_value[W:T] - C_plan_value[W:T])/(C_plan_value[W:T]), 
              "Excess demand percentage(%)", "Excess_demand.png", outdir, 
              zero_line=True, skip_points=skip, dpi=dpi)
    
    save_plot(I_value[W:T], "Investment (real value)", 
              "Investment.png", outdir, zero_line=True, skip_points=skip, dpi=dpi)
    
    save_plot(Output_Gap[W:T], "Output Gap Percentage (%)", 
              "Output_gap.png", outdir, zero_line=True, skip_points=skip, dpi=dpi)
    
    save_plot(Capacity_Utilization[W:T], "Capacity utilization (%)", 
              "Utilization.png", outdir, zero_line=True, skip_points=skip, dpi=dpi)
    
    # Three-series plots
    save_plot_three(
        GDP_real[W:T], Capacity[W:T], AD_value[W:T], 
        label1="Real GDP",
        label2="Potential GDP",
        label3="Aggregate Demand",
        title="GDP, Potential GDP, and Aggregate Demand",
        filename="GDP_Capacity_AD.png",
        outdir=outdir,
        zero_line=False,
        skip_points=skip,
        dpi=dpi
    )
    
    # Quarterly plots
    GDP_q = quarterly_average(GDP_real, start=W)
    Capacity_q = quarterly_average(Capacity, start=W)
    AD_q = quarterly_average(AD_value, start=W)
    
    save_plot_three(
        GDP_q, Capacity_q, AD_q,
        label1="Real GDP (quarterly avg)",
        label2="Potential GDP (quarterly avg)",
        label3="Aggregate Demand (quarterly avg)",
        title="GDP, Potential GDP, and Aggregate Demand (Quarterly)",
        filename="GDP_Capacity_AD_quarterly.png",
        outdir=outdir,
        zero_line=False,
        dpi=dpi
    )
    
    logger.info(f"All plots saved to {outdir}")
