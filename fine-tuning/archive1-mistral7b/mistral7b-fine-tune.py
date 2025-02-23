import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    get_peft_model,
    LoraConfig,
)
import json
import glob
from typing import List, Dict
import os


HF_TOKEN = os.environ['HF_TOKEN']


def load_chat_data(file_paths: List[str]) -> List[Dict]:
    """Load and process chat data from JSON files."""
    conversations = []

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            messages = json.load(f)

        # Format conversation
        formatted_convo = ""
        for msg in messages:
            role = "Assistant" if msg["role"] == "assistant" else "User"
            formatted_convo += f"{role}: {msg['content']}\n"

        conversations.append({
            "text": formatted_convo.strip()
        })

    return conversations

def prepare_training_data(conversations: List[Dict]) -> Dataset:
    """Convert conversations to HuggingFace Dataset."""
    return Dataset.from_list(conversations)

def main():
    # Configuration
    MODEL_NAME = "mistralai/Mistral-7B-v0.1"
    OUTPUT_DIR = "mistral-finetuned"
    CHAT_DATA_PATH = "/Users/john.wang/workspace/my_work/data-digital-self/google-voice/_training_set/*.json"  # Update this path

    # LoRA configurations - adjusted for efficiency on M1
    lora_config = LoraConfig(
        r=8,  # Rank
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        inference_mode=False
    )

    # Training arguments optimized for M1 Mac
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=2,  # Reduced batch size for M1
        gradient_accumulation_steps=8,   # Increased for smaller batch size
        learning_rate=2e-4,
        logging_steps=10,
        save_strategy="epoch",
        optim="adamw_torch",  # Using standard AdamW optimizer
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        gradient_checkpointing=True,  # Enable gradient checkpointing
        lr_scheduler_type="cosine",
        evaluation_strategy="no",
        remove_unused_columns=True,
        ddp_find_unused_parameters=False,
        report_to="none",  # Disable wandb logging
    )

    # Load and prepare data
    chat_files = glob.glob(CHAT_DATA_PATH)
    conversations = load_chat_data(chat_files)
    dataset = prepare_training_data(conversations)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True, token=HF_TOKEN)
    tokenizer.pad_token = tokenizer.eos_token

    # Determine the best available device
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load model with correct device initialization
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map=None,  # Don't use auto device mapping
        trust_remote_code=True,
        use_cache=False,
        token=HF_TOKEN,
    ).to(device)

    # Apply LoRA adapters
    model = get_peft_model(model, lora_config)

    # Enable gradient checkpointing for memory efficiency
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()  # Enable gradients for input

    def tokenize_function(examples):
        """Tokenize the text and return pytorch tensors."""
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512
        )

    # Tokenize dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )

    # Use the transformers data collator instead of custom collate_fn
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # We're doing causal language modeling, not masked
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator
    )

    # Start training
    trainer.train()

    # Save the final model and tokenizer
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

if __name__ == "__main__":
    main()
