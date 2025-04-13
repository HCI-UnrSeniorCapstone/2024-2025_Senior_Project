import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from matplotlib.figure import Figure

def plot_to_base64(plot_function):
    """Convert a matplotlib plot to base64 string"""
    # Create a new figure
    plt.figure(figsize=(10, 6))
    
    # Execute the plotting function
    plot_function()
    
    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    
    # Encode the image to base64 string
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    return img_str

def generate_task_completion_chart(task_data):
    """Generate a bar chart for task completion rates"""
    def plot_chart():
        task_names = [task['taskName'] for task in task_data]
        completion_rates = [task['successRate'] for task in task_data]
        
        plt.bar(task_names, completion_rates, color='#4CAF50')
        plt.xlabel('Tasks')
        plt.ylabel('Completion Rate (%)')
        plt.title('Task Completion Rates')
        plt.ylim(0, 100)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add percentage labels on top of each bar
        for i, rate in enumerate(completion_rates):
            plt.text(i, rate + 2, f'{rate:.1f}%', ha='center')
    
    return plot_to_base64(plot_chart)

def generate_error_rate_chart(task_data):
    """Generate a bar chart for error rates by task"""
    def plot_chart():
        task_names = [task['taskName'] for task in task_data]
        error_rates = [task.get('errorRate', 0) for task in task_data]
        
        plt.bar(task_names, error_rates, color='#F44336')
        plt.xlabel('Tasks')
        plt.ylabel('Error Rate')
        plt.title('Error Rates by Task')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add percentage labels on top of each bar
        for i, rate in enumerate(error_rates):
            plt.text(i, rate + 0.1, f'{rate:.2f}', ha='center')
    
    return plot_to_base64(plot_chart)

def plot_learning_curve(task_data):
    """Plot learning curve showing improvement over attempts"""
    colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#FF6D01', '#46BDC6']
    
    for i, (task_name, data) in enumerate(task_data.items()):
        color = colors[i % len(colors)]
        plt.plot(data['attempts'], data['times'], 'o-', label=task_name, color=color)
    
    plt.xlabel('Attempt Number')
    plt.ylabel('Completion Time (seconds)')
    plt.title('Learning Curve: Improvement Over Attempts')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

def calculate_interaction_metrics(tracking_data):
    """Calculate metrics from tracking data"""
    metrics = {
        'mouse_movements': len(tracking_data.get('mouse_movements', [])),
        'mouse_clicks': len(tracking_data.get('mouse_clicks', [])),
        'scrolls': len(tracking_data.get('scrolls', [])),
        'keystrokes': len(tracking_data.get('keystrokes', []))
    }
    
    # Calculate mouse travel distance if data available
    movements = tracking_data.get('mouse_movements', [])
    if len(movements) > 1:
        total_distance = 0
        prev_x, prev_y = movements[0]['x'], movements[0]['y']
        
        for movement in movements[1:]:
            curr_x, curr_y = movement['x'], movement['y']
            # Euclidean distance
            distance = ((curr_x - prev_x) ** 2 + (curr_y - prev_y) ** 2) ** 0.5
            total_distance += distance
            prev_x, prev_y = curr_x, curr_y
            
        metrics['mouse_travel_distance'] = total_distance
    
    return metrics
