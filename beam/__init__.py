import time
import sys

from beam.constans import BEAM_VERSION

h = "\n\x1b[43m\x1b[30m  .--------------------------------------------------------------------------.  " \
"\x1b[0m\n\x1b[43m\x1b[30m (::: BEAM Framework v%s    | by Krystian Rembas @ iFM | Enjoy the usage! :::) " \
"\x1b[0m\n\x1b[43m\x1b[30m  '--------------------------------------------------------------------------'  \x1b[0m\n"

print >> sys.stderr, h % BEAM_VERSION

# don't ask why ;)
time.sleep(0.1)
