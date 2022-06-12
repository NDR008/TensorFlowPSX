# -*- coding: utf-8 -*-
# (C) 2022 spicyjpeg

import os, logging

import numpy
from PIL      import Image
from ._util   import blitArray
from ._native import quantizeImage, toPS1ColorSpace, toPS1ColorSpace2D

## Image wrapper class

TEXPAGE_WIDTH  =  64
TEXPAGE_HEIGHT = 256

class ImageWrapper:
	"""
	Wrapper class for converted images and palettes, holding placement data.
	"""

	def __init__(self, data, palette = None, margin = ( 0, 0 ), flipMode = None):
		self.data     = data
		self.palette  = palette
		self.margin   = margin
		self.flipMode = flipMode

		self.height, self.width = data.shape

		# These attributes are set by the packing functions and used by the
		# blit*() methods.
		self.page        = None
		self.x,  self.y  = None, None
		self.px, self.py = None, None
		self.flip        = False

		#if data.dtype.itemsize == 2:
		if palette is None:
			self.bpp = 16
		else:
			self.bpp = 4 if (palette.size <= 32) else 8

	def getPackedSize(self, flip = False):
		scale = 16 // self.bpp

		if flip:
			return (self.height + scale - 1) // scale, self.width
		else:
			return (self.width + scale - 1) // scale, self.height

	def getPathologicalMult(self):
		return (self.width * self.height) * \
			max(self.width, self.height) / min(self.width, self.height)

	def canBePlaced(self, x, y, flip = False):
		boundaryX     = x + TEXPAGE_WIDTH - (x % TEXPAGE_WIDTH)
		boundaryY     = y + TEXPAGE_HEIGHT - (y % TEXPAGE_HEIGHT)
		width, height = self.getPackedSize(flip)

		return ((x + width) <= boundaryX and (y + height) <= boundaryY)

	def getHash(self):
		return hash(self.data.tobytes())

	def getPaletteHash(self):
		# Drop the least significant bit of each color. As the hash is used for
		# deduplication, this means palettes that are "similar" enough to other
		# palettes will be removed from the atlas.
		data = self.palette.view(numpy.uint16) & 0xfbde

		return hash(data.tobytes())

	def toInterlaced(self, field = 0):
		# https://numpy.org/doc/stable/user/basics.indexing.html#other-indexing-options
		data = self.data[field::2, :]

		# Note that the packing/blitting attributes are *not* preserved and the
		# palette object is not duplicated.
		return ImageWrapper(data, self.palette, self.margin)

	def blit(self, atlas):
		if self.flip:
			data = numpy.rot90(self.data)
		else:
			data = self.data

		# Cast the rotated image to a byte array (this is necessary for 16bpp).
		data = numpy.ascontiguousarray(data).view(numpy.uint8)

		# "Compress" 4bpp images by packing two pixels into each byte (NumPy
		# has no native support for 4-bit arrays, so a full byte is used for
		# each pixel even for <=16 colors). This is done by splitting the array
		# into vertically interlaced odd/even columns (after padding to ensure
		# the width is a multiple of 2) and binary OR-ing them after relocating
		# the odd columns' values to the upper nibble.
		if self.bpp == 4:
			if data.shape[1] % 2:
				data = numpy.c_[
					data,
					numpy.zeros(data.shape[0], numpy.uint8)
				]

			data = data[:, 0::2] | (data[:, 1::2] << 4)

		blitArray(data, atlas, ( self.y, self.x * 2 ))

	def blitPalette(self, atlas):
		width = 2 ** (self.bpp + 1)
		data  = self.palette.view(numpy.uint8).reshape(( 1, width ))

		blitArray(data, atlas, ( self.py, self.px * width ))

## Image downscaling and quantization

def _getMonoPalette(numSolid, numAlpha):
	return numpy.r_[
		numpy.linspace(
			( 0x00, 0x00, 0x00, 0xff ),
			( 0xff, 0xff, 0xff, 0xff ),
			numSolid,
			dtype = numpy.uint8
		),
		numpy.linspace(
			( 0x00, 0x00, 0x00, 0x80 ),
			( 0xff, 0xff, 0xff, 0x80 ),
			numAlpha,
			dtype = numpy.uint8
		),
		numpy.zeros(( 1, 4 ), numpy.uint8)
	]

PALETTES = {
	"auto":        None,
	"mono4":       _getMonoPalette( 15,   0), # 16 solid shades of gray
	"monoalpha4":  _getMonoPalette(  8,   7), # 8 solid shades + 7 semi-transparent shades
	"mono8":       _getMonoPalette(255,   0), # 256 solid shades of gray
	"monoalpha8":  _getMonoPalette(128, 127)  # 128 solid shades + 127 semi-transparent shades
}
SCALE_MODES = {
	"nearest":  Image.NEAREST,
	"lanczos":  Image.LANCZOS,
	"bilinear": Image.BILINEAR,
	"bicubic":  Image.BICUBIC,
	"box":      Image.BOX,
	"hamming":  Image.HAMMING
}

