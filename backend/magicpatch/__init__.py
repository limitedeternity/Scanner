import os
import sys

MAGIC_LIBRARY = "libmagic"
WINMAGIC_PATH = os.path.dirname(os.path.realpath(__file__))
MAGIC_LIBRARY_PATH = os.path.join(WINMAGIC_PATH, MAGIC_LIBRARY)
MAGIC_FILE = os.path.join(MAGIC_LIBRARY_PATH, "magic.mgc")

_activate = os.name == "nt" and sys.maxsize > 2 ** 32
if _activate:
    os.environ["PATH"] += os.pathsep + MAGIC_LIBRARY_PATH

import magic

if _activate:
    old_init = magic.Magic.__init__

    def new_init(self, mime=False, magic_file=None, mime_encoding=False, keep_going=False, uncompress=False):
        if magic_file == None:
            magic_file = MAGIC_FILE

        old_init(self, mime, magic_file, mime_encoding, keep_going, uncompress)

    magic.Magic.__init__ = new_init

__all__ = ("magic",)
