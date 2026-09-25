"""Custom sphinx-gallery image scrapers.

These live in their own module (rather than ``conf.py``) so they can be referenced
by fully qualified name, which keeps ``sphinx_gallery_conf`` picklable.
"""

import glob
import os
import shutil

from sphinx_gallery.scrapers import figure_rst


def png_scraper(block, block_vars, gallery_conf):
    """Collect .png files written by pygraphviz examples (e.g. ``A.draw("k5.png")``).

    Unlike ``pygraphviz.scraper.PNGScraper``, only collect files whose names appear
    in the current code block, so that examples in the same directory running in
    parallel do not grab each other's (possibly partially written) images.
    """
    example_dir = os.path.dirname(block_vars["src_file"])
    image_names = []
    for png in sorted(glob.glob(os.path.join(example_dir, "*.png"))):
        if os.path.basename(png) in block.content:
            image_path = next(block_vars["image_path_iterator"])
            shutil.move(png, image_path)
            image_names.append(image_path)
    return figure_rst(image_names, gallery_conf["src_dir"])
