# ************************************************************************************************
def get_github_repo(token, github_user, github_prjname):

    from github import Github
    gh = Github(token)
    repo = None
    while repo is None:
        try:
            repo = gh.get_user(github_user).get_repo(github_prjname)
        except Exception:
            print("Problem in retrieving the github repo")
            repo = None
    # print(repo.name)
    return repo


# ************************************************************************************************
def get_gitlab_project(token, prj_namespace):

    from gitlab import Gitlab
    gl = Gitlab("https://gitlab.com/", private_token=token)
    project = gl.projects.get(prj_namespace)
    # print(project.name)
    return project


# ************************************************************************************************
def get_local_ci_repo(repopath):

    from git import Repo
    repo = Repo(repopath)

    return repo


# ************************************************************************************************
def get_github_open_pr_numbers(github_repo):

    prs_open = github_repo.get_pulls("open")

    ids = []
    for pr in prs_open:
        # print(pr.number)
        ids.append(pr.number)

    print(
        "Open PRs on github project '{}': {}"
        .format(github_repo.full_name, len(ids))
    )
    return ids


# ************************************************************************************************
def get_github_open_pr_users_data(github_repo):

    prs_open = github_repo.get_pulls("open")

    prs_users_data = {}
    for pr in prs_open:
        if pr.user.login not in prs_users_data:
            prs_users_data[pr.user.login] = pr.head.repo.html_url
        else:
            if prs_users_data[pr.user.login] != pr.head.repo.html_url:
                print("Error, user uses different repos for his PRs.")

    for k, v in prs_users_data.items():
        print("{} --> {}".format(k, v))

    return prs_users_data


# ************************************************************************************************
def create_local_branch_foreach_pr(repo, ids_prs):

    # branch_names = sorted([h.name for h in repo.heads], reverse=True)
    # print(branch_names)

    # delete all branches starting with "PR_"
    for br in repo.heads:
        if br.name.startswith("PR_"):
            repo.git.branch("-D", br.name)
    # branch_names = sorted([h.name for h in repo.heads], reverse=True)
    # print(branch_names)

    # try to fetch freecad
    github_fc_remote = "freecad"
    try:
        out = repo.git.fetch(github_fc_remote)
        print("Try to fetch remote FreeCAD repo from github")
        print(out)
    except Exception:
        print(
        "Fetching reomte 'freecad' failed for local repo"
        "try 'git fetch freecad on local git repo, if it fails add"
        "'ceck if 'git remote add freecad https://github.com/FreeCAD/FreeCAD'"
        )
        return False

    # checkout a branch for each PR
    for pr_no in ids_prs:
        print(pr_no)
        fetch_string = "pull/{}/head:PR_{}".format(pr_no, pr_no)
        try:
            repo.git.fetch(github_fc_remote, fetch_string)
        except Exception:
            print("Failed to checkout on local FreeCAD_CI repo: {}".format(pr_no))

    return True


# ************************************************************************************************
def create_local_remote_foreach_pr_user(repo, prs_users_data):

    remote_names = []
    for remote in repo.remotes:
        remote_names.append(remote.name)

    remote_names

    for userlogin, repoaddress in prs_users_data.items():
        if userlogin not in remote_names:
            repo.create_remote(userlogin, repoaddress)
        try:
            repo.git.fetch(userlogin)
        except Exception:
            print("Could not fetch {}".format(userlogin))

    for r in repo.remotes:
        if r.name not in prs_users_data:
            print(r)

    return True


# ************************************************************************************************
def push_from_local_repo_to_gitlab_ci_repo(repo):

    # git push -f origin --all
    try:
        repo.git.push("-f", "origin", "--all")
    except Exception:
        print("Problem on push lokal repo to gitlab")


