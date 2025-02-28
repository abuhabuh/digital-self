#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <hugging-face-model> <data-directory> <model-output-dir>"
  exit 1
fi

# Access the arguments using positional parameters
HF_MODEL="$1"
DATA_DIR="$2"
MODEL_OUTPUT_DIR="$3"

######
# Train the model
#
echo "Training $HF_MODEL on data: $DATA_DIR"
# Activate virtual env for mlx tuning
source venv/bin/activate
# Clear the output directory
rm -rf $MODEL_OUTPUT_DIR/*
# Run fine tunning
python -m mlx_lm.lora \
       --model $HF_MODEL \
       --data $DATA_DIR \
       --adapter-path $MODEL_OUTPUT_DIR/adapters \
       --train \
       --num-layers 16 \
       --iters 100
# Fuse adapters into model
python -m mlx_lm.fuse \
       --model $HF_MODEL \
       --adapter-path $MODEL_OUTPUT_DIR/adapters \
       --save-path $MODEL_OUTPUT_DIR \
       --de-quantize  # de-quantize so we can convert to ollama
# Deactivate virtual env
deactivate

######
# Convert to ollama
#
echo "Convert model to ollama"
# Activate llama.cpp virtual env
LLAMA_CPP_DIR=~/workspace/other-repos/llama.cpp
source $LLAMA_CPP_DIR/venv/bin/activate
# Convert to gguf
python $LLAMA_CPP_DIR/convert_hf_to_gguf.py $MODEL_OUTPUT_DIR \
       --outfile $MODEL_OUTPUT_DIR/llama_model.gguf \
       --outtype q8_0
# Create Modelfile
echo "FROM ./llama_model.gguf" > $MODEL_OUTPUT_DIR/Modelfile
# Deactivate virtual env
deactivate
