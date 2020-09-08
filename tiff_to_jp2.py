import os

from pathlib import Path


input = "/Users/pgalligan/Desktop/image_compression/masters/"
tmp = "/Users/pgalligan/Desktop/image_compression/tmp/"
output = "/Users/pgalligan/Desktop/image_compression/derivatives/"

for file in os.listdir(input):
    input_file = input + file
    fname = file.split(".")[0]
    output_file = output + fname + ".jp2"
    os.system("opj_compress -i " + input_file + " -o " + output_file + " -r 1.5 -n 7 -c '[256,256],[256,256],[128,128]' -b '64,64' -p RPCL -SOP")
