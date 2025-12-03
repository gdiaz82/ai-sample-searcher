import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
from safetensors.torch import save_file


input_path = "./model_cache/pytorch_model.bin"
output_path = "./model_cache/model.safetensors"

if not os.path.exists(input_path):
    print(f"Error: No encuentro {input_path}")
    exit()

print("Cargando modelo antiguo (.bin)...")
# Cargamos los pesos en la CPU
state_dict = torch.load(input_path, map_location="cpu")

print("Guardando modelo nuevo (.safetensors)...")
# Guardamos en el formato seguro
save_file(state_dict, output_path)

print("¡Conversión completada! Ahora puedes borrar el archivo .bin")