from OOPModule import Dependency
import pandas as pd
import re
import os
import json

# function to generate Allan test for an outfile will add test results as new colunms 
# outfile -> path to Outfile
def genAllanTest(outfile, noun, saveDir):
    outfileDf = pd.read_csv(outfile)
    # drop old colunms 
    old = ['Denumerator', 'Type of Denumerator']
    outfileDf = outfileDf.drop(columns = old)
    # add new ones
    cols = ['A+N', 'F+N', 'all+N', 'O-Den']
    cols2 = ['Denumerator', 'Allan Type', 'SubType', 'Magnitude']
    for c in cols:
        outfileDf[c] = '0'
    outfileDf['Allan Test Result'] = 'unknown'
    for c in cols2:
        outfileDf[c] = ''
    # load required data
    for index in outfileDf.index:
        # if index == 372:
        #     print(outfileDf.at[index, "Sentence"])

        fullDeps = outfileDf.at[index, 'Dependencies']
        relDeps = outfileDf.at[index , 'Relevant Dependencies']
        nounIndex = outfileDf.at[index, 'Index']
        nounPlurality = outfileDf.at[index, 'Plurality of Noun']

        fullDepList = Dependency.generateDependencies(fullDeps)
        relDepsList = Dependency.generateDependencies(relDeps)
        if fullDepList == []: print(fullDeps)
        if relDepsList == []: print(relDeps)
        fullDepsDict = buildDependenciesDict(fullDepList)
        relDepsDict = buildDependenciesDict(relDepsList)

        denumerator = getDenumerator(fullDepsDict, nounIndex)
        if denumerator == None:continue
        allanClass = getAllenDnumClass(denumerator, relDepsDict, nounIndex)
        if allanClass == None: allanClass = ("Not Applicable", "", "")
        
        result = allanTest(allanClass[0], nounPlurality, relDepsDict, nounIndex)
        if denumerator == "all": denumerator = ''
        outfileDf.at[index, 'Denumerator'] = denumerator
        outfileDf.at[index, 'Allan Type'] = allanClass[0]
        outfileDf.at[index, 'SubType'] = allanClass[1]
        outfileDf.at[index, 'Magnitude'] = allanClass[2]
        for i in range(0,4):
            outfileDf.at[index, cols[i]] = result[i]
    
        # Allan test coutability result
        if result[2] == '1' :
            outfileDf.at[index, 'Allan Test Result'] = 'uncountable'
        elif result[0] == '1' or result[1] == '1':
            outfileDf.at[index, 'Allan Test Result'] = 'countable'

    filename = noun+'_AllanTest.csv'
    outfileDf.to_csv(saveDir+filename, index=False)
    # print(filename+" saved")

#function to create a dictonary from a list of dependencies 
def buildDependenciesDict(depList):
    depDict = {}
    for dep in depList:
        dType = dep.getDependencyRelationship()
        if dType in depDict:
            depDict[dType].append(dep)
        else:
            depDict[dType] = [dep]
    return depDict

# function to check if a dependency in a list of dependancies has an index 
def depListHasIndex(depList, index):
    for dep in depList:
        if dep.hasIndex(index):
            return dep.getDependent().getToken()
    return None

#Fill dictionaries 
with open("/Users/aeshaanwahlang/Documents/QuantitativeSemantics/Repo/AbstractNouns/PostProcessing/Countability/dnums_fuzzy.json", "r") as file:
    dnums_fuzzy = json.load(file)

with open("/Users/aeshaanwahlang/Documents/QuantitativeSemantics/Repo/AbstractNouns/PostProcessing/Countability/dnums_other.json", "r") as file:
    dnums_other = json.load(file)

with open("/Users/aeshaanwahlang/Documents/QuantitativeSemantics/Repo/AbstractNouns/PostProcessing/Countability/dnums_numbers.json", "r") as file:
    dnums_numbers = json.load(file)

with open("/Users/aeshaanwahlang/Documents/QuantitativeSemantics/Repo/AbstractNouns/PostProcessing/Countability/non_dnums.json", "r") as file:
    non_dnums = json.load(file)

