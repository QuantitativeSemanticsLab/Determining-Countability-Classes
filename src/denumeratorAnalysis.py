import os
import pandas as pd
from OOPModule import Dependency
from genAllanTest import buildDependenciesDict, depListHasIndex
import json

# returns list of denumerators
def getDenumerator(depDict, index):
    numMod = depDict.get('nummod', [])
    det = depDict.get('det', [])
    amod = depDict.get('amod', [])
    adj = ["most", "many", "few", "several", "some", "enough"]
    dnums = []
    # nummod check 
    for nm in numMod:
        if nm.hasIndex(index):
            dependent = nm.getDependent()
            # advmodCheck = depListHasIndex(depDict.get('advmod', []), dependent.getIndex())
            # detCheck = depListHasIndex(depDict.get('det', []), index)
            # if advmodCheck != None:
            #     dnums.append(advmodCheck.lower() + " " + dependent.getToken().lower())            
            # elif detCheck != None:
            #     dnums.append(detCheck.lower() + " " + dependent.getToken().lower())
            # else:
            #     dnums.append(dependent.getToken().lower())

            #* looking at cases like "200 cats and 2 dogs" and "2 or 3 sheep" Not yet implemented
            compoundCheck = depListHasIndex(depDict.get('compound', []), dependent.getIndex())
            if compoundCheck != None:
                dnums.append(compoundCheck + " " + dependent.getToken().lower())

            conjCheck = depListHasIndex(depDict.get('conj', []), dependent.getIndex())
            if conjCheck != None:
                dnums.append(conjCheck + " " + dependent.getToken().lower())

    # amod check
    # for a in amod:
    #     if a.hasIndex(index):
    #         dependentToken = a.getDependent().getToken().lower()
    #         if dependentToken in adj: dnums.append(dependentToken)
    # determiner check
    # for d in det:
    #     if d.hasIndex(index) and d.getSubType() == "qmod":
    #         dependentToken = d.getDependent().getToken().lower()
    #         dependentInx = d.getDependent().getIndex()
    #         mwe = depDict.get("mwe", [])
    #         for ex in mwe:
    #             if ex.getHead().getIndex() == dependentInx:
    #                 dependentToken += " " + ex.getDependent().getToken().lower()
    #                 dnums.append(dependentToken)
    return dnums   

# returns a dictionary {denumerator: count}
def denumeratorAnalysis(outfileDir):
    files = os.listdir(outfileDir)
    dnum = {}
    for file in files:
        print("...running " + file)
        outfile = pd.read_csv(outfileDir+file)
        for rows in outfile.iterrows():
            row = rows[1]
            fullDeps = Dependency.generateDependencies(row["Dependencies"])
            fullDepsDict = buildDependenciesDict(fullDeps)
            dnumList = getDenumerator(fullDepsDict, row['Index'])
            for d in dnumList:
                if d in dnum: dnum[d] += 1
                else: dnum[d] = 1
        
    return dnum

if __name__ == "__main__":
    oDir = "/Users/aeshaanwahlang/Documents/QuantitativeSemanticsData/test_outfiles/Allan/"

    d = denumeratorAnalysis(oDir)
    # with open('detQmods.json', 'w') as file:
    #     json.dump(d, file, indent=4)
    print(d)