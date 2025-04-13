import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

def plot_to_base64(plot_func, *args, **kwargs):
    """Convert a matplotlib plot to a base64 string for web display"""
    # Create a figure at a standard size and resolution
    plt.figure(figsize=(10, 6), dpi=100)
    plot_func(*args, **kwargs)
    
    # Save plot to an in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    
    # Convert to base64 for embedding in HTML
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return img_base64

def plot_learning_curve(task_data):
    """Create a line chart showing how performance improves with practice"""
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
    """Create a standard bar chart with customizable labels"""
    plt.bar(categories, values, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

def generate_task_completion_chart(task_data):
    """Create a color-coded bar chart of task success rates"""
    def plot_completion_rates():
        task_names = [task['taskName'] for task in task_data]
        success_rates = [task['successRate'] for task in task_data]
        
        # Color bars by success level (red, orange, or green)
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
    """Create a bar chart showing error frequency by task"""
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
    """Calculate user interaction rates (per minute)"""
    # Handle edge cases
    if not interaction_data or duration_seconds <= 0:
        return {
            "clicks": 0,
            "keyPresses": 0,
            "mouseMoves": 0,
            "scrolls": 0
        }
    
    # Count each interaction type
    clicks = sum(1 for e in interaction_data if e.get('type') == 'mouse_click')
    key_presses = sum(1 for e in interaction_data if e.get('type') == 'key_press')
    mouse_moves = sum(1 for e in interaction_data if e.get('type') == 'mouse_move')
    scrolls = sum(1 for e in interaction_data if e.get('type') == 'scroll')
    
    # Convert to per-minute rates
    duration_minutes = duration_seconds / 60
    
    return {
        "clicks": round(clicks / duration_minutes, 2),
        "keyPresses": round(key_presses / duration_minutes, 2),
        "mouseMoves": round(mouse_moves / duration_minutes, 2),
        "scrolls": round(scrolls / duration_minutes, 2)
    }