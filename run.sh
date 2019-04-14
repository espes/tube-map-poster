#!/bin/echo

# not a tested script, just the approximate commands run

echo "Extracting jpg from pdf"
pushd input
    pdfimages -j 2379-1819-QR\ TubeMap.pdf img
popd

# TODO crop img-000 here

echo "Cropping chunks from image"
mkdir tiles
convert img-000-crop.png -crop 2048x2048 tiles/%03d.png

echo "Vectorising chunks"
(cd tracer && ls ../tiles/*.png | xargs -n1 -P2 python go.py)

echo "Combining vectorised chunks..."
python svg_stack/svg_stack.py --direction h `printf "tiles/%.3d.png.out.svg " {0..7}` > l1.svg
python svg_stack/svg_stack.py --direction h `printf "tiles/%.3d.png.out.svg " {8..15}` > l2.svg
python svg_stack/svg_stack.py --direction h `printf "tiles/%.3d.png.out.svg " {16..23}` > l3.svg
python svg_stack/svg_stack.py --direction h `printf "tiles/%.3d.png.out.svg " {24..31}` > l4.svg
python svg_stack/svg_stack.py --direction h `printf "tiles/%.3d.png.out.svg " {32..39}` > l5.svg
python svg_stack/svg_stack.py --direction h `printf "tiles/%.3d.png.out.svg " {40..47}` > l6.svg
python svg_stack/svg_stack.py --direction v l{1..6}.svg > out/tube-map-poster.svg
