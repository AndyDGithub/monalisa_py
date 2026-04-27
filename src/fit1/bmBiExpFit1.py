from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, length, logical, repmat, size
from porting.lib.utils import errordlg, ndims, real


def bmBiExpFit1(argImagesTable, argX, argX_middle, varargin):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # varargin  = [monoErrorTh biErrorTh monoLowerBound monoUpperBound biLowerBound biUpperBound]
    # varargout = [monoExpFit biExpFit monoErrorMask biErrorMask]
    # This code cointains some magic numbers ! Type "magic numbers" to find it.
    # definition of the fit-model for mono-exponential fitting
    # definition of the fit-model for bi-exponential fitting
    # Fit mono exponentiel ----------------------------------------------------
    # options for the fitting function
    # opts = optimset('Display', 'off', 'Algorithm', 'levenberg-marquardt');
    # Fit biexponentiel --------------------------------------------------------
    # lsqLowerBound = [0      20.0e-3           1e-4             0.7]; % magic numbers
    # lsqUpperBound = [1      80/1000           monoExpFit_2(i)  1.3]; % magic numbers
    # lsqLowerBound = []; % magic numbers
    # lsqUpperBound = []; % magic numbers
    # Reshaping and naNing
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: mySize = size(argImagesTable);
    # MATLAB: mySize = [prod(mySize(1:end-1)) mySize(end)];
    # MATLAB: if not(length(argX) == mySize(2))
    # MATLAB: monoExpFit_2 = 0;
    # MATLAB: biExpFit_1 = 0;
    # MATLAB: biExpFit_2 = 0;
    # MATLAB: biExpFit_3 = 0;
    # MATLAB: errordlg('Wrong list of arguments');
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: monoErrorTh = [];
    # MATLAB: biErrorTh = [];
    # MATLAB: monoLowerBound = [];
    # MATLAB: monoUpperBound = [];
    # MATLAB: biLowerBound = [];
    # MATLAB: biUpperBound = [];
    # MATLAB: if isempty(varargin)
    # MATLAB: 1+1;
    # MATLAB: elseif isscalar(varargin)
    # MATLAB: monoErrorTh = varargin{1};
    # MATLAB: elseif length(varargin) == 2
    # MATLAB: monoErrorTh = varargin{1};
    # MATLAB: biErrorTh = varargin{2};
    # MATLAB: elseif length(varargin) == 4
    # MATLAB: monoErrorTh = varargin{1};
    # MATLAB: biErrorTh = varargin{2};
    # MATLAB: monoLowerBound = varargin{3};
    # MATLAB: monoUpperBound = varargin{4};
    # MATLAB: elseif length(varargin) == 6
    # MATLAB: monoErrorTh = varargin{1};
    # MATLAB: biErrorTh = varargin{2};
    # MATLAB: monoLowerBound = varargin{3};
    # MATLAB: monoUpperBound = varargin{4};
    # MATLAB: biLowerBound = varargin{5};
    # MATLAB: biUpperBound = varargin{6};
    # MATLAB: else
    # MATLAB: monoExpFit_2 = 0;
    # MATLAB: biExpFit_1 = 0;
    # MATLAB: biExpFit_2 = 0;
    # MATLAB: biExpFit_3 = 0;
    # MATLAB: errordlg('Wrong list of arguments');
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: mdl_mono_exp = @(beta,x)(beta(1)*exp(-x*beta(2)));
    # MATLAB: mdl_bi_exp = @(beta,x)(beta(4)*beta(1)*exp(-x*beta(2))+beta(4)*(1-beta(1))*exp(-x*beta(3)));
    # MATLAB: imagesTable = reshape(argImagesTable, mySize);
    # MATLAB: N = mySize(2);
    # MATLAB: x = squeeze(argX);
    # MATLAB: x = reshape(x, [length(x) 1]);
    # MATLAB: monoExpFit_2    = zeros(mySize(1), 1);
    # MATLAB: biExpFit_1      = zeros(mySize(1), 1);
    # MATLAB: biExpFit_2      = zeros(mySize(1), 1);
    # MATLAB: biExpFit_3      = zeros(mySize(1), 1);
    # MATLAB: biExpFit_4      = zeros(mySize(1), 1);
    # MATLAB: xTable = reshape(x, [1 length(x)]);
    # MATLAB: xTable = repmat(xTable, [mySize(1) 1]);
    # MATLAB: zTable = log(imagesTable);
    # MATLAB: MeanX = mean(xTable, 2);
    # MATLAB: MeanZ = mean(zTable, 2);
    # MATLAB: MeanX2 = mean(xTable.^2, 2);
    # MATLAB: MeanXZ = mean(xTable.*zTable, 2);
    # MATLAB: h = (MeanX2.*MeanZ-MeanX.*MeanXZ)./(MeanX2-MeanX.^2);
    # MATLAB: monoExpFit_1_start = exp(h);
    # MATLAB: monoExpFit_2_start = -(MeanXZ-MeanX.*MeanZ)./(MeanX2-MeanX.^2);
    # MATLAB: monoExpFit_1 = monoExpFit_1_start;
    # MATLAB: monoExpFit_2 = monoExpFit_2_start;
    # MATLAB: opts = optimset('Display', 'off');
    # MATLAB: lsqLowerBound = [];
    # MATLAB: lsqUpperBound = [];
    # MATLAB: for i = 1:mySize(1)
    # MATLAB: if isnan(monoExpFit_1_start(i))||isnan(monoExpFit_2_start(i))
    # MATLAB: monoExpFit_1(i) = NaN;
    # MATLAB: monoExpFit_2(i) = NaN;
    # MATLAB: else
    # MATLAB: y = squeeze(imagesTable(i, :))';
    # MATLAB: beta = [monoExpFit_1_start(i) monoExpFit_2_start(i)];
    # MATLAB: beta = lsqcurvefit(mdl_mono_exp , beta, x, y, lsqLowerBound, lsqUpperBound, opts);
    # MATLAB: monoExpFit_1(i) = beta(1);
    # MATLAB: monoExpFit_2(i) = beta(2);
    # MATLAB: end
    # MATLAB: end
    # MATLAB: monoExpFit_1_table = repmat(monoExpFit_1, [1 length(x)]);
    # MATLAB: monoExpFit_2_table = repmat(monoExpFit_2, [1 length(x)]);
    # MATLAB: myMonoExpFit = monoExpFit_1_table.*exp(-monoExpFit_2_table.*xTable);
    # MATLAB: myError = sqrt(mean((myMonoExpFit-imagesTable).^2./myMonoExpFit.^2,2));
    # MATLAB: if not(isempty(monoErrorTh))
    # MATLAB: monoErrorMask = (myError > monoErrorTh);
    # MATLAB: else
    # MATLAB: monoErrorMask = zeros(mySize(1), 1);
    # MATLAB: end
    # MATLAB: monoErrorMask = monoErrorMask + isnan(monoExpFit_1)+isnan(monoExpFit_2);
    # MATLAB: monoErrorMask = logical(monoErrorMask);
    # MATLAB: xEarlyMask   = (argX <= argX_middle);
    # MATLAB: xEarlyMask_2 = (argX <= argX_middle/2);
    # MATLAB: xLateMask  = (argX >= argX_middle);
    # MATLAB: xEarly     = argX(xEarlyMask);
    # MATLAB: xEarly_2   = argX(xEarlyMask_2);
    # MATLAB: xLate      = argX(xLateMask);
    # MATLAB: xEarlyTable   = reshape(xEarly, [1 length(xEarly)]);
    # MATLAB: xEarlyTable   = repmat(xEarlyTable, [mySize(1) 1]);
    # MATLAB: zEarlyTable   = log(imagesTable(:,xEarlyMask));
    # MATLAB: xEarlyTable_2   = reshape(xEarly_2, [1 length(xEarly_2)]);
    # MATLAB: xEarlyTable_2   = repmat(xEarlyTable_2, [mySize(1) 1]);
    # MATLAB: zEarlyTable_2  = log(imagesTable(:,xEarlyMask_2));
    # MATLAB: MeanX_early = mean(xEarlyTable, 2);
    # MATLAB: MeanZ_early = mean(zEarlyTable, 2);
    # MATLAB: MeanX2_early = mean(xEarlyTable.^2, 2);
    # MATLAB: MeanXZ_early = mean(xEarlyTable.*zEarlyTable, 2);
    # MATLAB: MeanX_early_2 = mean(xEarlyTable_2, 2);
    # MATLAB: MeanZ_early_2 = mean(zEarlyTable_2, 2);
    # MATLAB: MeanX2_early_2 = mean(xEarlyTable_2.^2, 2);
    # MATLAB: MeanXZ_early_2 = mean(xEarlyTable_2.*zEarlyTable_2, 2);
    # MATLAB: h_early = (MeanX2_early.*MeanZ_early-MeanX_early.*MeanXZ_early)./(MeanX2_early-MeanX_early.^2);
    # MATLAB: biExpFit_2_start = -(MeanXZ_early-MeanX_early.*MeanZ_early)./(MeanX2_early-MeanX_early.^2);
    # MATLAB: h_early_2 = (MeanX2_early_2.*MeanZ_early_2-MeanX_early_2.*MeanXZ_early_2)./(MeanX2_early_2-MeanX_early_2.^2);
    # MATLAB: biExpFit_2_start_2 = -(MeanXZ_early_2-MeanX_early_2.*MeanZ_early_2)./(MeanX2_early_2-MeanX_early_2.^2);
    # MATLAB: xLateTable = reshape(xLate, [1 length(xLate)]);
    # MATLAB: xLateTable = repmat(xLateTable, [mySize(1) 1]);
    # MATLAB: zLateTable = log(imagesTable(:,xLateMask));
    # MATLAB: MeanX_late = mean(xLateTable, 2);
    # MATLAB: ... (60 more lines)
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    monoExpFit_2 = None
    biExpFit_1 = None
    biExpFit_2 = None
    biExpFit_3 = None
    varargout = None
    return monoExpFit_2, biExpFit_1, biExpFit_2, biExpFit_3, varargout
