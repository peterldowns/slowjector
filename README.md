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


### Usage
First, clone the repository:

```bash
$ git clone https://github.com/peterldowns/slowjector.git
```

`slowjector` depends on [OpenCV](http://opencv.org/) and has been tested with
Python 2.7. If you'd like to use the command line interface wrapper, you can
install its requirements easily with
[`pip`](https://pip.pypa.io/en/stable/installing.html):

```bash
$ cd slowjector
$ pip install -r requirements.txt
```

If you just want to slowject some video, use the CLI (make sure you installed
its requirements, detailed above):

```bash
$ ./slowjector_cli.py
$ ./slowjector_cli.py --help # Show available flags

# Good demo parameters for being standing ~2 meters away
$ ./slowjector_cli.py \
--quick-catchup \
--mirror-src \
--show-delta-text \
--dubious-commitment \
--raw-output \
--quick-catchup-ratio 0.05
```

Everything's python, though, so feel free to import from slowjector and use its
functions in your own code.

### Modification
If you read the code, you'll see that there are various different flags and
variables, all of which can be used to change the way the video is processed
and displayed. At some point in the future I'll include some oducmentation, but
feel free to play around with them. The CLI provides a nice overview:

```bash
$ ./slowjector_cli.py --help
```

Pull requests are very, very welcome!


### License
MIT, check the LICENSE file for more information.
