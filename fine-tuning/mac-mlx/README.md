# Overview

Attempt to fine tune mistral7b on mlx library

Reference
* https://medium.com/rahasak/fine-tuning-llms-on-macos-using-mlx-and-run-with-ollama-182a20f1fd2c

# Latest commands / runs

2025-03-03
- ./fine-tuning-script.sh mlx-community/Meta-Llama-3.1-8B-Instruct-4bit ~/workspace/model-training-sandbox/data/mlx-test/ /Users/john.wang/workspace/model-training-sandbox/llama-3.1-8B/chat2/

# Results

## 2025-02-23

### Attempt 3

Full training data from google voice - saved 10% for validation.

(venv) john:arm64:mistral7b-mlx/$ python -m mlx_lm.lora --model mlx-community/Mistral-7B-Instruct-v0.2-4bit --data ~/workspace/model-training-sandbox/2025-02-23-mistral-attempt/data/mistral-mlx-test/ --train --num-layers 16 --iters 200
Loading pretrained model
Fetching 7 files: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00, 60411.79it/s]
Loading datasets
Training
Trainable parameters: 0.047% (3.408M/7241.732M)
Starting training..., iters: 200
Iter 1: Val loss 8.492, Val took 40.666s
Iter 10: Train loss 7.781, Learning Rate 1.000e-05, It/sec 0.265, Tokens/sec 53.382, Trained Tokens 2013, Peak mem 8.153 GB
Iter 20: Train loss 4.352, Learning Rate 1.000e-05, It/sec 0.307, Tokens/sec 57.686, Trained Tokens 3889, Peak mem 8.153 GB
Iter 30: Train loss 3.565, Learning Rate 1.000e-05, It/sec 0.327, Tokens/sec 54.906, Trained Tokens 5569, Peak mem 8.153 GB
Iter 40: Train loss 3.207, Learning Rate 1.000e-05, It/sec 0.325, Tokens/sec 56.502, Trained Tokens 7305, Peak mem 8.153 GB
Iter 50: Train loss 3.008, Learning Rate 1.000e-05, It/sec 0.302, Tokens/sec 58.883, Trained Tokens 9257, Peak mem 8.153 GB
Iter 60: Train loss 3.017, Learning Rate 1.000e-05, It/sec 0.270, Tokens/sec 46.275, Trained Tokens 10969, Peak mem 8.153 GB
Iter 70: Train loss 2.901, Learning Rate 1.000e-05, It/sec 0.340, Tokens/sec 56.821, Trained Tokens 12641, Peak mem 8.153 GB
Iter 80: Train loss 2.970, Learning Rate 1.000e-05, It/sec 0.264, Tokens/sec 56.190, Trained Tokens 14773, Peak mem 8.153 GB
Iter 90: Train loss 3.005, Learning Rate 1.000e-05, It/sec 0.315, Tokens/sec 57.099, Trained Tokens 16586, Peak mem 8.153 GB
Iter 100: Train loss 2.910, Learning Rate 1.000e-05, It/sec 0.305, Tokens/sec 53.447, Trained Tokens 18338, Peak mem 8.153 GB
Iter 100: Saved adapter weights to adapters/adapters.safetensors and adapters/0000100_adapters.safetensors.
Iter 110: Train loss 2.837, Learning Rate 1.000e-05, It/sec 0.301, Tokens/sec 52.017, Trained Tokens 20069, Peak mem 8.153 GB
Iter 120: Train loss 3.020, Learning Rate 1.000e-05, It/sec 0.472, Tokens/sec 52.109, Trained Tokens 21173, Peak mem 8.153 GB
Iter 130: Train loss 2.912, Learning Rate 1.000e-05, It/sec 0.368, Tokens/sec 53.963, Trained Tokens 22640, Peak mem 8.153 GB
Iter 140: Train loss 2.846, Learning Rate 1.000e-05, It/sec 0.342, Tokens/sec 55.824, Trained Tokens 24272, Peak mem 8.153 GB
Iter 150: Train loss 2.805, Learning Rate 1.000e-05, It/sec 0.381, Tokens/sec 55.988, Trained Tokens 25740, Peak mem 8.153 GB
Iter 160: Train loss 2.842, Learning Rate 1.000e-05, It/sec 0.337, Tokens/sec 56.448, Trained Tokens 27416, Peak mem 8.153 GB
Iter 170: Train loss 2.913, Learning Rate 1.000e-05, It/sec 0.341, Tokens/sec 56.031, Trained Tokens 29057, Peak mem 8.366 GB
Iter 180: Train loss 3.011, Learning Rate 1.000e-05, It/sec 0.270, Tokens/sec 58.740, Trained Tokens 31229, Peak mem 8.366 GB
Iter 190: Train loss 2.853, Learning Rate 1.000e-05, It/sec 0.373, Tokens/sec 56.753, Trained Tokens 32749, Peak mem 8.366 GB
Iter 200: Val loss 2.929, Val took 41.560s
Iter 200: Train loss 2.909, Learning Rate 1.000e-05, It/sec 1.572, Tokens/sec 483.299, Trained Tokens 35823, Peak mem 11.668 GB
Iter 200: Saved adapter weights to adapters/adapters.safetensors and adapters/0000200_adapters.safetensors.
Saved final weights to adapters/adapters.safetensors.
(venv) john:arm64:mistral7b-mlx/$


