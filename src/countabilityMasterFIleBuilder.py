import sys
import os
# sys.path.append("/Users/aeshaanwahlang/Documents/QuantitativeSemantics/Repo/AbstractNouns/")
import pandas as pd
# from PostPorcessing.MasterFileBuilder.masterFileBuilder import columnAnalysis
# from MasterFileBuilder.masterFileBuilder import columnAnalysis

# return a list of col values for each sense of a word in becl dataset
def beclGet(word, col, becl):
    return becl.loc[becl['lemma'] == word, col].values

# add countability columns to masterfile and saves it as a new csv
def build(masterFilePath, beclPath):
    new = pd.read_csv(masterFilePath).copy()
    becl = pd.read_csv(beclPath, sep=";")
    cols = ['BECL Test_I_1', 'BECL Test_I_2', 'BECL Test_II_1', 'BECL Test_II_2', 'BECL Test_III_1', 'BECL Test_III_2', 'class', 'major_class']
    for c in cols:
        new[c] = ""
    
    for i in range(new.shape[0]):
        noun = new.loc[i, "Noun"]
        for c in cols:
            test = c.replace("BECL ", "")
            new.at[i,c] = beclGet(noun, test, becl)

        if i%1000 == 0: print(str(i) + " rows completed...")
    
    new.to_csv("/Users/aeshaanwahlang/Desktop/countability_masterFile.csv", index=False)
    print("new file saved")
     

if __name__ == "__main__":
    m = "[PATH TO COCA]"
    b = "[PATH TO BECL]"

    # build(m, b)
    print(os.path.dirname(os.path.realpath(__file__)))