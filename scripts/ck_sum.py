import hashlib
import re
import sys


def get_ck_sum(fname):

    fh = open(fname, "r")
    contents_fh = fh.readlines()
    fh.close()

    if re.match(r'^\#md5sum*', contents_fh[1]):
        fh = open(fname, "w")
        contents_fh.remove(contents_fh[1])
        contents = "".join(contents_fh)
        fh.write(contents)
        fh.close()

    ck_sum = hashlib.md5(open(fname, "rb").read()).hexdigest()
    value = "#md5sum=<%s>\n" % (ck_sum)

    fh = open(fname, "w")
    contents_fh.insert(1, value)
    contents = "".join(contents_fh)
    fh.write(contents)
    fh.close()
