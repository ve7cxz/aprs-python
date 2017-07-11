import re
from aprslib.exceptions import ParseError

__all__ = [
    'parse_capability'
    ]


def parse_capability(body):
    # Strip off any newlines
    body = body.rstrip()

    match = re.match("^(\w+),(.*)", body)
    if not match:
        raise ParseError("invalid station capability message")

    # Get the capability type - this should (in reality) always be
    # IGATE, but the spec allows for other
    capability_type = match.group(1)

    # Build our parsed dicts
    parsed = {
        'format': 'capability',
    }

    capabilities = {
        'type': capability_type
    }

    # Loop through the capabilities
    for pair in match.group(2).rstrip().split(','):
        (token, value) = pair.split('=')
        capabilities.update({
            token: value
        })

    # Add capabilities to the returned parsed dict
    parsed.update({
        'capabilities': capabilities
    })

    return ('', parsed)
