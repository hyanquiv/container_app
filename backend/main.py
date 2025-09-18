from aligner import run_alignment
from io_utils import read_fasta
import os

# Crear carpetas si no existen
os.makedirs("in", exist_ok=True)
os.makedirs("out", exist_ok=True)

input_file = os.path.join("in", "example.fasta")
output_file = os.path.join("out", "aligned_output.fasta")

print("Leyendo archivo...")
seqs = read_fasta(input_file)

print("Ejecutando alineamiento...")
run_alignment(input_file, output_file)

print(f"Alineamiento completado. Resultado en: {output_file}")
