import os
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
from django.conf import settings

class DeerClassifier:
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'core', 'ai_models', 'deer_classifier.tflite')
        self.input_size = (224, 224)  # Standard input size for many models
        self.confidence_threshold = 0.7  # Minimum confidence to apply a tag
        self.interpreter = None
        
        # Labels for our classifier
        self.labels = ['buck', 'doe']
        
        # Load model if it exists, otherwise use mock predictions
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            print("No model found, using mock predictions")
    
    def load_model(self):
        """Load the TFLite model."""
        try:
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.interpreter = None
    
    def preprocess_image(self, image_path):
        """Preprocess the image for model input."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to expected input size
                img = img.resize(self.input_size, Image.Resampling.LANCZOS)
                
                # Convert to numpy array and normalize
                img_array = np.array(img, dtype=np.float32)
                img_array = img_array / 255.0
                
                # Add batch dimension
                img_array = np.expand_dims(img_array, axis=0)
                
                return img_array
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def mock_predict(self, image_path):
        """Mock prediction function for testing without a real model."""
        # Use image hash to make "random" but consistent predictions
        try:
            with Image.open(image_path) as img:
                # Get a simple hash of the image
                img_hash = hash(img.tobytes())
                # Use hash to determine prediction
                is_buck = img_hash % 2 == 0
                
                # Generate mock confidence scores
                confidence = 0.7 + (img_hash % 1000) / 10000  # Between 0.7 and 0.8
                
                if is_buck:
                    return {'buck': confidence, 'doe': 1 - confidence}
                else:
                    return {'doe': confidence, 'buck': 1 - confidence}
        except Exception as e:
            print(f"Error in mock prediction: {e}")
            return None
    
    def predict(self, image_path):
        """Predict whether the image contains a buck or doe."""
        # If no real model is loaded, use mock predictions
        if self.interpreter is None:
            return self.mock_predict(image_path)
        
        try:
            # Preprocess image
            input_data = self.preprocess_image(image_path)
            if input_data is None:
                return None
            
            # Get input and output details
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()
            
            # Set input tensor
            self.interpreter.set_tensor(input_details[0]['index'], input_data)
            
            # Run inference
            self.interpreter.invoke()
            
            # Get prediction results
            output_data = self.interpreter.get_tensor(output_details[0]['index'])
            scores = output_data[0]
            
            # Convert to dictionary
            predictions = {
                self.labels[i]: float(score)
                for i, score in enumerate(scores)
            }
            
            return predictions
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None
    
    def get_best_prediction(self, predictions):
        """Get the highest confidence prediction above threshold."""
        if not predictions:
            return None, 0
        
        best_label = max(predictions.items(), key=lambda x: x[1])
        if best_label[1] >= self.confidence_threshold:
            return best_label
        return None, 0

# Global instance
classifier = DeerClassifier() 