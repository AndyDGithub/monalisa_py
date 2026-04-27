"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.varargin.bmVarargin import bmVarargin
from third_part.matlab_compat.matlab_native import colormap, figure, imagesc, num2str, permute, repmat, str2double, title, xlabel, ylabel

def selectROI(dataRMS, dataMIP, N_u, varargin):
    # coordinates = selectROI(dataRMS, dataMIP, N_u, varargin)
    # 
    # This function allows to manually set the bounding box around the region
    # of interest (ROI) for every dimension of the image in dataRMS and
    # dataMIP. For both data a figure is created (6 images in total). The
    # bounding boxes update automatically to always use the same coordinates in
    # all images. The code is interrupted until the selection is confirmed or
    # the window is closed.
    # 
    # Authors:
    # Dominik Helbing
    # MattechLab 2024
    # 
    # Parameters:
    # dataRMS (array): Data for RMS image. Has to be data of a 3D image.
    # dataMIP (array): Data for MIP image. Has to be data of a 3D image.
    # N_u (list): Contains the size of the data in every dimension.
    # varargin{1}: Flag; allows changing of coordinates with input fields.
    # Default value is false.
    # varargin{2}: Array that contains the guessed position of the bounding
    # box. Has to have the structure [xMin, xWidth; yMin, yWidth; zMin,
    # zWidth]. Default value is
    # [2, min(N_u)-4; 2, min(N_u)-4; 2, min(N_u)-4]
    # 
    # Returns:
    # coordinates (array): The updated coordinates of the bounding box
    # including the same ROI for dataRMS and dataMIP. Has the structure
    # [xMin, xMax; yMin, yMax; zMin, zMax]
    # % Initialize arguments
    # Extract optional arguments
    [autoFlag, boxPos]  = bmVarargin(varargin)
    # Ensure correct size
    N_u = N_u.ravel().T
    dataRMS = bmBlockReshape(dataRMS, N_u)
    dataMIP = bmBlockReshape(dataMIP, N_u)
    # Set default value if position is not given
    # TODO(matlab-control): if isempty(boxPos)
    boxPos = repmat([2, min(N_u)-4], [3,1])
    # Set default value for flag
    # TODO(matlab-control): if isempty(autoFlag)
    autoFlag = False
    # Sum over every dimension and normalize
    zRMS = np.sum(dataRMS, 3)
    # TODO(matlab-line): zRMS = (zRMS - min(zRMS, [], "all")) / ...
    (max(zRMS, [], "all") - min(zRMS, [], "all"))
    yRMS = permute(dataRMS, [3, 1, 2])
    yRMS = np.sum(yRMS, 3)
    # TODO(matlab-line): yRMS = (yRMS - min(yRMS, [], "all")) / ...
    (max(yRMS, [], "all") - min(yRMS, [], "all"))
    xRMS = permute(dataRMS, [2, 3, 1])
    xRMS = np.sum(xRMS, 3)
    # TODO(matlab-line): xRMS = (xRMS - min(xRMS, [], "all")) / ...
    (max(xRMS, [], "all") - min(xRMS, [], "all"))
    # Repeat for MIP
    zMIP = np.sum(dataMIP, 3)
    # TODO(matlab-line): zMIP = (zMIP - min(zMIP, [], "all")) / ...
    (max(zMIP, [], "all") - min(zMIP, [], "all"))
    yMIP = permute(dataMIP, [3, 1, 2])
    yMIP = np.sum(yMIP, 3)
    # TODO(matlab-line): yMIP = (yMIP - min(yMIP, [], "all")) / ...
    (max(yMIP, [], "all") - min(yMIP, [], "all"))
    xMIP = permute(dataMIP, [2, 3, 1])
    xMIP = np.sum(xMIP, 3)
    # TODO(matlab-line): xMIP = (xMIP - min(xMIP, [], "all")) / ...
    (max(xMIP, [], "all") - min(xMIP, [], "all"))
    # % Prepare figure
    # Create 2 figures, 3 plot wide
    figMIP = figure("Name", "MIP", "Position", [100, 100, 1000, 400])
    figRMS = figure("Name", "RMS", "Position", [100, 150, 1000, 400])
    # Set image as grayscale
    colormap(figMIP, "gray")
    colormap(figRMS, "gray")
    # Have a tile layout of 1 row and 3 columns, a bit smaller and higher
    # to make space for the confirm button
    tRMS = tiledlayout(figRMS, 1, 3)
    tMIP = tiledlayout(figMIP, 1, 3)
    set(tRMS, "Position", [0.1, 0.15, 0.8, 0.8])
    set(tMIP, "Position", [0.1, 0.15, 0.8, 0.8])
    # Put overall title for both figures
    title(tRMS, "RMS Values Summed Along Each Axis")
    title(tMIP, "MIP Values Summed Along Each Axis")
    # Add a confirmation button
    # TODO(matlab-line): uicontrol(figRMS, 'Style', 'pushbutton', ...
    "String", "Confirm Selection",
    # TODO(matlab-line): 'Units', 'normalized', 'Position', [0.4 0.04 0.2 0.06], ...
    # TODO(matlab-line): 'Callback', @(src, event) confirmSelection(figRMS));
    # TODO(matlab-line): uicontrol(figMIP, 'Style', 'pushbutton', ...
    "String", "Confirm Selection",
    # TODO(matlab-line): 'Units', 'normalized', 'Position', [0.4 0.04 0.2 0.06], ...
    # TODO(matlab-line): 'Callback', @(src, event) confirmSelection(figRMS));
    # Add Update on move option (checkbox)
    # TODO(matlab-line): cbxR = uicontrol(figRMS, 'Style', 'checkbox', ...
    "String", " Update on move",
    # TODO(matlab-line): 'Units', 'normalized', 'Position', [0.04 0.04 0.2 0.06]);
    # TODO(matlab-line): cbxM = uicontrol(figMIP, 'Style', 'checkbox', ...
    "String", " Update on move",
    # TODO(matlab-line): 'Units', 'normalized', 'Position', [0.04 0.04 0.2 0.06]);
    # Add text fields to show min and max values
    # Make them editable if autoFlag is false
    fStyle = "text"
    # TODO(matlab-control): if ~autoFlag
    fStyle = "edit"
    # XMin
    # TODO(matlab-line): eXMinR = uicontrol(figRMS, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.425 0.15 0.05 0.05], 'Tooltip', 'XMin of the mask', ...
    # TODO(matlab-line): 'String', num2str(boxPos(1,1)));
    # TODO(matlab-line): eXMinM = uicontrol(figMIP, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.425 0.15 0.05 0.05], 'Tooltip', 'XMin of the mask', ...
    # TODO(matlab-line): 'String', num2str(boxPos(1,1)));
    # XMax
    xMaxStr = num2str(boxPos(1,1) + boxPos(1,2))
    # TODO(matlab-line): eXMaxR = uicontrol(figRMS, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.525 0.15 0.05 0.05], 'Tooltip', 'XMax of the mask', ...
    # TODO(matlab-line): 'String', xMaxStr);
    # TODO(matlab-line): eXMaxM = uicontrol(figMIP, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.525 0.15 0.05 0.05], 'Tooltip', 'XMax of the mask', ...
    # TODO(matlab-line): 'String', xMaxStr);
    # YMin
    # TODO(matlab-line): eYMinR = uicontrol(figRMS, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.715 0.15 0.05 0.05], 'Tooltip', 'YMin of the mask', ...
    # TODO(matlab-line): 'String', num2str(boxPos(2,1)));
    # TODO(matlab-line): eYMinM = uicontrol(figMIP, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.715 0.15 0.05 0.05], 'Tooltip', 'YMin of the mask', ...
    # TODO(matlab-line): 'String', num2str(boxPos(2,1)));
    # YMax
    yMaxStr = num2str(boxPos(2,1) + boxPos(2,2))
    # TODO(matlab-line): eYMaxR = uicontrol(figRMS, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.815 0.15 0.05 0.05], 'Tooltip', 'YMax of the mask', ...
    # TODO(matlab-line): 'String', yMaxStr);
    # TODO(matlab-line): eYMaxM = uicontrol(figMIP, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.815 0.15 0.05 0.05], 'Tooltip', 'YMax of the mask', ...
    # TODO(matlab-line): 'String', yMaxStr);
    # ZMin
    # TODO(matlab-line): eZMinR = uicontrol(figRMS, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.135 0.15 0.05 0.05], 'Tooltip', 'ZMin of the mask', ...
    # TODO(matlab-line): 'String', num2str(boxPos(3,1)));
    # TODO(matlab-line): eZMinM = uicontrol(figMIP, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.135 0.15 0.05 0.05], 'Tooltip', 'ZMin of the mask', ...
    # TODO(matlab-line): 'String', num2str(boxPos(3,1)));
    # ZMax
    zMaxStr = num2str(boxPos(3,1) + boxPos(3,2))
    # TODO(matlab-line): eZMaxR = uicontrol(figRMS, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.235 0.15 0.05 0.05], 'Tooltip', 'ZMax of the mask', ...
    # TODO(matlab-line): 'String', zMaxStr);
    # TODO(matlab-line): eZMaxM = uicontrol(figMIP, 'Style', fStyle, 'Units', 'normalized', ...
    # TODO(matlab-line): 'Position', [0.235 0.15 0.05 0.05], 'Tooltip', 'ZMax of the mask', ...
    # TODO(matlab-line): 'String', zMaxStr);
    # % Plot data
    # Plot YZ view for RMS
    axRMSx = nexttile(tRMS)
    imagesc(xRMS)
    # TODO(matlab-line): axis image;
    xlabel("Z")
    ylabel("Y")
    title("Along X")
    # Create movable rectangle on image
    nPos = [boxPos(3,1), boxPos(2,1), boxPos(3,2), boxPos(2,2)]
    xRectR = images.roi.Rectangle(axRMSx,"Position", nPos)
    # Plot YZ view for MIP
    axMIPx = nexttile(tMIP)
    imagesc(xMIP)
    # TODO(matlab-line): axis image;
    xlabel("Z")
    ylabel("Y")
    title("Along X")
    # Create movable rectangle on image
    xRectM = images.roi.Rectangle(axMIPx,"Position", nPos)
    # Plot XZ view for RMS
    axRMSy = nexttile(tRMS)
    imagesc(yRMS)
    # TODO(matlab-line): axis image;
    xlabel("X")
    ylabel("Z")
    title("Along Y")
    # Create movable rectangle on image
    nPos = [boxPos(1,1), boxPos(3,1), boxPos(1,2), boxPos(3,2)]
    yRectR = images.roi.Rectangle(axRMSy,"Position", nPos)
    # Plot XZ view for MIP
    axMIPy = nexttile(tMIP)
    imagesc(yMIP)
    # TODO(matlab-line): axis image;
    xlabel("X")
    ylabel("Z")
    title("Along Y")
    # Create movable rectangle on image
    yRectM = images.roi.Rectangle(axMIPy,"Position", nPos)
    # Plot XY view for RMS
    axRMSz = nexttile(tRMS)
    imagesc(zRMS)
    # TODO(matlab-line): axis image;
    xlabel("Y")
    ylabel("X")
    title("Along Z")
    # Create movable rectangle on image
    nPos = [boxPos(2,1), boxPos(1,1), boxPos(2,2), boxPos(1,2)]
    zRectR = images.roi.Rectangle(axRMSz,"Position", nPos)
    # Plot XY view for MIP
    axMIPz = nexttile(tMIP)
    imagesc(zMIP)
    # TODO(matlab-line): axis image;
    xlabel("Y")
    ylabel("X")
    title("Along Z")
    # Create movable rectangle on image
    zRectM = images.roi.Rectangle(axMIPz,"Position", nPos)
    # % Create struct for Call back functions
    # TODO(matlab-line): components = struct(...
    "xRectR", xRectR,
    "yRectR", yRectR,
    "zRectR", zRectR,
    "xRectM", xRectM,
    "yRectM", yRectM,
    "zRectM", zRectM,
    "eXMinR", eXMinR,
    "eXMaxR", eXMaxR,
    "eYMinR", eYMinR,
    "eYMaxR", eYMaxR,
    "eZMinR", eZMinR,
    "eZMaxR", eZMaxR,
    "eXMinM", eXMinM,
    "eXMaxM", eXMaxM,
    "eYMinM", eYMinM,
    "eYMaxM", eYMaxM,
    "eZMinM", eZMinM,
    "eZMaxM", eZMaxM
    # TODO(matlab-line): );
    # % Add callback functions to edit fields if autoFlag is false
    # TODO(matlab-control): if ~autoFlag
    # TODO(matlab-line): eXMinR.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eXMaxR.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eYMinR.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eYMaxR.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eZMinR.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eZMaxR.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eXMinM.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eXMaxM.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eYMinM.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eYMaxM.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eZMinM.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # TODO(matlab-line): eZMaxM.Callback = @(src, evnt)updateBorder(src, components, N_u);
    # % Add listeners to rectangles
    # Listeners update boxes after changing them in the image and letting
    # go
    # TODO(matlab-line): el1 = addlistener(xRectR, "ROIMoved", @(src, evnt)updateBorder(src, ...
    # TODO(matlab-line): components, N_u));
    # TODO(matlab-line): el2 = addlistener(yRectR, "ROIMoved", @(src, evnt)updateBorder(src, ...
    # TODO(matlab-line): components, N_u));
    # TODO(matlab-line): el3 = addlistener(zRectR, "ROIMoved", @(src, evnt)updateBorder(src, ...
    # TODO(matlab-line): components, N_u));
    # TODO(matlab-line): el4 = addlistener(xRectM, "ROIMoved", @(src, evnt)updateBorder(src, ...
    # TODO(matlab-line): components, N_u));
    # TODO(matlab-line): el5 = addlistener(yRectM, "ROIMoved", @(src, evnt)updateBorder(src, ...
    # TODO(matlab-line): components, N_u));
    # TODO(matlab-line): el6 = addlistener(zRectM, "ROIMoved", @(src, evnt)updateBorder(src, ...
    # TODO(matlab-line): components, N_u));
    # Combine listeners into array for easier access
    listeners = [el1, el2, el3, el4, el5, el6]
    # Callback function for checkboxes to change the listeners between
    # updating the boxes on dragging or after changing
    # TODO(matlab-line): cbxR.Callback = @(src,evnt)updateListeners(src, cbxR, cbxM, listeners);
    # TODO(matlab-line): cbxM.Callback = @(src,evnt)updateListeners(src, cbxR, cbxM, listeners);
    # Turn position into coordinates
    # TODO(matlab-line): coordinates = [boxPos(1,1), boxPos(1,1) + boxPos(1,2);
    boxPos(2,1), boxPos(2,1) + boxPos(2,2)
    # TODO(matlab-line): boxPos(3,1), boxPos(3,1) + boxPos(3,2)];
    # Interupt code execution until Confirm is pressed or the RMS figure
    # closed
    uiwait(figRMS)
    # Update with new values if figures were not closed
    # TODO(matlab-control): if ishandle(figRMS) && ishandle(figMIP)
    coordinates = borderExtraction(components, N_u)
    delete(figRMS)
    delete(figMIP)
    # TODO(matlab-control): else
    # TODO(matlab-line): disp("Use confirm to use the new values. " + ...
    # TODO(matlab-line): "Don't close the figures!");
    # End function
    # TODO(matlab-line): return
    # % Nested functions
    return coordinates