# ************************************************************************************************
def get_gitlab_prs_pipelinedata(gitlab_project, projectname_on_gitlab):

    try:
        pipelines = gitlab_project.pipelines.list(all=True)
    except Exception:
        print("Problems in getting the pipeline data from gitlab")
        pipelines = []

    print(len(pipelines))

    prs_pipelinedata = {}
    for pl in pipelines:
        if not pl.ref.startswith("PR_"):
            continue
        pr = int(pl.ref.lstrip("PR_"))
        if pr not in prs_pipelinedata:
            prs_pipelinedata[pr] = (pl.ref, pl.id, pl.status, pl.sha)
        else:
            plid_saved = prs_pipelinedata[pr][1]
            if plid_saved < pl.id:
                prs_pipelinedata[pr] = (pl.ref, pl.id, pl.status)

    return prs_pipelinedata


# ************************************************************************************************
base_comment_pr_pipeline = (
    '<a '
    'href="https://gitlab.com/projektname/-/commits/branchname"'
    '><img alt="pipeline status" src="'
    'https://gitlab.com/projektname/badges/branchname/pipeline.svg'
    '"/></a> '
    'for feature branch [branchname]('
    'https://gitlab.com/projektname/-/commits/branchname'
    '). Pipeline [pipelineid]('
    'https://gitlab.com/projektname/-/pipelines/pipelineid'
    ') was triggered at [shortidcommit]('
    'https://github.com/FreeCAD/FreeCAD/pull/pullid/commits/commitid'
    '). All CI [branches]('
    'https://gitlab.com/projektname/-/branches/all'
    ') and [pipelines]('
    'https://gitlab.com/projektname/-/pipelines?scope=branches'
    ').'
)
def generate_comment_foreach_pr_pipeline(
    github_repo,
    prs_pipelinedata,
    gitlab_freecadci_project
):

    prs_open = github_repo.get_pulls("open")

    comments_all = []
    comments_new = {}
    for pr in prs_open:
        # print(pr.number)
        if pr.number in prs_pipelinedata:
            projektname = gitlab_freecadci_project
            branchname = prs_pipelinedata[pr.number][0]
            pipelineid = str(prs_pipelinedata[pr.number][1])
            # statusvalue = prs_pipelinedata[pr.number][2]
            commitid = prs_pipelinedata[pr.number][3]
            pullid = str(pr.number)
            # the word commitid should not in there in next line, is ok :-)
            shortidcommit = prs_pipelinedata[pr.number][3][0:7]

            the_comment = base_comment_pr_pipeline
            the_comment = the_comment.replace("projektname", projektname)
            the_comment = the_comment.replace("branchname", branchname)
            the_comment = the_comment.replace("pipelineid", pipelineid)
            # the_comment = the_comment.replace("statusvalue", statusvalue)
            the_comment = the_comment.replace("commitid", commitid)
            the_comment = the_comment.replace("pullid", pullid)
            the_comment = the_comment.replace("shortidcommit", shortidcommit)
            comments_all.append(the_comment)
            # print(the_comment)
            # print("\n\n")

            for comment in pr.get_issue_comments():
                if pipelineid in comment.body:
                    break
            else:
                comments_new[pr.number] = the_comment
    return (comments_all, comments_new)


# ************************************************************************************************
def create_on_github_comment_foreach_pr_pipeline(github_repo, comments_new):

    prs_open = github_repo.get_pulls("open")

    for pr in prs_open:
        if pr.number in comments_new:
            the_comment = comments_new[pr.number]
            pr.create_issue_comment(body=the_comment)


# ************************************************************************************************
def get_github_prs_contain_text_in_a_comment(
    github_repo,
    search_text
):

    prs_open = github_repo.get_pulls("open")

    pr_textinacomment = []
    for pro in prs_open:
        # print(pro.number)
        for comment in pro.get_issue_comments():
            if search_text in comment.body:
                pr_textinacomment.append(pro.number)
                break

    return pr_textinacomment


