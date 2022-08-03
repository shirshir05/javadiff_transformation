try:
    from .diff import get_commit_diff
except:
    from diff import get_commit_diff
import sys
import git
import re
import os
import pandas as pd

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


def get_commits_files(repo):
    if type(repo) == type(''):
        repo = git.Repo(repo)
    data = repo.git.log('--numstat','--pretty=format:"sha: %H"').split("sha: ")
    comms = {}
    for d_ in data[1:]:
        d_ = d_.replace('"', '').replace('\n\n', '\n').split('\n')
        commit_sha = d_[0]
        comms[commit_sha] = []
        for x in d_[1:-1]:
            insertions, deletions, name = x.split('\t')
            names = fix_renamed_files([name])
            comms[commit_sha].extend(list(map(lambda file_name: (commit_sha, file_name, insertions, deletions), names)))
    ans = []
    for c in comms:
        if comms[c]:
            try:
                if any(list(map(lambda f: f[1].endswith('java'), comms[c]))):
                    ans.append(c)
            except Exception as e:
                pass
    return ans #list(map(lambda x: Commit(repo.commit(x), comms[x]), filter(lambda x: comms[x], comms)))


if __name__ == '__main__':
    # Set variables according to the project
    window_size = 50
    ind = int(sys.argv[1])
    commits_start = ind * window_size
    commits_end = commits_start + window_size

    # Commits Handling
    repo_path = r"local_repo"
    all_commits = get_commits_files(repo_path)
    commits = all_commits[commits_start: commits_end]
    if len(commits) == 0:
        exit()

    metrics = []
    for commit in commits:
        print(commit)
        c = get_commit_diff(repo_path, commit, analyze_diff=True)
        if c:
            metrics.extend(c.get_metrics())
    os.mkdir('./results')
    df = pd.DataFrame(metrics)
    print(df.head())
    print(os.path.abspath(f'./results/{ind}.csv'))
    df.to_csv(f'./results/{ind}.csv', index=False)
