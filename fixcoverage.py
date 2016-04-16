import coverage
import re
import sys

def main(argv):
    source = argv[1]
    dest = argv[2]
    coverage_data = coverage.CoverageData()
    coverage_data.read_file('.coverage')

    # Prefilter to filenames in NetworkX
    filenames = [filename for filename in coverage_data._lines.keys()
                 if 'networkx' in filename]

    for filename in filenames:
        new_filename = re.sub(source, dest, filename)
        if new_filename != filename:
            coverage_data._lines[new_filename] = coverage_data._lines.pop(filename)
        
    coverage_data.write_file('.coverage')

if __name__ == '__main__':
    sys.exit(main(sys.argv))
