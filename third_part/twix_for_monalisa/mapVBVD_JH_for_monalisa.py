from __future__ import annotations
from third_part.matlab_compat.matlab_native import disp, double, fullfile, isempty, length, logical, num2str, size
from porting.lib.utils import strcmp


def mapVBVD_JH_for_monalisa(filename, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # This file was written by Philipp Ehses. Some changes were done
    # by John Heerfordt in order to read large free-running acquisitions.
    # In addition, some lines were deleted by Bastien Milani because of some
    # compatibility problem with new Siemens environements.
    # The function names were also renamed with the extension
    # '_for_monalisa' in order to prevent any conflict of names with other
    # version (please don't see there an atempt of appropriation of this code).
    # Reads Siemens raw .dat file from VB/VD MRI raw data.
    # requires twix_map_obj.m & read_twix_hdr.m
    # 
    # 
    # Author: Philipp Ehses (philipp.ehses@tuebingen.mpg.de)
    # 
    # 
    # Philipp Ehses 11.02.07, original version
    # [..]
    # Philipp Ehses 22.03.11, port to VD11
    # Felix Breuer  31.03.11, added support for noise & ref scans, speed fixes
    # Philipp Ehses 19.08.11, complete reorganization of code, added
    # siemens_data_obj class to improve readability
    # Wolf Blecher  15.05.12, readout of slice position parameters for VB Data sets
    # Wolf Blecher  11.06.12, added distinction between PATREF and PATREF PHASCOR
    # Philipp Ehses 02.08.12, again massive code reorganization. The new class
    # twix_map_obj.m now stores the memory position of
    # each dataset (coils are included - size: NCol*NCha)
    # The actual data is not read until it is demanded
    # by a "data_obj()" call. This makes it possible
    # to selectively read in only parts of the data
    # (e.g. to preserve memory).
    # Philipp Ehses 27.08.12, speed optimizations (avoiding of .-subsref calls)
    # 07.09.12 Thanks to Stephen Yutzy for implementing support for raw data
    # correction (currently only supported for VB software version).
    # 15.01.13 Thanks to Zhitao Li for proper handling of SYNCDATA.
    # Philipp Ehses 28.08.13, added support for VD13 multi-raid files
    # Michael VÃ¶lker May-Aug 15 * Better error tolerance with incomplete files.
    # * Swapped out parsing loop into a separate function
    # without access to twix object (no thousands of subsref calls).
    # * For parsing, use an as-minimalistic-as-possible loop
    # to gather all mdhs in binary form. They are all stored
    # in one array "mdh_blob".
    # * Translation of mdhs from binary to struct is vectorized
    # and almost instant. It's done in evalMDH(), replacing
    # evalMDHvb() and evalMDHvd(), no more freads inside!
    # * vectorized readMDH(), quasi-instant
    # * When parsing, actually read the entire file without jumps.
    # This is weirdly faster than fseek(), plus the entire file is
    # kept in the file system cache, if possible. Next read
    # is therefore faster, too.
    # * => Parsing speed improved by factor 3...7 or so
    # * Speed increase for reading data, esp. when slicing,
    # os-removal or reflected lines. Also for random acquisitions.
    # Jonas Bause,    18.11.16   receiver phase for ramp-sampling fixed, now takes into account
    # Chris Mirkes & PE        offcenter shifts in readout direction
    # 
    # 
    # Input:
    # 
    # filename or simply meas. id, e.g. mapVBVD(122) (if file is in same path)
    # optional arguments (see below)
    # 
    # Output: twix_obj structure with elements (if available):
    # .image:         image scan
    # .noise:         for noise scan
    # .phasecor:      phase correction scan
    # .phasestab:     phase stabilization scan
    # .phasestabRef0: phase stab. ref. (MDH_REFPHASESTABSCAN && !MDH_PHASESTABSCAN)
    # .phasestabRef1: phase stab. ref. (MDH_REFPHASESTABSCAN &&  MDH_PHASESTABSCAN)
    # .refscan:       parallel imaging reference scan
    # .refscanPC:     phase correction scan for reference data
    # .refscanPS:     phase stabilization scan for reference data
    # .refscanPSRef0: phase stab. ref scan for reference data
    # .refscanPSRef1: phase stab. ref scan for reference data
    # .RTfeedback:    realtime feedback data
    # .vop:           vop rf data
    # 
    # 
    # The raw data can be obtained by calling e.g. twix_obj.image() or for
    # squeezed data twix_obj.image{''} (the '' are needed due to a limitation
    # of matlab's overloading capabilities).
    # Slicing is supported as well, e.g. twix_obj.image(:,:,1,:) will return
    # only the first line of the full data set (all later dimensions are
    # squeezed into one). Thus, slicing of the "memory-mapped" data objects
    # works exactly the same as regular matlab array slicing - with one
    # exception:
    # The keyword 'end' is not supported.
    # Overloading of the '()' and '{}' operators works by overloading matlab's
    # built-in 'subsref' function. Matlab calls subsref whenever the operators
    # '()', '{}', or '.' are called. In the latter case, the overloaded subsref
    # just calls the built-in subsref function since we don't want to change
    # the behaviour for '.'-calls. However, this has one minor consequence:
    # There's no way (afaik) to know whether the original call was terminated
    # with a semicolon. Thus, a call to e.g. twix_obj.image.NLin will produce
    # no output with or without semicolon termination. 'a = twix_obj.image.NLin'
    # will however produce the expected result.
    # 
    # 
    # Order of raw data:
    # 1) Columns
    # 2) Channels/Coils
    # 3) Lines
    # 4) Partitions
    # 5) Slices
    # 6) Averages
    # 7) (Cardiac-) Phases
    # 8) Contrasts/Echoes
    # 9) Measurements
    # 10) Sets
    # 11) Segments
    # 12) Ida
    # 13) Idb
    # 14) Idc
    # 15) Idd
    # 16) Ide
    # 
    # 
    # Optional parameters/flags:
    # 
    # removeOS:          removes oversampling (factor 2) in read direction
    # doAverage:         performs average (resulting avg-dim has thus size 1)
    # ignoreSeg:         ignores segment mdh index (works basically the same as
    # the average flag)
    # rampSampRegrid     optional on-the-fly regridding of ramp-sampled readout
    # doRawDataCorrect:  enables raw data correction if used in the acquisition
    # (only works for VB atm)
    # 
    # These flags can also be set/unset later, e.g "twix_obj.image.flagRemoveOS = 1"
    # 
    # 
    # Examples:
    # twix_obj = mapVBVD(measID);
    # 
    # % return all image-data:
    # image_data = twix_obj.image();
    # % return all image-data with all singular dimensions removed/squeezed:
    # image_data = twix_obj.image{''}; % '' necessary due to a matlab limitation
    # % return only data for line numbers 1 and 5; all dims higher than 4 are
    # % grouped into dim 5):
    # image_data = twix_obj.image(:,:,[1 5],:,:);
    # % return only data for coil channels 2 to 6; all dims higher than 4 are
    # % grouped into dim 5); but work with the squeezed data order
    # % => use '{}' instead of '()':
    # image_data = twix_obj.image{:,2:6,:,:,:};
    # 
    # So basically it works like regular matlab array slicing (but 'end' is
    # not supported; note that there are still a few bugs with array slicing).
    # 
    # % NEW: unsorted raw data (in acq. order):
    # image_data = twix_obj.image.unsorted(); % no slicing supported atm
    # 
    # 
    # Suppress silly editor warnings in the entire file, barking about
    # unused variables:
    # #ok<*NASGU>
    # assume that complete path is given
    # filename not a string, so assume that it is the MeasID
    # add absolute path, when no path is given
    # Parse varargin %%%%%
    # 
    # get file size
    # start of actual measurement data (sans header)
    # lazy software version check (VB or VD?)
    # number of different scans in file stored in 2nd in
    # in VB versions, the first 4 bytes indicate the beginning of the
    # raw data part of the file
    # SRY read data correction factors
    # do this for all VB datasets, so that the factors are available later
    # in the image_obj if the user chooses to set the correction flag
    # find the section of the protocol
    # note: the factors are also available in <ParamArray."CoilSelects">
    # along with element name and FFT scale, but the parsing is
    # significantly more difficult
    # find the line with correction factors
    # the factors are on the first line that begins with this
    # pattern
    # this does not work in this location because the MDHs
    # have not been parsed yet
    # if (length(rawfactors) ~= 2*max(image_obj.NCha))
    # error('Number of raw factors (%f) does not equal channel count (%d)', length(rawfactors)/2, image_obj.NCha);
    # end;
    # note the transpose, this makes the vector
    # multiplication during the read easier
    # data will be read in two steps (two while loops):
    # 1) reading all MDHs to find maximum line no., partition no.,... for
    # ima, ref,... scan
    # 2) reading the data
    # read header and calculate regridding (optional)
    # declare data objects:
    # print reader version information
    # jump to first mdh
    # find all mdhs and save them in binary form, first:
    # get mdhs and masks for each scan, no matter if noise, image, RTfeedback etc:
    # Assign mdhs to their respective scans and parse it in the correct twix objects.
    # 
    # logic really correct?
    # remove unused fields
    # recover from read error
    # Goal of this function is to gather all mdhs in the dat file and store them
    # in binary form, first. This enables us to evaluate and parse the stuff in
    # a MATLAB-friendly (vectorized) way. We also yield a clear separation between
    # a lengthy loop and other expressions that are evaluated very few times.
    # 
    # The main challenge is that we never know a priori, where the next mdh is
    # and how many there are. So we have to actually evaluate some mdh fields to
    # find the next one.
    # 
    # All slow things of the parsing step are found in the while loop.
    # => It is the (only) place where micro-optimizations are worthwhile.
    # 
    # The current state is that we are close to sequential disk I/O times.
    # More fancy improvements may be possible by using workers through parfeval()
    # or threads using a java class (probably faster + no toolbox):
    # http://undocumentedmatlab.com/blog/explicit-multi-threading-in-matlab-part1
    # arbitrary assumptions:
    # ======================================
    # constants and conditional variables
    # ======================================
    # 20 fill bytes in VD (21:40)
    # ======================================
    # Read mdh as binary (uint8) and evaluate as little as possible to know...
    # ... where the next mdh is (ulDMALength / ushSamplesInScan & ushUsedChannels)
    # ... whether it is only for sync (MDH_SYNCDATA)
    # ... whether it is the last one (MDH_ACQEND)
    # evalMDH() contains the correct and readable code for all mdh entries.
    # read everything and cut out the mdh
    # ok, look closer if really all *4* bytes are 0:
    # jump to next full 512 bytes
    # pehses: the pack bit indicates that multiple ADC are packed into one
    # DMA, often in EPI scans (controlled by fRTSetReadoutPackaging in IDEA)
    # since this code assumes one adc (x NCha) per DMA, we have to correct
    # the "DMA length"
    # if mdh.ulPackBit
    # it seems that the packbit is not always set correctly
    # grow arrays in batches
    # discard overallocation:
    # see pkg/MrServers/MrMeasSrv/SeqIF/MDH/mdh.h
    # and pkg/MrServers/MrMeasSrv/SeqIF/MDH/MdhProxy.h
    # unfortunately, typecast works on vectors, only
    # byte pos.
    # mdh.ulDMALength               = data_uint32(:,1);      %   1 :   4
    # inlining of evalInfoMask
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if ~exist('filename','var') || isempty(filename)
    # MATLAB: info = 'Please select binary file to read';
    # MATLAB: [fname,pathname]=uigetfile('*.dat',info);
    # MATLAB: if isempty(pathname)
    # MATLAB: return
    # MATLAB: end
    # MATLAB: filename=[pathname fname];
    # MATLAB: else
    # MATLAB: if ischar(filename)
    # MATLAB: if  ~strcmpi(filename(end-3:end),'.dat')
    # MATLAB: filename=[filename '.dat'];   %% adds filetype ending to file
    # MATLAB: end
    # MATLAB: else
    # MATLAB: measID   = filename;
    # MATLAB: filelist = dir('*.dat');
    # MATLAB: filesfound = 0;
    # MATLAB: for k=1:numel(filelist)
    # MATLAB: if regexp(filelist(k).name,['^meas_MID0*' num2str(measID) '_.*\.dat'])==1
    # MATLAB: if filesfound == 0
    # MATLAB: filename = filelist(k).name;
    # MATLAB: end
    # MATLAB: filesfound = filesfound+1;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: if filesfound == 0
    # MATLAB: error(['File with meas. id ' num2str(measID) ' not found.']);
    # MATLAB: elseif filesfound > 1
    # MATLAB: disp(['Multiple files with meas. id ' num2str(measID) ' found. Choosing first occurence.']);
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # MATLAB: [pathstr, name, ext] = fileparts(filename);
    # MATLAB: if isempty(pathstr)
    # MATLAB: pathstr  = pwd;
    # MATLAB: filename = fullfile(pathstr, [name ext]);
    # MATLAB: end
    # MATLAB: arg.bReadImaScan    = true;
    # MATLAB: arg.bReadNoiseScan  = true;
    # MATLAB: arg.bReadPCScan     = true;
    # MATLAB: arg.bReadRefScan    = true;
    # MATLAB: arg.bReadRefPCScan  = true;
    # MATLAB: arg.bReadRTfeedback = true;
    # MATLAB: arg.bReadPhaseStab  = true;
    # MATLAB: arg.bReadHeader     = true;
    # MATLAB: k=1;
    # MATLAB: while k <= numel(varargin)
    # MATLAB: if ~ischar(varargin{k})
    # MATLAB: error('string expected');
    # MATLAB: end
    # MATLAB: switch lower(varargin{k})
    # MATLAB: case {'readheader','readhdr','header','hdr'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.bReadHeader = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.bReadHeader = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: case {'removeos','rmos'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.removeOS = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.removeOS = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: case {'doaverage','doave','ave','average'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.doAverage = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.doAverage = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: case {'averagereps','averagerepetitions'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.averageReps = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.averageReps = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: case {'averagesets'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.averageSets = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.averageSets = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: case {'ignseg','ignsegments','ignoreseg','ignoresegments'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.ignoreSeg = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.ignoreSeg = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: case {'rampsampregrid','regrid'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.rampSampRegrid = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.rampSampRegrid = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: case {'rawdatacorrect','dorawdatacorrect'}
    # MATLAB: if numel(varargin) > k && ~ischar(varargin{k+1})
    # MATLAB: arg.doRawDataCorrect = logical(varargin{k+1});
    # MATLAB: k = k+2;
    # MATLAB: else
    # MATLAB: arg.doRawDataCorrect = true;
    # MATLAB: k = k+1;
    # MATLAB: end
    # MATLAB: otherwise
    # MATLAB: error('Argument not recognized.');
    # MATLAB: end
    # MATLAB: end
    # MATLAB: clear varargin
    # MATLAB: tic;
    # MATLAB: ... (392 more lines)
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    twix_obj = None
    return twix_obj
