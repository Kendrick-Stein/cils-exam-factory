"""Real browser-free fixture rendering and immutable-history checks."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pymupdf as fitz
import build_site
from test_build_site import make_fixture

class MuPdfTests(unittest.TestCase):
    def test_real_cjk_multipage_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);papers,docs=make_fixture(root)
            answers=papers/'2000-01-01/FX/answers.md'
            answers.write_text(answers.read_text()+'\n## Lettura avanzata — 中文解析\n\n| Item | Spiegazione |\n|---|---|\n'+''.join(f'| Q{i} | Perché l’argomentazione è coerente. 中文解释：这是答案。 |\n' for i in range(100)))
            argv=['--papers-root',str(papers),'--out',str(docs),'--pdf-engine','mupdf']
            self.assertEqual(build_site.main(argv),0)
            pair=[docs/'papers/2000-01-01/FX'/f'{k}.pdf' for k in ('paper','answers')]
            before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in pair}
            with fitz.open(pair[1]) as doc:
                text=''.join(p.get_text() for p in doc)
                self.assertGreater(len(doc),1)
                self.assertIn('中文',text)
                self.assertNotIn('\ufffd',text)
                for i in range(100):self.assertIn(f'Q{i}',text)
            self.assertFalse((docs/'papers/2000-01-01/FD').exists())
            # Source mtime changes must never regenerate published pairs.
            answers.touch()
            with patch.object(build_site.MuPdfPrinter,'render',side_effect=AssertionError('historical render')):
                self.assertEqual(build_site.main(argv),0)
            self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in pair})
            pair[1].unlink()
            self.assertEqual(build_site.main(argv),1)

if __name__=='__main__':unittest.main()
