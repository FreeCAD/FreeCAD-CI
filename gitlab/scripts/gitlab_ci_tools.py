# ************************************************************************************************
def get_github_open_pr_numbers(token=None):

    if token is None:
        print("No token given, nothing done.")
        return

    from github import Github
    g = Github(token)
    repo = g.get_user("FreeCAD").get_repo("FreeCAD")
    repo.name
    prs=repo.get_pulls("open")
    ids_prs = []
    for pr in prs:
        # print(pr.number)
        ids_prs.append(pr.number)

    print(len(ids_prs))
    return ids_prs


# ************************************************************************************************
def create_local_branch_foreach_pr(repopath, ids_prs):

    # the main FreeCAD repo must been set up
    # as remote "freecad"
    
    # TODO: even better error handling
    if repopath is None:
        print("No repopath given, nothing done.")
        return
    if ids_prs is None:
        print("No pr-ids given, nothing done.")
        return

    from git import Repo
    repo = Repo(repopath)
    branch_names = sorted([h.name for h in repo.heads], reverse=True)

    # delete all branches starting with "PR_"
    for br in repo.heads:
        if br.name.startswith("PR_"):
            repo.git.branch("-D", br.name)

    # checkout a branch for each PR
    for pr_no in ids_prs:
        print(pr_no)
        fetch_string = "pull/{}/head:PR_{}".format(pr_no, pr_no)
        try:
            repo.git.fetch("freecad", fetch_string)
        except:
            print("Failed: {}".format(pr_no))

    return True


# ************************************************************************************************
def push_to_local_repo(repopath):
    # git push -f origin --all
    
    # TODO: even better error handling
    if repopath is None:
        print("No repopath given, nothing done.")
        return

    from git import Repo
    repo = Repo(repopath)
    repo.git.push("-f", "origin", "--all")


# ************************************************************************************************
def get_gitlab_prs_pipelinedata(token, projectname_on_gitlab):

    from gitlab import Gitlab
    gl = Gitlab("https://gitlab.com/", private_token="")
    project = gl.projects.get(projectname_on_gitlab)
    project.name

    pipelines = project.pipelines.list(all=True)
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
base_comment_pr_pipeline = """<a href="https://gitlab.com/berndhahnebach/FreeCAD/-/commits/branchname"><img alt="pipeline status" src="https://gitlab.com/berndhahnebach/FreeCAD/badges/branchname/pipeline.svg" /></a> for feature branch [branchname](https://gitlab.com/berndhahnebach/FreeCAD/-/commits/branchname). Pipeline [#pipelineid ](https://gitlab.com/berndhahnebach/FreeCAD/-/pipelines/pipelineid) was triggered at [shortidcommit](https://github.com/FreeCAD/FreeCAD/pull/pullid/commits/commitid). All CI branch [pipelines](https://gitlab.com/berndhahnebach/FreeCAD/-/pipelines?scope=branches)."""


def generate_comment_foreach_pr_pipeline(token, prs_pipelinedata):

    from github import Github
    g = Github(token)
    repo = g.get_user("FreeCAD").get_repo("FreeCAD")
    repo.name

    prs_open = repo.get_pulls("open")
    comments_all = []
    comments_new = {}
    for pr in prs_open:
        # print(pr.number)
        if pr.number in prs_pipelinedata:
            branchname = prs_pipelinedata[pr.number][0]
            pipelineid = str(prs_pipelinedata[pr.number][1])
            # statusvalue = prs_pipelinedata[pr.number][2]
            commitid = prs_pipelinedata[pr.number][3]
            pullid = str(pr.number)
            shortidcommit = prs_pipelinedata[pr.number][3][0:7]  # commitid should not in here

            the_comment = base_comment_pr_pipeline.replace("branchname", branchname)
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
def create_on_github_comment_foreach_pr_pipeline(token, comments_new):

    from github import Github
    g = Github(token)
    repo = g.get_user("FreeCAD").get_repo("FreeCAD")
    repo.name

    prs_open = repo.get_pulls("open")
    for pr in prs_open:
        if pr.number in comments_new:
            the_comment = comments_new[pr.number]
            pr.create_issue_comment(body=the_comment)


# ************************************************************************************************
def get_github_prs_do_not_contain_text_in_all_comments(token, search_text):

    from github import Github
    g = Github(token)
    repogh = g.get_user("FreeCAD").get_repo("FreeCAD")
    repogh.name
    prs_open = repogh.get_pulls("open")

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
def get_gitlab_branches_without_pipline(token, projectname_on_gitlab):

    from gitlab import Gitlab
    gl = Gitlab("https://gitlab.com/", private_token=token)
    project = gl.projects.get(projectname_on_gitlab)
    project.name

    pipelines = project.pipelines.list(all=True)
    # len(pipelines)
    pipeline_branches = []
    for pl in pipelines:
        if not pl.ref.startswith("PR_"):
            continue
        pipeline_branches.append(pl.ref)

    pipeline_branches = sorted(list(set(pipeline_branches)))
    # len(pipeline_branches)

    branches = project.branches.list(all=True)
    branch_names = []
    for br in branches:
        if not br.name.startswith("PR_"):
            continue
        branch_names.append(br.name)

    branch_names = sorted(branch_names)
    # len(branch_names)

    brs_no_pipeline = []
    for brn in branch_names:
        if brn not in pipeline_branches:
            brs_no_pipeline.append(brn)

    return brs_no_pipeline


# ************************************************************************************************
def get_github_head_for_pr_branches(token, pr_branches):

    from github import Github
    g = Github(token)
    repo = g.get_user("FreeCAD").get_repo("FreeCAD")
    repo.name
    prs_open = repo.get_pulls("open")

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
def has_local_prbranch_a_specific_commit(repopath, prs_base,the_commit):
    
    # the unit test commit
    # https://gitpython.readthedocs.io/en/stable/tutorial.html#the-commit-object
    # unit test commit 70c5505a75ad545cb671eb73f29d5e1626aebf78

    from git import Repo
    repo = Repo(repopath)
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
def print_prlinks_according_user_and_pr(token, prslist):

    from github import Github
    g = Github(token)
    repo = g.get_user("FreeCAD").get_repo("FreeCAD")
    repo.name
    prs_open = repo.get_pulls("open")

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
