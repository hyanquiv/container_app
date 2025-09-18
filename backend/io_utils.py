from Bio import SeqIO

def read_fasta(filename):
    return list(SeqIO.parse(filename, "fasta"))