def convertImage(image, options):
	"""
	Downscales and optionally quantizes a PIL image using the given dict of
	options. Returns an ImageWrapper object.
	"""

	name       = options["name"]
	crop       = map(int, options["crop"])
	scale      = float(options["scale"])
	bpp        = int(options["bpp"])
	palette    = PALETTES[options["palette"].lower()]
	dither     = float(options["dither"])
	scaleMode  = SCALE_MODES[options["scalemode"].lower()]
	alphaRange = map(int, options["alpharange"])
	blackValue = int(options["blackvalue"])
	flipMode   = options["flipmode"].lower()

	# Crop the image if necessary. Note that cropping is done before rescaling.
	x, y, width, height = crop
	_image = image.crop((
		x,
		y,
		min(x + width,  image.width),
		min(y + height, image.height)
	))

	# Throw an error if attempting to rescale an image that already has a
	# palette, since indexed color images can only be scaled using nearest
	# neighbor interpolation (and it generally doesn't make sense to do so).
	if scale != 1.0:
		if image.mode == "P":
			raise RuntimeError(f"({name}) can't rescale indexed image")

		_image = _image.resize((
			int(_image.width  * scale),
			int(_image.height * scale)
		), scaleMode)

	# Trim any empty space around the image (but save the number of pixels
	# trimmed, so the margin can be restored on the PS1 side when drawing the
	# image).
	margin = _image.getbbox()
	if margin is None:
		raise RuntimeError(f"({name}) image is empty")

	_image    = _image.crop(margin)
	data      = None
	numColors = 2 ** bpp

	if bpp == 16:
		if _image.mode == "P":
			logging.warning(f"({name}) converting indexed image to 16bpp")

		data = toPS1ColorSpace2D(
			numpy.array(_image.convert("RGBA"), numpy.uint8),
			*alphaRange,
			blackValue
		)

		return ImageWrapper(data, None, margin[0:2])

	# If the image is in a suitable indexed format already, generate a 16x1 or
	# 256x1 bitmap out of its palette.
	if _image.mode == "P":
		if palette is not None:
			logging.warning(f"({name}) re-quantizing indexed image to apply custom palette")
		else:
			# Calculate how many entries there are in the palette. Pillow makes
			# this non-trival for some reason.
			paletteData = _image.palette.tobytes()
			_numColors  = {
				"RGB":  len(paletteData) // 3,
				"RGBA": len(paletteData) // 4,
				"L":    len(paletteData)
			}[_image.palette.mode]

			# If the number of entries is low enough, convert the palette to
			# RGBA format (by generating an Nx1 bitmap out of it) and from
			# there to a NumPy array.
			if _numColors > numColors:
				logging.warning(f"({name}) re-quantizing indexed image due to existing palette being too large")
			else:
				logging.debug(f"({name}) image has a valid {_numColors}-color palette, skipping quantization")

				_palette = Image.frombytes(
					_image.palette.mode,
					( _numColors, 1 ),
					paletteData
				)
				_palette = numpy.array(_palette.convert("RGBA"), numpy.uint8)
				_palette = _palette.reshape(( _numColors, 4 ))
				data     = numpy.array(_image, numpy.uint8)

	# If the image is not indexed color or the palette is incompatible with the
	# desidered format (see above), quantize the image.
	# NOTE: I didn't use Pillow's built-in quantization functions as they are
	# crap and don't support RGBA images/palettes properly. Using libimagequant
	# manually (via the _native DLL) yields much better results.
	if data is None:
		_palette, data = quantizeImage(
			numpy.array(_image.convert("RGBA"), numpy.uint8),
			numColors,
			palette,
			5, # PS1 color depth (15bpp = 5bpp per channel)
			dither
		)

	# Pad the palette with null entries.
	_palette = numpy.r_[
		_palette,
		numpy.zeros(( numColors - _palette.shape[0], 4 ), numpy.uint8)
	]

	# Sort the palette (inaccurately) by the average brightness of each color
	# and remap the pixel data accordingly, then perform color space conversion
	# on the palette.
	mapping  = _palette.view(numpy.uint32).flatten().argsort()
	data     = mapping.argsort().astype(numpy.uint8)[data]
	_palette = toPS1ColorSpace(_palette[mapping], *alphaRange, blackValue)

	return ImageWrapper(data, _palette, margin[0:2], flipMode)

## Texture/palette packer

