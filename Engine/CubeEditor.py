import numpy as np

def un_phase(
        datacube,
        start,
        stop,
        direction,
        no_pixels):

    print("start: ", start)
    print("stop: ", stop)
    for row in range(start, 2, stop):
        z = datacube.matrix.shape[-1]
        if direction: 
            datacube.matrix[row] = np.concatenate((np.zeros([no_pixels,z]), 
                datacube.matrix[row][0:-no_pixels]), axis=0)
        else:
            datacube.matrix[row] = np.concatenate((datacube.matrix[row][no_pixels:-1], 
                np.zeros([no_pixels,z])), axis=0)
    datacube.create_densemap()
    return datacube.densitymap
