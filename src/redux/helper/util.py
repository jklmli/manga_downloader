import gzip
import io
import random
import re
import time

try:
    import socks

    NO_SOCKS = False
except ImportError:
    NO_SOCKS = True
import socket

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

try:
    import HTMLParser
except ImportError:
    import html.parser as HTMLParser


class Util:
    @staticmethod
    def getSourceCode(url, proxy=None, returnRedirctUrl=False, maxRetries=1, waitRetryTime=1):
        """
        :rtype: str

        Loop to get around server denies for info or minor disconnects.
        """
        if (proxy != None):
            if (NO_SOCKS):
                raise RuntimeError('socks library required to use proxy (e.g. SocksiPy)')
            proxySettings = proxy.split(':')
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, proxySettings[0], int(proxySettings[1]),
                                  True)
            socket.socket = socks.socksocket
        ret = None
        request = urllib2.Request(url, headers={
            'User-agent': """Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML,
            like Gecko) Chrome/6.0.472.14 Safari/534.3""",
            'Accept-encoding': 'gzip'
        })
        while (ret == None):
            try:
                f = urllib2.urlopen(request)
                encoding = f.headers.get('Content-Encoding')
                if encoding == None:
                    ret = f.read()
                else:
                    if encoding.upper() == 'GZIP':
                        compressedstream = io.BytesIO(f.read())
                        gzipper = gzip.GzipFile(fileobj=compressedstream)
                        ret = gzipper.read()
                    else:
                        raise RuntimeError('Unknown HTTP Encoding returned')
            except urllib2.URLError:
                if (maxRetries == 0):
                    break
                else:
                    # random dist. for further protection against anti-leech
                    # idea from wget
                    time.sleep(random.uniform(0.5 * waitRetryTime, 1.5 * waitRetryTime))
                    maxRetries -= 1
        ret = str(ret)
        if returnRedirctUrl:
            return ret, f.geturl()
        else:
            return ret

    @staticmethod
    def normalize_value(s):
        """
        :rtype: str
        """
        try:
            float(s)
        except ValueError:
            return s
        else:
            return str(int(float(s)) if int(float(s)) == float(s) else float(s))

    @staticmethod
    # :SEE: http://stackoverflow.com/a/8940266/759714
    def natural_sort(l, key=lambda s: s):
        """
        :rtype: list

        Return a copy of the list in natural alphanumeric order.
        """

        def get_alphanum_key_func(key):
            convert = lambda text: int(text) if text.isdigit() else text
            return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]

        sort_key = get_alphanum_key_func(key)
        return sorted(l, key=sort_key)

    @staticmethod
    # :SEE: http://stackoverflow.com/a/275246/759714
    def unescape(s):
        """
        :rtype: str
        """
        return HTMLParser.HTMLParser().unescape(s)
