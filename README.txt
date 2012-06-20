Requires the android sdk, tesseract ocr, a word list, and a kindle sized android device.

word list:
http://itasoftware.com/careers/work-at-ita/PuzzleFiles/WORD.LST

tesseract install:
http://superuser.com/questions/337871/install-tesseract-ocr-3-on-osx

Install scramble with friends, start a game, pause when the letter grid comes up and run:
 android-sdk/tools/monkeyrunner robot.py -a

If everything goes well, the game will unpause for a second and repause while it analyzes
a screen shot. It will then unpause the game and start playing words alphabetically. 

It doesn't yet play a perfect game, but is more than adequate to beat a non-automated
player. 
