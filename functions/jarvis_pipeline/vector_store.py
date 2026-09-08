import os
import difflib
import math

class VectorStore:
    """
    Lightweight, cloud-friendly Vector/Deduplication store.
    Uses pure-Python embedding & string similarity fallback to ensure 100% portability in serverless clouds without heavy C-dependencies.
    """
    def __init__(self):
        self.items = []
        
    def reset_for_new_run(self):
        """Wipes previous memory for fresh daily run."""
        self.items = []
        print("Initialized fresh daily memory store.")

    def _calculate_similarity(self, text1, text2):
        """Calculates normalized similarity score between two texts (0.0 to 1.0)."""
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()
        
        # Sequence matcher similarity
        seq_ratio = difflib.SequenceMatcher(None, t1, t2).ratio()
        
        # Word overlap (Jaccard similarity)
        words1 = set(t1.split())
        words2 = set(t2.split())
        if words1 and words2:
            jaccard = len(words1.intersection(words2)) / len(words1.union(words2))
            return max(seq_ratio, jaccard)
        return seq_ratio

    def add_item_if_not_duplicate(self, item):
        """
        Deduplicates items comparing against already stored items today.
        Similarity > 0.85 indicates a duplicate news story.
        """
        title = item.get('title', '')
        text = item.get('text_to_embed', title)
        
        for existing in self.items:
            existing_text = existing.get('text_to_embed', existing.get('title', ''))
            
            # Check URL match
            if existing.get('url') and item.get('url') and existing.get('url') == item.get('url'):
                print(f"Skipping exact URL duplicate: {title}")
                return False
                
            # Check semantic/title similarity
            sim = self._calculate_similarity(text, existing_text)
            if sim > 0.85:
                print(f"Skipping semantic duplicate: {title} (Matches '{existing.get('title')}' with {sim:.2f} score)")
                return False
                
        self.items.append(item)
        print(f"Added item to daily store: {title}")
        return True

    def get_all_items(self):
        """Retrieves all items stored today to pass to the Gemini RAG LLM."""
        return self.items
