#!/usr/bin/env python3

import os, json, base64, hashlib, shutil, zipfile, subprocess

import util


def main():
    # load env:
    from dotenv import load_dotenv

    load_dotenv(f".aws.env")
    sync_dir = os.environ.get(util.SYNC_DIR, "_site")
    sync_type = os.environ[util.SYNC_TYPE]
    print(f"sync {sync_dir} to {sync_type}...")
    ctx = {}
    env = os.environ
    s3 = __import__(sync_type, [])
    s3.init(ctx, env)
    src_objs = util.walkdir(sync_dir)
    print(f"loaded {len(src_objs)} local files.")
    dest_objs = s3.list_all(ctx, env)
    print(f"loaded {len(dest_objs)} remote files.")
    add_objs, update_objs, delete_objs = util.diff(src_objs, dest_objs)
    for obj in add_objs:
        print(f"upload new file: {obj['key']}, size: {obj['size']}, md5: {obj['md5']}")
        s3.upload(ctx, env, obj["key"], os.path.join(sync_dir, obj["key"]), obj["md5"])
    for obj in update_objs:
        print(f"override exist file: {obj['key']}, size: {obj['size']}, md5: {obj['md5']}")
        s3.upload(ctx, env, obj["key"], os.path.join(sync_dir, obj["key"]), obj["md5"])
    for obj in delete_objs:
        print(f"remove unused file: {obj['key']}, size: {obj['size']}, md5: {obj['md5']}")
        s3.delete(ctx, env, obj["key"])
    print(f"synced ok: added {len(add_objs)} files, updated {len(update_objs)} files, deleted {len(delete_objs)} files.")


if __name__ == "__main__":
    main()
