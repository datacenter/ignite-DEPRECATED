from Crypto.Cipher import AES
import base64
import os

import logging
logger = logging.getLogger(__name__)


SECRET_KEY = "C!sc0D@t@center1"

# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 16

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)


def encrypt_data(text):
    cipher = AES.new(SECRET_KEY)
    logger.info("data encrypt")
    return EncodeAES(cipher, text)
    
def decrypt_data(text):
    cipher = AES.new(SECRET_KEY)
    logger.info("data decrypt")
    return DecodeAES(cipher, text)
