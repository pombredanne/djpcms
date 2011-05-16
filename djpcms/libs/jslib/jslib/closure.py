#!/usr/bin/python2.4

import httplib, urllib, sys

# Define the parameters for the POST request and encode them in
# a URL-safe format.

params = urllib.urlencode([
    ('code_url', sys.argv[1]),
    ('compilation_level', 'ADVANCED_OPTIMIZATIONS'),
    ('output_format', 'text'),
    ('output_info', 'compiled_code'),
    ('js_externs', 'function textDiv(text){}'), # <-- New parameter!
    ('formatting', 'pretty_print')
  ])

# Always use the following value for the Content-type header.
headers = { "Content-type": "application/x-www-form-urlencoded" }
conn = httplib.HTTPConnection('closure-compiler.appspot.com')
conn.request('POST', '/compile', params, headers)
response = conn.getresponse()
data = response.read()
conn.close
