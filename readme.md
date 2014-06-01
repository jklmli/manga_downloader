# Manga-Downloader

**Note: There is an ongoing rewrite in the [1.0.0 branch](https://github.com/jiaweihli/manga_downloader/tree/1.0.0) 
(pull requests welcome!), which will break backwards-compatibility with the current version (0.x).  
Once it's released, this version will be deprecated and all development and support will be dropped.**

Manga-Downloader is a cross-platform Windows/Mac/Linux Python 2/3 script.

It can be automated via an external xml file, and can convert images for viewing on the Kindle.

Currently supports mangafox.com, mangareader.net, mangapanda.com and mangahere.com with a total
of over 10,000 mangas. Downloads into .cbz format, can optionally download into .zip instead.

## Dependencies

Python 2.6+, including 3.x

PIL if using Kindle conversion.

How to backport to:

  - 2.5 - change the exception-handling code and use `StringIO` instead of `io` module
  - 2.4 - removing parentheses after class declarations

## Usage

`manga.py [options] <manga name> <manga name> <etc.>`

The script will offer a choice of 3 manga sites, it will default to the first upon pressing 'enter'.

After selecting a site, the script will output a list of all chapters of the series it has found on
the site you selected.

When it prompts "Download which chapters?", type in the ones you want delimited by '-' and ','.
You can also type 'all' if you did not specify `--all` before.

### Options

> `--version`

show program's version number and exit

> `-h, --help`

show this help message and exit

> `--all`

Download all available chapters.

> `-d <download path>, --directory=<download path>`

The destination download directory. Defaults to a directory named after the manga.

> `--overwrite`

Overwrites previous copies of downloaded chapters.

> `-t <number>, --threads=<number>`

Limits the number of chapter threads to the user specified value. Default value is `3`.

> `--verbose`

Verbose output.

> `-x <xmlfile path>, --xml=<xmlfile path>`

Parses the `.xml` file and downloads all chapters newer than the last chapter downloaded for the
listed mangas.

> `-z, --zip`

Downloads using `.zip` compression.  Omitting this option defaults to `.cbz.`

> `-c, --convertFiles`

Converts the files that are downloaded to a Format/Size ratio acceptable to the device specified by
the `device` parameter. The converted images are saved in the directory specified by the
`outputDirectory` paraemter.

> `--device`

Specifies the target device for the image conversion.

> `--convertDirectory`

Converts the image files stored in the directory specified by the `inputDirectory` parameter. Stores
the images in the directory specified by the `outputDirectory` Parameter

> `--inputDirectory`

The directory containing the images to convert when `convertDirectory` is specified.

> `--outputDirectory`

The directory to store the converted Images. Omitting this option defaults to
`DOWNLOAD_PATH/Pictures`.

### Usage

> `manga.py -d "C:\Documents and Settings\admin\Documents\Manga\" -z Bleach`

On a Windows machine, downloads 'Bleach' to `C:\Documents and Settings\admin\Documents\Manga\`,
using `.zip` compression.

> `./manga.py --overwrite Bleach`

On a Linux/Unix machine, downloads 'Bleach' to `./Bleach`, using `.cbz` compression and overwriting
previously downloaded chapters.

> `1,2,9-12`

Downloads chapters `1`, `2`, and `9` through `12`

> `all`

Downloads all chapters

> `./manga.py -x example.xml`

Parses `example.xml` to run the script.