__author__ = 'paul_new'

import hashlib
from settings.salts import SALTS
SALTS_LENGTH = len(SALTS)

class HashPassword(object):

    def __init__(self):
        super(HashPassword, self).__init__()

    def Action(self, text):
        if isinstance(text, unicode):
            text = text.encode("UTF-8")
        index = hash(str(text)) % (SALTS_LENGTH)
        password_hash = hashlib.sha1("%s+++%s"%( text, SALTS[index])).hexdigest()
        return password_hash
