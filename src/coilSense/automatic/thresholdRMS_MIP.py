"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from third_part.matlab_compat.matlab_native import colormap, double, hold, imagesc, legend, permute, plot, single, title, xlabel, ylabel

def thresholdRMS_MIP(colorMax, dataRMS, dataMIP, N_u, autoFlag):
    # [thRMS, thMIP] = thresholdRMS_MIP(colorMax, dataRMS, dataMIP, ...
    # N_u, automaticFlag)
    # 
    # This function sets a threshold for the values of the RMS and MIP value
    # calculated along the channels for 3D data. The threshold are
    # automatically estimated by assuming the data to have a multimodal
    # distribuition made out of two normal distributions. One for the noise and
    # one for the actual data. A Gaussian mixture model (GMM) is fitted to the
    # data and the point where the possibility of the pixel intensity belonging
    # to the data is higher than the possibility of the intensity to be noise
    # is taken as the treshold value. It is assumed that the mean of the noise
    # distribution is lower (darker pixels).
    # 
    # Authors:
    # Dominik Helbing
    # MattechLab 2024
    # 
    # Parameters:
    # colorMax (list): The value used to scale the RMS and MIP values. This
    # gives the possible maximum of the threshold (colorMax-1).
    # dataRMS (array): The RMS values of the data over its channels. This is
    # a 3D image.
    # dataMIP (array): The MIP values of the data over its channels. This is
    # a 3D image.
    # N_u (list): Size of the data in block format.
    # autoFlag (logical): flag; Automatically decide on thresholds if true.
    # Show figure and interrupt code to manually set if false.
    # 
    # Returns:
    # thRMS (int): The threshold value above which the RMS values are kept.
    # thMIP (int): The threshold value above which the MIP values are kept.
    # % Inizialize arguments
    # Ensure block format and single precision
    dataRMS = single(bmBlockReshape(dataRMS, N_u))
    dataMIP = single(bmBlockReshape(dataMIP, N_u))
    # Initialize variables spaning multiple nested functions for view
    permutation = [1,2,3]
    curImNum = 24
    useContrast = False
    activeSize = np.shape(dataRMS,3)
    # And to track dragging state and the dragged line
    isDragging = False
    activeLine = []
    # % Guess threshold
    # Get initial values for MIP and RMS thresholds
    # TODO(matlab-line): [thRMS, ~, ~] = detectThreshold_GMM2(dataRMS);
    # TODO(matlab-line): [thMIP, ~, ~] = detectThreshold_GMM2(dataMIP);
    # Return out of function if threshold is only detected automatically
    # TODO(matlab-control): if autoFlag
    # TODO(matlab-line): return
    # % Optionally show histogram (can only be set true here)
    showHistogram = False
    # TODO(matlab-control): if showHistogram
    figure
    tiledlayout("vertical")
    nexttile
    # TODO(matlab-line): hold on
    histogram(dataRMS, "Normalization", "pdf")
    xVal = linspace(min(dataRMS.ravel()), max(dataRMS.ravel()), 1000)
    plot(xVal, pdf1R(xVal), "--", "LineWidth", 2)
    plot(xVal, pdf2R(xVal), "--", "LineWidth", 2)
    # TODO(matlab-line): hold off
    nexttile
    # TODO(matlab-line): hold on
    histogram(dataMIP, "Normalization", "pdf")
    xVal = linspace(min(dataMIP.ravel()), max(dataMIP.ravel()), 1000)
    plot(xVal, pdf1M(xVal), "--", "LineWidth", 2)
    plot(xVal, pdf2M(xVal), "--", "LineWidth", 2)
    # TODO(matlab-line): hold off
    # % Prepare figure for threshold selection
    # Get number of points of x
    nPix = np.shape(dataRMS.ravel(), 1)
    n_RMS = np.zeros(1, colorMax)
    n_MIP = np.zeros(1, colorMax)
    # Calculate the fraction of points having a value bigger than every
    # integer from 0 to colorMax-1
    # TODO(matlab-control): for i = 0:colorMax-1
    # TODO(matlab-line): n_RMS(1, i+1) = sum(dataRMS(:) > i)/nPix;
    # TODO(matlab-line): n_MIP(1, i+1) = sum(dataMIP(:) > i)/nPix;
    # Create figure with tile layout (top is selection and bottom is view)
    # TODO(matlab-line): fig = figure('WindowScrollWheelFcn', @myWindowScrollWheelFcn);
    t = tiledlayout(fig,2,2)
    set(t, "Position", [0.1, 0.15, 0.8, 0.8])
    # Create axes
    axSel = nexttile([1,2])
    ax1 = nexttile
    ax2 = nexttile
    # Set up mouse click and motion callbacks for dragging the lines
    # TODO(matlab-line): set(fig, 'WindowButtonDownFcn', @(src, event) startDragFcn(fig));
    # TODO(matlab-line): set(fig, 'WindowButtonUpFcn', @(src, event) stopDragFcn(fig));
    # % Place interactive control elements
    # Add a confirmation button to finalize the selection
    # TODO(matlab-line): uicontrol(fig, 'Style', 'pushbutton', 'String', 'Confirm Selection', ...
    # TODO(matlab-line): 'Units', 'normalized', 'Position', [0.4 0.04 0.2 0.06], ...
    # TODO(matlab-line): 'Callback', @(src,even)confirmSelection());
    # Add dropdown to change the viewed dimensions, default is along Z
    # TODO(matlab-line): uicontrol(fig, 'Style', 'popupmenu', 'String', {'Along X', ...
    # TODO(matlab-line): 'Along Y', 'Along Z'}, 'Units', 'normalized', ...
    "Position", [0.44, 0.46, 0.12, 0.06], "Value", 3,  # For Along Z
    # TODO(matlab-line): 'Callback', @(src, event)changeView(src));
    # Add a checkbox to toggle between binary and percentile view
    # TODO(matlab-line): uicontrol(fig, 'Style', 'checkbox', 'String', ' Contrast', ...
    # TODO(matlab-line): 'Units', 'normalized', 'Position', [0.04 0.04 0.2 0.06], ...
    # TODO(matlab-line): 'Callback', @(src,event)toggleContrast());
    # % Plot selection plot with vertical lines
    hold(axSel, "on")
    # Plot RMS and MIP fractions above integers from 0 to colorMax - 1
    # TODO(matlab-line): x = (0:colorMax-1);
    plot(axSel, x, n_RMS, ".-")
    plot(axSel, x, n_MIP, ".-")
    xlabel(axSel, "X")
    ylabel(axSel, "Fraction above X")
    legend(axSel, "RMS", "MIP")
    title(axSel, "Fraction of points having a value above X")
    # Initial positions of the vertical lines
    # TODO(matlab-line): lineRMS = line(axSel, [thRMS thRMS], ylim, 'Color', 'b', ...
    # TODO(matlab-line): 'LineWidth', 2, 'DisplayName', 'RMS TH');
    # TODO(matlab-line): lineMIP = line(axSel, [thMIP thMIP], ylim, 'Color', 'r', ...
    # TODO(matlab-line): 'LineWidth', 2, 'DisplayName', 'MIP TH');
    hold(axSel, "off")
    # Draw view images
    refreshImages()
    # Wait for figure to close or the confirm button to be pressed
    uiwait
    # TODO(matlab-control): if ishandle(fig)
    thRMS = lineRMS.XData(1)
    thMIP = lineMIP.XData(1)
    delete(fig)
    # TODO(matlab-line): return;
    # % Nested functions - Threshold selection
    return (thRMS, thMIP)

