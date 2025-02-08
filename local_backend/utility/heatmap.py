# Purpose: Holds all functions related to generating heatmaps for mouse movement


import os
import csv
import cv2
import numpy as np
from PIL import ImageGrab
import time


def generate_heatmap(session_id, task, factor, logger):
    task_name = task['taskName'].replace(" ","")
    factor_name = factor['factorName'].replace(" ","")
    
    logger.debug("Capturing Screen! Please wait a moment...")

    # Taking screenshot
    time.sleep(1)
    screenshot_nm = f"screenshot_{session_id}_{task_name}_{factor_name}.png"
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_nm)

    screenshot = cv2.imread(screenshot_nm)

    # Extract mouse movement coordinates
    coordinates = extract_mouse_movements(f"./Session_{session_id}/{task_name}_{factor_name}/{session_id}_{task_name}_{factor_name}_MouseMovement_data.csv", logger)

    if coordinates:
        # Create the heatmap
        heatmap = create_heatmap(coordinates, screenshot.shape)

        # Overlay the heatmap on the screenshot
        overlay = overlay_heatmap(heatmap, screenshot)

        output_dir = os.path.join(f"Session_{session_id}", f"{task_name}_{factor_name}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the output
        heatmap_nm = f"{session_id}_{task_name}_{factor_name}_MouseMovement_heatmap.png"
        heatmap_output_path = os.path.join(output_dir, heatmap_nm)
        cv2.imwrite(heatmap_output_path, overlay)

        # removes the initial screenshot
        os.remove(screenshot_nm)
        
        logger.debug(f"heatmap has been saved")
    else:
        logger.warning(f"no mouse movement data found, abort heatmap creation")
    
        
def extract_mouse_movements(log_file, logger):
    coordinates = []
    try:
        with open(log_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skips the header
            for row in reader:
                x, y = int(row[2]), int(row[3])
                coordinates.append((x, y))
    except FileNotFoundError:
        logger.warning(f"mouse movement file not found")
    except Exception as e:
        logger.error(f"error reading mouse movement data")
        
    return coordinates


def create_heatmap(coordinates, screenshot_shape):
    heatmap = np.zeros(screenshot_shape[:2], dtype=np.float32)

    for (x, y) in coordinates:
        if 0 <= x < screenshot_shape[1] and 0 <= y < screenshot_shape[0]:
            heatmap[y, x] += 1

    # Apply Gaussian blur to smooth the heatmap
    heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)
    
    return heatmap


def overlay_heatmap(heatmap, screenshot):
    heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_colored = cv2.applyColorMap(
        heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)

    # Combine the heatmap with the original screenshot
    overlay = cv2.addWeighted(screenshot, 0.7, heatmap_colored, 0.3, 0)
    
    return overlay