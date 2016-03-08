from dulwich import porcelain

with porcelain.open_repo_closing(".") as repo:
    print(porcelain.status(repo))