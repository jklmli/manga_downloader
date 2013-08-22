# Redux

[![Build Status](https://travis-ci.org/jiaweihli/manga_downloader.png)](https://travis-ci.org/jiaweihli/manga_downloader)
[![Coverage Status](https://coveralls.io/repos/jiaweihli/manga_downloader/badge.png?branch=refactoring)](https://coveralls.io/r/jiaweihli/manga_downloader?branch=refactoring)

## Installation

    pip install -r requirements.txt --use-mirrors

## Layout
`helper` contains some shared, non-application-specific code.  (Or it will, after the Util class
is removed.)

`site` contains the library logic to retrieve data from the websites.  The hierarchy:

> MangaSite
>
>   - Noez
>     - MangaFox
>     - MangaHere
>   - Aftv
>     - MangaPanda
>     - MangaReader

Noez and Aftv appear to be the parent companies of the sites that exist under them.

## Usage

### Use Case
Q: What's the image url for the first page of the first chapter of 'Toriko'?

Step 1:  Navigate to the `src/` directory.

Step 2:

> \>\>\> from redux.site.mangafox import *

> \>\>\> MangaFox.series('toriko').chapters[0].pages[0].image.url

> 'http://z.mfcdn.net/store/manga/3660/01-001.0/compressed/toriko_v01_c01_01.jpg'

Alternatively, use MetaSite, which allows aggregation of multiple sites (there are some performance
issues related to error correction that are being worked out however):

> \>\>\> from metasite import MetaSite

> \>\>\> search = MetaSite([MangaFox, MangaHere, MangaPanda, MangaReader])

> \>\>\> from redux.site.mangafox import MangaFox

> \>\>\> from redux.site.mangahere import MangaHere

> \>\>\> from redux.site.mangapanda import MangaPanda

> \>\>\> from redux.site.mangareader import MangaReader

> \>\>\> search.series('death note').chapters['22'].pages[0].image.url

> 'http://i39.mangapanda.com/death-note/22/death-note-1678383.jpg'

Take a look at the `test/` folder for further examples.

## Version Support

Support is maintained on Python 2.7.  Support for 3.2 and 3.3 is pending a pull request in a
dependency.

## Testing

Make sure you have [nose](https://github.com/nose-devs/nose) (install via `pip install nose` if
not!), then run:

    nosetests --with-coverage --cover-package=redux