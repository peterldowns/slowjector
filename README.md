# slowjector
The code behind an art project created for [Steer Roast
2015](http://web.mit.edu/senior-house/www/steerroast.html). A webcam and
projector were set up in an empty room and visitors could interact with
themselves and their past selves. The goal was to create a sense of control
over time through control of space.

`slowjector` was inspired by (or in other words, is a rip-off of) ["The
Moment"](https://vimeo.com/119838128) by [HYBE](http://www.hybe.org/). Thanks
to [Noah](http://noah.org) for the [movement calculation
code](http://noah.org/wiki/movement.py).


### Installation
`slowjector` only depends on [OpenCV](http://opencv.org/) and has been tested
with Python 2.7. You must also have a webcam.


### Usage
Once you've installed the dependencies, clone the repository:

```bash
$ git clone https://github.com/peterldowns/slowjector.git
```

and run the code:

```bash
$ cd slowjector
$ python slowjector.py
```


### Modification
If you read the code, you'll see that there are various different flags and
variables, all of which can be used to change the way slowjector works. At some
point in the future I'll include some oducmentation, but feel free to play
around with them.


### License
Read the LICENSE file.
