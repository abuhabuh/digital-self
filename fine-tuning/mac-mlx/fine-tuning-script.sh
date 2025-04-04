#!/bin/bash

# USAGE EXAMPLE (2025-03-01): ./fine-tuning-script.sh mlx-community/Llama-3.2-1B-Instruct-4bit ~/workspace/model-training-sandbox/data/mlx-test/ /Users/john.wang/workspace/model-training-sandbox/llama-3.2-1B-2025-02-27/john-llama-chat-1


# Check if the correct number of arguments is provided
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <hugging-face-model> <data-directory> <model-output-dir> <ollama-model-name>"
  exit 1
fi

# Access the arguments using positional parameters
HF_MODEL="$1"
DATA_DIR="$2"
MODEL_OUTPUT_DIR="$3"
# Ollama model name to create
OLLAMA_MODEL_NAME="$4"

######
# Train the model
#
echo ""
echo "************************************************"
echo "Training $HF_MODEL on data: $DATA_DIR"
echo "************************************************"
echo ""
# Activate virtual env for mlx tuning
source venv/bin/activate
# Clear the output directory
rm -rf $MODEL_OUTPUT_DIR/*
# time run
start_time=$(date +%s)
# Run fine tunning
set -x
python -m mlx_lm.lora \
       --model $HF_MODEL \
       --data $DATA_DIR \
       --adapter-path $MODEL_OUTPUT_DIR/adapters \
       --train \
       --num-layers 16 \
       --iters 80
set +x
# time run
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
# calculate and display execution time
echo ""
echo "   *********************************************"
echo "   Model training time: $elapsed_time seconds"
echo "   *********************************************"
echo ""
# Fuse adapters into model
set -x
python -m mlx_lm.fuse \
       --model $HF_MODEL \
       --adapter-path $MODEL_OUTPUT_DIR/adapters \
       --save-path $MODEL_OUTPUT_DIR \
       --de-quantize  # de-quantize so we can convert to ollama
set +x
# Deactivate virtual env
deactivate

######
# Convert to ollama
#
echo ""
echo "************************************************"
echo "Convert model to ollama"
echo "************************************************"
echo ""
# Activate llama.cpp virtual env
LLAMA_CPP_DIR=~/workspace/other-repos/llama.cpp
source $LLAMA_CPP_DIR/venv/bin/activate
# Convert to gguf
set -x
python $LLAMA_CPP_DIR/convert_hf_to_gguf.py $MODEL_OUTPUT_DIR \
       --outfile $MODEL_OUTPUT_DIR/ollama_model.gguf \
       --outtype q8_0
set +x
# Create Modelfile
echo "FROM ./ollama_model.gguf" > $MODEL_OUTPUT_DIR/Modelfile
# Deactivate virtual env
deactivate

######
# Create ollama model
#
echo ""
echo "************************************************"
echo "Create ollama model"
echo "************************************************"
echo ""

set -x
ollama create $OLLAMA_MODEL_NAME -f $MODEL_OUTPUT_DIR/Modelfile
set +x

