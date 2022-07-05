# TODO after a longer break a few days, there are a lot new branches
# after a push only for 4 branches a pipeline is created
# ATM 4 branches will be deleted manually and afterwards pusched again
# this is repated as long as there are branches without a pipeling
# TODO: never push more than 4 branches at once


def run_forever():
    import time
    while True:
        print("Run started")
        try:
            run_all()
        except Exception:
            print("run_all() failed")
        print("Run finished")
        print("Pause time start")
        print("60")
        time.sleep(10)
        print("50")
        time.sleep(10)
        print("40")
        time.sleep(10)
        print("30")
        time.sleep(10)
        print("20")
        time.sleep(10)
        print("10")
        time.sleep(10)
        print("Pause time end")
    

def run_all():
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

    # ************************************************************************************************
    # see gitlab_ci_run module

    status = glci.create_local_branch_foreach_pr(
        local_ci_repo,
        glci.get_github_open_pr_numbers(github_repo)
    )
    status = glci.create_local_remote_foreach_pr_user(
        local_ci_repo,
        glci.get_github_open_pr_users_data(github_repo)
    )
    comments_all, comments_new = glci.generate_comment_foreach_pr_pipeline(
        github_repo,
        glci.get_gitlab_prs_pipelinedata(
            gitlab_project,
            gitlab_freecadci_project
        ),
        gitlab_freecadci_project
    )
    len(comments_new)
    for k, v in comments_new.items():
        print("\n# {} {}". format(k, 50*"*"))
        print(v)
    glci.create_on_github_comment_foreach_pr_pipeline(github_repo, comments_new)

    # push
    # push with bernd and not with freecadci thus not yet ok
    print("puuuush")
    glci.push_from_local_repo_to_gitlab_ci_repo(local_ci_repo)

    # ************************************************************************************************
    # delete branches on gitlab without a PR on github
    time.sleep(2)
    print("Branches on gitlab without PR on github will be deleted.")
    glci.delete_gitlab_branches_without_pr_on_github(github_repo, gitlab_project)
