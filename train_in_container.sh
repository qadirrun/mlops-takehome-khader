#!/bin/bash
# Train models inside the container

echo "Starting training inside container..."
docker exec iris-classifier-api python /app/train/main_loop_models.py
echo "Training completed!"

