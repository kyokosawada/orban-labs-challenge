import unicodedata
from ipaddress import IPv4Address, IPv6Address, IPv6Network, ip_address
from urllib.parse import SplitResult, urlsplit

WEB_SCHEMES = frozenset({"http", "https"})

LOOPBACK_NAME = "localhost"

HOST_DELIMITERS = frozenset("/\\:?#@[]%")

SCHEME_REFUSAL = "Destination must start with http:// or https://."
HOST_REFUSAL = "Destination must include a host, like https://example.com/page."
HOST_SHAPE_REFUSAL = (
    "Destination host must be a name or an address written in full, like "
    "https://example.com/page or https://93.184.216.34/page."
)
PORT_REFUSAL = (
    "Destination port must be a number below 65536, like https://example.com:8443/page."
)
PUBLIC_REFUSAL = (
    "Destination must point at a public host, not a loopback, link-local or "
    "private-network address."
)

_EMBEDDED_IPV4_PREFIXES = (
    IPv6Network("::/96"),
    IPv6Network("::ffff:0:0:0/96"),
    IPv6Network("64:ff9b::/96"),
)


def _split(destination: str) -> SplitResult:
    try:
        return urlsplit(destination)
    except ValueError as unparsable:
        raise ValueError(HOST_SHAPE_REFUSAL) from unparsable


def _host_of(parts: SplitResult) -> str:
    try:
        port = parts.port
    except ValueError as unreadable:
        raise ValueError(PORT_REFUSAL) from unreadable
    if port == 0:
        raise ValueError(PORT_REFUSAL)
    host = parts.hostname
    if not host:
        raise ValueError(HOST_REFUSAL)
    return unicodedata.normalize("NFKC", host).casefold().rstrip(".")


def _as_address(host: str) -> IPv4Address | IPv6Address | None:
    try:
        address = ip_address(host)
    except ValueError:
        return None
    if isinstance(address, IPv6Address):
        embedded = _embedded_ipv4(address)
        if embedded is not None:
            return embedded
    return address


def _embedded_ipv4(address: IPv6Address) -> IPv4Address | None:
    if address.ipv4_mapped is not None:
        return address.ipv4_mapped
    for prefix in _EMBEDDED_IPV4_PREFIXES:
        if address in prefix:
            return IPv4Address(int(address) & 0xFFFFFFFF)
    return None


def _is_public(address: IPv4Address | IPv6Address) -> bool:
    return address.is_global and not address.is_multicast


def _is_host_name(host: str) -> bool:
    labels = host.split(".")
    if any(not label for label in labels):
        return False
    if any(character.isspace() or character in HOST_DELIMITERS for character in host):
        return False
    return labels[-1][0].isalpha()


def _is_loopback_name(host: str) -> bool:
    return host == LOOPBACK_NAME or host.endswith(f".{LOOPBACK_NAME}")


def validate_destination(destination: str) -> str:
    parts = _split(destination)
    if parts.scheme.lower() not in WEB_SCHEMES:
        raise ValueError(SCHEME_REFUSAL)
    host = _host_of(parts)
    address = _as_address(host)
    if address is not None:
        if not _is_public(address):
            raise ValueError(PUBLIC_REFUSAL)
        return destination
    if not _is_host_name(host):
        raise ValueError(HOST_SHAPE_REFUSAL)
    if _is_loopback_name(host):
        raise ValueError(PUBLIC_REFUSAL)
    return destination
