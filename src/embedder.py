from collections.abc import Sequence 

import numpy as np 
import torch 
from PIL import Image 
from transformers import CLIPModel, CLIPProcessor 

class Embedder: 
    # Initialization / Constructor 
    def __init__(self, model_id: str = "openai/clip-vit-base-patch32") -> None: 
        self.model_id = model_id 
        self.device = self._select_device() 
        self.model = CLIPModel.from_pretrained(model_id).to(self.device) 
        self.processor = CLIPProcessor.from_pretrained(model_id) 
        self.model.eval() 

    @staticmethod  # This function does not need an existing Embedder object or any instance state. It only asks PyTorch which device is available 
    def _select_device() -> torch.device: 
        if torch.cuda.is_available(): 
            return torch.device("cuda") 

        if torch.backends.mps.is_available(): 
            return torch.device("mps")


        return torch.device("cpu") 

    # Normalization helper 
    @staticmethod 
    def _normalize_embeddings(embeddings: np.ndarray) -> np.ndarray: 
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) 
        if np.any(norms == 0): 
            raise ValueError("Cannot normalize an embedding with zero magnitude.")

        return embeddings / norms 

    # Add a tensor to-Numpy helper 
    @staticmethod 
    def _to_numpy(tensor: torch.Tensor) -> np.ndarray: 
        return (
            tensor 
            .detach()  # removes gradient-tracking information 
            .cpu()  # moves the tensor out of MPS/CUDA memory 
            .numpy() # converts it to a NumPy array 
        )

    # Add image batch embedding 
    def embed_images(self, images: Sequence[Image.Image]) -> np.ndarray:
        if not images: 
            raise ValueError("At least one image is required.") 

        image_inputs = self.processor(images=list(images), return_tensors="pt") 

        pixel_values = image_inputs["pixel_values"].to(self.device)

        with torch.no_grad(): 
            vision_outputs = self.model.vision_model(pixel_values=pixel_values)
            embeddings = self.model.visual_projection(vision_outputs.pooler_output)


        embeddings_np = self._to_numpy(embeddings) 

        return self._normalize_embeddings(embeddings_np)

    # Add single-image convenience method 
    def embed_image(self, image: Image.Image) -> np.ndarray: 
        embeddings = self.embed_images([image]) 
        return embeddings[0] 

    # Text embedding 
    def embed_text(self, text: str) -> np.ndarray: 
        if not text.strip(): 
            raise ValueError("Text cannot be empty.") 

        text_inputs = self.processor(text=[text], padding=True, return_tensors='pt') 

        text_inputs = {
            key: value.to(self.device) 
            for key, value in text_inputs.items() 
        }

        with torch.no_grad(): 
            text_outputs = self.model.text_model(
                input_ids = text_inputs["input_ids"], 
                attention_mask=text_inputs["attention_mask"], 
            )

            embedding = self.model.text_projection(
                text_outputs.pooler_output, 
            )

        embedding_np = self._to_numpy(embedding) 

        return self._normalize_embeddings(embedding_np)[0] 


