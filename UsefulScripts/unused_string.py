import sys
import os
import re


def file_match(fname, pat):
	try:
		f = open(fname, "rt")
	except IOError:
		return

	for i, line in enumerate(f):
		if pat.search(line):
			return True
	f.close()
	return False


def rgrep_match(dir_name, s_pat):
	pat = re.compile(s_pat)
	for dirpath, dirnames, filenames in os.walk(dir_name):
		for fname in filenames:
			fullname = os.path.join(dirpath, fname)
			match=file_match(fullname, pat)
			if match:
				return match
	return False

if __name__ == '__main__':
	strings_file = sys.argv[1]
	src_dir_name = sys.argv[2]

	for item in open(strings_file).readlines():
		grep_for = item.strip().split(' = ')[0].replace('"','')
		if rgrep_match(src_dir_name, grep_for):
			print item.strip()