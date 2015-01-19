import pickle
import re
import sys

def main(argv):
    source = argv[1]
    dest = argv[2]
    with open('.coverage', 'rb') as f:
        coverage_data = pickle.load(f)
    for filename in list(coverage_data['lines'].keys()):
        new_filename = re.sub(source, dest, filename)
        if new_filename != filename:
            coverage_data['lines'][new_filename] = coverage_data['lines'].pop(filename)
    with open('.coverage', 'wb') as f:
        pickle.dump(coverage_data, f)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
