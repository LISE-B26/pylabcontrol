import glob
import os


"""
this is still under development
the idea is to have a script that convets a series of images into a movie
"""


ffmpeq_path = 'C:\\ffmpeg\\bin'

tag = 'image_'
path = 'Z:\\Lab\\Cantilever\\Measurements\\20160617_Test_Homemade_Piezo\\160617-11_31_28_test_piezo\\image'
file_type = '.jpg'
image_files = glob.glob('{:s}/*{:s}*{}'.format(path, tag, file_type))

# command = '{:s}\\ffmpeg.exe '.format(ffmpeq_path)
# command = '{:s}\\ffmpeg -framerate 1 -pattern_type glob -i \'{:s}\\{:s}*.jpg\' -c:v libx264 out.mp4'.format(ffmpeq_path,path, tag)

command = '{:s}\\ffmpeg -framerate 1 -i {:s}\\{:s}%03d.jpg -c:v libx264 -r 30 -pix_fmt yuv420p out3.mp4'.format(ffmpeq_path,path, tag)
print(command)
os.system(command )

