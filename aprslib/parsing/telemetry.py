import re
from aprslib import base91
from aprslib.exceptions import ParseError
from aprslib.parsing import logger

__all__ = [
        'parse_telemetry',
        'parse_comment_telemetry',
        'parse_telemetry_config',
        'parse_telemetry_report'
        ]


def parse_telemetry(body):
    parsed = {}

    match = re.match(r'#(\d{3},|MIC,?)(\d{3}),(\d{3}),(\d{3}),(\d{3}),(\d{3}),([0-1]{8})(.*)', body, flags=re.I)

    if not match:
        raise ParseError("Invalid telemetry format")

    data = match.groups()

    parsed.update({
        'format': 'telemetry',
        'sequence_number': 0 if data[0].lower().startswith('mic') else int(data[0][:3]),
        'analog_values': list(map(int, data[1:6])),
        'digital_value': int(data[6], 2)
        })

    return '', parsed


def parse_comment_telemetry(text):
    """
    Looks for base91 telemetry found in comment field
    Returns [remaining_text, telemetry]
    """
    parsed = {}
    match = re.findall(r"^(.*?)\|([!-{]{4,14})\|(.*)$", text)

    if match and len(match[0][1]) % 2 == 0:
        text, telemetry, post = match[0]
        text += post

        temp = [0] * 7
        for i in range(7):
            temp[i] = base91.to_decimal(telemetry[i*2:i*2+2])

        parsed.update({
            'telemetry': {
                'seq': temp[0],
                'vals': temp[1:6]
                }
            })

        if temp[6] != '':
            parsed['telemetry'].update({
                'bits': "{0:08b}".format(temp[6] & 0xFF)[::-1]
                })

    return (text, parsed)

def parse_telemetry_report(body):
    parsed = {}

    # Strictly speaking, the spec says the values should be 3 digits with a
    # range of 0 to 255, however in practice you may see decimals. Even Bob
    # WB4APR suggests that it's merely 3 bytes, and allows values up to 999 -
    # http://www.tapr.org/pipermail/aprssig/2013-March/041637.html
    match = re.findall(r"^#(MIC|\d+),?([\d\.,]+)$", body)
    if not match:
        raise ParseError("incorrect format for telemetry report packet - non-integer values?")

    else:
        logger.debug("Attempting to parse telemetry report packet")
        sequence, values = match[0]

        parsed.update({'format': 'telemetry-report'})

        # Given the note above, rather than converting to an integer or a
        # decimal/float, just pass the extracted values back as strings and let
        # the recipient deal with them as they see fit.
        parsed.update({
            'telemetry': {
                'seq': sequence,
                'vals': values.split(',')
            }
        })

    return ('', parsed)

def parse_telemetry_config(body):
    parsed = {}

    match = re.findall(r"^(PARM|UNIT|EQNS|BITS)\.(.*)$", body)
    if match:
        logger.debug("Attempting to parse telemetry-message packet")
        form, body = match[0]

        parsed.update({'format': 'telemetry-message'})

        if form in ["PARM", "UNIT"]:
            vals = body.rstrip().split(',')[:13]

            for val in vals:
                if not re.match(r"^(.{1,20}|)$", val):
                    raise ParseError("incorrect format of %s (name too long?)" % form)

            defvals = [''] * 13
            defvals[:len(vals)] = vals

            parsed.update({
                't%s' % form: defvals
                })
        elif form == "EQNS":
            eqns = body.rstrip().split(',')[:15]
            teqns = [0, 1, 0] * 5

            for idx, val in enumerate(eqns):
                if not re.match(r"^([-]?\d*\.?\d+|)$", val):
                    raise ParseError("value at %d is not a number in %s" % (idx+1, form))
                else:
                    try:
                        val = int(val)
                    except:
                        val = float(val) if val != "" else 0

                    teqns[idx] = val

            # group values in 5 list of 3
            teqns = [teqns[i*3:(i+1)*3] for i in range(5)]

            parsed.update({
                't%s' % form: teqns
                })
        elif form == "BITS":
            match = re.findall(r"^([01]{8}),(.{0,23})$", body.rstrip())
            if not match:
                raise ParseError("incorrect format of %s (title too long?)" % form)

            bits, title = match[0]

            parsed.update({
                't%s' % form: bits,
                'title': title.strip(' ')
                })

    return (body, parsed)

