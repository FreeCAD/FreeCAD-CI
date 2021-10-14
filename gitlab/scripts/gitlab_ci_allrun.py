def run_forever():
    import time
    while True:
        print("Run started")
        run_all()
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
        run_all()
        print("Pause looong")
        time.sleep(1000)
    

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
