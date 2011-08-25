import re

from djpcms.utils.text import compress_string
from djpcms.utils.cache import patch_vary_headers

re_accepts_gzip = re.compile(r'\bgzip\b')


class GZipMiddleware(object):
    """
    This middleware compresses content if the browser allows gzip compression.
    It sets the Vary header accordingly, so that caches will base their storage
    on the Accept-Encoding header.
    """
    def process_response(self, request, response):
        # It's not worth compressing non-OK or really short responses.
        if response.status_code != 200 or response.is_streamed:
            return response
        
        patch_vary_headers(response, ('Accept-Encoding',))

        # Avoid gzipping if we've already got a content-encoding.
        if 'Content-Encoding' in response:
            return response
        
        environ = request.environ
        
        # MSIE have issues with gzipped response of various content types.
        if "msie" in environ.get('HTTP_USER_AGENT', '').lower():
            ctype = response.get('Content-Type', '').lower()
            if not ctype.startswith("text/") or "javascript" in ctype:
                return response

        ae = environ.get('HTTP_ACCEPT_ENCODING', '')
        if not re_accepts_gzip.search(ae):
            return response

        content = '\n'.join(response.content)
        if len(content) < 200:
            return response
        
        response.content = (compress_string(content),)
        response['Content-Encoding'] = 'gzip'
        #response['Content-Length'] = str(len(response.content))
        return response
    