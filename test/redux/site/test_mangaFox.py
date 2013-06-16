from unittest import TestCase

from redux.site.mangafox import MangaFox


class TestMangaFox(TestCase):
    SERIES = MangaFox.series('toriko')

    def test_chapter_count(self):
        self.assertEqual(len(TestMangaFox.SERIES.chapters), 237)