# j3d-animation-editor
editor for a variety of j3d animation files. still a work in progress. any bugs can be reported to me on discord tarsa#8462.

# filetypes supported:
* .btk: texture srt key
* .brk: tev register key (integer values only)
* .bpk: color key (integer values only)
* .bck: joint key 
* .bca: joint all 
* .blk: cluster key 
* .bla: cluster all 
* .btp: texture palette all (integer values only)

can also import .anim and .fbx, both as .bck

# additional features:
* tangent type 0 and 1 saving, with automatic linear tangent generation
* conversion between key and all frame animations, where applicable, and automatic interpolation for all frame animations
* for .bck files, the ability to change between smooth and linear tangent interpolation
* drag n drop for all supported filetypes

# run from source code:
The source code requires PyQt5 and the Autodesk Python FBX SDK to be installed. PyQt5 can be installed by 
`pip install PyQt5`
The FBX SDK can be installed by
`pip --verbose install fbxsdkpy --extra-index-url https://gitlab.inria.fr/api/v4/projects/18692/packages/pypi/simple` 
More details about the FBX SDK installation can be found [here](https://gitlab.inria.fr/radili/fbxsdk_python).

# special thanks:
* Yoshi2, from whom a lot of the animation reading / writing code and gui code is adapted
* NoClip.Website, which provided guidance on how to read/write certain file types (.brk, .bpk, .bva)