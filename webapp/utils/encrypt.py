# -*- coding: utf-8 -*-

import base64

BLOCK_SIZE = 16


def pkcs5_pad(s):
    n = BLOCK_SIZE - len(s) % BLOCK_SIZE
    return s + n * chr(n)


def pkcs5_unpad(s):
    return s[0:-ord(s[-1])]
