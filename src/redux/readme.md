# Redux

[![Build Status](https://travis-ci.org/jiaweihli/manga_downloader.png)](https://travis-ci.org/jiaweihli/manga_downloader)
[![Coverage Status](https://coveralls.io/repos/jiaweihli/manga_downloader/badge.png?branch=refactoring)](https://coveralls.io/r/jiaweihli/manga_downloader?branch=refactoring)

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

## Version Support

Support is maintained on Python 2.6, 2.7, 3.2, and 3.3.
