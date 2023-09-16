#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Thanks to the help of spicyjpeg

import numpy, requests
from PIL import Image

image = Image.open("texture.png")
image.load()

# NDR008" Easy swap to palette mode and resize :)
image = image.convert('RGBA').convert('P', colors=3)
image = image.resize((256,256))

if image.mode != "P":
	raise RuntimeError("texture is not in indexed color format")

## Palette conversion

# Analyze the palette's raw size to determine how many entries it contains. (If
# there's a better/more efficient way to get the number of colors in a palette,
# I don't know about it.)
colorSize = { "RGB": 3, "RGBA": 4 }[image.palette.mode]
palette   = image.palette.tobytes()
numColors = len(palette) // colorSize

# Extract the palette into a 2D array; Pillow makes this harder than it should
# be. The array is then converted to 16bit to make sure there's enough room for
# the large values temporarily produced by the 15bpp conversion (see below).
paletteData = numpy \
	.frombuffer(palette, numpy.uint8) \
	.reshape(( numColors, colorSize )) \
	.astype(numpy.uint16)

# For each RGB channel, convert it from 24bpp (0-255) to 15bpp (0-31) by
# adjusting its levels and right-shifting it, then recombine the channels into
# a single 16bpp 2D array which is going to be uploaded to the GPU as a 16xN
# "image".
# https://github.com/stenzek/duckstation/blob/master/src/core/gpu_types.h#L135
red   = ((paletteData[:, 0] * 249) + 1014) >> 11
green = ((paletteData[:, 1] * 249) + 1014) >> 11
blue  = ((paletteData[:, 2] * 249) + 1014) >> 11

paletteData = red | (green << 5) | (blue << 10)
paletteData = paletteData.reshape(( 1, numColors ))

## Texture conversion

# Get the image data as a 2D array of indices into the palette and ensure the
# width of this array is even, as the GPU requires VRAM uploads to be done in
# 16bit units (see upload()).
imageData = numpy.asarray(image, numpy.uint8)

if imageData.shape[1] % 2:
	padding   = numpy.zeros(imageData.shape[0], numpy.uint8)
	imageData = numpy.c_[ imageData, padding ]

# If the texture is 4bpp, pack two pixels into each byte. This is done by
# splitting the array into vertically interlaced odd/even columns and binary
# OR-ing them after relocating the odd columns' values to the upper nibble. As
# this operation halves the width of the image, another alignment check must be
# performed afterwards.
# https://numpy.org/doc/stable/user/basics.indexing.html#other-indexing-options
if numColors <= 16:
	imageData = imageData[:, 0::2] | (imageData[:, 1::2] << 4)

	if imageData.shape[1] % 2:
		padding   = numpy.zeros(imageData.shape[0], numpy.uint8)
		imageData = numpy.c_[ imageData, padding ]

## Uploading

def upload(x, y, numpyArray):
	requests.post(
		"http://localhost:8080/api/v1/gpu/vram/raw",
		data   = numpyArray.tobytes(),
		params = {
			"x":      str(x),
			"y":      str(y),
			# The width is always in 16bit units.
			"width":  str(numpyArray.shape[1] // 2 * numpyArray.itemsize),
			"height": str(numpyArray.shape[0])
		}
	)
 
AllFlag = True
if AllFlag:

    imageData2 = imageData
    for i in range(448, 800, 128):
        upload(i, 0, imageData2)
        upload(i, 256, imageData2)
    for i in range(640, 1024-127, 128):
        upload(i, 0, imageData)
        upload(i, 256, imageData)
else:

    for i in range(640, 1024-127, 128):
        upload(i, 0, imageData)
        upload(i, 256, imageData)
