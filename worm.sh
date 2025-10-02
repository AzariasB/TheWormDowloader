#! /bin/bash

set -euxo pipefail

if ! [ -f ./worm.html ]; then
  echo "Downloading the content of the website"
  python3 main.py
fi

echo "Converting html to pdf"
pandoc worm.html \
    -o worm.pdf \
    -V 'mainfont:DejaVu Sans' \
    -V 'fontsize:14pt' \
    -V 'pagestyle:empty' \
    -V 'documentclass:extarticle' \
    -V 'geometry:margin=2cm' \
    --pdf-engine=xelatex \
    --lua-filter=pagebreak.lua