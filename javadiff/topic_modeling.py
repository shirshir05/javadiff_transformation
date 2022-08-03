from diff import get_java_commits, get_changed_methods, get_changed_methods_from_file_diffs
import sys
import os
import shutil
import git
import gc
import jira
import json
from projects import projects
from tempfile import mkdtemp
try:
    from .CommitsDiff import FormatPatchCommitsDiff
except:
    from CommitsDiff import FormatPatchCommitsDiff
try:
    import StringIO
except:
    from io import StringIO



def clean_commit_message(commit_message):
    if "git-svn-id" in commit_message:
        return commit_message.split("git-svn-id")[0]
    return commit_message


class Commit(object):
    def __init__(self, bug_id, git_commit):
        self._commit_id = git_commit.hexsha
        self._bug_id = bug_id
        # self._files = Commit.fix_renamed_files(git_commit.stats.files.keys())
        # self._commit_date = time.mktime(git_commit.committed_datetime.timetuple())

    def is_bug(self):
        return self._bug_id != '0'

    @classmethod
    def init_commit_by_git_commit(cls, git_commit, bug_id):
        return Commit(bug_id, git_commit)

    def to_list(self):
        return {self._commit_id: str(self._bug_id)}

    @staticmethod
    def fix_renamed_files(files):
        """
        fix the paths of renamed files.
        before : u'tika-core/src/test/resources/{org/apache/tika/fork => test-documents}/embedded_with_npe.xml'
        after:
        u'tika-core/src/test/resources/org/apache/tika/fork/embedded_with_npe.xml'
        u'tika-core/src/test/resources/test-documents/embedded_with_npe.xml'
        :param files: self._files
        :return: list of modified files in commit
        """
        new_files = []
        for file in files:
            if "=>" in file:
                if "{" and "}" in file:
                    # file moved
                    src, dst = file.split("{")[1].split("}")[0].split("=>")
                    fix = lambda repl: re.sub(r"{[\.a-zA-Z_/\-0-9]* => [\.a-zA-Z_/\-0-9]*}", repl.strip(), file)
                    new_files.extend(map(fix, [src, dst]))
                else:
                    # full path changed
                    new_files.extend(map(lambda x: x.strip(), file.split("=>")))
                    pass
            else:
                new_files.append(file)
        return new_files


def commits_and_issues(git_path, issues):
    def replace(chars_to_replace, replacement, s):
        temp_s = s
        for c in chars_to_replace:
            temp_s = temp_s.replace(c, replacement)
        return temp_s

    def get_bug_num_from_comit_text(commit_text, issues_ids):
        text = replace("[]?#,:(){}", "", commit_text.lower())
        text = replace("-_", " ", text)
        for word in text.split():
            if word.isdigit():
                if word in issues_ids:
                    return word
        return "0"

    commits = []
    issues_ids = map(lambda issue: issue, issues)
    for git_commit in git.Repo(git_path).iter_commits():
        commits.append(
            Commit.init_commit_by_git_commit(git_commit, get_bug_num_from_comit_text(clean_commit_message(git_commit.summary), issues_ids)).to_list())
    return commits


def get_jira_issues(project_name, url, bunch=100):
    jira_conn = jira.JIRA(url)
    all_issues = []
    extracted_issues = 0
    while True:
        issues = jira_conn.search_issues("project={0}".format(project_name), maxResults=bunch, startAt=extracted_issues)
        all_issues.extend(filter(lambda issue: issue.fields.description, issues))
        extracted_issues = extracted_issues + bunch
        if len(issues) < bunch:
            break
    return dict(map(lambda issue: (issue.key.strip().split("-")[1].lower(), (
    issue.fields.issuetype.name.lower(), issue.fields.description.encode('utf-8').lower())), all_issues))


def topic_modeling_data(project_ind):
    git_link, jira_link = projects[sorted(projects.keys())[int(project_ind)]]
    jira_project_name = os.path.basename(jira_link)
    git_path = os.path.abspath(r"repo")
    out_dir = os.path.abspath(r"out_dir")
    os.system("git clone {0} repo".format(git_link))
    os.mkdir(out_dir)
    os.mkdir(os.path.join(out_dir, jira_project_name))
    path_to_format_patch = mkdtemp()
    repo = git.Repo(git_path)
    commits_diffs = dict()
    # repo_files = list(filter(lambda x: x.endswith(".java") and not x.lower().endswith("test.java"),
    #                     repo.git.ls_files().split()))
    #
    # for commit in list(repo.iter_commits())[:30]:
        # if any(filter(lambda f: f in files, repo_files)):
        #     commits.append(commit)
    methods_descriptions = {}
    methods_per_commit = {}
    for f in repo.git.format_patch("--root", "-o", path_to_format_patch, "--function-context", "--unified=900000", "--no-renames", "--full-index", "--patch", "-k", "--numbered-files", "--no-stat", "-N").split():
        gc.collect()
        cd = FormatPatchCommitsDiff(os.path.normpath(os.path.join(path_to_format_patch, f)), analyze_source_lines=False)
        if not cd.commit:
            continue
        methods = get_changed_methods_from_file_diffs(cd.diffs)
        if methods:
            map(lambda method: methods_descriptions.setdefault(method, StringIO.StringIO()).write(
                repo.commit(cd.commit).message), methods)
            methods_per_commit[cd.commit] = list(map(repr, methods))
    with open(os.path.join(out_dir, jira_project_name, "methods_descriptions.json"), "wb") as f:
        data = dict(map(lambda x: (x[0].method_name_parameters, x[1].getvalue()), methods_descriptions.items()))
        json.dump(data, f)
    with open(os.path.join(out_dir, jira_project_name, "methods_per_commit.json"), "wb") as f:
        json.dump(methods_per_commit, f)

    issues = get_jira_issues(jira_project_name, r"http://issues.apache.org/jira")
    issues = dict(map(lambda issue: (issue, issues[issue][1]), filter(lambda issue: issues[issue][0] == 'bug', issues)))
    with open(os.path.join(out_dir, jira_project_name, "bugs_data.json"), "wb") as f:
        json.dump(commits_and_issues(git_path, issues), f)

    shutil.rmtree(path_to_format_patch)
    shutil.make_archive(project_ind, 'zip', out_dir)


if __name__ == "__main__":
    topic_modeling_data(sys.argv[1])
