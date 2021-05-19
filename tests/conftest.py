from os.path import dirname, join
import sys

my_path = dirname(__file__)
my_path = join(my_path, "..")

sys.path.insert(0, my_path)
