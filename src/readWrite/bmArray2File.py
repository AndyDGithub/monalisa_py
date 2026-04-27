"""Auto-generated from MATLAB source. Review manually before production use."""

from src.sparseMat.m.bmSparseMat_vec import ndims
from third_part.matlab_compat.matlab_native import num2str
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmArray2File(argDir, argName, argArray, argChar, argType):
    # TODO(matlab-control): if argChar == 't'
    myVarName = argName
    myFileName = strcat(argName,".txt")
    myFilePath = strcat(argDir, "/", myFileName)
    myNdims = ndims(argArray)
    mySize = np.shape(argArray)
    myLength = len(argArray.ravel().T)
    dlmwrite(myFilePath, myNdims,"delimiter"," ", "newline","pc")
    dlmwrite(myFilePath, mySize,"-append","delimiter"," ", "newline","pc")
    dlmwrite(myFilePath, myLength,"-append","delimiter"," ", "newline","pc")
    # TODO(matlab-line): dlmwrite(myFilePath,argArray(:)','-append','delimiter',' ','precision',17, 'newline','pc');
    # TODO(matlab-control): elseif argChar == 'c'
    myVarName = argName
    myFileName = strcat(argName,".csv")
    myFilePath = strcat(argDir, "/", myFileName)
    myNdims = ndims(argArray)
    mySize = np.shape(argArray)
    myLength = len(argArray.ravel().T)
    dlmwrite(myFilePath, myNdims,"delimiter"," ", "newline","pc")
    dlmwrite(myFilePath, mySize,"-append","delimiter"," ", "newline","pc")
    dlmwrite(myFilePath, myLength,"-append","delimiter"," ", "newline","pc")
    # TODO(matlab-control): for i = 1:length(argArray(:))/mySize(1)/mySize(2)
    dlmwrite(myFilePath, "","-append","delimiter"," ", "roffset",1)
    # TODO(matlab-line): dlmwrite(myFilePath,argArray(:,:,i),'-append','delimiter',' ','precision',17, 'newline','pc');
    # TODO(matlab-control): elseif argChar == 'd'
    myVarName = argName
    myFileNameH = strcat(argName,".hdat")
    myFileNameD = strcat(argName,".dat")
    myFilePath = strcat(argDir, "/", myFileNameH)
    myNdims  = ndims(argArray)
    mySize   = np.shape(argArray)
    myLength = len(argArray.ravel().T)
    mySize_string = num2str(mySize(1))
    # TODO(matlab-control): for i = 2:size(mySize, 2)
    mySize_string = [mySize_string, " ", num2str(mySize(i))]
    myLength_string = num2str(myLength)
    dlmwrite(myFilePath, myNdims,          "delimiter"," ", "newline","pc")
    dlmwrite(myFilePath, mySize_string,    "-append", "delimiter", "", "newline","pc")
    dlmwrite(myFilePath, myLength_string,  "-append", "delimiter", "", "newline","pc")
    myFilePath = strcat(argDir, "/", myFileNameD)
    myFile = fopen(myFilePath, "w")
    fwrite(myFile,argArray,argType)
    fclose(myFile)
    # TODO(matlab-control): elseif argChar == 'm'
    myVarName = argName
    myFileNameH = strcat(argName,".hdat")
    myFileNameD = strcat(argName,".dat")
    myFileNameM = strcat(argName,"_LOAD.m")
    myFilePath = strcat(argDir, "/", myFileNameH)
    myNdims = ndims(argArray)
    mySize = np.shape(argArray)
    myLength = len(argArray.ravel().T)
    dlmwrite(myFilePath, myNdims,   "delimiter"," ", "newline","pc")
    dlmwrite(myFilePath, mySize,    "-append","delimiter"," ", "newline","pc")
    dlmwrite(myFilePath, myLength,  "-append","delimiter"," ", "newline","pc")
    myFilePath = strcat(argDir, "/", myFileNameD)
    myFile = fopen(myFilePath, "w")
    fwrite(myFile,argArray,argType)
    fclose(myFile)
    myFilePath = strcat(argDir, "/", myFileNameM)
    # TODO(matlab-line): myString = strcat('bmArrayLoadFilePath = '' ', myFileNameD,''';');
    dlmwrite(myFilePath,myString,"delimiter","", "newline","pc")
    myString = strcat("bmArrayLoadLength = ",num2str(len(argArray.ravel())),";")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    # TODO(matlab-line): myString = strcat('bmArrayLoadType ='' ', argType,''';');
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = "bmArrayLoadSize =["
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    dlmwrite(myFilePath,num2str(mySize),"-append","delimiter","", "newline","pc")
    myString = "];"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat("clear",{" "}, argName, ";")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat(argName," = np.zeros(bmArrayLoadSize)", ";")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = "bmArrayLoadFile = fopen(bmArrayLoadFilePath);"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat(argName,"(:) = fread(bmArrayLoadFile, bmArrayLoadLength, bmArrayLoadType);")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = "fclose(bmArrayLoadFile);"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = "clear ans bmArrayLoadFile bmArrayLoadFilePath bmArrayLoadLength bmArrayLoadSize bmArrayLoadType"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    # TODO(matlab-control): elseif argChar == 's'
    myVarName = argName
    myFileName = strcat(argName,"_LOAD.m")
    myFilePath = strcat(argDir, "/", myFileName)
    myNdims = ndims(argArray)
    mySize = np.shape(argArray)
    myLength = len(argArray.ravel().T)
    myString = strcat("myNdims =",num2str(myNdims),";")
    dlmwrite(myFilePath,myString,"delimiter","", "newline","pc")
    myString = "mySize =["
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    dlmwrite(myFilePath,num2str(mySize),"-append","delimiter","", "newline","pc")
    myString = "];"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat("myLength = ",num2str(myLength),";")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = "if myNdims == 1"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat(myVarName," = np.zeros(mySize,1);")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = "else"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat(myVarName," = np.zeros(mySize);")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = "end"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat(myVarName,"(:) = [")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    # TODO(matlab-line): dlmwrite(myFilePath,argArray(:)','-append','delimiter',' ','precision',17, 'newline','pc');
    myString = "];"
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
    myString = strcat("clear myNdims mySize myLength")
    dlmwrite(myFilePath,myString,"-append","delimiter","", "newline","pc")
