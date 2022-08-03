import difflib
import javalang
import operator
import sys
import jira
import git
import json
import gc
from itertools import imap
import StringIO
from javadiff.diff import get_methods_descriptions



def commits_and_issues(gitPath, issues):
    def get_bug_num_from_comit_text(commit_text, issues_ids):
        s = commit_text.lower().replace(":", "").replace("#", "").replace("-", " ").replace("_", " ").split()
        for word in s:
            if word.replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}',
                                                                                                                 '').isdigit():
                if word in issues_ids:
                    return word
        return "0"

    commits = []
    issues_per_commits = dict()
    repo = git.Repo(gitPath)
    for git_commit in repo.iter_commits():
        commit_text = clean_commit_message(git_commit.message)
        issue_id = get_bug_num_from_comit_text(commit_text, issues.keys())
        if issue_id != "0":
            methods = get_changed_methods(gitPath, git_commit)
            if methods:
                issues_per_commits.setdefault(issue_id, (issues[issue_id], []))[1].extend(methods)
    return issues_per_commits


def get_bugs_data(gitPath, jira_project_name, jira_url, json_out, number_of_bugs=100):
    issues = get_jira_issues(jira_project_name, jira_url)
    issues = dict(map(lambda issue: (issue, issues[issue][1]), filter(lambda issue: issues[issue][0] == 'bug', issues)))
    with open(json_out, "wb") as f:
        json.dump(commits_and_issues(gitPath, issues), f)


if __name__ == "__main__":
    args = sys.argv
    get_changed_methods(r"C:\Temp\commons-lang",
                        git.Repo(r"C:\Temp\commons-lang").commit("a40b2a907a69e51675d7d0502b2608833c4da343"))
    assert len(args) == 6, "USAGE: diff.py git_path jira_project_name jira_url json_method_file json_bugs_file"
    get_bugs_data(args[1], args[2], args[3], args[5])
    get_methods_descriptions(args[1], args[4])
