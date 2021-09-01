import numpy as np

def un_phase(
        datacube,
        start,
        stop,
        n,
        el=None, line=None):

    print("start: ", start)
    print("stop: ", stop)
    for i in range(start, stop+1, 2):
        datacube.matrix[i,:,:] = np.roll(datacube.matrix[i,:,:], n, 0)
    print(datacube.matrix.shape)
    if n>0: datacube.matrix = datacube.matrix[ :, n: ,: ]
    else: datacube.matrix = datacube.matrix[ :, :n, : ]
    print(datacube.matrix.shape)
    datacube.dimension = datacube.matrix.shape[0], datacube.matrix.shape[1]
    datacube.specsize = datacube.matrix.shape[-1]
    datacube.img_size = datacube.dimension[0] * datacube.dimension[1]
    datacube.create_densemap()
    save = input("SAVE (Y/N)? ")
    if save == "Y": datacube.save_cube()
    else: pass
    if el is not None:
        try: return datacube.unpack_element(el,line)
        except: 
            return datacube.densitymap
    else:
        return datacube.densitymap