### Attempt 2

(venv) john:arm64:mistral7b-mlx/$ python -m mlx_lm.lora --model mlx-community/Mistral-7B-Instruct-v0.2-4bit --data ~/workspace/data-train/mistral-mlx-test/ --train --num-layers 16 --iters 70
Loading pretrained model
Fetching 7 files: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00, 44552.55it/s]
Loading datasets
Training
Trainable parameters: 0.047% (3.408M/7241.732M)
Starting training..., iters: 70

4:40 pm ET

Iter 1: Val loss 8.249, Val took 42.295s
Iter 10: Train loss 6.321, Learning Rate 1.000e-05, It/sec 0.214, Tokens/sec 55.823, Trained Tokens 2606, Peak mem 8.549 GB
Iter 20: Train loss 3.514, Learning Rate 1.000e-05, It/sec 0.161, Tokens/sec 55.953, Trained Tokens 6081, Peak mem 8.549 GB
Iter 30: Train loss 3.214, Learning Rate 1.000e-05, It/sec 0.161, Tokens/sec 44.596, Trained Tokens 8846, Peak mem 9.553 GB
Iter 40: Train loss 2.976, Learning Rate 1.000e-05, It/sec 0.201, Tokens/sec 52.496, Trained Tokens 11462, Peak mem 9.553 GB
Iter 50: Train loss 2.822, Learning Rate 1.000e-05, It/sec 0.194, Tokens/sec 50.216, Trained Tokens 14050, Peak mem 9.553 GB
Iter 60: Train loss 2.764, Learning Rate 1.000e-05, It/sec 0.221, Tokens/sec 54.040, Trained Tokens 16496, Peak mem 9.553 GB
Iter 70: Val loss 3.145, Val took 47.070s
Iter 70: Train loss 2.820, Learning Rate 1.000e-05, It/sec 2.290, Tokens/sec 596.079, Trained Tokens 19099, Peak mem 9.553 GB
Saved final weights to adapters/adapters.safetensors.
(venv) john:arm64:mistral7b-mlx/$


### Attempt 1

(venv) john:arm64:mistral7b-mlx/$ python -m mlx_lm.lora --model mlx-community/Mistral-7B-Instruct-v0.2-4bit --data ~/workspace/data-train/mistral-mlx-test/ --train --num-layers 16 --iters 100
Loading pretrained model
Fetching 7 files: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00, 45378.87it/s]
Loading datasets
Training
Trainable parameters: 0.047% (3.408M/7241.732M)
Starting training..., iters: 100
Iter 1: Val loss 7.570, Val took 5.958s
Iter 10: Train loss 4.783, Learning Rate 1.000e-05, It/sec 0.035, Tokens/sec 29.652, Trained Tokens 8400, Peak mem 13.351 GB
Iter 20: Train loss 2.780, Learning Rate 1.000e-05, It/sec 0.034, Tokens/sec 28.143, Trained Tokens 16800, Peak mem 13.351 GB
Iter 30: Train loss 1.933, Learning Rate 1.000e-05, It/sec 0.035, Tokens/sec 29.222, Trained Tokens 25200, Peak mem 13.351 GB
Iter 40: Train loss 0.780, Learning Rate 1.000e-05, It/sec 0.038, Tokens/sec 31.707, Trained Tokens 33600, Peak mem 13.351 GB
Iter 50: Train loss 0.151, Learning Rate 1.000e-05, It/sec 0.037, Tokens/sec 31.447, Trained Tokens 42000, Peak mem 13.351 GB
Iter 60: Train loss 0.086, Learning Rate 1.000e-05, It/sec 0.040, Tokens/sec 33.288, Trained Tokens 50400, Peak mem 13.351 GB
Iter 70: Train loss 0.079, Learning Rate 1.000e-05, It/sec 0.039, Tokens/sec 32.829, Trained Tokens 58800, Peak mem 13.351 GB
Iter 80: Train loss 0.076, Learning Rate 1.000e-05, It/sec 0.038, Tokens/sec 31.725, Trained Tokens 67200, Peak mem 13.351 GB
Iter 90: Train loss 0.075, Learning Rate 1.000e-05, It/sec 0.040, Tokens/sec 33.232, Trained Tokens 75600, Peak mem 13.351 GB
Iter 100: Val loss 5.899, Val took 5.796s
Iter 100: Train loss 0.074, Learning Rate 1.000e-05, It/sec 0.358, Tokens/sec 300.380, Trained Tokens 84000, Peak mem 13.351 GB
Iter 100: Saved adapter weights to adapters/adapters.safetensors and adapters/0000100_adapters.safetensors.
Saved final weights to adapters/adapters.safetensors.
(venv) john:arm64:mistral7b-mlx/$

