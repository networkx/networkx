wget https://raw.githubusercontent.com/networkx/branding/main/logo/networkx_favicon.svg
inkscape -w 16 -h 16 -o 16.png networkx_favicon.svg
inkscape -w 32 -h 32 -o 32.png networkx_favicon.svg
inkscape -w 48 -h 48 -o 48.png networkx_favicon.svg
convert 16.png 32.png 48.png favicon.ico
