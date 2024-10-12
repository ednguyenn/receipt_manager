#!/bin/bash

# Register the ECS Task Definition
echo "Registering ECS Task Definition..."
aws ecs register-task-definition \
  --cli-input-json file://scripts/task-definition.json
