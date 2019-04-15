# ohno
extract the last panel of comics (especially [these](http://webcomicname.com/)) programmatically

## how:
1. install Python 3.6 or greater, probably
    * also install Python 2.7 if you need tumblr-utils to work, like with `go.sh`. sorry :/
2. install OpenCV from somewhere (this is why I didn't bother packaging this properly)
3. clone this repo
    * with `git clone --recurse-submodules` if you want `go.sh` to work

## now:
* run `./go.sh` on a cron to get an automatically updated feed full of sweet reaction images
* run `./ohnoify.py input.png -o /tmp` to extract just one panel and send it to a temporary dir
* run `./ohnoify.py input.png -o /tmp --debug` to interactively debug issues (or show off the sweet magic to your friends, up to you)

## but how does it work?
it does some pretty typical stuff to clean up the image before finding the rectangular contours. then it finds the contour closest to the bottom right, masks out the image with it, and crops the image to the size of the axis-aligned bounding box of the contour.

## ohno, it broke
1. don't panic
2. make sure you followed all of the install instructions above
3. try running it with the `--debug` flag against your image
4. try to fix the bug, if you can
5. file an issue with the whole debug log, all package and Python and OS versions, and all images involved