def borderExtraction(comp, N_u):
    # This function extracts the border values, makes the rectangles
    # non interactive and returns the border values as a [3,2] array
    # comp is the structure containing all fields and rectangles
    # Get array size
    Nx = N_u(1)
    Ny = N_u(2)
    Nz = N_u(3)
    # Extract borders
    yMin = comp.xRectR.Vertices(1,2)
    yMax = comp.xRectR.Vertices(3,2)
    zMin = comp.xRectR.Vertices(1,1)
    zMax = comp.xRectR.Vertices(3,1)
    xMin = comp.yRectR.Vertices(1,1)
    xMax = comp.yRectR.Vertices(3,1)
    # Scale from [0.5, N_u + 0.5] to [1, N_u] and round
    xMin = round(1 + ((xMin - 0.5) / Nx) * (Nx - 1))
    xMax = round(1 + ((xMax - 0.5) / Nx) * (Nx - 1))
    yMin = round(1 + ((yMin - 0.5) / Ny) * (Ny - 1))
    yMax = round(1 + ((yMax - 0.5) / Ny) * (Ny - 1))
    zMin = round(1 + ((zMin - 0.5) / Nz) * (Nz - 1))
    zMax = round(1 + ((zMax - 0.5) / Nz) * (Nz - 1))
    # Make squares non interactive
    comp.xRectR.InteractionsAllowed = "none"
    comp.yRectR.InteractionsAllowed = "none"
    comp.zRectR.InteractionsAllowed = "none"
    comp.xRectM.InteractionsAllowed = "none"
    comp.yRectM.InteractionsAllowed = "none"
    comp.zRectM.InteractionsAllowed = "none"
    # TODO(matlab-line): coordinates = [xMin, xMax; yMin, yMax; zMin, zMax];
    return coordinates

