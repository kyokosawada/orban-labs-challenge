from urllib.parse import urlsplit

WEB_SCHEMES = frozenset({"http", "https"})

SCHEME_REFUSAL = "Destination must start with http:// or https://."
HOST_REFUSAL = "Destination must include a host, like https://example.com/page."


def _host_of(destination: str) -> str:
    try:
        parts = urlsplit(destination)
        scheme = parts.scheme.lower()
    except ValueError as unparsable:
        raise ValueError(HOST_REFUSAL) from unparsable
    if scheme not in WEB_SCHEMES:
        raise ValueError(SCHEME_REFUSAL)
    try:
        host = parts.hostname
    except ValueError as unparsable:
        raise ValueError(HOST_REFUSAL) from unparsable
    if not host:
        raise ValueError(HOST_REFUSAL)
    return host.rstrip(".")


def validate_destination(destination: str) -> str:
    _host_of(destination)
    return destination
