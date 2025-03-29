"""
Object Detector - Responsible for detecting objects in images using YOLO model
"""
import cv2
import numpy as np
import time
import os
from ultralytics import YOLO
from config import DETECTION, PATHS, COLORS

class ObjectDetector:
    def __init__(self):
        """Initialize object detector"""
        # Load YOLO model
        self.model = None
        self.model_path = PATHS["model"]
        
        # Try to load the model
        self._load_model()
        
        # Detection settings
        self.confidence_threshold = DETECTION["confidence_threshold"]
        self.cooldown = DETECTION["cooldown"]
        self.last_detection_time = 0
        
        # Detection results
        self.detection_results = []
        self.detection_history = []
    
    def _load_model(self):
        """Load YOLO model with better error handling"""
        # Check if model file exists
        if not os.path.exists(self.model_path):
            print(f"Warning: Model file not found at {self.model_path}")
            print("Searching for alternative model files...")
            
            # Try to find yolo11x.pt or yolov8n.pt in the current directory
            for model_name in ["yolo11x.pt", "yolov8n.pt"]:
                if os.path.exists(model_name):
                    self.model_path = model_name
                    print(f"Found alternative model: {model_name}")
                    break
        
        try:
            print(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            print(f"Successfully loaded YOLO model")
            
            # Print model information
            print(f"Model type: {self.model.task}")
            print(f"Classes: {len(self.model.names)}")
            
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            print("Trying alternative method...")
            
            try:
                # Try loading with explicit task
                self.model = YOLO(self.model_path, task='detect')
                print("Successfully loaded YOLO model using alternative method")
            except Exception as e:
                print(f"Error loading YOLO model using alternative method: {e}")
                
                # Final fallback: Try with yolov8n.pt from Ultralytics
                try:
                    print("Trying to load default yolov8n model from Ultralytics...")
                    self.model = YOLO("yolov8n")
                    print("Successfully loaded default YOLO model")
                except Exception as e:
                    print(f"Critical error: Failed to load any YOLO model: {e}")
                    raise RuntimeError("Failed to load YOLO model")
    
    def detect_objects(self, frame):
        """Detect objects in image"""
        # Check if model was loaded
        if self.model is None:
            print("Model not loaded, trying to reload...")
            self._load_model()
            if self.model is None:
                return self.detection_results
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_detection_time < self.cooldown:
            return self.detection_results
        
        # Update last detection time
        self.last_detection_time = current_time
        
        # Use YOLO model for detection
        try:
            results = self.model(frame)
            
            # Get detection results
            detected_objects = []
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Get class ID and confidence
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Get class name
                    class_name = self.model.names[class_id]
                    
                    # Add to detection list if confidence is above threshold
                    if confidence > self.confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        detected_objects.append((class_name, confidence, (x1, y1, x2, y2)))
            
            # Sort by confidence
            detected_objects.sort(key=lambda x: x[1], reverse=True)
            
            # Update detection results
            self.detection_results = detected_objects[:10]  # Keep top 10 results
            
            # Update detection history
            if detected_objects:
                # Add only the highest confidence result to history
                self.detection_history.append(detected_objects[0][0])
                # Keep only recent history
                if len(self.detection_history) > DETECTION["history_size"]:
                    self.detection_history.pop(0)
            
            return self.detection_results
        
        except Exception as e:
            print(f"Error during object detection: {e}")
            return self.detection_results
    
    def check_target_found(self, target_object):
        """Check if target object is found"""
        # Check current detection results
        for obj, conf, _ in self.detection_results:
            if obj == target_object and conf > self.confidence_threshold:
                return True
        
        # Check history for consecutive detections
        if len(self.detection_history) >= DETECTION["required_consecutive"]:
            last_n = self.detection_history[-DETECTION["required_consecutive"]:]
            if all(obj == target_object for obj in last_n):
                return True
        
        return False
    
    def draw_detection_boxes(self, frame, target_object=None):
        """Draw detection boxes on image"""
        for i, (obj_name, confidence, box) in enumerate(self.detection_results):
            x1, y1, x2, y2 = box
            
            # Set color - green for target object, yellow for others
            if target_object and obj_name == target_object:
                color = COLORS["green"]
            else:
                color = COLORS["yellow"]
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{obj_name}: {confidence:.2f}"
            
            # Calculate text size and position
            text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            y_offset = max(y1 - 10, text_size[1] + 10)  # Ensure label is above box and within image
            
            # Draw label background
            cv2.rectangle(frame, 
                         (x1, y_offset - text_size[1] - 10), 
                         (x1 + text_size[0] + 10, y_offset), 
                         color, 
                         -1)
            
            # Draw label text
            cv2.putText(frame, 
                       label, 
                       (x1 + 5, y_offset - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, 
                       (0, 0, 0), 
                       1)
        
        return frame
    
    def get_detection_summary(self, max_items=5):
        """Get detection results summary"""
        if not self.detection_results:
            return "No objects detected"
        
        # Get names of top N detections
        objects = [obj[0] for obj in self.detection_results[:max_items]]
        
        # Add ellipsis if there are more results
        if len(self.detection_results) > max_items:
            objects.append("...")
        
        return "Detected: " + ", ".join(objects)
    
    def reset_history(self):
        """Reset detection history"""
        self.detection_history = [] 