def n(fig):
    # This function resumes the code execution
    # TODO(matlab-control): if ishandle(fig)
    # Resume execution
    uiresume(fig)
    return confirmSelectio

def r(src, comp, N_u):
    # This function updates all squares if one is modified. comp is the
    # structure containing all fields and rectangles.
    # Ensure the source of the event is actually a rectangle or edit
    # field
    # TODO(matlab-control): if isa(src,'images.roi.Rectangle')
    # Read position of updated square
    pos = src.Position
    # TODO(matlab-control): elseif isa(src, 'matlab.ui.control.UIControl')
    # Read new extrema
    ext = str2double(src.String)
    # If it is not a number it will be returned as nan
    # TODO(matlab-control): if isnan(ext)
    # Overwrite field with coordinates from rectangles
    updateFields(comp)
    # TODO(matlab-line): return
    # TODO(matlab-control): else
    # TODO(matlab-line): return
    # Read all squares position's (xRectR = xRectM sizewise)
    posX = comp.xRectR.Position
    posY = comp.yRectR.Position
    posZ = comp.zRectR.Position
    # TODO(matlab-control): switch src
    # TODO(matlab-control): case {comp.xRectR, comp.xRectM}
    # Update position lists with the new values
    posX = pos
    posY = [posY(1), pos(1), posY(3), pos(3)]
    posZ = [pos(2), posZ(2), pos(4), posZ(4)]
    # TODO(matlab-control): case {comp.yRectR, comp.yRectM}
    # Update position lists with the new values
    posX = [pos(2), posX(2), pos(4), posX(4)]
    posY = pos
    posZ = [posZ(1), pos(1), posZ(3), pos(3)]
    # TODO(matlab-control): case {comp.zRectR, comp.zRectM}
    # Update position lists with the new values
    posX = [posX(1), pos(1), posX(3), pos(3)]
    posY = [pos(2), posY(2), pos(4), posY(4)]
    posZ = pos
    # TODO(matlab-control): case {comp.eXMinR, comp.eXMinM}
    # Clip input to valid range
    ext = min(max(0.5, ext), N_u(1) + 0.5)
    # Update position lists with the new values
    posY = [ext, posY(2), posY(3) + posY(1) - ext, posY(4)]
    posZ = [posZ(1), ext, posZ(3), posZ(4) + posZ(2) - ext]
    # TODO(matlab-control): case {comp.eYMinR, comp.eYMinM}
    # Clip input to valid range
    ext = min(max(0.5, ext), N_u(2) + 0.5)
    # Update position lists with the new values
    posX = [posX(1), ext, posX(3), posX(4) + posX(2) - ext]
    posZ = [ext, posZ(2), posZ(3) + posZ(1) - ext, posZ(4)]
    # TODO(matlab-control): case {comp.eZMinR, comp.eZMinM}
    # Clip input to valid range
    ext = min(max(0.5, ext), N_u(3) + 0.5)
    # Update position lists with the new values
    posX = [ext, posX(2), posX(3) + posX(1) - ext, posX(4)]
    posY = [posY(1), ext, posY(3), posY(4) + posY(2) - ext]
    # TODO(matlab-control): case {comp.eXMaxR, comp.eXMaxM}
    # Clip input to valid range and calculate width
    ext = min(max(0.5, ext), N_u(1) + 0.5)
    ext = ext - posY(1)
    # Update position lists with the new values
    posY = [posY(1), posY(2), ext, posY(4)]
    posZ = [posZ(1), posZ(2), posZ(3), ext]
    # TODO(matlab-control): case {comp.eYMaxR, comp.eYMaxM}
    # Clip input to valid range and calculate width
    ext = min(max(0.5, ext), N_u(1) + 0.5)
    ext = ext - posZ(1)
    # Update position lists with the new values
    posX = [posX(1), posX(2), posX(3), ext]
    posZ = [posZ(1), posZ(2), ext, posZ(4)]
    # TODO(matlab-control): case {comp.eZMaxR, comp.eZMaxM}
    # Clip input to valid range and calculate width
    ext = min(max(0.5, ext), N_u(1) + 0.5)
    ext = ext - posX(1)
    # Update position lists with the new values
    posX = [posX(1), posX(2), ext, posX(4)]
    posY = [posY(1), posY(2), posY(3), ext]
    # TODO(matlab-control): otherwise
    # Override positions of all squares (M and R have the same
    # squares)
    comp.xRectR.Position = posX
    comp.yRectR.Position = posY
    comp.zRectR.Position = posZ
    comp.xRectM.Position = posX
    comp.yRectM.Position = posY
    comp.zRectM.Position = posZ
    # Update text fields
    updateFields(comp)
    return updateBorde

