import sys

from dulwich import porcelain
from dulwich.client import get_transport_and_path
from dulwich.objectspec import parse_reftuples

with porcelain.open_repo_closing(".") as repo:

    client, host_path = get_transport_and_path("git://github.com/godfoder/dulwitch_selfref")

    remote_refs = client.fetch(host_path.encode('utf-8'), repo, progress=sys.stderr.write)
    # print(remote_refs)

    # print(repo.refs)

    dirty = False
    for ref in remote_refs:
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

    if dirty:
        print("dirty index, syncing")
        tree = repo[b"HEAD"].tree
        repo.reset_index()