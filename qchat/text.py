import re
import unicodedata

SPECIAL = ['<pad>', '<unk>', '<bos>', '<sep>', '<eos>']

def words(text):
    text = unicodedata.normalize('NFC', text.strip().lower())
    return re.findall(r"\d+|[^\W\d_]+|[^\w\s]", text, flags=re.UNICODE)

class Tokenizer:
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self.ids = {word: i for i,word in enumerate(vocabulary)}

    @classmethod
    def build(cls, rows):
        vocabulary = sorted({w for r in rows for field in ('prompt','answer') for w in words(r[field])})
        return cls(SPECIAL + vocabulary)

    def encode(self, text):
        return [self.ids.get(w, 1) for w in words(text)]

    def prompt(self, text):
        return [2] + self.encode(text) + [3]

    def decode(self, ids):
        s = ' '.join(self.vocabulary[i] for i in ids if i >= len(SPECIAL))
        return re.sub(r'\s+([.,!?;:])', r'\1', s)