def s(comp):
    # This functions updates the fields with the value from the
    # rectangles. Comp is the structure containing all fields and
    # rectangles.
    comp.eXMinR.String = num2str(comp.yRectR.Vertices(1,1))
    comp.eXMaxR.String = num2str(comp.yRectR.Vertices(3,1))
    comp.eYMinR.String = num2str(comp.xRectR.Vertices(1,2))
    comp.eYMaxR.String = num2str(comp.xRectR.Vertices(3,2))
    comp.eZMinR.String = num2str(comp.xRectR.Vertices(1,1))
    comp.eZMaxR.String = num2str(comp.xRectR.Vertices(3,1))
    comp.eXMinM.String = comp.eXMinR.String
    comp.eXMaxM.String = comp.eXMaxR.String
    comp.eYMinM.String = comp.eYMinR.String
    comp.eYMaxM.String = comp.eYMaxR.String
    comp.eZMinM.String = comp.eZMinR.String
    comp.eZMaxM.String = comp.eZMaxR.String
    return updateField

def s(src, cbxR, cbxM, listeners):
    # This function changes the listener event between MovingROI and
    # ROIMoved depending on the checkbox
    # Change checkbox value of the one in the figure not clicked on
    # TODO(matlab-control): if strcmp(src.Parent.Name, 'RMS')
    cbxM.Value = src.Value
    # TODO(matlab-control): elseif strcmp(src.Parent.Name, 'MIP')
    cbxR.Value = src.Value
    # TODO(matlab-control): else
    # TODO(matlab-line): return
    # Choose event depending on the checkbox value
    # TODO(matlab-control): if src.Value == 1
    eventName = "MovingROI"
    # TODO(matlab-control): else
    eventName = "ROIMoved"
    # Update all listeners to listen to the new event
    # TODO(matlab-control): for i=1:size(listeners(:), 1)
    listeners(i).EventName = eventName
    return updateListener
