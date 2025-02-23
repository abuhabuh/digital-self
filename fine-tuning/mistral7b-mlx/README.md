# Overview

Attempt to fine tune mistral7b on mlx library

Reference
* https://medium.com/rahasak/fine-tuning-llms-on-macos-using-mlx-and-run-with-ollama-182a20f1fd2c

# Results

## 2025-02-23

### Second attempt

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



### First attempt

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

