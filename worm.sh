#! /bin/bash

set -euxo pipefail

if ! [ -f ./out.html ]; then
  echo "Downloading the content of the website"
  python3 main.py
fi

echo "Converting html to pdf"
weasyprint out.html out.pdf --optimize-images