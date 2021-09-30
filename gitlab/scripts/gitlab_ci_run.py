# personal data
from personal_data import github_token
from personal_data import gitlab_token
from personal_data import local_freecadci_repopath
from personal_data import gitlab_freecadci_project


# imports
import gitlab_ci_tools as glci
import importlib
importlib.reload(glci)


# ************************************************************************************************
# the CI tools
# ************************************************************************************************
# get open PRs and create a local branch for each PR, delete all local PR branches before
ids_prs = glci.get_github_open_pr_numbers(
    github_token
)
status = glci.create_local_branch_foreach_pr(
    local_freecadci_repopath,
    ids_prs
)
# get github pr users data, create a remote if not exists and fetch remote
prs_users_data = glci.get_github_open_pr_users_data(
    github_token
)    
status = glci.create_local_remote_foreach_pr_user(
    local_freecadci_repopath,
    prs_users_data
)


# push
# if pushed from bash some information it printed about what was updated
# TODO should be possible with gitpython too
# TODO how to push without putting in login or password
# glci.push_to_local_repo(local_freecadci_repopath)
# git push -f origin --all


# ************************************************************************************************
# get pipelinedata for the prs
# generate comment if a pipline of any updated or added PR has finished
prs_pipelinedata = glci.get_gitlab_prs_pipelinedata(
    gitlab_token,
    gitlab_freecadci_project
)
comments_all, comments_new = glci.generate_comment_foreach_pr_pipeline(
    github_token,
    prs_pipelinedata
)
#for c in comments_all:
#    print("\n\n{}".format(c))
# printing the new comments before actually make them
len(comments_new)
for k, v in comments_new.items():
    print("\n# {} {}". format(k, 50*"*"))
    print(v)


# create commit on github, do comment if not in use
# glci.create_on_github_comment_foreach_pr_pipeline(github_token, comments_new)


# ************************************************************************************************
# more helpers
# ************************************************************************************************
# find which PRs does not have a special comment, just search for text ...
pr_notextincomments = glci.get_github_prs_do_not_contain_text_in_all_comments(
    github_token,
    "The CI-status is available on the latest commit of the branch."
)
pr_notextincomments


# ************************************************************************************************
# get the branches without pipeline and check if the have the CI unit test commit
# gitlab get branches without a pipeline
brs_no_pipeline = glci.get_gitlab_branches_without_pipline(
    gitlab_token,
    gitlab_freecadci_project    
)
# github ...
prs_base = glci.get_github_head_for_pr_branches(
    github_token,
    brs_no_pipeline
)
# local ...
cicommit_notok, cicommit_ok = glci.has_local_prbranch_a_specific_commit(
    local_freecadci_repopath,
    prs_base,
    "70c5505a75ad545cb671eb73f29d5e1626aebf78"
)
cicommit_notok  # no pipeline and not commit --> rebase
len(cicommit_notok)
cicommit_ok  # no pipeline but commit exists --> activate pipeline


# TODO do no use curl or https but gitlab python to activate a pipeline
"""
https://gitlab.com/api/v4/projects/29769711/ref/REF_NAME/trigger/pipeline?token=TOKEN
https://gitlab.com/api/v4/projects/29769711/ref/PR_5050/trigger/pipeline?token=the_gitlab_token

# oder

curl -X POST \
     -F token=the_gitlab_token \
     -F ref=PR_4975 \
     https://gitlab.com/api/v4/projects/29769711/trigger/pipeline

"""


# nice output of branches to rebase
result = glci.print_prlinks_according_user_and_pr(
    github_token,
    cicommit_notok
)


# ************************************************************************************************
