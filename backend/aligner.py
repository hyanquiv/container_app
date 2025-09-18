import subprocess
import os

def run_alignment(input_file, output_prefix="aligned"):
    exec_dir = "./exec"

    # Definir rutas de salida
    muscle_output = f"{output_prefix}_muscle.fasta"
    msa_output = f"{output_prefix}_msa.fasta"

    # Ejecutar Muscle5
    muscle_exe = "muscle"
    # muscle_exe = os.path.join(exec_dir, "muscle5.exe")
    subprocess.run([muscle_exe, "-align", input_file, "-output", muscle_output], check=True)

    # Ejecutar MSAligner
    msa_exe = os.path.join(exec_dir, "MSAligner")
    subprocess.run([msa_exe, input_file, msa_output], check=True)

    return muscle_output, msa_output
