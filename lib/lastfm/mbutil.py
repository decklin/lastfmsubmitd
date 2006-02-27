# This is only here because I can't get codecs.EncodedFile to work. E for
# effort!

import locale

class EncodedFile:
    def __init__(self, f):
        self.f = f
    def __getattr__(self, a):
        return getattr(self.f, a)
    def write(self, s):
        encoding = self.f.encoding or locale.getpreferredencoding()
        self.f.write(s.encode(encoding, 'replace'))
