import sys

import semver

from dulwich import porcelain
from dulwich.client import get_transport_and_path
from dulwich.objectspec import parse_reftuples

with porcelain.open_repo_closing(".") as repo:
    latest_version = None
    latest_version_ref = None

    for ref in repo.refs.as_dict(b"refs/tags"):
        if ref.startswith(b"v"):
            sv_part = ref[1:].decode('ascii')
            if latest_version is None:
                latest_version = sv_part
                latest_version_ref = repo.refs[b"refs/tags/" + ref]
            elif semver.compare(sv_part, latest_version) > 0:
                latest_version = sv_part
                latest_version_ref = repo.refs[b"refs/tags/" + ref]

    client, host_path = get_transport_and_path("git://github.com/godfoder/dulwitch_selfref")

    remote_refs = client.fetch(host_path.encode('utf-8'), repo, progress=sys.stderr.write)
    # print(remote_refs)

    # print(repo.refs)

    dirty = False
    for ref in remote_refs:
        if ref.startswith(b"refs/tags/v"):
            sv_part = ref[11:].decode('ascii')
            if latest_version is None:
                latest_version = sv_part
                latest_version_ref = remote_refs[ref]
            elif semver.compare(sv_part, latest_version) > 0:
                latest_version = sv_part
                latest_version_ref = remote_refs[ref]
        elif ref == b"HEAD":            
            continue # Skip remote HEAD (only update to latest tagged)

        # Update Local Refs from remote
        if ref not in repo.refs:
            print("changed_ref", ref, remote_refs[ref])
            repo.refs[ref] = remote_refs[ref]
            dirty = True
        elif ref in repo.refs and remote_refs[ref] != repo.refs[ref]:
            print("changed_ref", ref, remote_refs[ref])
            repo.refs[ref] = remote_refs[ref]
            dirty = True
        else:
            pass

    if repo.refs[b"HEAD"] != latest_version_ref:
        repo.refs[b"HEAD"] = latest_version_ref
        dirty = True

    if dirty:
        print("dirty index, syncing")
        tree = repo[b"HEAD"].tree
        repo.reset_index()