# ************************************************************************************************
def get_github_prs_do_not_contain_text_in_all_comments(
    github_repo,
    search_text
):

    prs_open = github_repo.get_pulls("open")

    pr_notextincomments = []
    for pro in prs_open:
        # print(pro.number)
        for comment in pro.get_issue_comments():
            if search_text in comment.body:
                break
        else:
            pr_notextincomments.append(pro.number)

    return pr_notextincomments


# ************************************************************************************************
def get_gitlab_prbranches_names(gitlab_project):

    branches = gitlab_project.branches.list(all=True)

    branch_names = []
    for br in branches:
        if not br.name.startswith("PR_"):
            continue
        branch_names.append(br.name)

    branch_names = sorted(branch_names)
    # len(branch_names)

    return branch_names


# ************************************************************************************************
def get_gitlab_branches_without_pipline(gitlab_project):

    pipelines = gitlab_project.pipelines.list(all=True)

    pipeline_branches = []
    for pl in pipelines:
        if not pl.ref.startswith("PR_"):
            continue
        pipeline_branches.append(pl.ref)

    pipeline_branches = sorted(list(set(pipeline_branches)))
    # len(pipeline_branches)

    prbranches_names = get_gitlab_prbranches_names(gitlab_project)

    brs_no_pipeline = []
    for brn in prbranches_names:
        if brn not in pipeline_branches:
            brs_no_pipeline.append(brn)

    return brs_no_pipeline


# ************************************************************************************************
def get_github_head_for_pr_branches(github_repo, pr_branches):

    prs_open = github_repo.get_pulls("open")

    prs_found = []
    for pro in prs_open:
        if "PR_{}".format(pro.number) in pr_branches:
            prs_found.append(pro)

    prs_base = {}
    for pro in prs_found:
        # print(pro.number)
        prs_base[pro.number] = pro.base.sha  # base commit

    return prs_base


# ************************************************************************************************
def has_local_prbranch_a_specific_commit(repo, prs_base, the_commit):

    # the unit test commit
    # https://gitpython.readthedocs.io/en/stable/tutorial.html#the-commit-object
    # unit test commit 70c5505a75ad545cb671eb73f29d5e1626aebf78

    co_max_timestamp = repo.commit(the_commit).committed_date

    cicommit_ok = []
    cicommit_notok = []
    for prnr, coid in prs_base.items():
        coclass = repo.commit(coid)
        if coclass.committed_date < co_max_timestamp:
            cicommit_notok.append(prnr)
        elif coclass.committed_date >= co_max_timestamp:
            cicommit_ok.append(prnr)
        else:
            print("error")

    return (cicommit_notok, cicommit_ok)


# ************************************************************************************************
def print_prlinks_according_user_and_pr(github_repo, prslist):

    prs_open = github_repo.get_pulls("open")

    prs_noreb_user = {}
    for pro in prs_open:
        if pro.number in prslist:
            if pro.user.login not in prs_noreb_user:
                prs_noreb_user[pro.user.login] = [pro.number]
            else:
                prs_noreb_user[pro.user.login].append(pro.number)

    prs_noreb_user
    for us, prs in prs_noreb_user.items():
        print("\ngithub user {}:".format(us))
        for pr in prs:
            print("  https://github.com/FreeCAD/FreeCAD/pull/{}".format(pr))

    # TODO return string
    return True


# ************************************************************************************************
def delete_gitlab_branches_without_pr_on_github(github_repo, gitlab_project):

    # get branches without open PRs
    prs_ids = sorted(get_github_open_pr_numbers(github_repo))
    prbranches_names = sorted(get_gitlab_prbranches_names(gitlab_project))

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
    for prbr in branches_without_open_pr:
        try:
            gitlab_project.branches.delete(prbr)
            print("branch: {} has been deleted on gitlab FreeCAD-CI.".format(prbr))
        except Exception:
            print("Problem  deleting branch {} on gitlab FreeCAD-CI.".format(prbr))

    return True
