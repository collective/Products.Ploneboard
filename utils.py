def toAscii(s):
    if type(s) != type(u''):
        s = str(s)
    snew = ''
    for c in s:
        if ord(c) < 128:
            snew += c
    return str(snew)