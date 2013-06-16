from unittest import TestCase

from redux.site.mangahere import MangaHere


class TestMangaHere(TestCase):
    SERIES = MangaHere.series('toriko')

    def test_chapter_count(self):
        self.assertEqual(len(TestMangaHere.SERIES.chapters), 237)