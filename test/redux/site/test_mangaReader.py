from unittest import TestCase

from redux.site.mangareader import MangaReader


class TestMangaFox(TestCase):
    SERIES = MangaReader.series('gantz')
    CHAPTERS = SERIES.chapters

    def test_chapter_count(self):
        self.assertEqual(len(TestMangaFox.SERIES.chapters), 383)

    def test_chapter_title(self):
        self.assertEqual(TestMangaFox.CHAPTERS[-2].title, 'Lightning Counterstrike')