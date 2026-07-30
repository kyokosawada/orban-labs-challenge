import re
from ipaddress import IPv4Address, IPv6Address, ip_address
from urllib.parse import urlsplit

WEB_SCHEMES = frozenset({"http", "https"})

LOOPBACK_NAME = "localhost"

SCHEME_REFUSAL = "Destination must start with http:// or https://."
HOST_REFUSAL = "Destination must include a host, like https://example.com/page."
PUBLIC_REFUSAL = (
    "Destination must point at a public host, not a loopback, link-local or "
    "private-network address."
)

_HOST_NAME = re.compile(r"^(?:[^\s./]+\.)*[A-Za-z][^\s./]*$")


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


def _as_address(host: str) -> IPv4Address | IPv6Address | None:
    try:
        address = ip_address(host)
    except ValueError:
        return None
    if isinstance(address, IPv6Address) and address.ipv4_mapped is not None:
        return address.ipv4_mapped
    return address


def _is_public(address: IPv4Address | IPv6Address) -> bool:
    return address.is_global and not address.is_multicast


def validate_destination(destination: str) -> str:
    host = _host_of(destination)
    address = _as_address(host)
    if address is not None:
        if not _is_public(address):
            raise ValueError(PUBLIC_REFUSAL)
        return destination
    if not _HOST_NAME.match(host):
        raise ValueError(HOST_REFUSAL)
    if host == LOOPBACK_NAME or host.endswith(f".{LOOPBACK_NAME}"):
        raise ValueError(PUBLIC_REFUSAL)
    return destination
