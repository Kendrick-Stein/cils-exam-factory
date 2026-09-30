"""Regression checks for partial same-day publication revisions."""
import tempfile
import unittest
from pathlib import Path
from build_site import Paper, render_index


class LatestSessionTests(unittest.TestCase):
    def test_partial_revision_retains_other_levels_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units = [('2026-09-29', 'C1'), ('2026-09-30', 'A1'),
                     ('2026-09-30', 'A2'), ('2026-09-30', 'B1'),
                     ('2026-09-30', 'B2'), ('2026-09-30-r1', 'A2'),
                     ('2026-09-30-r2', 'A1'), ('2026-09-30-r10', 'A1')]
            papers = []
            for date, level in units:
                folder = root / 'papers' / date / level
                folder.mkdir(parents=True)
                for kind in ('paper', 'answers'):
                    (folder / f'{kind}.pdf').write_bytes(b'%PDF-fixture')
                papers.append(Paper(date, level, folder, {}))
            page = render_index(papers, root)
            latest = page.split('id="sessione">')[1].split('</section>')[0]
            self.assertEqual(latest.count('<article'), 4)
            self.assertIn('4 fascicoli pubblicati', latest)
            for date, level in [('2026-09-30-r10', 'A1'), ('2026-09-30-r1', 'A2'),
                                ('2026-09-30', 'B1'), ('2026-09-30', 'B2')]:
                for kind in ('paper', 'answers'):
                    self.assertIn(f'papers/{date}/{level}/{kind}.pdf', latest)
            self.assertNotIn('papers/2026-09-29/C1', latest)
            self.assertIn('C1: per questa data', latest)
            self.assertIn('C2 non è incluso', latest)
            self.assertIn('papers/2026-09-29/C1/paper.pdf', page)
            self.assertNotIn('Cinque fascicoli', page)

    def test_empty_collection(self):
        self.assertIn('Nessun fascicolo pubblicato', render_index([], Path('/tmp')))


if __name__ == '__main__':
    unittest.main()
