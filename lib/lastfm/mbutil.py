# This is only here because I can't get codecs.EncodedFile to work. E for
# effort!

class EncodedFile:
    def __init__(self, f):
        self.f = f
    def __getattr__(self, a):
        return getattr(self.f, a)
    def write(self, s):
        self.f.write(s.encode(self.f.encoding or 'ascii', 'replace'))
