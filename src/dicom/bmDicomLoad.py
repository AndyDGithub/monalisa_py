from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, length, size, str2double
from porting.lib.utils import ndims, strcmp


def bmDicomLoad(argDirectoryPath):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # This file comes from the natural sharing in the research community.
    # The original file was unsigned. The original author
    # remains therefore unkown. We would be happy to mention his name if he
    # recognizes parts of his code.
    # initial myItemList and myNameList ---------------------------------------
    # end initial myItemList and myNameList -----------------------------------
    # initial counters --------------------------------------------------------
    # end initial counters ----------------------------------------------------
    # counting the total number of series -------------------------------------
    # of series.
    # end counting the total number of series ---------------------------------
    # initial of the output mySerieList ---------------------------------------
    # end initial of the output mySerieList -----------------------------------
    # main loop loading the data in mySerieList -------------------------------
    # mySerieCounter is never reseted to 0.
    # counters
    # counters
    # counters
    # mySerieName
    # mySerieNumber
    # mySerieDate
    # mySerieTime
    # mySerieInstanceUID
    # mySerieFolder
    # filling the output mySerieList ------------------------------------------
    # end filling the output mySerieList --------------------------------------
    # counters
    # myImageNameList
    # mySerieFolder bis
    # myStudyFolder bis
    # myStudyPath   bis
    # myImageTimeList
    # end main loop loading the data in mySerieList ---------------------------
    # reordering the series by series time ------------------------------------
    # end reordering the series by series time --------------------------------
    # storing all the image matrices in a 3 dimensional array -----------------
    # we load the first dicom image of the serie
    # end storing all the image matrices in a 3 dimensional array -------------
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: myDicomdirPath = strcat(argDirectoryPath, '\DICOMDIR');
    # MATLAB: myInfo=dicominfo(myDicomdirPath);
    # MATLAB: myItemList = myInfo.DirectoryRecordSequence;
    # MATLAB: myNameList = fieldnames(myItemList);
    # MATLAB: myPatientCounter    = 0;
    # MATLAB: myStudyCounter      = 0;
    # MATLAB: mySerieCounter      = 0;
    # MATLAB: myImageCounter      = 0;
    # MATLAB: mySerieCounter = 0;
    # MATLAB: for i = 1:length(myNameList) % Begin loop over fields to count the number
    # MATLAB: myItem     = getfield(myItemList,myNameList{i});
    # MATLAB: myItemType = getfield(myItem,'DirectoryRecordType');
    # MATLAB: if strcmp(myItemType,'SERIES')
    # MATLAB: mySerieCounter = mySerieCounter + 1;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: mySerieList = cell(1, mySerieCounter);
    # MATLAB: mySerieListLength = length(mySerieList);
    # MATLAB: mySerieCounter = 0;
    # MATLAB: for i = 1:length(myNameList) % Begin loop over fields, note that
    # MATLAB: myItem = getfield(myItemList,myNameList{i});
    # MATLAB: myItemType = getfield(myItem,'DirectoryRecordType');
    # MATLAB: if strcmp(myItemType,'PATIENT')
    # MATLAB: myPatientCounter = myPatientCounter + 1;
    # MATLAB: myStudyCounter   = 0;
    # MATLAB: myImageCounter   = 0;
    # MATLAB: myPatientName = myItem.PatientName.FamilyName;
    # MATLAB: if isfield(myItem.PatientName,'GivenName')
    # MATLAB: myPatientForename = myItem.PatientName.GivenName;
    # MATLAB: else
    # MATLAB: myPatientForename = 'none';
    # MATLAB: end
    # MATLAB: myPatientID         = myItem.PatientID;
    # MATLAB: myPatientBirthDate  = myItem.PatientBirthDate;
    # MATLAB: elseif strcmp(myItemType,'STUDY')
    # MATLAB: myStudyCounter = myStudyCounter + 1;
    # MATLAB: myImageCounter = 0;
    # MATLAB: myStudyDescription  = myItem.StudyDescription;
    # MATLAB: myStudyDate         = myItem.StudyDate;
    # MATLAB: myStudyID           = myItem.StudyID;
    # MATLAB: myStudyFolder       = '';
    # MATLAB: myStudyPath         = '';
    # MATLAB: myStudyFolderFlag = 0;
    # MATLAB: elseif strcmp(myItemType,'SERIES')
    # MATLAB: mySerieCounter = mySerieCounter + 1;
    # MATLAB: myImageCounter = 0;
    # MATLAB: if isfield(myItem,'SeriesDescription')
    # MATLAB: mySerieName = myItem.SeriesDescription;
    # MATLAB: else
    # MATLAB: mySerieName = 'no_name';
    # MATLAB: end
    # MATLAB: mySerieNumber      = myItem.SeriesNumber;
    # MATLAB: mySerieDate        = myItem.SeriesDate;
    # MATLAB: mySerieTime        = myItem.SeriesTime;
    # MATLAB: mySerieInstanceUID = myItem.SeriesInstanceUID;
    # MATLAB: mySerieFolder      = '';
    # MATLAB: mySerieList{mySerieCounter}.patientName       = myPatientName;
    # MATLAB: mySerieList{mySerieCounter}.patientForename   = myPatientForename;
    # MATLAB: mySerieList{mySerieCounter}.patientID         = myPatientID;
    # MATLAB: mySerieList{mySerieCounter}.patientBirthDate  = myPatientBirthDate;
    # MATLAB: mySerieList{mySerieCounter}.studyDescription  = myStudyDescription;
    # MATLAB: mySerieList{mySerieCounter}.studyDate         = myStudyDate;
    # MATLAB: mySerieList{mySerieCounter}.studyID           = myStudyID;
    # MATLAB: mySerieList{mySerieCounter}.studyFolder       = myStudyFolder;
    # MATLAB: mySerieList{mySerieCounter}.studyPath         = myStudyPath;
    # MATLAB: mySerieList{mySerieCounter}.serieName        = mySerieName;
    # MATLAB: mySerieList{mySerieCounter}.serieNumber      = mySerieNumber;
    # MATLAB: mySerieList{mySerieCounter}.serieDate        = mySerieDate;
    # MATLAB: mySerieList{mySerieCounter}.serieTime        = mySerieTime;
    # MATLAB: mySerieList{mySerieCounter}.serieInstanceUID = mySerieInstanceUID;
    # MATLAB: mySerieList{mySerieCounter}.serieFolder      = mySerieFolder;
    # MATLAB: mySerieList{mySerieCounter}.imagesTable       = [];
    # MATLAB: mySerieList{mySerieCounter}.imageNameList     = [];
    # MATLAB: mySerieList{mySerieCounter}.imageTimeList     = [];
    # MATLAB: elseif strcmp(myItemType,'IMAGE') || strcmp(myItemType,'PRIVATE')
    # MATLAB: myImageCounter = myImageCounter + 1;
    # MATLAB: [myPathString, myImageName] = fileparts(myItem.ReferencedFileID);
    # MATLAB: mySerieList{mySerieCounter}.imageNameList{myImageCounter} = myImageName;
    # MATLAB: if myImageCounter == 1
    # MATLAB: [myPathString, mySerieFolder] = fileparts(myPathString);
    # MATLAB: mySerieList{mySerieCounter}.serieFolder = mySerieFolder;
    # MATLAB: if myStudyFolderFlag == 0
    # MATLAB: [~, myStudyFolder] = fileparts(myPathString);
    # MATLAB: myStudyPath = strcat(argDirectoryPath,'\DICOM\',myStudyFolder,'\');
    # MATLAB: mySerieList{mySerieCounter}.studyFolder = myStudyFolder;
    # MATLAB: mySerieList{mySerieCounter}.studyPath = myStudyPath;
    # MATLAB: myStudyFolderFlag = 1;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: myImageLongNameForAcqTime = [myStudyPath,mySerieFolder,'\',myImageName];
    # MATLAB: if exist(myImageLongNameForAcqTime) == 2
    # MATLAB: myInfoForAcqTime = dicominfo(myImageLongNameForAcqTime);
    # MATLAB: if isfield(myInfoForAcqTime,'AcquisitionTime')
    # MATLAB: myTime = myInfoForAcqTime.AcquisitionTime;
    # MATLAB: myImageTimeList(myImageCounter) = 3600*str2num(myTime(1:2))+60*str2num(myTime(3:4))+str2num(myTime(5:6))+10^(-6)*str2num(myTime(8:13));
    # MATLAB: else
    # MATLAB: myImageTimeList(myImageCounter) = 0;
    # MATLAB: end
    # MATLAB: else
    # MATLAB: myImageTimeList(myImageCounter) = 0;
    # MATLAB: end
    # MATLAB: mySerieList{mySerieCounter}.imageTimeList = myImageTimeList;
    # MATLAB: else
    # MATLAB: mySerieList{mySerieCounter}.imagesTable       = [];
    # MATLAB: mySerieList{mySerieCounter}.imageNameList     = [];
    # MATLAB: mySerieList{mySerieCounter}.imageTimeList     = [];
    # MATLAB: end
    # MATLAB: end
    # MATLAB: mySwitchFlag = 1;
    # MATLAB: while mySwitchFlag == 1
    # MATLAB: mySwitchFlag = 0;
    # MATLAB: for i = 1:mySerieListLength - 1
    # MATLAB: if str2double(mySerieList{i+1}.serieTime) < str2double(mySerieList{i}.serieTime)
    # MATLAB: myTemp = mySerieList{i+1};
    # MATLAB: mySerieList{i+1} = mySerieList{i};
    # MATLAB: mySerieList{i} = myTemp;
    # MATLAB: mySwitchFlag = 1;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # MATLAB: ... (27 more lines)
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    mySerieList = None
    return mySerieList
