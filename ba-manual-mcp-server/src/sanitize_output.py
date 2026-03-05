import re
from functools import wraps
from typing import Any

SECRET_KEYWORDS = [
    "password", "passwd", "pwd", "secret", "token", "apikey", "api_key", "api-key", "accessToken", "access_token", "access-token", "authorization"
]

def _mask_secrets_in_str(s: str) -> str:
    keywords_pattern = '|'.join(map(re.escape, SECRET_KEYWORDS))

    pattern = rf'(["\']?)(\b(?:{keywords_pattern})\b)\1\s*[:=]\s*(".*?"|\'.*?\'|[^\s,;]+)'
    s = re.sub(
        pattern,
        lambda m: f"{m.group(2)}: ****",
        s,
        flags=re.IGNORECASE
    )

    return s

def _escape_quotation_marks_and_ticks(unescaped: str) -> str:

    double_escaped = unescaped.replace('"', '\\"')
    single_escaped = double_escaped.replace("'", "\\'")
    tick_escaped = single_escaped.replace("`", "\\`")

    return tick_escaped

def _remove_path_traversal(path: str) -> str:

    while path.startswith("../"):
        path = path.replace("../", "")

    return path

def _sanitize_value(value: Any) -> Any:

    if isinstance(value, str):
        value_redacted = _mask_secrets_in_str(value)
        value_escaped = _escape_quotation_marks_and_ticks(value_redacted)
        value_stripped = _remove_path_traversal(value_escaped)
        return value_stripped

    if isinstance(value, dict):
        out = {}
        for k, val in value.items():
            out[k] = "****" if any(kw in k.lower() for kw in SECRET_KEYWORDS) and not isinstance(val, (dict, list, tuple)) else _sanitize_value(val)
        return out

    if isinstance(value, list):
        return [_sanitize_value(x) for x in value]

    if isinstance(value, tuple):
        return tuple(_sanitize_value(x) for x in value)

    return value

def sanitize_output():

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            result = await func(*args, **kwargs)
            return _sanitize_value(result)

        return wrapper

    return decorator
