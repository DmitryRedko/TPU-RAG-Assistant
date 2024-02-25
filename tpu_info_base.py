from rank_bm25 import BM25Okapi

class TextSearchEngine:
    def __init__(self, texts):
        self.texts = texts

    def __split_into_chunks(self, chunk_size=100):
        # print(self.texts)
        words = self.texts.split()
        # print(words)
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            # print(current_chunk,len(current_chunk),chunk_size)
            if len(current_chunk) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _get_top_matching_texts(self, query, max_words_per_split=100, top_n=5):
        # print(self.texts)
        all_splits = self.__split_into_chunks(max_words_per_split)
        # print("HERE:",all_splits)

        # tokenized_texts = [text.split() for text in all_splits]
        # print(tokenized_texts)
        bm25_model = BM25Okapi(all_splits)
        tokenized_query = query.split()
        scores = bm25_model.get_scores(tokenized_query)
        results = [(score, text) for score, text in zip(scores, all_splits)]
        sorted_results = sorted(results, reverse=True)
        
        top_results = sorted_results[:top_n]
        prompts = [text for _, text in top_results]
        return prompts

    def get_closest_matching_text(self, query):
        top_matching_texts = self._get_top_matching_texts(query, top_n=3)
        return top_matching_texts

# # Пример использования
# query = "По какому адресу найти Главный корпус ТПУ?"
# search_engine = TextSearchEngine(all_text)
# closest_matching_text = search_engine.get_closest_matching_text(query)
# print(closest_matching_text)
