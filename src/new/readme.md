## Usage
Navigate to the root directory (the one above `src/`)

> \>\>\> from src.new.mangafox.mangafox import *

> \>\>\> MangaFox.series('toriko')

> <src.new.mangafox.mangafoxseries.MangaFoxSeries instance at 0x1048c2b90>

> \>\>\> MangaFox.series('toriko').chapters[0].pages[0].image.url

> 'http://z.mfcdn.net/store/manga/3660/01-001.0/compressed/toriko_v01_c01_01.jpg'

Yep.