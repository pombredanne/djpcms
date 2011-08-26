import djpcms

STYLING = 'smooth'

if djpcms.ispy3k:
    PYTHON_LOGO_URL = 'http://pypi.python.org/python-3.png'
else:
    PYTHON_LOGO_URL = 'http://www.python.org/community/logos/\
python-logo-master-v3-TM.png'

PYTHON_POWERED_200x80 = 'http://www.python.org/community/logos/python\
-powered-w-200x80.png'
PYTHON_POWERED_140x56 = 'http://www.python.org/community/logos/python\
-powered-w-140x56.png'
PYTHON_POWERED_100x40 = 'http://www.python.org/community/logos/python\
-powered-w-100x40.png'
PYTHON_POWERED_70x28 = 'http://www.python.org/community/logos/python\
-powered-w-70x28.png'

COMPRESS_ENABLED = False
# Allows changing verbosity from the settings.
COMPRESS_VERBOSE = False
# the backend to use when parsing the JavaScript or Stylesheet files
COMPRESS_PARSER = 'compressor.parser.AutoSelectParser'
COMPRESS_OUTPUT_DIR = 'CACHE'
COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'
COMPRESS_CSS_COMPRESSOR = "compressor.css.CssCompressor"
COMPRESS_JS_COMPRESSOR = "compressor.js.JsCompressor"
