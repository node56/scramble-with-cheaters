import urllib
import urllib2
import re
import commands
import time
import sys
import getopt
import pickle
import string

class Search:
  def __init__(self,grid):
    self.grid = grid.lower().replace('qu','q')
    i=0
    self.map = {}
    for letter in string.ascii_lowercase:
      self.map[letter]=[]
    for letter in self.grid:
      self.map[letter].append(i)
      i+=1
    self.adj = []
    for i in range(16):
      r = i >> 2
      c = i & 3
      self.adj.append([])
      for j in range(16):
        rj = j >> 2
        cj = j & 3
        self.adj[i].append((rj == r and (cj == c-1 or cj == c+1)) or
           ((rj == r-1 or rj == r+1) and (cj == c-1 or cj == c+1 or cj == c)))

  def extend(self, used, letters, res):
    if not letters:
      res.append(used)
      return
    for pos in self.map[letters[0]]:
      if not used or self.adj[pos][used[-1]] and not pos in used:
        self.extend(used + [pos], letters[1:], res)

def findWords(grid):
  s = Search(grid)
  f = open('words.txt', 'r')
  hits = []
  for line in f:
    word = line.strip().lower().replace('qu','q')
    res = []
    s.extend([], word, res)
    if res:
      hits.append([1, res[0], word, res])
  return hits

def unpack(file):
  f = open(file, 'r')
  words = pickle.load(f)
  for word in words:
    print word[2]

def main():
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "ahgxw:p:",
        ["help"] )
  except getopt.error, msg:
    print msg
    print "for help use --help"
    sys.exit(2)
  # process options
  for o, a in opts:
    if o in ("-h", "--help"):
      print __doc__
      sys.exit(0)
    if o in ("-w"):
      words = findWords(a)
      for word in words:
        print word[2] + " " + str(word[3])
    if o in ("-p"):
      unpack(a)
  for arg in args:
    pass

if __name__ == "__main__":
    main()

