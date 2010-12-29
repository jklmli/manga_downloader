# Copyright (C) 2010  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from PIL import Image, ImageDraw


class ImageFlags:
    Orient = 1 << 0
    Resize = 1 << 1
    Frame = 1 << 2
    Quantize = 1 << 3


class KindleData:
    Palette4 = [
        0x00, 0x00, 0x00,
        0x55, 0x55, 0x55,
        0xaa, 0xaa, 0xaa,
        0xff, 0xff, 0xff
    ]

    Palette15 = [
        0x00, 0x00, 0x00,
        0x11, 0x11, 0x11,
        0x22, 0x22, 0x22,
        0x33, 0x33, 0x33,
        0x44, 0x44, 0x44,
        0x55, 0x55, 0x55,
        0x66, 0x66, 0x66,
        0x77, 0x77, 0x77,
        0x88, 0x88, 0x88,
        0x99, 0x99, 0x99,
        0xaa, 0xaa, 0xaa,
        0xbb, 0xbb, 0xbb,
        0xcc, 0xcc, 0xcc,
        0xdd, 0xdd, 0xdd,
        0xff, 0xff, 0xff,
    ]

    Profiles = {
        'Kindle 1': ((600, 800), Palette4),
        'Kindle 2': ((600, 800), Palette15),
        'Kindle 3': ((600, 800), Palette15),
        'Kindle DX': ((824, 1200), Palette15),
        'Kindle DXG': ((824, 1200), Palette15)
    }


def quantizeImage(image, palette):
    colors = len(palette) / 3
    if colors < 256:
        palette = palette + palette[:3] * (256 - colors)

    palImg = Image.new('P', (1, 1))
    palImg.putpalette(palette)

    return image.quantize(palette=palImg)


def resizeImage(image, size):
    widthDev, heightDev = size
    widthImg, heightImg = image.size

    if widthImg <= widthDev and heightImg <= heightDev:
        return image

    ratioImg = float(widthImg) / float(heightImg)
    ratioWidth = float(widthImg) / float(widthDev)
    ratioHeight = float(heightImg) / float(heightDev)

    if ratioWidth > ratioHeight:
        widthImg = widthDev
        heightImg = int(widthDev / ratioImg)
    elif ratioWidth < ratioHeight:
        heightImg = heightDev
        widthImg = int(heightDev * ratioImg)
    else:
        widthImg, heightImg = size

    return image.resize((widthImg, heightImg), Image.ANTIALIAS)


def formatImage(image):
    if image.mode == 'RGB':
        return image
    return image.convert('RGB')


def orientImage(image, size):
    widthDev, heightDev = size
    widthImg, heightImg = image.size

    if (widthImg > heightImg) != (widthDev > heightDev):
        return image.rotate(90, Image.BICUBIC, True)

    return image


def frameImage(image, foreground, background, size):
    widthDev, heightDev = size
    widthImg, heightImg = image.size

    pastePt = (
        max(0, (widthDev - widthImg) / 2),
        max(0, (heightDev - heightImg) / 2)
    )

    corner1 = (
        pastePt[0] - 1,
        pastePt[1] - 1
    )

    corner2 = (
        pastePt[0] + widthImg + 1,
        pastePt[1] + heightImg + 1
    )

    imageBg = Image.new(image.mode, size, background)
    imageBg.paste(image, pastePt)

    draw = ImageDraw.Draw(imageBg)
    draw.rectangle([corner1, corner2], outline=foreground)

    return imageBg


def convertImage(source, target, device, flags):
    try:
        size, palette = KindleData.Profiles[device]
    except KeyError:
        raise RuntimeError('Unexpected output device %s' % device)

    try:
   	    image = Image.open(source)
    except IOError:
        raise RuntimeError('Cannot read image file %s' % source)

    image = formatImage(image)
    if flags & ImageFlags.Orient:
        image = orientImage(image, size)
    if flags & ImageFlags.Resize:
        image = resizeImage(image, size)
    if flags & ImageFlags.Frame:
        image = frameImage(image, tuple(palette[:3]), tuple(palette[-3:]), size)
    if flags & ImageFlags.Quantize:
        image = quantizeImage(image, palette)

    try:
        image.save(target)
    except IOError:
        raise RuntimeError('Cannot write image file %s' % target)
