# j3d-animation-editor
editor for a variety of j3d animation files. still a work in progress. any bugs can be reported to me on discord tarsa#8462.

# filetypes supported:
.btk: texture srt key </br>
.brk: tev register key (integer values only)</br>
.bpk: color key (integer values only)</br>
.bck: joint key </br>
.bca: joint all </br>
.blk: cluster key </br>
.bla: cluster all </br>
.btp: texture palette all (integer values only)</br>

# features:
tangent type 0 and 1 saving, with automatic linear tangent generation </br>
conversion between key and all frame animations, where applicable, and automatic interpolation for all frame animations </br>
* for .bck files, the ability to change between smooth and linear tangent interpolation
ability to import .anim files as .bck </br>

# run from source code:
you need the latest version of python and pyqt5. make sure that the version of python that you are using has pyqt5 installed, or you will get a module not found error. </br>
i will have an .exe as soon as i can be confident that most of the bugs are taken out.

# special thanks:
a lot of this code is stolen / based off of yoshi2's .btk and .brk conversion programs. </br>
thomasjamesart for the linear/smooth graphics




