import numpy as np
import matplotlib.pyplot as plt

def bmFieldPlot2_noImage(arg_x, arg_y, arg_vx, arg_vy, argSize, autoScaleFlag, myNorm_max):
    # argin initial
    argSize = np.array(argSize).reshape(-1)
    argSize = argSize[:2]
    nArrow = 20
    arg_x = np.reshape(arg_x, argSize)
    arg_y = np.reshape(arg_y, argSize)
    arg_vx = np.reshape(arg_vx, argSize)
    arg_vy = np.reshape(arg_vy, argSize)

    # internal variables
    x, y, vx, vy = None, None, None, None
    mySize = argSize
    transpose_flag = False

    # function to reset field
    def reset_field():
        nonlocal x, y, vx, vy, mySize, x_label, y_label, transpose_string
        x = arg_x.copy()
        y = arg_y.copy()
        vx = arg_vx.copy()
        vy = arg_vy.copy()
        mySize = argSize.copy()
        x_label = 'X'
        y_label = 'Y'
        transpose_string = 'off'

    # function to reduce field
    def reduce_field():
        nonlocal x, y, vx, vy
        myNorm = np.sqrt(vx**2 + vy**2)
        myNorm[np.isinf(myNorm)] = 0
        myNorm[np.isnan(myNorm)] = 0
        vx[myNorm > myNorm_max] = 0
        vy[myNorm > myNorm_max] = 0
        nPart_1 = int(np.fix(argSize[0] / (nArrow+1))) + 1
        nPart_2 = int(np.fix(argSize[1] / (nArrow+1))) + 1
        x = x[::nPart_1, ::nPart_2]
        y = y[::nPart_1, ::nPart_2]
        vx = vx[::nPart_1, ::nPart_2]
        vy = vy[::nPart_1, ::nPart_2]

    # function to transpose field
    def transpose_field():
        nonlocal x, y, vx, vy, mySize, x_label, y_label, transpose_string
        if transpose_flag:
            x, y = y, x
            vx, vy = vy, vx
            x = x.T
            y = y.T
            vx = vx.T
            vy = vy.T
            mySize = mySize[::-1]
            x_label, y_label = y_label, x_label
            transpose_string = 'on'

    # update field
    def update_field():
        reset_field()
        reduce_field()
        transpose_field()

    # initial update
    update_field()

    # create figure
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('bmFieldPlot2')
    # event handling functions
    controlFlag, shiftFlag, escFlag = 0, 0, 0
    reverse_flag, mirror_flag = False, False
    reverse_string, transpose_string, mirror_string = 'off', 'off', 'off'
    x_label, y_label = 'X', 'Y'

    def on_key(event):
        nonlocal controlFlag, shiftFlag, escFlag, autoScaleFlag, myNorm_max, mirror_flag, mirror_string
        if event.key == 'control':
            controlFlag = 1
        elif event.key == 'shift':
            shiftFlag = 1
        elif event.key == 'escape':
            escFlag = 1
        elif event.key == 'a':
            if controlFlag and shiftFlag:
                autoScaleFlag = not autoScaleFlag
                refresh()
                shiftFlag = 0
                controlFlag = 0
        elif event.key == 'n':
            if controlFlag and shiftFlag:
                myNorm_max = np.max(np.sqrt(vx**2 + vy**2))
                update_field()
                refresh()
                controlFlag = 0
                shiftFlag = 0
        elif event.key == 'm':
            if controlFlag and shiftFlag:
                mirror_flag = not mirror_flag
                mirror_string = 'on' if mirror_flag else 'off'
                refresh()
                controlFlag = 0
                shiftFlag = 0

    def on_key_release(event):
        nonlocal controlFlag, shiftFlag, escFlag
        if event.key == 'control':
            controlFlag = 0
        elif event.key == 'shift':
            shiftFlag = 0
        elif event.key == 'escape':
            escFlag = 0

    fig.canvas.mpl_connect('key_press_event', on_key)
    fig.canvas.mpl_connect('key_release_event', on_key_release)

    def refresh():
        fig.clear()
        ax = fig.add_subplot(111)
        ax.quiver(y, x, vy, vx, angles='xy', scale_units='xy', scale=1, width=0.003, color='black')
        ax.set_aspect('equal')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        if mirror_flag:
            ax.set_xlim(ax.get_xlim()[::-1])
        else:
            ax.set_xlim(ax.get_xlim())
        if reverse_flag:
            ax.set_ylim(ax.get_ylim())
        else:
            ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_title(f'Autoscale : {int(autoScaleFlag)}, normMax : {myNorm_max}; reverse : {reverse_string}; transpose : {transpose_string}')
        ax.set_xlabel(y_label)
        ax.set_ylabel(x_label)

    # initial refresh
    refresh()
