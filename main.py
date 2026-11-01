from src.embedder import Embedder 
from PIL import Image 
import numpy as np 
embedder = Embedder() 

print(embedder.device) 
print() 
print(embedder.model.config.projection_dim) 
print() 

# test_image = Image.open("data/ABO/abo-images-small/images/small/0e/0e0c839a.jpg").convert("RGB")
# image_vector = embedder.embed_image(test_image) 

# print(image_vector.shape) 
# print(np.linalg.norm(image_vector))
# image_vecotrs = embedder.embed_images([test_image]) 
# text_vector = embedder.embed_text("red handbag") 
# print(text_vector.shape) 
# print(np.linalg.norm(text_vector)) 

images = [
    Image.open(
        "data/ABO/abo-images-small/images/small/0e/0e0c839a.jpg"
    ).convert("RGB"),
    Image.open(
        "data/ABO/abo-images-small/images/small/12/12298343.jpg"
    ).convert("RGB"),
]

image_vectors = embedder.embed_images(images)

print(image_vectors.shape)
print(np.linalg.norm(image_vectors, axis=1))