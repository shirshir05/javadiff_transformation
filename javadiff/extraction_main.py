from .extraction import LineExtraction, MethodExtraction, FileExtraction, FileDiffExtraction, CommitExtraction
import pandas as pd


class Extraction:
    def __init__(self, line_extractors=(), method_extractors=(), file_extractors=(), file_diff_extractors=(), commit_extractors=()):
        self.line_extractions = []
        self.method_extractions = []
        self.file_extractions = []
        self.file_diff_extractions = []
        self.commit_extractions = []
        self.line_extractors = line_extractors
        self.method_extractors = method_extractors
        self.file_extractors = file_extractors
        self.file_diff_extractors = file_diff_extractors
        self.commit_extractors = commit_extractors

    def initialze_from_commit_diff(self, commit_diffs):
        for cd in commit_diffs:
            ce = CommitExtraction(cd, self.commit_extractors)
            for fd in cd.diffs:
                fde = FileDiffExtraction(fd, self.file_diff_extractions)
                for source_type, source_file in [('before', fd.before_file), ('after', fd.after_file)]:
                    fe = FileExtraction(source_file, self.file_extractors)
                    for method in source_file.methods.values():
                        me = MethodExtraction(method, self.method_extractors)
                        for line in method.source_lines:
                            le = LineExtraction(line, self.line_extractors)
                            me.add(le)
                            self.line_extractions.append(le)
                        fe.add(me)
                        self.method_extractions.append(me)
                    fde.add_source(source_type, fe)
                    self.file_extractions.append(fe)
                ce.add(fde)
                self.file_diff_extractions.append(fde)
            self.commit_extractions.append(ce)

    def extract(self):
        for extractions in [self.line_extractions, self.method_extractions, self.file_extractions, self.file_diff_extractions, self.commit_extractions]:
            for x in extractions:
                x.extract()

    def export(self):
        for out_file, extractions in [('lines.csv', self.line_extractions), ('methods.csv', self.method_extractions), ('files.csv', self.file_extractions),
                            ('file_diffs.csv', self.file_diff_extractions), ('commits.csv', self.commit_extractions)]:
            pd.DataFrame(list(map(lambda x: x.export(), extractions))).to_csv(out_file, index=False)