# The algorithm is based on the one implemented by the rectpack2D library, with
# several PS1-specific optimization tricks added.
# https://github.com/TeamHypersomnia/rectpack2D

# Sorting doesn't take the images' color depths and packed widths into account.
SORT_ORDERS = {
	"area":         lambda image: image.width * image.height,
	"perimeter":    lambda image: (image.width + image.height) * 2,
	"longest":      lambda image: max(image.width, image.height),
	"width":        lambda image: image.width,
	"height":       lambda image: image.height,
	"pathological": lambda image: image.getPathologicalMult()
}
FLIP_MODES = {
	"none":            ( False, ),
	"flip":            ( True, ),
	"preferunflipped": ( False, True ),
	"preferflipped":   ( True, False )
}

def _attemptPacking(images, atlasWidth, atlasHeight, altSplit):
	# Start with a single empty space representing the entire atlas.
	spaces = [
		( 0, 0, atlasWidth, atlasHeight )
	]

	area   = 0
	packed = 0
	hashes = {} # hash: image

	# Remove duplicate images by skipping an image if its hash matches the one
	# of another image. Note that hashing relies on palettes being sorted with
	# the same criteria across all images.
	for image in images:
		if (_hash := image.getHash()) in hashes:
			_image = hashes[_hash]

			image.x    = _image.x
			image.y    = _image.y
			image.flip = _image.flip
			packed    += 1
			continue

		image.x = None
		image.y = None

		# Try placing the texture in either orientation. As the image's actual
		# width in the texture page depends on its color depth (i.e. indexed
		# color images are always squished horizontally), we have to calculate
		# it in either case.
		for flip in FLIP_MODES[image.flipMode]:
			width, height = image.getPackedSize(flip)

			# Find the smallest available space the image can be placed into.
			# This implementation is slightly different from rectpack2D as it
			# always goes through all empty spaces, which is inefficient but
			# might lead to better packing ratios, and ensures images are not
			# placed in the middle of the atlas (where they'd be split across
			# two different PS1 texture pages).
			lowestIndex  = None
			lowestMargin = 1e10

			for index, space in enumerate(spaces):
				x, y, maxWidth, maxHeight = space
				if width > maxWidth or height > maxHeight:
					continue
				if not image.canBePlaced(x, y, flip):
					continue

				margin = (maxWidth * maxHeight) - (width * height)
				if margin < lowestMargin:
					lowestIndex  = index
					lowestMargin = margin

			# If at least one suitable empty space was found, remove it from
			# the list and possibly replace with two smaller rectangles
			# representing the empty margins remaining after placement.
			if lowestIndex is None:
				continue

			x, y, maxWidth, maxHeight = spaces.pop(lowestIndex)

			# There are quite a few potential cases here:
			# - Both dimensions match the available space's dimensions
			#   => add no new empty spaces
			# - Only one dimension equals the space's respective dimension
			#   => add a single space
			# - Both dimensions are smaller, and the image is not square
			#   => add two spaces, trying to keep both as close to a square as
			#      possible by using the image's longest side as a splitting
			#      axis (or the shortest side if altSplit = True)
			if width < maxWidth or height < maxHeight:
				marginX = maxWidth  - width
				marginY = maxHeight - height

				if altSplit != (maxWidth * marginY < maxHeight * marginX):
					# Split along bottom side (horizontally)
					spaces.insert(lowestIndex,
						( x, y + height, maxWidth, marginY )
					)
					if width < maxWidth: spaces.insert(lowestIndex,
						( x + width, y, marginX, height )
					)
				else:
					# Split along right side (vertically)
					spaces.append(
						( x + width, y, marginX, maxHeight )
					)
					if height < maxHeight: spaces.insert(lowestIndex,
						( x, y + height, width, marginY )
					)

			image.x       = x
			image.y       = y
			image.flip    = flip
			hashes[_hash] = image
			area         += width * height
			packed       += 1
			break

	return area, packed

