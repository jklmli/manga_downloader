# Redux

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
Q: What's image url for the first page of the first chapter of 'Toriko'?

Step 1:  Navigate to the `src/` directory.

Step 2:

> \>\>\> from redux.site.mangafox import *

> \>\>\> MangaFox.series('toriko').chapters[0].pages[0].image.url

> 'http://z.mfcdn.net/store/manga/3660/01-001.0/compressed/toriko_v01_c01_01.jpg'

