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
        try:
            (token, value) = pair.split('=')
            capabilities.update({
                token: value
            })
        except ValueError:
            # There's two possibilities here:-
            try:
                # 1. The last field is a comment and has a ',' in it
                # - for this, append the whole thing, comma and all, to the
                # previous one.
                capabilities.update({
                    token: '{},{}'.format(value, pair)
                })
            except UnboundLocalError:
                # 2. The format is something like: <IGATE,CLOSED
                # - in this case, there's no 'previous' token for us to append to,
                # so we can just add a single blank entry with CLOSED as the
                # token.
                capabilities.update({
                    pair: None
                })

    # Add capabilities to the returned parsed dict
    parsed.update({
        'capabilities': capabilities
    })

    return ('', parsed)
