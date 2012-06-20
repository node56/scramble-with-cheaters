# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import urllib
import urllib2
import re
import commands
import time
import sys
import getopt
import pickle
import boggle
from java.awt.image import BufferedImage 
from java.io import File
from javax.imageio import ImageIO

class LetterGrid:
  xpad= 292
  ypad= 33
  xspace=71
  yspace=31
  xsize=70
  ysize=110
  def __init__(self,dev,w=1024,h=600):
    self.w = w
    self.h = h
    self.dev = dev

  def tilePos(g,i):
    return (g.xpad+(i>>2)*(g.xspace+g.xsize),
          g.h-(g.ypad+(i&3)*(g.yspace+g.ysize)))

  def touch(self,x, y, action=MonkeyDevice.DOWN_AND_UP):
    self.dev.touch(self.h - y, x, action)

  def drag(self, x1, y1, x2, y2, delay, steps):
    self.dev.drag((self.h - y1, x1),
        (self.h - y2, x2), delay, steps)

 
def getPage(grid):
  url = 'http://www.scramblewithfriends-cheat.com/#results'
  grid = re.sub(r'QU', 'Q', grid)
  values = {'grid' : grid}
  data = urllib.urlencode(values)
  req = urllib2.Request(url, data)
  response = urllib2.urlopen(req)
  the_page = response.read()
  return the_page

def findWords(text):
  matches = re.findall(r'title=\"(\d+) .*? data\-path="\[([\d, ]+)\]">(\w+)<',
      text)
  matches.sort(key=lambda k:k[2])  
  return matches

def threshold(lg, getPixel):
  b = BufferedImage(16*lg.ysize, lg.xsize, BufferedImage.TYPE_BYTE_GRAY)
  for i in range(16):
      dx, dy = lg.tilePos(i)
      for y in range(lg.ysize):
        for x in range(lg.xsize):
          color = getPixel(dx+x,dy-y)
          b.setRGB(y+i*lg.ysize, x, color & 255 < 60 and 0xffffff or 0)
  return b

def readImage(name):
  return ImageIO.read(File(name))

def doThreshold():
  img = readImage("game.png")
  w = img.getWidth()
  h = img.getHeight()
  d = threshold(LetterGrid(w,h), img.getRGB)
  ImageIO.write(d, "png", File("game-thresh.png")) 

def doThresholdSnap(snap, lg, filename):
  d = threshold(lg, snap.getRawPixelInt)
  ImageIO.write(d, "png", File(filename)) 

def getDevice():  
  return MonkeyRunner.waitForConnection()

def getSnap(lg):
  return lg.dev.takeSnapshot()
 
def write(snap):
  snap.writeToFile('check.png','png')

def playWords(lg, words):
  for word in words:
    print 'playing %s' % word[2]
    playWord(lg, word[1]) # re.split(r',\s*', word[1]))

def playWord(lg, tiles):
  lg.touch(200, 540)
  for tile in tiles:
    x, y = lg.tilePos(int(tile))
    lg.touch(x,y) 
  lg.touch(200, 70)

def toLetters(file, basename):
  fname = '%s-ocr' % basename
  status, output = commands.getstatusoutput('tesseract %s %s -psm 7' % (file, fname))
  f = open('%s.txt' % fname,'r')
  result = f.read()
  grid = re.sub(r'\s+', '', result) 
  return grid

class MockDevice:
  def drag(self,f, to, t, s):
    print 'drag ' + str(f)+' '+str(to)

  def touch(self,x,y,t):
    print 'touch ' +str(x) + ' '+ str(y)

def doResume(lg):
  lg.touch(410, 300)
  time.sleep(1.2)

def doPause(lg):
  lg.touch(75, 50)

def doSnap(lg, basename):
  doResume(lg)
  snap = getSnap(lg)
  doPause(lg)
  snap.writeToFile('%s.png' % basename)
  thresh = '%s-thresh.png' % basename
  doThresholdSnap(snap, lg, thresh)
  g = toLetters(thresh, basename)
  return boggle.findWords(g)

def callOut(g):
  text = getPage(g)
  words = findWords(text)
  f = open('%s-words.pickle' % basename, 'w')
  pickle.dump(words, f)
  f.close()
  return words

def doPlay(lg, words):
  doResume(lg)
  playWords(lg, words)
  doPause(lg)
 
def process(arg):
  print "extra arg %s" % arg

def main():
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "ahgxw:",
        ["help", "snap", "pause", "word=", "all"])
  except getopt.error, msg:
    print msg
    print "for help use --help"
    sys.exit(2)
  # process options
  basename = 'g%d' % int(time.time())
  print basename
  for o, a in opts:
    if o in ("-h", "--help"):
      print __doc__
      sys.exit(0)
    if o in ("-g", "--snap"):
      lg = LetterGrid(getDevice())
      doSnap(lg,basename)
    if o in ("-x", "--pause"):
      lg = LetterGrid(getDevice())
      #doPause(lg)
      #write(getSnap(lg))
      doThreshold()
    if o in ("-w", "--word"):
      lg = LetterGrid(getDevice())
      f = open(a, 'r')
      words = pickle.load(f)
      doPlay(lg, words)
    if o in ("-a", "--all"):
      lg = LetterGrid(getDevice())
      words = doSnap(lg,basename)
      doPlay(lg, words)


  # process arguments
  for arg in args:
    process(arg) # process() is defined elsewhere

if __name__ == "__main__":
    main()

#doThreshold()


