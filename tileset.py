from PIL  import Image, ImageChops, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import argparse
import os

def same(img1, img2):
    if img1.size != img2.size:
        return False
    
    for x in range(0, img1.size[0]):
        for y in range(0, img1.size[1]):
            if (img1.getpixel((x, y)) != img2.getpixel((x, y))):
                return False
    return True
    
# Create the parser
parser = argparse.ArgumentParser()

# Add an argument
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--output', type=str, required=True)
parser.add_argument('--tileWidth', type=int, default=8)
parser.add_argument('--tileHeight', type=int, default=8)
parser.add_argument('--transparent', type=int, nargs=3)
args = parser.parse_args()


print("Opening image", args.input)
image = Image.open(args.input)
imageWidth, imageHeight = image.size
if image.mode != "RGBA":
    print("Format is ", image.mode)
    image = image.convert("RGBA")
    image.putalpha(255)
    print("Converted to ", image.mode)

# Convert specific colour to transparent
if args.transparent:
    print("Making backgound transparent")
    from itertools import product
    for p in product(range(0, imageWidth), range(0, imageHeight)):
        if image.getpixel(p) == (args.transparent[0], args.transparent[1], args.transparent[2], 255):
            image.putpixel(p, (0, 0, 0, 0))

tileMap = []
tileSet = []
tileSet.append((0, Image.new('RGBA', (args.tileWidth, args.tileHeight), (0, 0, 0, 0))))

for tileY in range(0, imageHeight, args.tileHeight):
    print("{}% complete\r".format(100 * tileY // imageHeight), end='')
    for tileX in range(0, imageWidth, args.tileWidth):
    
        tileRect = (tileX, tileY, tileX + args.tileWidth, tileY + args.tileHeight)
        tileImg = image.crop(tileRect)

        tileFound = None
        for tileId, tile in tileSet:
            diff = ImageChops.difference(tile, tileImg)
            if same(tile, tileImg):
                tileFound = tileId
                tileSet.insert(0, tileSet.pop(tileSet.index((tileId, tile))))
                break

        if tileFound is None:
            tileFound = len(tileSet)
            tileSet.insert(0, (tileFound, tileImg))

        tileMap.append(tileFound)

print(len(tileSet), "unique tiles found")

tileSetImageDim = 1
while (tileSetImageDim * tileSetImageDim) < len(tileSet):
    tileSetImageDim *= 2

tileSetImageWidth = args.tileWidth * tileSetImageDim
tileSetImageHeight = args.tileHeight * tileSetImageDim

tileSetImage = Image.new('RGBA', (tileSetImageWidth, tileSetImageHeight), (0, 0, 0, 255))

for tileId, tile in tileSet:
    tileSetX = ((tileId - 1) % tileSetImageDim) * args.tileWidth
    tileSetY = ((tileId - 1) // tileSetImageDim) * args.tileHeight
    tileSetImage.paste(tile, (tileSetX, tileSetY))

tileSetImage.save(args.output + '.png')

# Build the root node ("map")
mapEl = ET.Element("map")
mapEl.attrib["version"] = "1.0"
mapEl.attrib["orientation"] = "orthogonal"
mapEl.attrib["renderorder"] = "right-down"
mapEl.attrib["width"] = "%d" % (imageWidth // args.tileWidth)
mapEl.attrib["height"] = "%d" % (imageHeight // args.tileHeight)
mapEl.attrib["tilewidth"] = "%d" % args.tileWidth
mapEl.attrib["tileheight"] = "%d" % args.tileHeight

# Build the tileset
tileSetEl = ET.SubElement(mapEl, "tileset")
tileSetEl.attrib["firstgid"] = "1"
tileSetEl.attrib["name"] = args.output
tileSetEl.attrib["tilewidth"] = "%d" % args.tileWidth
tileSetEl.attrib["tileheight"] = "%d" % args.tileHeight

# Add the image information for the tileset
imgEl = ET.SubElement(tileSetEl, "image")
imgEl.attrib["source"] = args.output + '.png'
imgEl.attrib["width"] = "%d" % tileSetImageWidth
imgEl.attrib["height"] = "%d" % tileSetImageHeight
imgEl.attrib["trans"] = "%s" % "FF0FF"

layerEl = ET.SubElement(mapEl, "layer")
layerEl.attrib["name"] = 'Platforms'
layerEl.attrib["width"] = "%d" % (imageWidth // args.tileWidth)
layerEl.attrib["height"] = "%d" % (imageHeight // args.tileHeight)
dataEl = ET.SubElement(layerEl, "data")

# In each layer, there are width x height tiles.
for tile in tileMap:
    tileEl = ET.SubElement(dataEl, "tile")
    tileEl.attrib["gid"] = "%d" % (tile)

tree = ET.ElementTree(mapEl)
ET.indent(tree, space="\t", level=0)
tree.write(args.output + '.tmx', encoding="UTF-8", xml_declaration=True)

