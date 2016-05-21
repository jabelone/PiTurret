# PortalTurret
## Introduction
PortalTurret is an open source portal 2 turret.  Yes, eventually it will
actually track things with a laser pointer and nerf gun.  Ensure you have 
the latest version of OpenCV and python 3 installed.  PortalTurret is
sill in an "alpha" stage so don't be disappointed if you run into issues
when trying to run or use it.
 
## Usage
There are two main "versions" that you may find useful.  Both have
exactly the same functionality and logic/algorithms used.  The only
difference between them is one will run on a raspberry pi, using the
built in pi camera module and the other will use the first available
webcam.  

The names are pretty self explanatory, `pi_turret.py` runs
only with a pi camera module and `pc_turret.py` should run on most
computers with a webcam attached.  It is very simple to use, simply
invoke python and run the program: `python pc_turret.py`.  That's it.

This is also a pycharm project, meaning you can open the cloned 
folder in pycharm as a project.

## Contribute
PortalTurret is currently being developed by just @jabelone.  As the
project is currently just a personal one I'm not looking for contributors.
However, if you send a pull request and it looks decent I probably
won't say no.

## Author
PortalTurret is currently being developed by @jabelone.  I'm a 1st year
university student studying computer science at the Queensland
University of Technology.  I _strongly_ beleive in the open source
philosophy and release most things I do under a GNU GPL license.  If
you want to get in touch the best way is to find my email on my GitHub
profile.

## License
As I mentioned before, I love open source projects.  PortalTurret is 
released uner a GNU GPL v3 or later license and is free for everyone to 
use for whatever purpose they want. Whilst you don't have to, I would 
love to see any cool things or implementations you have done with it, 
just open an issue on GitHub or find my email on my GitHub profile.