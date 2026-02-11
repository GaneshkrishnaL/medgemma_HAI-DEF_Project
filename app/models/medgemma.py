import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

DEFAULT_MODEL_ID = "google/medgemma-1.5-4b-it"  # multimodal instruction-tuned

class MedGemmaClient:
    def __init__(self, model_id: str = DEFAULT_MODEL_ID, device: str | None = None):
        self.model_id = model_id
        self.device = device or ("mps" if torch.backends.mps.is_available() else "cpu")

        self.processor = AutoProcessor.from_pretrained(model_id)
        
        # Using bfloat16 is generally more stable for Gemma models than float16
        dtype = torch.bfloat16 if self.device != "cpu" else torch.float32
        
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map=self.device
        )

    @torch.inference_mode()
    def generate(self, prompt: str, image=None, max_new_tokens: int = 512, temperature: float = 0.2) -> str:
        # Construct messages for chat template
        content = []
        if image is not None:
            content.append({"type": "image"})
        content.append({"type": "text", "text": prompt})
        
        messages = [
            {"role": "user", "content": content}
        ]

        # Use processor's chat template which handles <image> tokens automatically
        formatted_prompt = self.processor.apply_chat_template(
            messages, 
            add_generation_prompt=True, 
            tokenize=False
        )
        
        print(f"DEBUG: Formatted Prompt: {formatted_prompt}")

        # Processor handles text and images
        # Ensure images is a list as some processors expect it
        images = [image] if image is not None else None
        
        inputs = self.processor(
            text=formatted_prompt,
            images=images,
            return_tensors="pt"
        )
        # Ensure inputs match the model's device and dtype
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        if "pixel_values" in inputs:
            inputs["pixel_values"] = inputs["pixel_values"].to(self.model.dtype)

        # Use greedy decoding if temperature is 0 or very low for stability
        do_sample = temperature > 0.01

        input_len = inputs["input_ids"].shape[1]

        out = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature if do_sample else None,
        )
        # Only decode the newly generated tokens
        new_tokens = out[0][input_len:]
        return self.processor.decode(new_tokens, skip_special_tokens=True).strip()
