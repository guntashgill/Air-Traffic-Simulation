from simulation.demand_predictor import DemandPredictor

# Initialize demand predictor
demand_predictor = DemandPredictor()

# Train model
print("Training demand forecasting model...")
mse = demand_predictor.train_model("data/demand_data.csv", epochs=100)
print(f"Training completed with MSE: {mse:.4f}")