#? confirm 'the' and 'that' with unit
unit = ['a', 'an', 'one', '1', 'only one', 'i','just one', 'the 1', 'that one', 'this one', 'any one']
# returns list of denumerators
def getDenumerator(depDict, index):
    numMod = depDict.get('nummod', [])
    det = depDict.get('det', [])
    amod = depDict.get('amod', [])
    #? expand this list
    adj = ["most", "many", "few", "several", "some", "enough"]
    # nummod check 
    for nm in numMod:
        if nm.hasIndex(index):
            dependent = nm.getDependent()
            advmodCheck = depListHasIndex(depDict.get('advmod', []), dependent.getIndex())
            if(advmodCheck == None):
                return(dependent.getToken().lower())
            else:
                return(advmodCheck.lower() + " " + dependent.getToken().lower())  

            detCheck = depListHasIndex(depDict.get('det', []), index)
            if(detCheck == None):
                return(dependent.getToken().lower())
            else:
                return(detCheck.lower() + " " + dependent.getToken().lower())  
            #? check for mew with nummod+advmod and nummod + det
            
    # amod check
    for a in amod:
        if a.hasIndex(index):
            dependentToken = a.getDependent().getToken().lower()
            if dependentToken in adj: 
                #few with det check
                if dependentToken == "few":
                    for d in det:
                        if d.hasIndex(index):
                            return (d.getDependent().getToken().lower() + " " + dependentToken)

                return(dependentToken)

    # determiner check
    for d in det:
        if d.hasIndex(index):
            dependentToken = d.getDependent().getToken().lower()
            if d.getSubType() == "qmod":
                dependentInx = d.getDependent().getIndex()
                mwe = depDict.get("mwe", [])
                for ex in mwe:
                    if ex.getHead().getIndex() == dependentInx:
                        dependentToken += " " + ex.getDependent().getToken().lower()
                        
            return(dependentToken)  

# returns Allan denumerator class with subtype and magnitude (class, subtype, magnitude)
def getAllenDnumClass(dnum, relDepsDict, index):
    dnum = dnum.lower()
    #non dnum check:
    if dnum in non_dnums: return('non-Denumerator', non_dnums[dnum]['subtype'], '')
    #unit check
    if dnum in unit:
        #qmod check
        det = relDepsDict.get("det", [])
        for d in det:
            if d.hasIndex(index):
                if d.getSubType() == "qmod": return None

        if 'one' in dnum: return ('unit', 'number', 'small')
        if '1' in dnum: return ('unit', 'digits', 'small')
        if 'a' in dnum or 'an' in dnum: return('unit', 'a/an', 'small')
    
    #fuzzy check
    #check few with determiner
    if "few" in dnum:
        detInstance = dnum.replace(" few", "")
        dets = relDepsDict.get("det", [])
        for d in dets:
            if d.hasWord(detInstance): return('fuzzy', 'imprecise quantifier', 'small')
    if dnum in dnums_fuzzy: return ('fuzzy', dnums_fuzzy[dnum]['subtype'], dnums_fuzzy[dnum]['magnitude'])
    #check for about with nummod (assuming that about will only be picked up with nummod )
    #? add 'more' 'about
    checkList1 = ['about', 'almost', 'approximately', 'roughly']
    for val in checkList1:
        if val in dnum:
            #? need to confirm magnitude
            return("fuzzy", 'imprecise quantifier', 'N/A')
    #other check
    if dnum in dnums_numbers: return ('other', dnums_numbers[dnum]['subtype'], dnums_numbers[dnum]["magnitude"])
    if dnum in dnums_other: return ('other', dnums_other[dnum]['subtype'], dnums_other[dnum]["magnitude"])
    if 'all' in dnum: return ('', '', '')

# function to return results of Allan Test
# depDict-> dependency dictionary 
# denumeratorType-> exactly what the name says
# nounPlurality -> again, why we use good variable names
# returns result list where 0/1 corresponds to [A+N, F+N, all+N]
def allanTest(denumeratorType, nounPlurality, relDict, nounIndex):
    result = ['0','0','0','0']
    # unlisted denumerator check 
    if denumeratorType == 'Not Applicable': return result
    # A+N test
    if denumeratorType == 'unit' and nounPlurality != 'plural':
        result[0] = '1'
    # F+N test
    if denumeratorType == 'fuzzy':
        result[1] = '1'
    # all + N test
    determiners = relDict.get('det', [])
    if(len(determiners) == 1):
        det = determiners[0]
        if det.getDependent().getToken().lower() == 'all' and det.getSubType() == '' and nounPlurality == 'singular':
            result[2] = '1'
    # *EX-PL test = verb plurality (in outfile or masterfile)
    # O-Den test
    if denumeratorType == 'other':
        result[3] = '1'

    return result
    
    
if __name__ == '__main__':
    # path = '/Volumes/AbstractNounsFiles/outFiles_Feb2019/outfiles_new_v3/'
    # sDir = '/Volumes/AbstractNounsFiles/outFiles_Feb2019/AllenTest/'
    path = '/Users/aeshaanwahlang/Documents/QuantitativeSemanticsData/test_outfiles/Allan/'
    sDir = '/Users/aeshaanwahlang/Documents/QuantitativeSemanticsData/AllanTest/'
    files = os.listdir(path)

    # df = pd.read_csv(path+"materialOut.csv")
    # x = df.at[260,'Relevant Dependencies']
    # print(x) 
    # d = Dependency.generateDependencies(x)
    # di = buildDependenciesDict(d)
    # print(di.get('det')[0].getDependent().getToken())

    for f in files:
        # f = "waterOut.csv"
        noun = f.replace("Out.csv", "")
        print("..running "+f)
        genAllanTest(path+f, noun, sDir)
        # break
    print("Allen Test Completed!")

    # genAllanTest(path+"adviceOut.csv", "advice", sDir)

