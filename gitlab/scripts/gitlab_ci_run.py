# imports
import gitlab_ci_tools as glci
import importlib

# repo data
from personal_data import github_token
from personal_data import gitlab_token
from personal_data import local_freecadci_repopath
from personal_data import gitlab_freecadci_project as gitlab_freecadci_prj
from personal_data import github_user
from personal_data import github_prjname
github_repo = glci.get_github_repo(github_token, github_user, github_prjname)
gitlab_project = glci.get_gitlab_project(gitlab_token, gitlab_freecadci_prj)
local_ci_repo = glci.get_local_ci_repo(local_freecadci_repopath)


# reloads after imports because of pep8
importlib.reload(glci)


# ************************************************************************************************
# the CI tools
# ************************************************************************************************


# ************************************************************************************************
# get open PR numberns
ids_prs = glci.get_github_open_pr_numbers(
    github_repo
)
# delete all local PR branches, create a local branch for each PR
status = glci.create_local_branch_foreach_pr(
    local_ci_repo,
    ids_prs
)
# get github pr users data
prs_users_data = glci.get_github_open_pr_users_data(
    github_repo
)
# create a remote if not exists and fetch remote
status = glci.create_local_remote_foreach_pr_user(
    local_ci_repo,
    prs_users_data
)


# push
# if pushed from bash some information it printed about what was updated
# TODO should be possible with gitpython too
# TODO how to push without putting in login or password
# glci.push_from_local_repo_to_gitlab_ci_repo(local_ci_repo)
# git push -f origin --all


# ************************************************************************************************
# get pipelinedata for the prs
# generate comment if a pipline of any updated or added PR has finished
prs_pipelinedata = glci.get_gitlab_prs_pipelinedata(
    gitlab_project,
    gitlab_freecadci_prj
)
comments_all, comments_new = glci.generate_comment_foreach_pr_pipeline(
    github_repo,
    prs_pipelinedata,
    gitlab_freecadci_prj
)
# for c in comments_all:
#     print("\n\n{}".format(c))
# printing the new comments before actually make them
len(comments_new)
for k, v in comments_new.items():
    print("\n# {} {}". format(k, 50*"*"))
    print(v)


# create commit on github, do comment if not in use
# glci.create_on_github_comment_foreach_pr_pipeline(github_repo, comments_new)


# ************************************************************************************************
# more helpers
# ************************************************************************************************


# ************************************************************************************************
# find which PRs does not have a special comment, just search for text ...
pr_notextincomments = glci.get_github_prs_do_not_contain_text_in_all_comments(
    github_repo,
    "The CI-status is available on the latest commit of the branch."
)
pr_notextincomments


# ************************************************************************************************
# get the branches without a pipeline
# check if they have the CI unit test commit
# gitlab get branches without a pipeline
brs_no_pipeline = glci.get_gitlab_branches_without_pipline(
    gitlab_project
)
# github ...
prs_base = glci.get_github_head_for_pr_branches(
    github_repo,
    brs_no_pipeline
)
# local ...
cicommit_notok, cicommit_ok = glci.has_local_prbranch_a_specific_commit(
    local_ci_repo,
    prs_base,
    "70c5505a75ad545cb671eb73f29d5e1626aebf78"
)
cicommit_notok  # no pipeline and not commit --> rebase
len(cicommit_notok)
cicommit_ok  # no pipeline but commit exists --> activate pipeline


"""
# Create a new pipeline for a branch
- CI/CD --> Editor
- choose the branch
- commit changes
- the pipeline is triggered
- make a force push to overwrite the commit
- a new pipeline is triggered
- the one before can be deleted
"""


# nice output of branches to rebase
result = glci.print_prlinks_according_user_and_pr(
    github_repo,
    cicommit_notok
)


# ************************************************************************************************
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

branches_without_open_pr
