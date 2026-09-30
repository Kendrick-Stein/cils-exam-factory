"""Browser discovery and fail-closed PDF rendering; no browser required."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import build_site as site

class PdfTests(unittest.TestCase):
    def test_override_and_invalid_override(self):
        with patch.dict(os.environ, {'CILS_CHROME': '/missing/browser'}):
            with self.assertRaises(site.BuildError): site.find_chrome()
        with patch.dict(os.environ, {'CILS_CHROME': '/bin/true'}):
            self.assertEqual(site.find_chrome(), Path('/bin/true'))

    def test_linux_and_missing(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(site, 'CHROME', Path('/missing')), patch.object(site.shutil, 'which', side_effect=lambda n: '/usr/bin/chromium' if n == 'chromium' else None):
            self.assertEqual(site.find_chrome(), Path('/usr/bin/chromium'))
        with patch.dict(os.environ, {}, clear=True), patch.object(site, 'CHROME', Path('/missing')), patch.object(site.shutil, 'which', return_value=None):
            with self.assertRaises(site.BuildError): site.find_chrome()

    def test_macos(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(site, 'CHROME', Path('/bin/true')):
            self.assertEqual(site.find_chrome(), Path('/bin/true'))

    def test_render_success_failure_and_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); html = root/'paper.html'; pdf = root/'paper.pdf'
            html.write_text('<p>Fixture</p>')
            def print_pdf(cmd, **kwargs):
                out = Path(next(x.split('=',1)[1] for x in cmd if x.startswith('--print-to-pdf=')))
                out.write_bytes(b'%PDF-1.4\nfixture')
                return subprocess.CompletedProcess(cmd, 0, '', '')
            with patch.object(site, 'find_chrome', return_value=Path('/browser')), patch.object(site.subprocess, 'run', side_effect=print_pdf):
                site.PdfPrinter(True).render(html, pdf, [html])
            self.assertTrue(site.valid_pdf(pdf))
            with patch.object(site, 'find_chrome', side_effect=AssertionError('cache should skip browser')):
                site.PdfPrinter(False).render(html, pdf, [html])
            for result in (subprocess.CompletedProcess([], 0, '', ''), subprocess.CompletedProcess([], 1, '', 'failed'), subprocess.TimeoutExpired([], 120), OSError('missing')):
                before = pdf.read_bytes()
                with patch.object(site, 'find_chrome', return_value=Path('/browser')), patch.object(site.subprocess, 'run', **({'side_effect':result} if isinstance(result, Exception) else {'return_value':result})):
                    with self.assertRaises(site.BuildError): site.PdfPrinter(True).render(html, pdf, [html])
                self.assertEqual(pdf.read_bytes(), before)
            pdf.write_bytes(b'not a PDF')
            with patch.object(site, 'find_chrome', side_effect=site.BuildError('missing')):
                with self.assertRaises(site.BuildError): site.PdfPrinter(False).render(html, pdf, [html])

if __name__ == '__main__': unittest.main()