def detectThreshold_GMM2(data):
    # This function fits two Gaussians to the data by fitting a
    # gaussian mixture model with two components. This is done with the
    # assumption that the data contains noise and actual data, both of
    # which can be described with a Gaussian.
    # The threshold is taken at the crossing point of the two
    # Gaussians. The noise is assumed to be the left Gaussian (smaller
    # intensity than the data)
    # Ensure data is a column vector
    data = data.ravel()
    # Fit Gaussian mixture model with two components to data
    gm = fitgmdist(data, 2)
    # Extract parameters of the two Gaussians
    mu1 = double(gm.mu(1))
    sigma1 = sqrt(gm.Sigma(1))
    mu2 = double(gm.mu(2))
    sigma2 = sqrt(gm.Sigma(2))
    # Define the PDFs of the two Gaussians as anonymous functions
    # TODO(matlab-line): pdf1 = @(x) normpdf(x, mu1, sigma1) * gm.ComponentProportion(1);
    # TODO(matlab-line): pdf2 = @(x) normpdf(x, mu2, sigma2) * gm.ComponentProportion(2);
    # Define the difference of the two PDFs (0 at crossing point)
    # TODO(matlab-line): diff_pdf = @(x) pdf1(x) - pdf2(x);
    # Find the crossing point and return it as the threshold
    threshold = round(fzero(diff_pdf, (mu1 + mu2)/2))

