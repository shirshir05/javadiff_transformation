import os
from dataclasses import dataclass, asdict
from typing import List
from collections import Counter

import jsons

# types from src/org/refactoringminer/api/RefactoringType.java
REFACTORING_TYPES = {'Extract Method', 'Rename Class', 'Move Attribute', 'Move And Rename Attribute',
                     'Replace Attribute', 'Rename Method', 'Inline Method', 'Move Method', 'Move And Rename Method',
                     'Pull Up Method', 'Move Class', 'Move And Rename Class', 'Move Source Folder', 'Pull Up Attribute',
                     'Push Down Attribute', 'Push Down Method', 'Extract Interface', 'Extract Superclass',
                     'Extract Subclass', 'Extract Class', 'Merge Method', 'Extract And Move Method',
                     'Move And Inline Method', 'Convert Anonymous Class to Type', 'Introduce Polymorphism',
                     'Rename Package', 'Move Package', 'Extract Variable', 'Extract Attribute', 'Inline Variable',
                     'Rename Variable', 'Rename Parameter', 'Rename Attribute', 'Merge Variable', 'Merge Parameter',
                     'Merge Attribute', 'Split Variable', 'Split Parameter', 'Split Attribute',
                     'Replace Variable With Attribute', 'Replace Attribute With Variable', 'Parameterize Variable',
                     'Localize Parameter', 'Parameterize Attribute', 'Change Return Type', 'Change Variable Type',
                     'Change Parameter Type', 'Change Attribute Type', 'Add Method Annotation',
                     'Remove Method Annotation', 'Modify Method Annotation', 'Add Attribute Annotation',
                     'Remove Attribute Annotation', 'Modify Attribute Annotation', 'Add Class Annotation',
                     'Remove Class Annotation', 'Modify Class Annotation', 'Add Parameter Annotation',
                     'Remove Parameter Annotation', 'Modify Parameter Annotation', 'Add Parameter', 'Remove Parameter',
                     'Reorder Parameter', 'Add Variable Annotation', 'Remove Variable Annotation',
                     'Modify Variable Annotation', 'Add Thrown Exception Type', 'Remove Thrown Exception Type',
                     'Change Thrown Exception Type', 'Change Method Access Modifier',
                     'Change Attribute Access Modifier', 'Encapsulate Attribute', 'Add Method Modifier',
                     'Remove Method Modifier', 'Add Attribute Modifier', 'Remove Attribute Modifier',
                     'Add Variable Modifier', 'Add Parameter Modifier', 'Remove Variable Modifier',
                     'Remove Parameter Modifier', 'Change Class Access Modifier', 'Add Class Modifier',
                     'Remove Class Modifier', 'Split Package', 'Merge Package', 'Change Type Declaration Kind',
                     'Collapse Hierarchy', 'Replace Loop With Pipeline', 'Replace Anonymous With Lambda'}


@dataclass
class RefactoringMinerLocation:
    filePath: str
    startLine: int = 0
    endLine: int = 0
    startColumn: int = 0
    endColumn: int = 0
    codeElementType: str = ''
    description: str = ''
    codeElement: str = ''
    repository: str = ''
    sha1: str = ''
    refactor_ind: int = 0
    side: str = ''

    def set(self, repo, sha1, refactor_ind, side):
        self.filePath = os.path.normpath(self.filePath)
        self.startLine = self.startLine - 1 # start from 0
        self.endLine = self.endLine - 1
        self.repository = repo
        self.sha1 = sha1
        self.refactor_ind = refactor_ind
        self.side = side

    def get(self, **kargs):
        d = asdict(self)
        d.update(kargs)
        return d


@dataclass
class RefactoringMinerRefactor:
    refactor_type: str
    description: str
    leftSideLocations: List[RefactoringMinerLocation]
    rightSideLocations: List[RefactoringMinerLocation]
    repository: str = ''
    sha1: str = ''

    def set(self, repo, sha1):
        self.repository = repo
        self.sha1 = sha1
        for ind, l in enumerate(self.leftSideLocations):
            l.set(repo, sha1, ind, 'left')
        for ind, r in enumerate(self.rightSideLocations):
            r.set(repo, sha1, ind, 'right')

    def get(self):
        return list(map(lambda x: x.get(refactor_type=self.refactor_type, refactor_description=self.description), self.leftSideLocations + self.rightSideLocations)) #{'refactor_type': self.refactor_type, 'description': self.description, 'repository': self.repository, 'sha1': self.sha1}


@dataclass
class RefactoringMinerCommit:
    repository: str
    sha1: str
    url: str
    refactorings: List[RefactoringMinerRefactor]

    def set(self):
        for r in self.refactorings:
            r.set(self.repository, self.sha1)

    def get(self):
        ans = []
        for r in self.refactorings:
            ans.extend(r.get())
        return ans


@dataclass
class RefactoringMinerOutput:
    commits: List[RefactoringMinerCommit]

    def set(self):
        for c in self.commits:
            c.set()

    def get(self):
        ans = []
        for r in self.commits:
            ans.extend(r.get())
        return ans


def get_types_count(refactorings):
    d = dict.fromkeys(REFACTORING_TYPES, 0)
    d.update(Counter(list(map(lambda r: r.refactor_type, refactorings))))
    return d


def refactoring_miner_loader(file_path):
    with open(file_path) as f:
        ans = jsons.loads(f.read(), cls=RefactoringMinerOutput)
        ans.set()
        return get_types_count(ans.commits[0].refactorings)


if __name__ == "__main__":
    refactorings = refactoring_miner_loader(r"C:\temp\rm_ca2.json")
    pass
