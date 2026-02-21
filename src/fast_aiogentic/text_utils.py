"""Text utilities for Telegram message formatting."""


def _split_long_paragraph(para: str, max_length: int) -> list[str]:
    """Split a paragraph that exceeds max_length by words, then by characters."""
    chunks: list[str] = []
    current = ""

    for word in para.split():
        if len(current) + len(word) + 1 <= max_length:
            current = f"{current} {word}" if current else word
        elif len(word) > max_length:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(word[i : i + max_length] for i in range(0, len(word), max_length))
        else:
            if current:
                chunks.append(current)
            current = word

    if current:
        chunks.append(current)
    return chunks


def split_for_telegram(text: str, max_length: int = 4096) -> list[str]:
    """Split text into chunks safe for Telegram's message limit."""
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    current_chunk = ""

    for para in text.split("\n\n"):
        if len(current_chunk) + len(para) + 2 <= max_length:
            current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
        elif len(para) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            chunks.extend(_split_long_paragraph(para, max_length))
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
