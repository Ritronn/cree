"""
Train the Adaptive Learning ML Model
Generates synthetic training data and trains a Random Forest classifier
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib


def generate_training_data(n_samples=1000):
    """
    Generate synthetic training data for adaptive learning
    
    Features:
    1. accuracy (0-100)
    2. avg_time_per_question (10-120 seconds)
    3. first_attempt_correct (0-100)
    4. current_difficulty (1-3)
    5. sessions_completed (1-50)
    6. score_trend (-50 to +50)
    7. mastery_level (0-1)
    8. is_new_topic (0 or 1)
    
    Target:
    - next_difficulty (1, 2, or 3)
    """
    np.random.seed(42)
    
    data = []
    
    for _ in range(n_samples):
        # Generate features
        current_difficulty = np.random.randint(1, 4)
        sessions_completed = np.random.randint(1, 51)
        is_new_topic = 1 if sessions_completed == 1 else 0
        
        # Generate correlated features
        if is_new_topic:
            accuracy = np.random.uniform(30, 70)
            mastery_level = np.random.uniform(0, 0.3)
        else:
            accuracy = np.random.uniform(40, 95)
            mastery_level = np.random.uniform(0.2, 1.0)
        
        first_attempt_correct = accuracy + np.random.uniform(-10, 10)
        first_attempt_correct = np.clip(first_attempt_correct, 0, 100)
        
        avg_time = np.random.uniform(20, 100)
        score_trend = np.random.uniform(-30, 30)
        
        # Determine next difficulty based on rules
        if is_new_topic:
            next_difficulty = 1
        elif accuracy >= 85 and sessions_completed >= 2:
            next_difficulty = min(3, current_difficulty + 1)
        elif accuracy < 50:
            next_difficulty = max(1, current_difficulty - 1)
        elif score_trend > 10 and accuracy >= 70:
            next_difficulty = min(3, current_difficulty + 1)
        elif score_trend < -10:
            next_difficulty = max(1, current_difficulty - 1)
        else:
            next_difficulty = current_difficulty
        
        data.append([
            accuracy,
            avg_time,
            first_attempt_correct,
            current_difficulty,
            sessions_completed,
            score_trend,
            mastery_level,
            is_new_topic,
            next_difficulty
        ])
    
    columns = [
        'accuracy',
        'avg_time_per_question',
        'first_attempt_correct',
        'current_difficulty',
        'sessions_completed',
        'score_trend',
        'mastery_level',
        'is_new_topic',
        'next_difficulty'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    return df


def train_model():
    """Train the Random Forest model"""
    print("Generating training data...")
    df = generate_training_data(n_samples=2000)
    
    # Save training data
    data_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'training_data.csv')
    df.to_csv(data_path, index=False)
    print(f"Training data saved to {data_path}")
    
    # Split features and target
    X = df.drop('next_difficulty', axis=1)
    y = df['next_difficulty']
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train Random Forest
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Level 1', 'Level 2', 'Level 3']))
    
    # Feature importance
    print("\nFeature Importance:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(feature_importance)
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'adaptive_model.pkl')
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")
    
    return model


if __name__ == '__main__':
    print("=" * 60)
    print("Adaptive Learning ML Model Training")
    print("=" * 60)
    
    # Create ml_models directory if it doesn't exist
    ml_models_dir = os.path.join(os.path.dirname(__file__), 'ml_models')
    os.makedirs(ml_models_dir, exist_ok=True)
    
    # Train model
    model = train_model()
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run migrations: python manage.py makemigrations adaptive_learning")
    print("2. Apply migrations: python manage.py migrate")
    print("3. Start Django server: python manage.py runserver")
    print("4. Start React frontend: cd frontend && npm run dev")
