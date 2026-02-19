import os
import logging
from multiprocessing import Pool, cpu_count

# Crea un file per il debugging
logging.basicConfig(filename='debug_blast.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def parse_fasta(path):
    records = {}
    try:
        with open(path, 'r') as f:
            chunks = f.read().split(">")[1:]
            for chunk in chunks:
                lines = chunk.splitlines()
                if not lines: continue
                header = lines[0]
                sequence = "".join(lines[1:]).upper().strip()
                records[header] = sequence
        logging.info(f"Caricato file {path}: {len(records)} record trovati")
    except Exception as e:
        logging.error(f"Errore lettura {path}: {e}")
    return records

def smith_waterman(query, target):
    # Match=2, Mismatch=-1, Gap=-1
    m, n = len(query), len(target)
    if n == 0: return 0
    H = [[0] * (n + 1) for _ in range(m + 1)]
    max_score = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score = max(
                H[i-1][j-1] + (2 if query[i-1] == target[j-1] else -1),
                H[i-1][j] - 1, 
                H[i][j-1] - 1, 
                0
            )
            H[i][j] = score
            if score > max_score: max_score = score
    return max_score

def _process_chunk(args):
    query, seq, fname, header, min_score = args
    # Se la sequenza è troppo lunga, la dividiamo in pezzi da 500
    chunk_size = 500
    best_score = 0
    for i in range(0, len(seq), chunk_size):
        chunk = seq[i:i+chunk_size]
        score = smith_waterman(query, chunk)
        if score > best_score: best_score = score
    
    if best_score >= min_score:
        return {"file": fname, "score": best_score, "header": header[:20]}
    return None

def search_pipeline(query, genomes_dir, min_score=10):
    query = query.strip().upper()
    if not query: return []
    
    logging.info(f"Inizio ricerca per query: {query} in {genomes_dir}")
    
    if not os.path.exists(genomes_dir):
        logging.error(f"La cartella {genomes_dir} non esiste!")
        return []

    tasks = []
    files = [f for f in os.listdir(genomes_dir) if f.lower().endswith((".fa", ".fasta", ".txt"))]
    logging.info(f"File trovati: {files}")

    for fname in files:
        records = parse_fasta(os.path.join(genomes_dir, fname))
        for h, s in records.items():
            tasks.append((query, s, fname, h, min_score))
    
    if not tasks:
        logging.warning("Nessun task generato. File vuoti o estensioni errate?")
        return []

    with Pool(cpu_count()) as pool:
        results = pool.map(_process_chunk, tasks)
    
    found = [r for r in results if r]
    logging.info(f"Ricerca completata. Match trovati: {len(found)}")
    return sorted(found, key=lambda x: x["score"], reverse=True)
