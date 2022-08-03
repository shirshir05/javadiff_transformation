import csv

try:
    from javadiff.FileDiff import FileDiff
except:
    from javadiff.javadiff.diff import FileDiff

import sys

from diff import get_commit_diff

if __name__ == "__main__":
    _, nameProject, numberFold, nameTransform, commit_sha, first_commit, second_commit = sys.argv

    m = FileDiff(None, commit_sha, first_commit, second_commit, analyze_source_lines=True,  git_dir=None)
    ans = m.get_metrics()
    with open("C:\\Users\\shir0\\ans_from_java_diff_transformation" + "\\" + nameProject + "\\" + numberFold + "\\" +
              "\\" + nameTransform + '\\all.csv', 'a',newline='') as file:
        writer = csv.writer(file)

        writer.writerow(list(ans.values()))

    # m = get_commit_diff(r"C:\temp\commons-math", c, analyze_diff=True)
    # m.get_metrics()
    #
    # commits_diffs = [m]
    # final = []
    # for cd in commits_diffs:
    #     ce = CommitExtraction(cd, [])
    #     for fd in cd.diffs:
    #         fde = FileDiffExtraction(fd, [])
    #         for source_type, source_file in [('before', fd.before_file), ('after', fd.after_file)]:
    #             fe = FileExtraction(source_file, [])
    #             for method in source_file.methods.values():
    #                 me = MethodExtraction(method, [])
    #                 for line in method.source_lines:
    #                     le = LineExtraction(line, [])
    #                     me.add(le)
    #                 fe.add(me)
    #             fde.add_source(source_type, fe)
    #         ce.add(fde)
    #     final.append(ce)
    #
    # pass

    import glob
    import pandas as pd

    # STATIC = ['PDA', 'LOC', 'CLOC', 'PUA', 'McCC', 'LLOC', 'LDC', 'NOS', 'MISM', 'CCL', 'TNOS', 'TLLOC',
    #           'NLE', 'CI', 'HPL', 'MI', 'HPV', 'CD', 'NOI', 'NUMPAR', 'MISEI', 'CC', 'LLDC', 'NII', 'CCO', 'CLC', 'TCD',
    #           'NL', 'TLOC', 'CLLC', 'TCLOC', 'MIMS', 'HDIF', 'DLOC', 'NLM', 'DIT', 'NPA', 'TNLPM',
    #           'TNLA', 'NLA', 'AD', 'TNLPA', 'NM', 'TNG', 'NLPM', 'TNM', 'NOC', 'NOD', 'NOP', 'NLS', 'NG', 'TNLG',
    #           'CBOI',
    #           'RFC', 'NLG', 'TNLS', 'TNA', 'NLPA', 'NOA', 'WMC', 'NPM', 'TNPM', 'TNS', 'NA', 'LCOM5', 'NS', 'CBO',
    #           'TNLM',
    #           'TNPA']

    # name_project = 'before'
    # directoryPath = "C:/Users/shir0/AppData/Local/Temp/2/results/before/java/2021-07-11-13-59-49/" + name_project
    #
    # x = pd.read_csv(directoryPath+"-Class.csv", low_memory=False)
    # aggregation_functions = {i: 'sum' for i in [i for i in STATIC if i in list(x.columns)]}
    # x_sum = x.agg(aggregation_functions)
    # y = pd.read_csv(directoryPath + "-Method.csv", low_memory=False)
    # aggregation_functions = {i: 'sum' for i in [i for i in STATIC if i not in list(x.columns)]}
    # y_sum = y.agg(aggregation_functions)
    # all = pd. concat([x_sum, y_sum], axis=0)
    # print("s")
