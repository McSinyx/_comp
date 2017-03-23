#!/usr/bin/env python3

import curses
import json
from argparse import ArgumentParser
from configparser import ConfigParser
from os.path import expanduser

import mpv


def mpv_wrapper(media, video=True):
    if video:
        player = mpv.MPV(ytdl=True, input_default_bindings=True,
                         input_vo_keyboard=True, ytdl_format=ytdl_format)
    else:
        player = mpv.MPV(ytdl=True, input_default_bindings=True,
                         input_vo_keyboard=True, vid=False,
                         ytdl_format=ytdl_format)
    player.play(media)
    player.wait_for_playback()
    del player


def interface(stdscr):
    def reattr(y):
        track = DATA[start + y - 1]
        invert = 8 if track['highlight'] else 0
        if track['error']:
            stdscr.chgat(y, 0, curses.color_pair(1 + invert) | curses.A_BOLD)
        elif track['playing']:
            stdscr.chgat(y, 0, curses.color_pair(3 + invert) | curses.A_BOLD)
        elif track['selected']:
            stdscr.chgat(y, 0, curses.color_pair(5 + invert) | curses.A_BOLD)
        elif invert:
            stdscr.chgat(y, 0, curses.color_pair(12) | curses.A_BOLD)
        else:
            stdscr.chgat(y, 0, curses.color_pair(0) | curses.A_NORMAL)

    def reprint():
        stdscr.clear()
        stdscr.addstr(0, curses.COLS-12, 'URL')
        stdscr.addstr(0, 0, 'Title')
        stdscr.chgat(0, 0, curses.color_pair(10) | curses.A_BOLD)
        for i, d in enumerate(DATA[start : start+curses.LINES-3]):
            stdscr.addstr(i + 1, 0, d['url'].rjust(curses.COLS - 1))
            stdscr.addstr(i + 1, 0, d['title'][:curses.COLS-12])
            reattr(i + 1)
        stdscr.addstr(
            curses.LINES - 2,
            curses.COLS - 16,
            '{:7} {:8}'.format(mode, 'selected' if selected else 'all')
        )
        stdscr.chgat(curses.LINES - 2, 0, curses.color_pair(8))
        stdscr.refresh()

    def move(y, delta):
        nonlocal start
        reattr(y)
        if start + y + delta < 1:
            start = 0
            reprint()
            stdscr.move(1, 0)
            DATA[0]['highlight'] = True
            reattr(1)
            DATA[0]['highlight'] = False
            return 1
        elif start + y + delta > len(DATA):
            start = len(DATA) - curses.LINES + 3
            reprint()
            y = curses.LINES - 3
            stdscr.move(y, 0)
            DATA[-1]['highlight'] = True
            reattr(y)
            DATA[-1]['highlight'] = False
            return y

        if 0 < y + delta < curses.LINES - 2:
            y = y + delta
        elif y + delta < 1:
            start += y + delta - 1
            reprint()
            y = 1
        else:
            start += y + delta - curses.LINES + 3
            reprint()
            y = curses.LINES - 3
        stdscr.move(y, 0)
        DATA[start + y - 1]['highlight'] = True
        reattr(y)
        DATA[start + y - 1]['highlight'] = False
        stdscr.refresh()
        return y

    # Init color pairs
    curses.use_default_colors()
    curses.init_pair(1, 1, -1)
    curses.init_pair(2, 2, -1)
    curses.init_pair(3, 3, -1)
    curses.init_pair(4, 4, -1)
    curses.init_pair(5, 5, -1)
    curses.init_pair(6, 6, -1)
    curses.init_pair(7, 7, -1)
    curses.init_pair(8, -1, 7)
    curses.init_pair(9, -1, 1)
    curses.init_pair(10, -1, 2)
    curses.init_pair(11, -1, 3)
    curses.init_pair(12, -1, 4)
    curses.init_pair(13, -1, 5)
    curses.init_pair(14, -1, 6)
    curses.curs_set(False)

    # Print initial content
    start = 0
    reprint()
    y = 1
    DATA[0]['highlight'] = True
    stdscr.move(1, 0)
    reattr(1)
    DATA[0]['highlight'] = False

    while True:
        c = stdscr.getch()
        if c == curses.KEY_RESIZE:
            curses.update_lines_cols()
            reprint()
            y = 1
            reattr(y)
        elif c in (ord('j'), curses.KEY_DOWN):
            y = move(y, 1)
        elif c in (ord('k'), curses.KEY_UP):
            y = move(y, -1)
        elif c == curses.KEY_PPAGE:
            y = move(y, -curses.LINES)
        elif c == curses.KEY_NPAGE:
            y = move(y, curses.LINES)
        elif c == curses.KEY_HOME:
            y = move(y, -len(DATA))
        elif c == curses.KEY_END:
            y = move(y, len(DATA))
        elif c == ord(' '):
            DATA[start + y - 1]['selected'] = not DATA[start + y - 1]['selected']
            y = move(y, 1)
        elif c == ord('x'):     # temporally behavior
            mpv_wrapper('https://youtu.be/' + DATA[start + y - 1]['url'], video)
        elif c == ord('v'):
            player.quit_watch_later()
        elif c in (ord('q'), 27):   # 27 is Escape key
            stdscr.addstr(curses.LINES - 1, 0, 'Quit comp? [y/N]')
            if stdscr.getch() == ord('y'):
                break
            reprint()
        stdscr.refresh()


parser = ArgumentParser(description="console/curses online media player")
parser.add_argument('-j', '--json-playlist', required=False,
                    help='path to playlist in JSON format')
args = parser.parse_args()

config = ConfigParser()
config.read(expanduser('~/.config/comp/settings.ini'))
ytdl_format = config.get('Init', 'ytdl-format', fallback='best')
mode = config.get('Runtime', 'play-mode', fallback='normal')
selected = config.getboolean('Runtime', 'play-selected-only', fallback=False)
video = config.getboolean('Runtime', 'video', fallback=True)

with open(args.json_playlist) as f:
    DATA = json.load(f)
for i in DATA:
    i['error'] = False
    i['playing'] = False
    i['selected'] = False
    i['highlight'] = False
curses.wrapper(interface)