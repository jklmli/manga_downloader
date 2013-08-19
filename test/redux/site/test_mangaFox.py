from unittest import TestCase

from redux.site.mangafox import MangaFox


class TestMangaFox(TestCase):
    SERIES = MangaFox.series('gantz')
    CHAPTERS = SERIES.chapters

    def test_chapter_count(self):
        self.assertEqual(len(TestMangaFox.CHAPTERS), 386)

    def test_chapter_title(self):
        self.assertEqual(TestMangaFox.CHAPTERS[-2].title, 'Lightning Counterstrike')