import difflib
import gc
import os
import tempfile
import shutil
import ntpath
from subprocess import run
from collections import Counter

try:
    from .SourceFile import SourceFile
    from .methodData import SourceLine
    from .ast_diff_parser import AstDiff
    from .refactoring_miner_parser import refactoring_miner_loader
    from .utils import get_java_exe_by_version
except:
    from SourceFile import SourceFile
    from methodData import SourceLine
    from ast_diff_parser import AstDiff
    from refactoring_miner_parser import refactoring_miner_loader
    from utils import get_java_exe_by_version


class FileDiff(object):
    REMOVED = '- '
    ADDED = '+ '
    UNCHANGED = '  '
    NOT_IN_INPUT = '? '
    BEFORE_PREFIXES = [REMOVED, UNCHANGED]
    AFTER_PREFIXES = [ADDED, UNCHANGED]

    def __init__(self, diff, commit_sha, first_commit=None, second_commit=None, git_dir=None, analyze_source_lines=True,
                 analyze_diff=True):
        self.file_name = first_commit.split("/")[-1]  # TODO: get name
        # self.commit_sha = commit_sha
        # self.is_ok = self.file_name.endswith(".java")
        # if not self.is_ok:
        #     return
        # before_contents = self.get_before_content_from_diff(diff, first_commit)  # TODO: change read file
        # after_contents = self.get_after_content_from_diff(diff, git_dir, second_commit)  # TODO: change read file
        with open(first_commit) as f:
            before_contents = f.read().splitlines()
        with open(second_commit) as f:
            after_contents = f.read().splitlines()
        self.removed_indices, self.added_indices = self.get_changed_indices(before_contents, after_contents)  # TODO: ok
        self.before_file = SourceFile(before_contents, first_commit.split("/")[-1], self.removed_indices,
                                      analyze_source_lines=analyze_source_lines, delete_source=not analyze_diff, analyze_diff=analyze_diff)
        self.after_file = SourceFile(after_contents, first_commit.split("/")[-1], self.added_indices,
                                     analyze_source_lines=analyze_source_lines, delete_source=not analyze_diff, analyze_diff=analyze_diff)
        self.modified_names = self.after_file.modified_names
        self.ast_metrics = {}
        self.halstead = {}
        self.refactorings = {}
        self.osa_metrics = {}
        self.decls = SourceLine.get_decles_empty_dict()
        if analyze_source_lines:
            for k in self.decls:
                self.decls[k] = self.after_file.decls[k] - self.before_file.decls[k]
            for k in self.after_file.halstead:
                self.halstead[k] = self.after_file.halstead[k] - self.before_file.halstead[k]
        if analyze_diff:
            ast_diff_json, rf_json = None, None
            try:
                f, ast_diff_json = tempfile.mkstemp()
                os.close(f)
                # run([get_java_exe_by_version(11), '-cp', os.path.abspath(os.path.join(os.path.dirname(__file__), r'..\externals\gumtree-spoon-ast-diff-SNAPSHOT-jar-with-dependencies.jar')), 'gumtree.spoon.AstComparator', self.before_file.path_to_source,
                # self.after_file.path_to_source, ast_diff_json])

                run([r'C:\Program Files\Java\jdk-11.0.11\bin\java.exe', '-cp', os.path.abspath(
                    os.path.join(os.path.dirname(__file__),
                                 r'..\externals\gumtree-spoon-ast-diff-SNAPSHOT-jar-with-dependencies.jar')),
                     'gumtree.spoon.AstComparator', self.before_file.path_to_source,
                     self.after_file.path_to_source, ast_diff_json])

                f, rf_json = tempfile.mkstemp()
                os.close(f)
                for k, v in AstDiff.load(ast_diff_json).items():
                    if k != 'operations':
                        self.ast_metrics[k] = v

                for k in self.after_file.osa_metrics:
                    self.osa_metrics[k] = self.after_file.osa_metrics[k] - self.before_file.osa_metrics[k]
                run([get_java_exe_by_version(11), '-cp', os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                                      r'..\externals\RefactoringMiner-2.2.0\RefactoringMiner-2.2.0\lib\*')),
                     'org.refactoringminer.RefactoringMiner', '-bd', self.before_file.path_to_dir_source,
                     self.after_file.path_to_dir_source, self.commit_sha, '-json', rf_json])
                self.refactorings = refactoring_miner_loader(rf_json)
            except:
                pass
            finally:
                if ast_diff_json:
                    os.remove(ast_diff_json)
                if rf_json:
                    os.remove(rf_json)
                self.before_file.remove_source()
                self.after_file.remove_source()

    def get_after_content_from_diff(self, diff, git_dir, second_commit):
        after_contents = [b'']
        if diff.deleted_file:
            assert diff.b_blob is None
            after_contents = []
        else:
            try:
                after_contents = diff.b_blob.data_stream.stream.readlines()
            except:
                if second_commit:
                    try:
                        after_contents = second_commit.repo.git.show(
                            "{0}:{1}".format(second_commit.hexsha, diff.b_path)).split('\n')
                    except:
                        gc.collect()
                elif git_dir:
                    path = os.path.join(git_dir, diff.b_path)
                    with open(path) as f:
                        after_contents = f.readlines()
                gc.collect()
        return list(map(lambda x: x.decode("utf-8", errors='ignore'), after_contents))

    def get_before_content_from_diff(self, diff, first_commit):
        before_contents = [b'']
        if diff.new_file:
            assert diff.a_blob is None
            before_contents = []
        else:
            try:
                before_contents = diff.a_blob.data_stream.stream.readlines()
            except:
                gc.collect()
                if first_commit:
                    try:
                        before_contents = first_commit.repo.git.show(
                            "{0}:{1}".format(first_commit.hexsha, diff.a_path)).split('\n')
                    except:
                        gc.collect()
        return list(map(lambda x: x.decode("utf-8", errors='ignore'), before_contents))

    def is_java_file(self):
        return self.is_ok

    @staticmethod
    def get_changed_indices(before_contents, after_contents):
        def get_lines_by_prefixes(lines, prefixes):
            return list(filter(lambda x: any(map(lambda p: x.startswith(p), prefixes)), lines))

        def get_indices_by_prefix(lines, prefix):
            return list(map(lambda x: x[0], filter(lambda x: x[1].startswith(prefix), enumerate(lines))))

        def comment(line, char_remove):
            line = line.replace(char_remove, "")
            return (line.strip().startswith('//') or line.strip().startswith('*') or line.strip().startswith(
                '/*') or line.strip().startswith('*/') or line.strip() == "")

        diff = list(difflib.ndiff(before_contents, after_contents,  # ))
                                  # ,linejunk=lambda l: difflib.IS_LINE_JUNK(l) or l.strip().startswith('//') or l.strip().startswith('*') or l.strip().startswith('/*') or l.strip().startswith('*/'),
                                  charjunk=lambda c: difflib.IS_CHARACTER_JUNK(c) or c.isspace()))

        before_ind = -1
        after_ind = -1
        removed_indices_ = []
        added_indices_ = []
        for line in diff:
            if line.startswith(FileDiff.UNCHANGED):
                before_ind += 1
                after_ind += 1
            elif line.startswith(FileDiff.REMOVED):
                before_ind += 1
                if not comment(line, FileDiff.REMOVED):
                    removed_indices_.append(before_ind)
            elif line.startswith(FileDiff.ADDED):
                after_ind += 1
                if not comment(line, FileDiff.ADDED):
                    added_indices_.append(after_ind)

        # diff_before_lines = get_lines_by_prefixes(diff, FileDiff.BEFORE_PREFIXES)
        # # assert list(map(lambda x: x[2:], diff_before_lines)) == before_contents
        # removed_indices = get_indices_by_prefix(diff_before_lines, FileDiff.REMOVED)
        #
        # diff_after_lines = get_lines_by_prefixes(diff, FileDiff.AFTER_PREFIXES)
        # # assert list(map(lambda x: x[2:], diff_after_lines)) == after_contents
        # added_indices = get_indices_by_prefix(diff_after_lines, FileDiff.ADDED)

        return removed_indices_, added_indices_

    def get_changed_methods(self):
        return self.after_file.get_changed_methods() + self.before_file.get_changed_methods()

    def get_methods(self):
        return list(self.before_file.methods.values()) + list(self.after_file.methods.values())

    def get_methods_dict(self):
        before = list(self.before_file.methods.values())
        after = list(self.after_file.methods.values())
        before_changed = list(filter(lambda x: x.changed, before))
        before_unchanged = list(filter(lambda x: not x.changed, before))
        after_changed = list(filter(lambda x: x.changed, after))
        after_unchanged = list(filter(lambda x: not x.changed, after))
        return {'before_changed': before_changed, 'before_unchanged': before_unchanged,
                'after_changed': after_changed, 'after_unchanged': after_unchanged}

    def get_changed_exists_methods(self):
        return list(filter(lambda m: m.id in self.before_file.methods, self.after_file.get_changed_methods())) + \
               list(filter(lambda m: m.id in self.after_file.methods, self.before_file.get_changed_methods()))

    def __repr__(self):
        return self.file_name

    def get_metrics(self, commit=None):
        ans = {'commit': commit, 'file_name': self.file_name}
        # if not self.is_ok:
        #     return None
        before = self.before_file.get_file_metrics()
        after = self.after_file.get_file_metrics()
        for prefix, d in (('parent_', before), ('current_', after)):
            for k in d:
                ans[prefix + k] = d[k]
        # deltas
        for k in self.decls:
            ans['delta_' + k] = self.decls[k]
        for k in self.halstead:
            ans['delta_' + k] = self.halstead[k]
        for k in self.ast_metrics:
            ans['ast_diff_' + k] = self.ast_metrics[k]
        for k in self.osa_metrics:
            ans['delta_' + k] = self.osa_metrics[k]
        for k in self.refactorings:
            ans['refactorings_' + k] = self.refactorings[k]
        # churn
        ans['added_lines+removed_lines'] = after['changed_lines'] + before['changed_lines']
        ans['added_lines-removed_lines'] = after['changed_lines'] - before['changed_lines']
        ans['used_added_lines+used_removed_lines'] = after['changed_used_lines'] + before['changed_used_lines']
        ans['used_added_lines-used_removed_lines'] = after['changed_used_lines'] - before['changed_used_lines']
        return ans


class FormatPatchFileDiff(FileDiff):
    def get_after_content_from_diff(self, diff, git_dir, second_commit):
        return diff.after_contents

    def get_before_content_from_diff(self, diff, first_commit):
        return diff.before_contents
