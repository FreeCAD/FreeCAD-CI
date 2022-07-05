import sys
# private tokens kastanie
sys.path.append("/home/freecadci/Documents/dev/freecad_src_ci_tools/")
# script code kastanie
sys.path.append("/home/freecadci/Documents/dev/freecad_src_ci_tools/freecadci/gitlab/scripts/")
# move inside the other modules

def delete_branche_with_no_pr():
    # imports
    import gitlab_ci_tools as glci
    import importlib
    importlib.reload(glci)

    # repo data
    from personal_data import github_token
    from personal_data import gitlab_token
    from personal_data import local_freecadci_repopath
    from personal_data import gitlab_freecadci_project
    from personal_data import github_user
    from personal_data import github_prjname
    github_repo = glci.get_github_repo(github_token, github_user, github_prjname)
    gitlab_project = glci.get_gitlab_project(gitlab_token, gitlab_freecadci_project)
    local_ci_repo = glci.get_local_ci_repo(local_freecadci_repopath)

    # see ci_run
    # get branches without open PRs
    prs_ids = sorted(glci.get_github_open_pr_numbers(github_repo))
    prbranches_names = sorted(glci.get_gitlab_prbranches_names(gitlab_project))

    branches_without_open_pr = []
    for prbr in prbranches_names:
        if int(prbr.lstrip("PR_")) not in prs_ids:
            branches_without_open_pr.append(prbr)

    len(prs_ids)
    len(prbranches_names)
    prs_ids
    prbranches_names

    print(branches_without_open_pr)


    # delete these branches
    for prbr in prbranches_names:
        try:
            gitlab_project.branches.delete(prbr)
        except Exception:
            print("Problem on deleting branch on gitlab: {}".format(prbr))
