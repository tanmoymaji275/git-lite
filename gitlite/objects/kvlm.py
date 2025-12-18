import collections

def kvlm_parse(raw, start=0, dct=None):
    if not dct:
        dct = collections.OrderedDict()

    spc = raw.find(b' ', start)
    nl = raw.find(b'\n', start)

    # If no space or newline is found, or newline comes before space,
    # it means we are at the blank line before the message.
    if (spc < 0) or (nl < spc):
        if nl != start:
            raise ValueError(f"Invalid object: expected blank line at position {start}")
        dct[None] = raw[start+1:]
        return dct

    key = raw[start:spc]

    # Find the end of the value. Continuation lines start with space.
    end = start
    while True:
        end = raw.find(b'\n', end+1)
        if end < 0:
            raise ValueError("Invalid object: unterminated header value")
        if end + 1 >= len(raw) or raw[end+1] != ord(' '):
            break

    value = raw[spc+1:end].replace(b'\n ', b'\n')

    if key in dct:
        if isinstance(dct[key], list):
            dct[key].append(value)
        else:
            dct[key] = [dct[key], value]
    else:
        dct[key] = value

    return kvlm_parse(raw, start=end+1, dct=dct)

def kvlm_serialize(kvlm):
    ret = b""
    for k in kvlm.keys():
        if k is None: continue
        val = kvlm[k]
        if not isinstance(val, list):
            val = [val]

        for v in val:
            ret += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'

    ret += b'\n'
    if None in kvlm:
        ret += kvlm[None]
        
    return ret
