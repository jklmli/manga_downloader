from unittest import TestCase

from redux.site.mangapanda import MangaPanda


class TestMangaPanda(TestCase):
    SERIES = MangaPanda.series('toriko')

    def test_chapter_count(self):
        self.assertEqual(len(TestMangaPanda.SERIES.chapters), 237)
