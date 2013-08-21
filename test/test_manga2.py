from unittest import TestCase

from underscore import _

import manga2


class TestManga2(TestCase):
    CHAPTERS = manga2.chapters('death note')

    def test_chapters(self):
        # MangaFox has more chapters...
        self.assertEqual(len(TestManga2.CHAPTERS), 112)
        # But MangaPanda has more titles!
        chapters = TestManga2.CHAPTERS['42']

        titles = (_(chapters).chain()
            .map(lambda chapter, index, l: chapter.title)
            .reject(lambda title: title == '').value())

        self.assertEqual(_(titles).first() or '', 'Heaven')
