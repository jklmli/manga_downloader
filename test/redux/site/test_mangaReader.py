from unittest import TestCase

from redux.site.mangareader import MangaReader


class TestMangaFox(TestCase):
    SERIES = MangaReader.series('gantz')

    def test_chapter_count(self):
        self.assertEqual(len(TestMangaFox.SERIES.chapters), 383)