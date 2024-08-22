#!/usr/bin/env python3

import os, base64, hashlib, shutil, mimetypes
from functools import reduce

SYNC_DIR = "sync_dir"
SYNC_TYPE = "sync_type"
SYNC_BUCKET = "sync_bucket"
SYNC_REGION = "sync_region"
SYNC_ACCESS_ID = "sync_access_id"
SYNC_ACCESS_SECRET = "sync_access_secret"


mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/woff2", ".woff2")


def guess_mime(fpath):
    """
    Guess mime by any path.

    >>> guess_mime('path/to/index.html')
    'text/html'
    >>> guess_mime('path/to/index.xhtml')
    'application/xhtml+xml'
    >>> guess_mime('path/to/index.txt')
    'text/plain'
    >>> guess_mime('path/to/INDEX.JPEG')
    'image/jpeg'
    >>> guess_mime('path/to/INDEX.WEBP')
    'image/webp'
    >>> guess_mime('path/to/index.otf')
    'font/otf'
    >>> guess_mime('path/to/index.woff')
    'font/woff'
    >>> guess_mime('path/to/index.woff2')
    'font/woff2'
    >>> guess_mime('path/to/index.css')
    'text/css'
    >>> guess_mime('path/to/index.js')
    'text/javascript'
    >>> guess_mime('path/to/index.mp4')
    'video/mp4'
    >>> guess_mime('path/to/download.zip')
    'application/zip'
    >>> guess_mime('path/to/favicon.ico')
    'image/x-icon'
    >>> guess_mime('path/to/index.tgzzz')
    'application/octet-stream'
    >>> guess_mime('path/to/index')
    'application/octet-stream'
    """
    _, ext = os.path.splitext(fpath)
    return mimetypes.types_map.get(ext.lower(), "application/octet-stream")


def sorted_objs(objs):
    return sorted(objs, key=lambda d: d["key"])


def file_objs_to_dict(acc, obj):
    'file object list to dict using obj["key"] as key.'
    key = obj["key"]
    if not key.endswith("/"):
        acc[key] = obj
    return acc


def diff(src_objs, dest_objs):
    """
    Create a diff by return adds, updates, deletes object list.

    >>> objs = walkdir('_site')
    >>> src_objs = objs[:] + [dict(key='z/update.txt', size=200, md5='UUUUUUUUUUUUUUUUUUUUUU==')]
    >>> dest_objs = objs[1:] + [dict(key='z/update.txt', size=100, md5='GOVl8c0J5IQiUlDtTe4LFM=='), dict(key='z/delete.txt', size=123, md5='ZZZZZZZZZZZZZZZZZZZZZZ==')]
    >>> a, u, d = diff(src_objs, dest_objs)
    >>> a
    [{'key': 'README.md', 'size': 47, 'md5': 'SPgiydU0kcyQmcQv/4ZIyA=='}]
    >>> u
    [{'key': 'z/update.txt', 'size': 200, 'md5': 'UUUUUUUUUUUUUUUUUUUUUU=='}]
    >>> d
    [{'key': 'z/delete.txt', 'size': 123, 'md5': 'ZZZZZZZZZZZZZZZZZZZZZZ=='}]
    """
    adds = []
    updates = []
    deletes = []
    local_objs = src_objs[:]
    remote_objs = reduce(file_objs_to_dict, dest_objs, {})
    for obj in local_objs:
        key = obj["key"]
        if key in remote_objs:
            # remote has obj with same key:
            robj = remote_objs[key]
            if obj["size"] != robj["size"] or obj["md5"] != robj["md5"]:
                # need update:
                updates.append(obj)
            del remote_objs[key]
        else:
            # key not found in remote:
            adds.append(obj)
    deletes = list(remote_objs.values())
    return sorted_objs(adds), sorted_objs(updates), sorted_objs(deletes)


def file_b64md5(fpath):
    """
    File md5 using base64.

    >>> file_b64md5('LICENSE')
    'HrvT40I3rybaXcCKTkQEZA=='
    """
    md5 = hashlib.md5()
    with open(fpath, "rb") as fp:
        md5.update(fp.read())
    return base64.b64encode(md5.digest()).decode("utf-8")


def etag_to_md5(s):
    """
    Convert E-Tag to b64-md5.

    >>> etag_to_md5("1ebbd3e34237af26da5dc08a4e440464")
    'HrvT40I3rybaXcCKTkQEZA=='
    >>> etag_to_md5('"1ebbd3e34237af26da5dc08a4e440464"')
    'HrvT40I3rybaXcCKTkQEZA=='
    >>> etag_to_md5('"1EBBD3E34237AF26DA5DC08A4E440464"')
    'HrvT40I3rybaXcCKTkQEZA=='
    """
    etag = s
    if etag.startswith('"'):
        etag = etag[1:]
    if etag.endswith('"'):
        etag = etag[:-1]
    if len(etag) == 32:
        etag = etag.lower()
        return base64.b64encode(bytes.fromhex(etag)).decode("utf-8")
    # for etag not using MD5, return '000...000':
    return "AAAAAAAAAAAAAAAAAAAAAA=="


def walkdir(p):
    """
    List files recursively in a directory. Each object is a dict with:
    {
        "key": "path/to/file",            # s3 compatible path without prefix "/"
        "size": 12345,                    # file size
        "md5": "HrvT40I3rybaXcCKTkQEZA==" # base64-encoded md5
    }

    >>> fs = walkdir('_site')
    >>> fs[0]
    {'key': 'README.md', 'size': 47, 'md5': 'SPgiydU0kcyQmcQv/4ZIyA=='}
    >>> fs[-1]
    {'key': 'z/last.txt', 'size': 22, 'md5': '9PR5WPGJrCSbsqksh2SBlQ=='}
    """
    prefix = len(p)
    if not p.endswith("/"):
        prefix = prefix + 1
    objs = []
    for root, _, files in os.walk(p):
        for f in files:
            fp = os.path.join(root, f)
            objs.append({"key": fp[prefix:], "size": os.path.getsize(fp), "md5": file_b64md5(fp)})
    return sorted_objs(objs)


def rmdir(p):
    if os.path.isdir(p):
        shutil.rmtree(p)


def mkdirs(p):
    if not os.path.isdir(p):
        os.makedirs(p)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
