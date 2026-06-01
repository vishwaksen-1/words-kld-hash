def load_words(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def words_to_bytes(words, separator=b""):
    return separator.join(word.encode("utf-8") for word in words)


def word_key(words, index):
    return words[index % len(words)].encode("utf-8")
