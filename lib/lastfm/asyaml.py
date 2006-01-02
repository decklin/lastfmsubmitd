import time

TIME_FMT = "%Y-%m-%d %H:%M:%S"

def format_time(timespec):
    """Return a string representation of time in %s UTC format.""" % TIME_FMT
    return time.strftime(TIME_FMT, timespec)

def parse_time(timespec):
    """Returns a time tuple representing the given time, specified either in
    seconds since the epoch or a string in %s UTC format.""" % TIME_FMT
    try:
        return time.gmtime(float(timespec))
    except ValueError:
        return time.strptime(timespec, TIME_FMT)

def parse_length(length):
    """Returns the number of seconds in the given time, specified as seconds,
    or a string in 'minutes:seconds' format."""
    try:
        return int(length)
    except ValueError:
        m, s = map(int, length.split(':'))
        return m * 60 + s

class Metadata:
    """Generic metadata container. May have any of artist, title, length,
    album, or mbid."""

    def __init__(self, **kwargs):
        for meta in ('artist', 'title', 'length', 'album', 'mbid'):
            if kwargs.has_key(meta):
                setattr(self, meta, kwargs[meta])

class Serializable(Metadata):
    """A pseudo-YAML document representing one of the types we recognise: Song
    or Submission. Any document which does not start with !asyaml/Submission:
    or !asyaml/Song: will cause an error.

    This format should be parseable and emittable by a *real* YAML
    implementation, but for reference, the subset we implement has the
    following restrictions:

    * Documents may only contain a single map
    * No escaping or quoting
    * No unprintable characters
    * Encoding is always UTF-8, unless it's just ASCII."""

    def __init__(self, header):
        self.content = {}
        header = header.strip()
        if header == "!asyaml/Song:":
            self.type = Song
        elif header == "!asyaml/Submission:":
            self.type = Submission
        else:
            raise ValueError("unknown type '%s'" % header)

    def feed_line(self, line):
        if ":" in line:
            k, v = map(str.strip, line.split(":", 1))
            if k in ('artist', 'title', 'album'):
                self.content[k] = v.decode('utf-8')
            elif k == 'length':
                self.content[k] = parse_length(v)
            elif k == 'time':
                self.content[k] = parse_time(v)
            else:
                self.content[k] = v
        else:
            raise ValueError("bad line '%s'" % line)

    def finish(self):
        return self.type(**self.content)

    def __str__(self):
        header = "--- !asyaml/%s:\n" % self.__class__.__name__
        data = [
            "artist: %s" % self.artist.encode('utf-8'),
            "title: %s" % self.title.encode('utf-8'),
            "length: %d:%02d" % divmod(self.length, 60),
            ]
        if hasattr(self, 'album'):
            data.append("album: %s" % self.album.encode('utf-8'))
        if hasattr(self, 'mbid'):
            data.append("mbid: %s" % self.mbid.encode('utf-8'))
        if hasattr(self, 'time'):
            data.append("time: %s" % format_time(self.time))
        return header + "\n".join(data)

    def shortname(self):
        return "%s - %s [%d:%02d]" % ((self.artist, self.title) +
            divmod(self.length, 60))

class Song(Metadata, Serializable):
    """Metadata representing an actual song. Must have artist/title/length,
    album/mbid are optional."""

    def __init__(self, **kwargs):
        for meta in ('artist', 'title', 'length'):
            if not kwargs.has_key(meta):
                raise ValueError("missing metadata: %s" % meta)
        Metadata.__init__(self, **kwargs)

class Submission(Song):
    """A submission for an Audioscrobbler service such as Last.fm. Exactly
    like a Song, but it also must have a time (i.e, when it was played). Can
    optionally be initialized with 'track' and 'time' as keyword arguments as
    opposed to the full set."""

    def __init__(self, **kwargs):
        if kwargs.has_key('track'):
            trackinfo = {}
            for meta in ('artist', 'title', 'length', 'album', 'mbid'):
                if hasattr(kwargs['track'], meta):
                    trackinfo[meta] = getattr(kwargs['track'], meta)
            Song.__init__(self, **trackinfo)
        else:
            Song.__init__(self, **kwargs)
        try:
            self.time = kwargs['time']
        except KeyError, e:
            raise ValueError("no time specified for submission: %s" %
                repr(kwargs))

class Parser:
    """Reads a list of one or more serialized tracks or submissions, and makes
    them available in self.items. Only parses the subset of YAML that we emit
    (see Doc)."""

    def __init__(self, data=None):
        if data:
            self.feed(data)

    def feed(self, data):
        self.items = [i for i in self._parse(data)]

    def _parse(self, data):
        if data:
            doc = None
            for line in map(str.strip, data.split("\n")):
                if line == "":
                    pass
                elif line.startswith("---"):
                    if doc: yield doc.finish()
                    try:
                        doc = Serializable(line[3:])
                    except ValueError:
                        doc = None
                else:
                    if doc:
                        try:
                            doc.feed_line(line)
                        except ValueError:
                            pass
                    else:
                        raise ValueError("found data with no header: '%s'" %
                            line)
            if doc:
                yield doc.finish()
