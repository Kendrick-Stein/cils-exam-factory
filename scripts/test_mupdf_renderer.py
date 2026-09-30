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
    def test_glossary_icon_extracts_correctly_without_changing_pixels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            papers, _ = make_fixture(root)
            source = papers / '2000-01-01/FX/answers.md'
            source.write_text('# 📚 Glossario\n\nCittà, caffè, più. 中文解释。\n', encoding='utf-8')
            paths = [source, source.with_name('manifest.yaml')]
            original, corrected = root / 'original.pdf', root / 'corrected.pdf'
            with patch.object(build_site, 'repair_story_tounicode', return_value=None):
                build_site.MuPdfPrinter().render(root / 'original.html', original, paths)
            build_site.MuPdfPrinter().render(root / 'corrected.html', corrected, paths)
            with fitz.open(original) as before, fitz.open(corrected) as after:
                self.assertEqual(len(before), len(after))
                self.assertIn('📚 Glossario', after[0].get_text())
                self.assertIn('Città, caffè, più. 中文解释。', after[0].get_text(flags=0))
                for old, new in zip(before, after):
                    self.assertEqual(old.get_pixmap(alpha=False).samples,
                                     new.get_pixmap(alpha=False).samples)

    def test_strikethrough_preserves_inline_markdown_and_literals(self):
        cases = (
            ('~~laboratorio~~', '<p><del>laboratorio</del></p>'),
            ('~~**esempio**~~', '<p><del><strong>esempio</strong></del></p>'),
            ('`~~codice~~`', '<p><code>~~codice~~</code></p>'),
            (r'\~\~letterale\~\~', '<p>~~letterale~~</p>'),
            ('~~~letterale~~~', '<p>~~~letterale~~~</p>'),
            ('~~ aperto ~~', '<p>~~ aperto ~~</p>'),
            ('[link](https://example.com/~~path~~)',
             '<p><a href="https://example.com/~~path~~">link</a></p>'),
        )
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'inline.md'
            for markdown, expected in cases:
                with self.subTest(markdown=markdown):
                    source.write_text(markdown, encoding='utf-8')
                    self.assertEqual(build_site.render_markdown(source)[1], expected)

    def test_worked_examples_have_visible_strikethrough_in_html_and_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            papers, _ = make_fixture(root)
            source = papers / '2000-01-01/FX/paper.md'
            source.write_text(
                '# Esempi svolti\n\n'
                '| Esempio | A | B | C | D |\n|---|---|---|---|---|\n'
                '| 0. | ~~laboratorio~~ | concerto | convegno | festival |\n'
                '| 0. | ~~fotografico~~ | teatrale | sportivo | letterario |\n',
                encoding='utf-8',
            )
            manifest_path = source.with_name('manifest.yaml')
            paper = build_site.Paper('2000-01-01', 'FX', source.parent,
                                     build_site.load_yaml(manifest_path))
            html = build_site.render_page(source, paper, 'paper')
            self.assertNotIn('~~', html)
            for word in ('laboratorio', 'fotografico'):
                self.assertIn(f'<del>{word}</del>', html)
            pdf = root / 'example.pdf'
            build_site.MuPdfPrinter().render(root / 'example.html', pdf, [source, manifest_path])
            with fitz.open(pdf) as document:
                self.assertEqual(len(document), 1)
                page = document[0]
                self.assertNotIn('~', page.get_text())
                for word in ('laboratorio', 'fotografico', 'concerto', 'teatrale'):
                    with self.subTest(word=word):
                        matches = page.search_for(word, flags=0)
                        self.assertEqual(len(matches), 1)
                        bounds = matches[0]
                        rules = [d for d in page.get_drawings()
                                 if d['type'] == 's' and d['rect'].height < 0.1
                                 and abs(d['rect'].x0 - bounds.x0) < 1
                                 and abs(d['rect'].x1 - bounds.x1) < 1
                                 and bounds.y0 + bounds.height * 0.25 < d['rect'].y0
                                 < bounds.y1 - bounds.height * 0.25]
                        if word in ('concerto', 'teatrale'):
                            self.assertEqual(rules, [])
                            continue
                        self.assertEqual(len(rules), 1)
                        # Require actual dark raster pixels across the word,
                        # not just stripped tildes or an invisible PDF path.
                        y = rules[0]['rect'].y0
                        pixels = page.get_pixmap(
                            matrix=fitz.Matrix(4, 4), colorspace=fitz.csGRAY, alpha=False,
                            clip=fitz.Rect(bounds.x0, y - 0.5, bounds.x1, y + 0.5),
                        )
                        dark_columns = sum(min(pixels.samples[x::pixels.width]) < 160
                                           for x in range(pixels.width))
                        self.assertGreater(dark_columns, pixels.width * 0.9)

    def test_native_font_subsets_preserve_pixels_text_and_credits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            papers, optimized = make_fixture(root)
            baseline = root / 'unoptimized'
            answers = papers / '2000-01-01/FX/answers.md'
            answers.write_text(
                answers.read_text() + '\n## Perché è così — 中文解析\n\n'
                '| Item | Spiegazione |\n|---|---|\n' + ''.join(
                    f'| Q{i} | L’argomentazione è coerente: città, più, già, caffè. '
                    '中文解释：请按题目中的信息回答。这是答案。 |\n'
                    for i in range(60)
                ) + '\nDopo la tabella: un’ottima affinità. 中文范文：所有内容必须保留。\n'
            )
            save = fitz.Document.save

            def save_unoptimized(document, filename, *args, **kwargs):
                kwargs.pop('garbage', None)
                kwargs.pop('deflate', None)
                return save(document, filename, *args, **kwargs)

            # Exercise the same real renderer with only its final optimizations
            # disabled, retaining layout, footers, attribution, and coverage gates.
            with patch.object(fitz.Document, 'subset_fonts', return_value=None) as subset, \
                    patch.object(fitz.Document, 'save', new=save_unoptimized):
                self.assertEqual(build_site.main([
                    '--papers-root', str(papers), '--out', str(baseline),
                    '--pdf-engine', 'mupdf',
                ]), 0)
                self.assertEqual(subset.call_count, 2)
                for call in subset.call_args_list:
                    self.assertEqual(call.args, ())
                    self.assertEqual(call.kwargs, {})
            self.assertEqual(build_site.main([
                '--papers-root', str(papers), '--out', str(optimized),
                '--pdf-engine', 'mupdf',
            ]), 0)
            for stem in ('paper', 'answers'):
                relative = Path('papers/2000-01-01/FX') / f'{stem}.pdf'
                old, new = baseline / relative, optimized / relative
                self.assertLess(new.stat().st_size, old.stat().st_size / 2)
                with fitz.open(old) as original, fitz.open(new) as compact:
                    self.assertEqual(len(original), len(compact))
                    if stem == 'answers':
                        self.assertGreater(len(compact), 1)
                        text = ''.join(page.get_text() for page in compact)
                        for expected in ('中文', 'città', 'Testo autentico', 'https://example.com/testo'):
                            self.assertIn(expected, text)
                        self.assertNotIn('\ufffd', text)
                    for index, (before, after) in enumerate(zip(original, compact)):
                        with self.subTest(stem=stem, page=index + 1):
                            self.assertEqual(before.get_text(), after.get_text())
                            a = before.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                            b = after.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                            self.assertEqual((a.width, a.height, a.n), (b.width, b.height, b.n))
                            self.assertEqual(a.samples, b.samples)

    def test_blank_writing_space_has_real_width(self):
        blank = '<table><thead><tr><th></th></tr></thead><tbody><tr><td>&nbsp;<br>&nbsp;<br>&nbsp;</td></tr></tbody></table>'
        content = '<table><tr><th>Item</th></tr><tr><td>Answer</td></tr></table>'
        grid = '<table><tr><th></th><th></th></tr><tr><td>&nbsp;</td><td>&nbsp;</td></tr></table>'
        transformed = build_site.expand_blank_writing_tables(blank)
        self.assertEqual(transformed.count('class="writing-line"'), 3)
        self.assertEqual(build_site.expand_blank_writing_tables(content), content)
        self.assertEqual(build_site.expand_blank_writing_tables(grid), grid)
        with tempfile.TemporaryDirectory() as tmp:
            pdf=Path(tmp)/'writing.pdf'
            css=Path(build_site.__file__).with_name('assets').joinpath('mupdf.css').read_text()
            writer=fitz.DocumentWriter(str(pdf))
            fitz.Story(transformed,user_css=css).write(writer,lambda n,f:(fitz.Rect(0,0,595,842),fitz.Rect(51,48,544,785),None))
            writer.close()
            with fitz.open(pdf) as document:
                rules=[d['rect'] for d in document[0].get_drawings()
                       if d['rect'].width > 450 and d['rect'].height < 1]
                self.assertEqual(len(rules),3)
                self.assertTrue(all(r.x0 >= 51 and r.x1 <= 544 for r in rules))

    def test_writing_task_keeps_prompt_and_all_lines_together(self):
        for line_counts in ((8, 6), (18, 16)):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                papers, docs = make_fixture(root)
                paper = papers / '2000-01-01/FX/paper.md'
                tasks = []
                for number, lines in enumerate(line_counts, start=1):
                    tasks.append(
                        f'\n## Produzione scritta — Prova n. {number}\n\n'
                        f'> TracciaUnica{number}: Racconta una volta in cui hai preparato un piatto '
                        'insieme a un’altra persona. Scrivi quando è successo, con chi eri, '
                        'che cosa avete preparato e perché questa esperienza ti è piaciuta. '
                        'Spiega come avete scelto la ricetta e quali ingredienti avete usato. '
                        'Descrivi ogni fase della preparazione e il risultato finale del vostro lavoro. '
                        'Racconta anche che cosa avete fatto dopo il pranzo e se vorresti ripetere questa esperienza.\n\n'
                        '*Scrivi qui il tuo testo:*\n\n'
                        '| |\n|---|\n| ' + '<br>'.join(['&nbsp;'] * lines) + ' |\n'
                    )
                paper.write_text(
                    '# Test di produzione scritta\n\n'
                    'Tempo a disposizione: 40 minuti. Numero delle prove: 2.\n' +
                    ''.join(tasks) + '\n---\n\n# Test di produzione orale\n\nParla della tua giornata.\n'
                )
                argv = ['--papers-root', str(papers), '--out', str(docs), '--pdf-engine', 'mupdf']
                self.assertEqual(build_site.main(argv), 0)
                with fitz.open(docs / 'papers/2000-01-01/FX/paper.pdf') as document:
                    task_pages = []
                    for number, expected_lines in enumerate(line_counts, start=1):
                        matches = [(i, page) for i, page in enumerate(document)
                                   if f'TracciaUnica{number}' in page.get_text()]
                        self.assertEqual(len(matches), 1)
                        index, page = matches[0]
                        task_pages.append(index)
                        self.assertIn(f'Produzione scritta — Prova n. {number}', page.get_text())
                        self.assertIn('Scrivi qui il tuo testo:', page.get_text())
                        heading = page.search_for(f'Produzione scritta — Prova n. {number}')[0]
                        following = page.search_for(f'Produzione scritta — Prova n. {number+1}')
                        bottom = following[0].y0 if following else 785
                        rules = [d['rect'] for d in page.get_drawings()
                                 if d['rect'].width > 450 and d['rect'].height < 1
                                 and heading.y1 < d['rect'].y0 < bottom]
                        self.assertEqual(len(rules), expected_lines)
                    if line_counts == (18, 16):
                        self.assertNotEqual(*task_pages)
                    for page in document:
                        # No blank-line-only continuation page, even with a footer.
                        self.assertTrue(page.get_text(clip=(0, 0, 595, 800)).strip())

    def test_mixed_tables_keep_following_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);papers,docs=make_fixture(root)
            answers=papers/'2000-01-01/FX/answers.md'
            additions=[]
            expected=[]
            for section in range(3):
                additions.append(f'\n## Tabella mista {section}\n\n| Item | Risposta | Spiegazione |\n|---|---|---|\n')
                for row in range(25):
                    marker=f'UnivocoS{section}R{row}'
                    expected.append(marker)
                    additions.append(f'| {marker} | A | La risposta segue il testo autentico con una spiegazione completa. 中文解释：请按题目中的信息回答。 |\n')
                for paragraph in range(4):
                    marker=f'ModelloDopoTabella{section}Paragrafo{paragraph}'
                    expected.append(marker)
                    additions.append(f'\n{marker}: Ogni mattina faccio colazione. Buongiorno, cerco una camera. 中文范文：所有内容必须保留。\n')
            answers.write_text(answers.read_text()+''.join(additions))
            self.assertEqual(build_site.main(['--papers-root',str(papers),'--out',str(docs),'--pdf-engine','mupdf']),0)
            with fitz.open(docs/'papers/2000-01-01/FX/answers.pdf') as document:
                text=''.join(p.get_text() for p in document)
                for marker in expected:self.assertIn(marker,text)
                with self.assertRaises(build_site.BuildError):
                    build_site.require_pdf_coverage(document,['This source sentence is deliberately absent'],answers)

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
