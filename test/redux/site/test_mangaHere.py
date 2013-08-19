from unittest import TestCase

from redux.site.mangahere import MangaHere


class TestMangaHere(TestCase):
    SERIES = MangaHere.series('gantz')
    CHAPTERS = SERIES.chapters

    def test_chapter_count(self):
        self.assertEqual(len(TestMangaHere.SERIES.chapters), 377)

    def test_chapter_title(self):
        self.assertEqual(TestMangaHere.CHAPTERS[-2].title, 'Lightning Counterstrike')

    def test_chapter_pages(self):
        self.assertEqual(len(TestMangaHere.CHAPTERS[0].pages), 43)
