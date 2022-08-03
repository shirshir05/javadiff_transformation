from dataclasses import dataclass, asdict
from typing import List
import jsons

@dataclass
class Operation:
    toString: str
    action: str
    before_file: str
    before_line: str
    after_file: str
    after_line: str
    SimpleNodeType: str
    nodeType: str
    nodeLabel: str
    OperationKind: str
    size: str


@dataclass
class AstDiff:
    operations: List[Operation]
    condBlockOthersAdd: int = 0
    condBlockRetAdd: int = 0
    condBlockExcAdd: int = 0
    condBlockRem: int = 0
    expLogicExpand: int = 0
    expLogicReduce: int = 0
    expLogicMod: int = 0
    expArithMod: int = 0
    wrapsIf: int = 0
    wrapsIfElse: int = 0
    wrapsElse: int = 0
    wrapsTryCatch: int = 0
    wrapsMethod: int = 0
    wrapsLoop: int = 0
    unwrapIfElse: int = 0
    unwrapMethod: int = 0
    unwrapTryCatch: int = 0
    wrongVarRef: int = 0
    wrongMethodRef: int = 0
    missNullCheckP: int = 0
    missNullCheckN: int = 0
    singleLine: int = 0
    copyPaste: int = 0
    constChange: int = 0
    codeMove: int = 0
    notClassified: int = 0
    binOperatorModif: int = 0
    addassignment: int = 0
    assignAdd: int = 0
    assignRem: int = 0
    assignExpChange: int = 0
    condBranIfAdd: int = 0
    condBranIfElseAdd: int = 0
    condBranElseAdd: int = 0
    condBranCaseAdd: int = 0
    condBranRem: int = 0
    condExpExpand: int = 0
    condExpRed: int = 0
    condExpMod: int = 0
    loopAdd: int = 0
    loopRem: int = 0
    loopCondChange: int = 0
    loopInitChange: int = 0
    mcAdd: int = 0
    mcRem: int = 0
    mcRepl: int = 0
    mcMove: int = 0
    mcParAdd: int = 0
    mcParRem: int = 0
    mcParSwap: int = 0
    mcParValChange: int = 0
    mdAdd: int = 0
    mdRem: int = 0
    mdRen: int = 0
    mdParAdd: int = 0
    mdParRem: int = 0
    mdParTyChange: int = 0
    mdRetTyChange: int = 0
    mdModChange: int = 0
    mdOverride: int = 0
    objInstAdd: int = 0
    objInstRem: int = 0
    objInstMod: int = 0
    exTryCatchAdd: int = 0
    exTryCatchRem: int = 0
    exThrowsAdd: int = 0
    exThrowsRem: int = 0
    retBranchAdd: int = 0
    retRem: int = 0
    retExpChange: int = 0
    varAdd: int = 0
    varRem: int = 0
    varTyChange: int = 0
    varModChange: int = 0
    varReplVar: int = 0
    varReplMc: int = 0
    tyAdd: int = 0
    tyImpInterf: int = 0

    @staticmethod
    def load(json_file):
        with open(json_file) as f:
            ans = jsons.loads(f.read(), cls=AstDiff)
            return asdict(ans)

