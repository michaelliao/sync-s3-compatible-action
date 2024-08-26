#!/usr/bin/env python3

import os

import util


def main():
    # load env for test:
    env_file = ".env"
    if os.path.exists(env_file):
        from dotenv import load_dotenv

        load_dotenv(env_file)
    sync_dir = os.environ.get(util.SYNC_DIR, "_site")
    sync_type = os.environ.get(util.SYNC_TYPE, "aws")
    sync_region = os.environ.get(util.SYNC_REGION, "")
    if not sync_region:
        print(f"ERROR: env not set: {util.SYNC_REGION}")
        exit(1)
    print(f"sync dir '{sync_dir}' to {sync_type}/{sync_region}...")
    # check env:
    for env_key in (util.SYNC_ACCESS_ID, util.SYNC_ACCESS_SECRET):
        if not os.environ.get(env_key, ""):
            print(f"ERROR: env not set: {env_key}")
            exit(1)
    # check if running in github action:
    gh_workspace = os.environ.get("GITHUB_WORKSPACE", "")
    if gh_workspace:
        sync_dir = os.path.join(gh_workspace, sync_dir)
        print(f"GitHub workspace: {gh_workspace}")
        print(f"Sync dir: {sync_dir}")

    # opt for unused files:
    opt_unused = os.environ.get(util.SYNC_OPT_UNUSED, "keep")
    print(f"sync strategy for unused files: {opt_unused}")

    ctx = {}
    env = os.environ
    s3 = __import__(sync_type, [])
    s3.init(ctx, env)
    src_objs = util.walkdir(sync_dir)
    print(f"loaded {len(src_objs)} local files.")
    dest_objs = s3.list_all(ctx, env)
    print(f"loaded {len(dest_objs)} remote files.")
    add_objs, update_objs, delete_objs = util.diff(src_objs, dest_objs)

    force_delete = opt_unused == "delete"
    keep_or_delete = "delete" if force_delete else "keep unused"
    print(f"sync start: will add {len(add_objs)} files, update {len(update_objs)} files, {keep_or_delete} {len(delete_objs)} files.")

    for obj in add_objs:
        print(f"upload new file: {obj['key']}, size: {obj['size']}, md5: {obj['md5']}")
        s3.upload(ctx, env, obj["key"], os.path.join(sync_dir, obj["key"]), obj["md5"])
    for obj in update_objs:
        print(f"override exist file: {obj['key']}, size: {obj['size']}, md5: {obj['md5']}")
        s3.upload(ctx, env, obj["key"], os.path.join(sync_dir, obj["key"]), obj["md5"])
    for obj in delete_objs:
        if force_delete:
            print(f"remove unused file: {obj['key']}, size: {obj['size']}, md5: {obj['md5']}")
            s3.delete(ctx, env, obj["key"])
        else:
            print(f"keep unused file: {obj['key']}, size: {obj['size']}, md5: {obj['md5']}")
    keep_or_delete = "deleted" if force_delete else "keep unused"
    print(f"synced ok: added {len(add_objs)} files, updated {len(update_objs)} files, {keep_or_delete} {len(delete_objs)} files.")


if __name__ == "__main__":
    main()
