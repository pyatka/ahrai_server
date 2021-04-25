import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/ahrai_server")

from haluka import app as application
application.secret_key = 'e875109d-66a6-47c6-a0c0-4525bfb16312'