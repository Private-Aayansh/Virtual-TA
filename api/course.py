from typing import List, Dict
import numpy as np
from utils import load_index_and_metadata

def course_query_search(embedding, index_path: str, metadata_path: str, k: int = 2) -> List[Dict]:
    index, metadata = load_index_and_metadata(index_path, metadata_path)
    embedding = np.array(embedding, dtype=np.float32)
    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1)

    distances, indices = index.search(embedding, k)
    
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        item = metadata[idx].copy()
        item['similarity'] = float(1 / (1 + distance))
        results.append(item)

    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    return results
