#!/usr/bin/env python
# coding: utf-8
import click
from slowjector import slowjector

@click.command()
@click.option('--device-id', default=0, help='Video device number.')
@click.option('--src-width', default=640, help='Video source width (pixels).')
@click.option('--src-height', default=480, help='Video source height (pixels).')
@click.option(
    '--motion-threshold-ratio',
    default=0.005,
    help=('Ratio of pixels necessary to be changed in order for motion to'
          ' start dilating time. Increasing this number increases the amount of'
          ' motion necessary to trigger the slow motion effect.'))
@click.option(
    '--motion-unit-ratio',
    default=0.005,
    help=('Ratio of pixels changed used to calculate amount of slow motion.'
          ' Increasing this number decreases the amount of "slow motion" that'
          ' takes place due to movement.'))
@click.option(
    '--max-frame-count',
    default=24,
    help=('The maximum number of times any given frame will be repeated as'
          ' part of the slow motion effect. Increasing this number can lead to'
          ' visual "lag" during use, as frames with a lot of motion may be'
          ' shown for a larger amount of time'))
@click.option(
    '--quick-catchup/--slow-catchup',
    default=True,
    help=('Quick catchup will "snap" back to reality after a motion sequence'
          ' finishes. Slow catchup will attempt to display frames as fast as'
          ' possible in order to catch up to reality, which may take some time.'
          ' The biggest difference is that slow catchup will play every source'
          ' frame captured, while quick catchup will jump over some to catch'
          ' up faster.'))
@click.option(
    '--quick-catchup/--slow-catchup',
    default=True,
    help=('Quick catchup will "snap" back to reality after a motion sequence'
          ' finishes. Slow catchup will attempt to display frames as fast as'
          ' possible in order to catch up to reality, which may take some time.'
          ' The biggest difference is that slow catchup will play every source'
          ' frame captured, while quick catchup will jump over some to catch'
          ' up faster.'))
@click.option(
    '--quick-catchup-ratio',
    default=0.002,
    help=('The threshold ratio of pixels to be changed in a given frame. When'
          ' a given sequence of slow-motion frames includes a frame that has'
          ' fewer pixel changes (as a ratio) than this number, the slow motion'
          ' will end and the output will "catch up" to reality.'))
@click.option(
    '--show-delta-text/--hide-delta-text',
    default=False,
    help='Include frame delta statistics in the output video.')
@click.option(
    '--mirror-src/--no-mirror-src',
    default=True,
    help='Mirror the source video input, common for webcams.')
@click.option(
    '--raw-output/--processed-output',
    default=False,
    help=('Raw output uses the raw frames from the video source as output.'
          ' Processed output is black and white and slightly blurred, but'
          ' smoother. For that art film effect the critics love.'))
@click.option(
    '--sparkle-motion/--dubious-commitment',
    default=True,
    help=('Highlight frame differences in the output video. Have you seen'
          ' Donnie Darko? https://www.youtube.com/watch?v=_SbgEYBG-Y8'))
def slowjector_cli(*args, **kargs):
  return slowjector(*args, **kargs)


if __name__ == '__main__':
  slowjector_cli()
