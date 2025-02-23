import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import json
import os


HF_TOKEN = os.environ['HF_TOKEN']


def load_model(base_model_name, adapter_path):
    """
    Load the base model and fine-tuned adapter weights.
    """
    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, token=HF_TOKEN)
    tokenizer.pad_token = tokenizer.eos_token

    # Determine device
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map=None,
        trust_remote_code=True,
        token=HF_TOKEN,
    ).to(device)

    # Load adapter weights
    model = PeftModel.from_pretrained(
        base_model,
        adapter_path,
        token=HF_TOKEN,
    )

    return model, tokenizer, device

def generate_response(model, tokenizer, prompt, device,
                     max_length=512,
                     temperature=0.7,
                     top_p=0.9):
    """
    Generate a response using the fine-tuned model.
    """
    # Format the prompt
    formatted_prompt = f"User: {prompt}\nAssistant:"

    # Tokenize input
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(device)

    # Generate response
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_length=max_length,
        temperature=temperature,
        top_p=top_p,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

    # Decode response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract assistant's response
    response = response.split("Assistant:")[-1].strip()

    return response

def main():
    # Configuration
    BASE_MODEL_NAME = "mistralai/Mistral-7B-v0.1"
    ADAPTER_PATH = "mistral-finetuned"  # Path to your fine-tuned model

    # Load model
    model, tokenizer, device = load_model(BASE_MODEL_NAME, ADAPTER_PATH)
    model.eval()  # Set to evaluation mode

    print("Model loaded successfully! Enter your messages (type 'quit' to exit)")

    # Interactive loop
    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == 'quit':
            break

        response = generate_response(model, tokenizer, user_input, device)
        print("\nAssistant:", response)

if __name__ == "__main__":
    main()
