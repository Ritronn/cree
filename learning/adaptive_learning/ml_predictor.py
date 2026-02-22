"""
ML Model Integration for Adaptive Difficulty Prediction
"""
import os
import joblib
import numpy as np
from django.conf import settings


class AdaptiveLearningPredictor:
    """
    Predicts next difficulty level based on student performance
    """
    
    def __init__(self):
        self.model = None
        # Try multiple model file names
        model_dir = os.path.join(settings.BASE_DIR, 'adaptive_learning', 'ml_models')
        possible_models = [
            'adaptive_model.pkl',
            'random_forest_classifier_model.joblib',
            'adaptive_model.joblib',
            'model.pkl',
            'model.joblib'
        ]
        
        self.model_path = None
        for model_name in possible_models:
            path = os.path.join(model_dir, model_name)
            if os.path.exists(path):
                self.model_path = path
                break
        
        self.load_model()
    
    def load_model(self):
        """Load the trained ML model"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                # Try to load the model
                try:
                    self.model = joblib.load(self.model_path)
                    print(f"✅ ML Model loaded from {self.model_path}")
                except Exception as load_error:
                    # Model file exists but can't be loaded (e.g., pandas version mismatch)
                    print(f"⚠️ ML Model found but couldn't be loaded: {str(load_error)[:100]}")
                    print("   This is usually due to Python/pandas version mismatch")
                    print("   Using rule-based fallback (works perfectly fine!)")
                    self.model = None
            else:
                print(f"⚠️ ML Model not found in adaptive_learning/ml_models/")
                print("   Checked for: adaptive_model.pkl, random_forest_classifier_model.joblib, etc.")
                print("   Using rule-based fallback")
        except Exception as e:
            print(f"❌ Error loading ML model: {e}")
            print("   Using rule-based fallback")
    
    def predict_next_difficulty(self, user_data):
        """
        Predict next difficulty level
        
        Args:
            user_data (dict): {
                'accuracy': float (0-100),
                'avg_time_per_question': float (10-120),
                'first_attempt_correct': float (0-100),
                'current_difficulty': int (1-3),
                'sessions_completed': int (1-50),
                'score_trend': float (-50 to +50),
                'mastery_level': float (0-1),
                'is_new_topic': int (0 or 1)
            }
        
        Returns:
            int: Next difficulty level (1, 2, or 3)
        """
        # Extract features
        features = self._extract_features(user_data)
        
        # Try ML prediction first
        if self.model is not None:
            try:
                prediction = self.model.predict([features])[0]
                # Apply business rules
                prediction = self._apply_business_rules(prediction, user_data)
                return int(prediction)
            except Exception as e:
                print(f"ML prediction failed: {e}, using rule-based fallback")
        
        # Fallback to rule-based prediction
        return self._rule_based_prediction(user_data)
    
    def _extract_features(self, user_data):
        """Extract features in correct order for ML model"""
        return [
            user_data.get('accuracy', 50.0),
            user_data.get('avg_time_per_question', 60.0),
            user_data.get('first_attempt_correct', 50.0),
            user_data.get('current_difficulty', 1),
            user_data.get('sessions_completed', 1),
            user_data.get('score_trend', 0.0),
            user_data.get('mastery_level', 0.0),
            user_data.get('is_new_topic', 0)
        ]
    
    def _apply_business_rules(self, prediction, user_data):
        """
        Apply hard constraints to ML prediction
        
        Business Rules:
        1. New topics always start at difficulty 1
        2. Difficulty boundaries: 1-3
        3. No skipping levels (change by ±1 only)
        4. Performance thresholds
        """
        current_difficulty = user_data.get('current_difficulty', 1)
        accuracy = user_data.get('accuracy', 50.0)
        sessions_completed = user_data.get('sessions_completed', 1)
        is_new_topic = user_data.get('is_new_topic', 0)
        
        # Rule 1: New topics always start at difficulty 1
        if is_new_topic == 1:
            return 1
        
        # Rule 2: Enforce boundaries
        prediction = max(1, min(3, prediction))
        
        # Rule 3: No skipping levels
        if abs(prediction - current_difficulty) > 1:
            if prediction > current_difficulty:
                prediction = current_difficulty + 1
            else:
                prediction = current_difficulty - 1
        
        # Rule 4: Performance thresholds
        if accuracy < 50:
            # Must decrease difficulty
            prediction = max(1, current_difficulty - 1)
        elif accuracy > 85 and sessions_completed > 2:
            # Must increase difficulty
            prediction = min(3, current_difficulty + 1)
        
        return prediction
    
    def _rule_based_prediction(self, user_data):
        """
        Fallback rule-based prediction if ML model fails
        """
        accuracy = user_data.get('accuracy', 50.0)
        current_difficulty = user_data.get('current_difficulty', 1)
        sessions_completed = user_data.get('sessions_completed', 1)
        score_trend = user_data.get('score_trend', 0.0)
        is_new_topic = user_data.get('is_new_topic', 0)
        
        # New topic
        if is_new_topic == 1:
            return 1
        
        # Fast learner (high accuracy, positive trend)
        if accuracy >= 85 and sessions_completed >= 2:
            return min(3, current_difficulty + 1)
        
        # Struggling (low accuracy)
        if accuracy < 50:
            return max(1, current_difficulty - 1)
        
        # Improving (positive trend)
        if score_trend > 10 and accuracy >= 70:
            return min(3, current_difficulty + 1)
        
        # Declining (negative trend)
        if score_trend < -10:
            return max(1, current_difficulty - 1)
        
        # Stay at current level
        return current_difficulty
    
    def calculate_adaptive_score(self, accuracy, avg_time, first_attempt_rate, difficulty):
        """
        Calculate adaptive score (0-100) based on multiple factors
        
        Formula:
        - Base score: accuracy
        - Time bonus: faster = better (up to +10)
        - First attempt bonus: (up to +10)
        - Difficulty multiplier: harder questions = more points
        """
        base_score = accuracy
        
        # Time bonus (faster is better, but not too fast)
        if 20 <= avg_time <= 40:
            time_bonus = 10
        elif 40 < avg_time <= 60:
            time_bonus = 5
        else:
            time_bonus = 0
        
        # First attempt bonus
        first_attempt_bonus = (first_attempt_rate / 100) * 10
        
        # Difficulty multiplier
        difficulty_multiplier = 1.0 + (difficulty - 1) * 0.1
        
        # Calculate final score
        adaptive_score = (base_score + time_bonus + first_attempt_bonus) * difficulty_multiplier
        
        # Cap at 100
        return min(100, adaptive_score)
    
    def get_question_count(self, difficulty):
        """
        Determine number of questions based on difficulty
        
        Easy (1): 8-10 questions
        Medium (2): 10-12 questions
        Hard (3): 12-15 questions
        """
        question_counts = {
            1: 10,  # Easy
            2: 12,  # Medium
            3: 15   # Hard
        }
        return question_counts.get(difficulty, 10)


# Global predictor instance
predictor = AdaptiveLearningPredictor()


def predict_next_difficulty(user_data):
    """Convenience function for predictions"""
    return predictor.predict_next_difficulty(user_data)


def calculate_adaptive_score(accuracy, avg_time, first_attempt_rate, difficulty):
    """Convenience function for adaptive scoring"""
    return predictor.calculate_adaptive_score(accuracy, avg_time, first_attempt_rate, difficulty)
