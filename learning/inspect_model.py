import joblib
import os

model_path = 'adaptive_learning/ml_models/xgb_learning_state_classifier.joblib'
model = joblib.load(model_path)

print("Model type:", type(model))
print("Number of features expected:", model.n_features_in_)

if hasattr(model, 'feature_names_in_'):
    print("\nFeature names:")
    for i, name in enumerate(model.feature_names_in_):
        print(f"  {i}: {name}")
else:
    print("\nNo feature names stored in model")
    print(f"Model expects {model.n_features_in_} features")
