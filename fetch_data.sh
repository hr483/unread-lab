#!/bin/sh
# Re-creates data/ at the pinned versions in data/SOURCES.lock
set -e
mkdir -p data && cd data
for pair in "khobwa lexibank/lieberherrkhobwa" "sagartst lexibank/sagartst" "northeuralex lexibank/northeuralex" "bodtkhobwa lexibank/bodtkhobwa" "suntb lexibank/suntb"; do
  set -- $pair; rm -rf "$1"; git clone -q https://github.com/$2 "$1"
  (cd "$1" && git checkout -q "$(grep "^$1 " ../SOURCES.lock | cut -d' ' -f2)")
done
echo "data ready"
