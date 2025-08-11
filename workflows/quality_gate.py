def complexity_score(code_or_text: str) -> float:
    length = len(code_or_text or '')
    if length < 120:
        return 0.1
    if length < 500:
        return 0.4
    return 0.8
def quality_check(code_or_text: str) -> str:
    score = complexity_score(code_or_text)
    if score > 0.7:
        return 'cloud'
    return 'local'
