import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

def plot_to_base64(plot_func, *args, **kwargs):
    """
    Convert a matplotlib plot to a base64 encoded string
    
    Args:
        plot_func: Function that creates the plot
        *args: Arguments to pass to plot_func
        **kwargs: Keyword arguments to pass to plot_func
        
    Returns:
        Base64 encoded string of the plot image
    """
    # Create a figure and call the plot function
    plt.figure(figsize=(10, 6), dpi=100)
    plot_func(*args, **kwargs)
    
    # Save the figure to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    
    # Convert to base64
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return img_base64

def plot_learning_curve(task_data):
    """
    Plot learning curve for tasks
    
    Args:
        task_data: Dictionary of task data with attempts and completion times
    """
    for task_name, data in task_data.items():
        attempts = data['attempts']
        times = data['times']
        plt.plot(attempts, times, 'o-', label=task_name)
    
    plt.xlabel('Attempt Number')
    plt.ylabel('Completion Time (s)')
    plt.title('Learning Curve: Completion Time vs Attempt')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

def plot_bar_chart(categories, values, title, xlabel, ylabel, color='#1976D2'):
    """
    Create a bar chart
    
    Args:
        categories: List of category labels
        values: List of values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Bar color
    """
    plt.bar(categories, values, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

def generate_task_completion_chart(task_data):
    """
    Generate a bar chart showing task completion rates
    
    Args:
        task_data: List of task data with success rates
        
    Returns:
        Base64 encoded string of the chart image
    """
    def plot_completion_rates():
        task_names = [task['taskName'] for task in task_data]
        success_rates = [task['successRate'] for task in task_data]
        
        # Define colors based on success rate
        colors = ['#f44336' if rate < 50 else 
                '#ff9800' if rate < 70 else
                '#4caf50' for rate in success_rates]
        
        plt.bar(task_names, success_rates, color=colors)
        plt.xlabel('Task')
        plt.ylabel('Success Rate (%)')
        plt.title('Task Completion Rates')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
    
    return plot_to_base64(plot_completion_rates)

def generate_error_rate_chart(task_data):
    """
    Generate a bar chart showing error rates by task
    
    Args:
        task_data: List of task data with error rates
        
    Returns:
        Base64 encoded string of the chart image
    """
    def plot_error_rates():
        task_names = [task['taskName'] for task in task_data]
        error_rates = [task['errorRate'] for task in task_data]
        
        plt.bar(task_names, error_rates, color='#FFC107')
        plt.xlabel('Task')
        plt.ylabel('Error Rate (errors/min)')
        plt.title('Error Rate by Task')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
    
    return plot_to_base64(plot_error_rates)

def calculate_interaction_metrics(interaction_data, duration_seconds):
    """
    Calculate interaction metrics per minute
    
    Args:
        interaction_data: List of interaction events
        duration_seconds: Total duration in seconds
        
    Returns:
        Dictionary of interaction metrics
    """
    if not interaction_data or duration_seconds <= 0:
        return {
            "clicks": 0,
            "keyPresses": 0,
            "mouseMoves": 0,
            "scrolls": 0
        }
    
    # Count events by type
    clicks = sum(1 for e in interaction_data if e.get('type') == 'mouse_click')
    key_presses = sum(1 for e in interaction_data if e.get('type') == 'key_press')
    mouse_moves = sum(1 for e in interaction_data if e.get('type') == 'mouse_move')
    scrolls = sum(1 for e in interaction_data if e.get('type') == 'scroll')
    
    # Convert to per minute
    duration_minutes = duration_seconds / 60
    
    return {
        "clicks": round(clicks / duration_minutes, 2),
        "keyPresses": round(key_presses / duration_minutes, 2),
        "mouseMoves": round(mouse_moves / duration_minutes, 2),
        "scrolls": round(scrolls / duration_minutes, 2)
    }