def n(fig):
    # This function checks if a line is clicked and starts the dragging
    # function if this is the case
    # Check if the click is close to either line
    cp = get(gca, "CurrentPoint")
    x_click = cp(1,1)
    # Test if RMS line was clicked
    # TODO(matlab-control): if abs(x_click - lineRMS.XData(1)) < 0.8  % Adjust as needed
    activeLine = lineRMS
    isDragging = True
    # Test if MIP line was clicked
    # TODO(matlab-control): elseif abs(x_click - lineMIP.XData(1)) < 0.8
    activeLine = lineMIP
    isDragging = True
    # TODO(matlab-control): if isDragging
    # Activate dragging function if either line is clicked
    # TODO(matlab-line): set(fig, 'WindowButtonMotionFcn', @(src, event) draggingFcn());
    return startDragFc

def n():
    # This function updates the line and the images when a line is
    # dragged
    # Test if dragginFcn is correctly called
    # TODO(matlab-control): if isDragging && ~isempty(activeLine)
    # Get current point and extract x values for redrawing the
    # active line
    cp = get(gca, "CurrentPoint")
    # clip data and round to integer
    new_x = max(min(round(cp(1,1)), colorMax-1), 0)
    # Redraw line
    # TODO(matlab-line): set(activeLine, 'XData', [new_x new_x]);
    drawnow
    # Redraw MIP or RMS image
    refreshImages()
    return draggingFc

def n(fig):
    # This function resets the active line and motion function when
    # the mouse button is let go
    isDragging = False
    activeLine = []
    set(fig, "WindowButtonMotionFcn", "")
    return stopDragFc

def n():
    # Resume execution
    uiresume
    # % Nested functions - RMS/MIP image view
    return confirmSelectio

def w(src):
    # This function permutes the data to show different views when
    # another view is selected from the dropdown menu.
    # Make sure the function is called from the correct source
    # TODO(matlab-control): if ~isa(src, 'matlab.ui.control.UIControl')
    # TODO(matlab-line): return
    # TODO(matlab-control): if ~strcmp(src.Style, 'popupmenu')
    # TODO(matlab-line): return
    # Get value as a string
    newSelection = src.String[src.Value]
    # Change size and permutation depending on selection
    # TODO(matlab-control): switch newSelection
    # TODO(matlab-control): case 'Along X'
    permutation = [2,3,1]
    activeSize = np.shape(dataRMS, 1)
    # TODO(matlab-control): case 'Along Y'
    permutation = [3,1,2]
    activeSize = np.shape(dataRMS, 2)
    # TODO(matlab-control): case 'Along Z'
    permutation = [1,2,3]
    activeSize = np.shape(dataRMS, 3)
    # TODO(matlab-control): otherwise
    # Refresh images
    refreshImages()
    return changeVie

def n(unused, evnt):
    # Mousewheel callback function to give interactions to bmImage3
    # TODO(matlab-control): if evnt.VerticalScrollCount > 0
    # Scrolling towards body -> reducing slice by one
    curImNum = curImNum - 1
    # Wrap around
    # TODO(matlab-control): if curImNum < 1
    curImNum = activeSize
    # TODO(matlab-control): elseif evnt.VerticalScrollCount < 0
    # Scrolling away from body -> increasing slice by one
    curImNum = curImNum + 1
    # Wrap around
    # TODO(matlab-control): if curImNum > activeSize
    curImNum = 1
    # Refresh images
    refreshImages()
    return myWindowScrollWheelFc

def s():
    # This function refreshes both images (RMS and MIP)
    # Refresh RMS image
    refreshImage(dataRMS, ax1, lineRMS, "RMS")
    # Refresh MIP image
    refreshImage(dataMIP, ax2, lineMIP, "MIP")
    return refreshImage

def e(data, ax, line, name):
    # This helper function refreshes a given image
    # Permute data to show correct slice
    data = permute(data, permutation)
    # TODO(matlab-line): data = data(:, :, curImNum);
    # Get threshold and apply to data to visualize its effect
    th = line.XData(1)
    # TODO(matlab-control): if useContrast
    data = data > th
    # TODO(matlab-control): else
    # TODO(matlab-line): data(data <= th) = 0;
    # Update image and title
    imagesc(ax, data)
    # TODO(matlab-line): title(ax, [name, ' [', num2str(curImNum), '/', ...
    # TODO(matlab-line): num2str(activeSize), ']']);
    axis(ax, "image")
    colormap(ax, "gray")
    return refreshImag

def t():
    # This function is called by the checkbox to update contrast use
    useContrast = ~useContrast
    refreshImages
    return toggleContras
