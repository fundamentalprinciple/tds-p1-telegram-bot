def strip_code_fences(text: str) -> str:
    text = text.strip()

    if text.startswith("```python"):
        text = text[len("```python"):]

    elif text.startswith("```"):
        text = text[len("```"):]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()
