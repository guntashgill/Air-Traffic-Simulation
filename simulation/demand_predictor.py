import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os
from datetime import datetime

class DemandPredictor:
    def __init__(self, sequence_length=24, n_features=4):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.scaler = MinMaxScaler()
        self.model = None
        self.model_path = "models/demand_model.h5"
        self.scaler_path = "models/demand_scaler.pkl"
        
    def create_model(self):
        """Create LSTM model architecture"""
        model = Sequential()
        model.add(LSTM(50, activation='relu', 
                      input_shape=(self.sequence_length, self.n_features)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def load_model(self):
        """Load trained model if available"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = self.create_model()
            self.model.load_weights(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            return True
        return False
    
    def train_model(self, data_file, epochs=50, batch_size=32):
        """Train LSTM model on historical data"""
        # Load and preprocess data
        df = pd.read_csv(data_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Resample to hourly
        df = df.resample('H').mean().fillna(0)
        
        # Feature engineering
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        
        # Select features and target
        features = ['demand', 'hour', 'day_of_week', 'weather_impact']
        dataset = df[features].values
        
        # Scale data
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(dataset)
        
        # Create sequences
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i, 0])  # Demand is first column
            
        X, y = np.array(X), np.array(y)
        
        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Create and train model
        self.model = self.create_model()
        self.model.fit(X_train, y_train, 
                      epochs=epochs, 
                      batch_size=batch_size,
                      validation_data=(X_test, y_test))
        
        # Save model and scaler
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save_weights(self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        return self.model.evaluate(X_test, y_test)
    
    def predict_demand(self, historical_data, current_weather):
        """Predict demand for next hour"""
        if not self.model:
            self.load_model()
            if not self.model:
                return 5  # Default if no model
        
        # Prepare input data
        df = historical_data.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Feature engineering
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        
        # Select features
        features = ['demand', 'hour', 'day_of_week', 'weather_impact']
        input_data = df[features].values[-self.sequence_length:]
        
        # Scale data
        scaled_data = self.scaler.transform(input_data)
        
        # Reshape for LSTM
        X = np.array([scaled_data])
        
        # Predict
        prediction = self.model.predict(X)
        
        # Inverse scale
        dummy_row = np.zeros((1, self.n_features))
        dummy_row[0, 0] = prediction[0, 0]
        prediction = self.scaler.inverse_transform(dummy_row)[0, 0]
        
        return max(0, prediction)