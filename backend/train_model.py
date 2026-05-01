import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os

def train_model():
    # Load training data
    df = pd.read_csv('../data/training_data.csv')
    
    # Remove rows with missing labels
    df = df.dropna(subset=['label'])
    
    if len(df) < 10:
        print(f"Not enough training data. Only {len(df)} rows. Need at least 10.")
        print("Generate more data first by running the data collector.")
        return False
    
    # Features (exclude timestamp and label)
    feature_cols = [col for col in df.columns if col not in ['timestamp', 'label']]
    X = df[feature_cols]
    y = df['label']
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Evaluate
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    print(f"Model trained! Accuracy: {accuracy:.2%}")
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\nTop 5 features:")
    print(importance.head())
    
    # Save model
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("Model saved as model.pkl")
    return True

def generate_sample_training_data():
    """Generate synthetic training data for testing"""
    import random
    from datetime import datetime, timedelta
    
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(100):
        timestamp = start_date + timedelta(minutes=15 * i)
        
        # Generate random features
        basket_momentum = random.uniform(-5, 5)
        momentum_strength = abs(basket_momentum) + random.uniform(0, 2)
        avg_relative_volume = random.uniform(0.5, 2.5)
        volume_spike_ratio = 1 if avg_relative_volume > 1.5 else 0
        avg_volatility = random.uniform(2, 15)
        volatility_trend = random.uniform(0, 1)
        avg_news_sentiment = random.uniform(0.2, 0.8)
        positive_ticker_ratio = random.uniform(0, 1)
        qqq_change_pct = random.uniform(-2, 2)
        agreement_strength = random.uniform(0, 1)
        leader_gap = random.uniform(0, 2)
        
        # Label: 1 for UP, 0 for DOWN based on basket_momentum
        label = 1 if basket_momentum > 0 else 0
        
        data.append([
            timestamp, basket_momentum, momentum_strength, avg_relative_volume,
            volume_spike_ratio, avg_volatility, volatility_trend, avg_news_sentiment,
            positive_ticker_ratio, qqq_change_pct, agreement_strength, leader_gap, label
        ])
    
    # Save to CSV
    df = pd.DataFrame(data, columns=[
        'timestamp', 'basket_momentum', 'momentum_strength', 'avg_relative_volume',
        'volume_spike_ratio', 'avg_volatility', 'volatility_trend', 'avg_news_sentiment',
        'positive_ticker_ratio', 'qqq_change_pct', 'agreement_strength', 'leader_gap', 'label'
    ])
    df.to_csv('../data/training_data.csv', index=False)
    print(f"Generated {len(df)} sample training rows at ../data/training_data.csv")

if __name__ == "__main__":
    # First, generate sample data if needed
    csv_path = '../data/training_data.csv'
    if not os.path.exists(csv_path) or pd.read_csv(csv_path).dropna().empty:
        print("No training data found. Generating sample data...")
        generate_sample_training_data()
    
    # Train the model
    train_model()