def packImages(images, atlasWidth, atlasHeight, discardStep, trySplits):
	"""
	Takes a list of ImageWrapper objects and packs them in an atlas, setting
	their x, y and flip attributes (or leaving them set to None in case of
	failure). Returns a ( totalArea, numPackedImages ) tuple.
	"""

	splitModes  = ( False, True ) if trySplits else ( False, )
	highestArgs = None
	highestArea = 0

	for reverse in ( True, False ):
		for orderName, order in SORT_ORDERS.items():
			_images = sorted(images, key = order, reverse = reverse)

			newWidth  = atlasWidth
			newHeight = atlasHeight
			packed    = None
			step      = min(atlasWidth, atlasHeight) // 2

			while step >= discardStep:
				# Try decreasing the width, height and both, and calculate the
				# packing ratio for each case.
				packResults = [] # packed, ratio
				candidates  = (
					( newWidth - step, newHeight - step ),
					( newWidth - step, newHeight ),
					( newWidth,        newHeight - step ),
					( newWidth,        newHeight )
				)

				for altSplit in splitModes:
					for width, height in candidates:
						packResults.append(
							_attemptPacking(_images, width, height, altSplit)
						)

				# Find the case that led to the highest packing area. Stop once
				# the atlas can't be further shrunk down nor needs to be
				# enlarged, or if we're trying to exceed the maximum size.
				bestResult   = max(packResults)
				bestIndex    = packResults.index(bestResult) % 4
				area, packed = bestResult

				# If all attempts to shrink the size led to an increase in
				# failures, increase both dimensions by the current step and
				# try shrinking again; otherwise, accept the new sizes and
				# continue shrinking. Stop once all images have been packed or
				# if we're trying to exceed the maximum atlas size.
				if bestIndex == 3 or bestIndex == 7:
					if packed == len(images):
						logging.debug(f"sort by {orderName} rev={reverse}: all images packed, aborting search")
						break

					if (
						(newWidth + step) > atlasWidth or
						(newHeight + step) > atlasHeight
					):
						logging.debug(f"sort by {orderName} rev={reverse}: can't extend atlas, aborting search")
						break

					newWidth  += step
					newHeight += step
				else:
					newWidth, newHeight = candidates[bestIndex % 4]

				step //= 2

			logging.debug(f"sort by {orderName} rev={reverse}: {newWidth}x{newHeight}, {packed} images packed")

			if area > highestArea:
				highestArgs = _images, newWidth, newHeight, (bestIndex > 3)
				highestArea = area

				# Stop trying other sorting algorithms if all images have been
				# packed.
				if packed == len(images):
					break

	if not highestArea:
		return 0, 0

	return _attemptPacking(*highestArgs)

def packPalettes(images, atlasWidth, atlasHeight):
	"""
	Takes an iterable of ImageWrapper objects and returns a
	( newAtlas, freeHeight ) tuple containing an atlas with all 16-color
	palettes placed at the bottom. The px and py attributes of each image are
	also set to point to their respective palettes.
	"""

	_images = []
	hashes  = {} # hash: image
	px, py  = 0, atlasHeight - 1

	# Remove duplicate/similar palettes by comparing their hashes. The LSB of
	# each RGB value is masked off (see getPaletteHash()) to remove palettes
	# that are close enough to another palette. As usual the palettes have to
	# be sorted ahead of time for this to work.
	for image in images:
		if image.bpp != 4:
			continue

		if (_hash := image.getPaletteHash()) in hashes:
			_image = hashes[_hash]

			image.px = _image.px
			image.py = _image.py
			continue

		image.px      = px
		image.py      = py
		hashes[_hash] = image
		_images.append(image)

		px += 1
		py -= px // (atlasWidth // 16)
		px %= (atlasWidth // 16)

	if not _images:
		return

	atlas = numpy.zeros(( atlasHeight, atlasWidth * 2 ), numpy.uint8)
	for image in _images:
		image.blitPalette(atlas)

	logging.debug(f"packed {len(_images)} palettes")
	return atlas, py + (0 if px else 1)

## PS1 texture atlas packing and output

def buildTexpages(images, margin = 0, discardStep = 1, trySplits = False):
	_images = images
	index   = 0

	# Gather all 16-color palettes and pack them at the bottom of the first
	# atlas. Empty rows are also reserved for 256-color palettes, which are
	# allocated at runtime. The packer thus treats atlases as 128x254x16bpp
	# rather than 256x255x8bpp.
	atlas, freeHeight = packPalettes(
		_images, TEXPAGE_WIDTH, TEXPAGE_HEIGHT - margin
	)

	while _images:
		area, packed = packImages(
			_images, TEXPAGE_WIDTH, freeHeight, discardStep, trySplits
		)
		if not packed:
			raise RuntimeError("can't pack any further, one or more images might be larger than atlas size")

		failed = []

		for image in _images:
			if image.x is None:
				failed.append(image)
				continue

			image.page = index
			image.blit(atlas)

		ratio = 100 * area / (TEXPAGE_WIDTH * freeHeight)
		logging.info(f"generated atlas {index} ({ratio:4.1f}% packing ratio, {len(failed)} images left)")
		yield atlas

		# Create a new empty atlas for the remaining images.
		freeHeight = TEXPAGE_HEIGHT - margin
		atlas      = numpy.zeros(( freeHeight, TEXPAGE_WIDTH * 2 ), numpy.uint8)
		_images    = failed
		index     += 1
