# B1 corpus — 2026-09-30

S1 only. No paper authoring. Original Italian prose, cleaned only of navigation, images, captions and web controls. Six distinct URLs; no historical used-sources URL reused. All licenses permit adaptation and publication subject to attribution. Publication must expose attribution and license information alongside the downloadable material; an inaccessible private manifest is not sufficient.

## Pool-first and fetch record

pool_select run for T1 news_general 400–480; T2 practical_realia 300–360; T3 blogs_lifestyle 250–300; T4 news_general 230–260; T5 interview 200–240; T6 news_general 170–200. Only T3 returned a candidate (Viaggiapiccoli Malta); rejected because no explicit adaptation/publication license established. All other queries returned []. Live fallback uses openly licensed sources outside the preferred list because ordinary public access is not copyright permission.

Reading authoring target: T1 410 + T2 305 + T3 255 = 970 words. Bands remain hard limits; source full text can exceed them for bounded excerpt selection.


## T1 — Intervista a Mario Furlan

```json

{
  "slot": "T1",
  "used_in": [
    "L1"
  ],
  "url": "https://it.wikinews.org/wiki/Intervista_a_Mario_Furlan",
  "title": "Intervista a Mario Furlan",
  "publisher": "Wikinotizie",
  "authors": [
    "Ferdi2005",
    "Bramfab",
    "Wikinotizie contributors"
  ],
  "published": "2023-01-30",
  "genre": "interview",
  "cefr": "B2",
  "usable_levels": [
    "B1",
    "B2"
  ],
  "band": [
    400,
    480
  ],
  "target_words": 410,
  "license": "CC BY 4.0",
  "license_url": "https://creativecommons.org/licenses/by/4.0/",
  "hard_lexis": "5–7%",
  "accessed": "2026-09-30",
  "adapted": true,
  "words_used": null,
  "license_verified": true,
  "status": "accepted_with_adaptation",
  "license_evidence_url": "https://it.wikinews.org/wiki/Intervista_a_Mario_Furlan",
  "text_file": "papers/2026-09-30/B1/source-texts/T1.txt",
  "original_words": 655,
  "average_words_per_sentence": 15.6,
  "attribution_requirements": "Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement.",
  "pool_source_file": "factory/corpus/pool/eb97c97012b6.md"
}

```

### License evidence

Original HTML footer explicitly licenses post-25-09-2005 texts CC BY 4.0; article is dated 2023. Full interview fetched in Italian with curl browser UA.

License terms: https://creativecommons.org/licenses/by/4.0/ ; Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement.

### CEFR verdict

ACCEPT WITH ADAPTATION (B2 → B1), at most one level. Passato prossimo and imperfetto in personal experience: «ho cancellato», «volevo», «Mi sembrava» Relative and conditional structures: «se chiunque può», «Se non esistesse, bisognerebbe» Ordinary internet/study vocabulary; some harder terms «veridicità», «soppesate», «distopico»

Anchor comparison: Authentic question-answer human-interest text, comparable in layout and personal-experience register to the B1 Alessandra Pallanti anchor; thematic abstraction is slightly harder.

Quantitative sanity: 655 whitespace-delimited words; 15.6 words/sentence; estimated non-everyday vocabulary 5–7%. Estimates are editorial judgments, not vocabulary-frequency measurements.

### Bounded adaptation plan

Select introduction plus question-answer blocks 1–4 and the final block on paper/digital reading or sibling projects to reach about 410 words. Drop the 52-word historical Encyclopédie question, legal-license question, Fahrenheit allusion and institutional thanks. Split at most four long sentences; replace at most six harder words with common synonyms. Preserve the speaker’s opinions, tense distinctions, question-answer structure and attribution; no new biographical facts. This is a historical interview, not a current endorsement or current news.

### Full cleaned original Italian text

Wikinotizie vi presenta un'intervista a Mario Furlan. Giornalista, docente e formatore, fondatore dei City Angels ha accolto il nostro invito a rispondere ad alcune domande, elaborate da Ferdi2005 e Bramfab, sulla sua esperienza con Wikipedia, e il suo giudizio su di essa.

Quando Lei si è imbattuto/a per la prima volta in Wikipedia? Per quale motivo?

È stato una ventina di anni fa. Mi sembrava bizzarra l'idea di dare vita ad una enciclopedia online cui tutti potessero contribuire: come si fa, pensavo, a controllare la veridicità di quanto scritto, se chiunque può mettere mano al testo? Invece i miei dubbi sono stati dissolti dalla serietà e dal rigore di Wikipedia. Che secondo me è, insieme ai motori di ricerca, la più utile creatura del web.

Dopo di che, col passare degli anni, come è cambiata la sua confidenza con l'enciclopedia? È rimasta invariata o ne è diventato un utilizzatore abitudinario?

Da almeno una quindicina di anni sono un quotidiano utilizzatore di Wikipedia. È accurata, degna di fiducia e democratica: chiunque può farsi una cultura gratuitamente. Se non esistesse, bisognerebbe inventarla!

Ha mai modificato delle pagine di Wikipedia o avuto la tentazione di farlo? Come è andata?

È stato un disastro: da cavernicolo tecnologico quale sono, ho cancellato tutta una voce che volevo semplicemente modificare. Per fortuna sono riuscito a tornare indietro e azzerare i danni...

Come valuta l'impatto che Wikipedia ha avuto nel suo ambiente di lavoro/studio?

Ha avuto un grande impatto positivo. Consiglio ai miei studenti all'università di consultare Wikipedia, soprattutto quando si tratta di argomenti delicati, che possono influenzare l'opinione pubblica. Una sola parola in più o in meno può fare la differenza, quando, ad esempio, si parla di politica. E su Wikipedia anche le singole parole vengono, giustamente, soppesate con attenzione.

Wikipedia è nata e cresciuta senza una redazione e senza direttori, in opposizione alle maggiori enciclopedie cartacee e anche all'Encyclopédie, di d'Alembert e Diderot, eppure il suo successo sembra dimostrare che questa modalità di scrivere un'enciclopedia sia quello che consenta maggiormente di raggiungere l'obiettivo di aggregare il sapere dell'umanità. Cosa ne pensa a riguardo?

Ero molto scettico, oggi sono molto favorevole! È la dimostrazione che è possibile cooperare per il bene comune.

Se lei avesse la biografia scritta in Wikipedia questa sarebbe è distribuita secondo una licenza libera che consente di riutilizzarla gratuitamente anche a scopi commerciali, cosa ne pensa? Appoggia la scelta di scrivere l'enciclopedia secondo una licenza libera o secondo lei dovrebbe essere più restrittiva?

Appoggio totalmente la scelta di lasciare la licenza libera. Viviamo in una società dove le restrizioni e i divieti si moltiplicano costantemente per motivi economici e speculativi, quindi per favore lasciamo libere le licenze di Wikipedia!

Cosa ne pensa di un possibile futuro senza testi cartacei, in cui la conoscenza sia trasmessa gratuitamente, soltanto digitalmente su testi liberamente modificabile?

Mi auguro che anche in futuro i testi digitali possano convivere con quelli cartacei; un mondo privo di libri cartacei mi sembra distopico, alla Fahrenheit 451. Certamente sono favorevole ad un futuro in cui la conoscenza sia sempre più accessibile a tutti, gratuitamente, in tutto il mondo.

Ha mai sentito parlare dei progetti fratelli di Wikipedia, come Wikinotizie? O anche Wikisource, la libreria che si pone lo scopo di raccogliere e preservare i testi entrati nel pubblico dominio? Che cosa ne pensa a riguardo?

Ne penso tutto il bene possibile, così come di Wikimedia Commons! Sono tutti strumenti atti a divulgare cultura e conoscenza, quindi preziosi. E per questo voglio ringraziare Jimmy Wales, Larry Sanger e tutti i wikipediani, che ogni giorno, in silenzio, come formichine operose contribuiscono a diffondere il sapere. Credo che mai come oggi, nell'era delle fake news, questo sia fondamentale. Non solo per la nostra formazione intellettuale, ma anche per farci un'idea di ciò che avviene nel mondo. Pertanto ritengo che Wikipedia sia utile anche per la difesa della democrazia, che per vivere ha bisogno che i cittadini conoscano la verità.


## T2 — Wiki Loves Monuments 2026 – Regolamento

```json

{
  "slot": "T2",
  "used_in": [
    "L2"
  ],
  "url": "https://www.wikimedia.it/news/wiki-loves-monuments-2026-regolamento/",
  "title": "Wiki Loves Monuments 2026 – Regolamento",
  "publisher": "Wikimedia Italia",
  "authors": [
    "Simona Cannataro",
    "Wikimedia Italia"
  ],
  "published": "2026-07-08",
  "genre": "practical_realia",
  "cefr": "B2",
  "usable_levels": [
    "B1",
    "B2"
  ],
  "band": [
    300,
    360
  ],
  "target_words": 305,
  "license": "CC BY-SA 3.0",
  "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
  "hard_lexis": "6–8% full regulation; selected concrete clauses about 4–5%",
  "accessed": "2026-09-30",
  "adapted": true,
  "words_used": null,
  "license_verified": true,
  "status": "accepted_with_adaptation",
  "license_evidence_url": "https://www.wikimedia.it/news/wiki-loves-monuments-2026-regolamento/",
  "text_file": "papers/2026-09-30/B1/source-texts/T2.txt",
  "original_words": 1643,
  "average_words_per_sentence": 23.1,
  "attribution_requirements": "Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement. Keep adapted text under CC BY-SA 3.0 (or an explicitly permitted compatible successor); no additional restrictions.",
  "pool_source_file": "factory/corpus/pool/244b5c7d7e52.md"
}

```

### License evidence

Original HTML footer: «Tutti i contenuti del sito sono disponibili con licenza CC BY-SA 3.0 salvo diversamente specificato.» No exception on the regulation text. The separate CC BY-SA 4.0 rule concerns entrants’ photographs, not this article.

License terms: https://creativecommons.org/licenses/by-sa/3.0/ ; Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement. Keep adapted text under CC BY-SA 3.0 (or an explicitly permitted compatible successor); no additional restrictions.

### CEFR verdict

ACCEPT WITH ADAPTATION (B2 → B1), at most one level. Real binding contest rules use dovere, potere, future and impersonal/passive forms Clear conditional duties: valid email, museum entrance rules and photograph requirements Legal references and embedded clauses raise full regulation to B2; concrete participation clauses fit B1 after selection

Anchor comparison: Same genuine photo-contest-regulation genre as the B1 #quellidellabiblioteca anchor, with explicit eligibility, format and deadlines.

Quantitative sanity: 1643 whitespace-delimited words; 23.1 words/sentence; estimated non-everyday vocabulary 6–8% full regulation; selected concrete clauses about 4–5%. Estimates are editorial judgments, not vocabulary-frequency measurements.

### Bounded adaptation plan

Select only participation, dates, authorship/originality, permitted formats, site access costs and award timing clauses from arts 1–3 and 8, for about 305 words. Remove addresses, identifiers, legal citations and liability provisions rather than rewriting them. Split long clauses and replace «previa» by «dopo la» if needed; preserve all quantities, limits and dates. Do not imply this is a current invitation after the stated 30-09-2026 deadline.

### Full cleaned original Italian text

Wikimedia Italia – Associazione per la diffusione della conoscenza libera – APS-ETS, associazione di promozione sociale con sede legale in via Bergognone, 34 – 20144, Milano – P. IVA IT05599740965, C.F. 94039910156 organizza il concorso Wiki Loves Monuments Italia 2026.

Tale concorso si propone di valorizzare e documentare l’immenso patrimonio culturale dell’Italia sul web, promuovendo la sua ricchezza artistico-culturale presso una vasta platea internazionale, in particolare, attraverso la promozione della conoscenza e i progetti a contenuto libero sostenuti da Wikimedia Foundation e da Wikimedia Italia stessa, tra i quali Wikipedia.

Art. 1 – Definizione del concorso

Wiki Loves Monuments è un concorso fotografico che potenzia la visibilità dei monumenti e invita ciascuno a essere protagonista nel documentare, valorizzare e tutelare il patrimonio culturale.

Il concorso fotografico è pertanto escluso dal regime di cui al DPR 430/01 in forza dell’articolo 6, comma 1, lettera a) della norma in quanto viene indetto “per la produzione di opere […] artistiche” per le quali i premi agli autori rappresentano “un titolo d’incoraggiamento nell’interesse della collettività”.

L’iniziativa si inserisce in un contesto internazionale: le edizioni nazionali e/o locali di Wiki Loves Monuments sono infatti promosse contemporaneamente dal 1º al 30 settembre o dal 1º al 31 ottobre in diversi Paesi del mondo.

Il concorso Wiki Loves Monuments Italia 2026 si svolge dal 1º al 30 settembre 2026 ed è strutturato in due livelli:

Il concorso nazionale;

I concorsi regionali e locali, organizzati da volontari delegati da Wikimedia Italia.

Art. 2 – Requisiti e modalità di partecipazione

La partecipazione al concorso è gratuita e aperta a tutti, italiani o stranieri, previa registrazione sul sito Wikimedia Commons.

Sono esclusi dall’assegnazione di premi i membri degli organi statutari di Wikimedia Italia, loro dipendenti e i collaboratori retribuiti, che potranno però partecipare al caricamento di fotografie nell’ambito del concorso. Sono inoltre esclusi dall’assegnazione di premi i soggetti che verranno chiamati a formare le giurie di cui ai successivi articoli 4, 5 e 6.

I partecipanti, all’atto della registrazione su Wikimedia Commons, dovranno specificare un proprio indirizzo e-mail valido in modo da poter essere contattati privatamente da Wikimedia Italia. La mancata indicazione di un indirizzo e-mail valido comporta l’impossibilità di concorrere al premio.

Le informazioni relative al trattamento dei dati personali sono riportate nella procedura di registrazione su Wikimedia Commons.

Tutti i partecipanti sono chiamati a rispettare le regole di comportamento vigenti presso i luoghi dove ha sede ogni singolo bene o monumento. Partecipare al concorso non implica possedere particolari privilegi nell’accesso alle sedi dei monumenti (salvo diversamente indicato dai gestori del luogo). Per esempio, se vige il divieto di utilizzare il cavalletto o il flash, tale divieto va rispettato; se è richiesto il pagamento di un biglietto d’ingresso a un museo, sarà necessario acquistarlo. I partecipanti non possono vantare titolo al rimborso di eventuali costi sostenuti, inclusi quelli di accesso ai monumenti.

I partecipanti, nella partecipazione al concorso, non sono considerati volontari (neppure occasionali) ai sensi dell’art. 17 del D Lgs 117/17 e gli organizzatori non sono ritenuti responsabili dei danni che i partecipanti possono procurare a sé stessi, a terzi o a cose.

Art. 3 – Requisiti delle fotografie che partecipano al concorso

Le fotografie (di seguito indicate anche come “opere”):

devono essere realizzate e caricate esclusivamente dal fotografo che partecipa al concorso;

devono essere caricate su Wikimedia Commons durante il mese di settembre con licenza Creative Commons Attribuzione Condividi allo stesso modo (CC BY-SA 4.0);

possono essere state scattate anche precedentemente, ma non devono essere già state pubblicate su Wikimedia Commons o su altri siti web, social network o pubblicazioni cartacee prima dell’inizio del concorso;

devono avere come soggetto un bene culturale o una vista di insieme scelti tra quelli presenti nelle liste pubblicate sulla web-app app.wikilovesmonuments.it;

devono preferibilmente essere caricate attraverso la procedura guidata apposita; è possibile, ma sconsigliato, utilizzare il caricamento manuale, ricordandosi però di inserire il codice identificativo del bene culturale (ID) e le categorie appropriate;

devono avere un breve titolo descrittivo del soggetto ripreso, che comprenda un breve riferimento al nome del monumento o alla vista d’insieme con alcuni dettagli ulteriori; sono caldamente sconsigliati i nomi generati dallo scatto della foto (p. es. codici alfanumerici o nomi generici e non significativi);

devono essere caricate in uno dei formati ammessi da Wikimedia Commons, come per esempio JPEG, PNG e TIFF e pubblicate accettando per intero la licenza “Creative Commons Attribuzione – Condividi allo stesso modo 4.0” proposta dal sistema (il cui testo legale integrale è disponibile all’indirizzo https://creativecommons.org/licenses/by-sa/4.0/legalcode) o licenze più aperte;

devono avere la massima risoluzione e la minima compressione possibili;

possono essere modificate solo con tecniche quali adattamenti della luminosità, contrasto e colore, sovraesposizione e sottoesposizione;

non devono riportare firme, filigrane, cornici, scritte o disegni sovraimpressi.

Ogni fotografo può caricare fotografie per un numero illimitato di soggetti diversi. Per un singolo soggetto ciascun fotografo può eccedere la soglia di 5 fotografie solo avendo cura di scegliere angolazioni[3.1] o condizioni di luce significativamente diverse[3.2]. In caso di superamento della soglia senza il rispetto del suddetto principio di differenziazione, gli organizzatori si riservano il diritto di squalificare le sole foto ripetute o tutte le foto del concorrente indipendentemente dal soggetto ritratto.

3.1. Ad esempio le diverse stazioni di una via crucis o le opere all’interno di un museo.

3.2 A esempio diurna estiva, diurna invernale, innevata, notturna, luce dell’ora blu, ombre lunghe dell’alba.

Art. 4 – Pregiuria nazionale

Una pregiuria nominata da Wikimedia Italia sceglierà, a proprio insindacabile giudizio, una preselezione delle fotografie che partecipano al concorso secondo i criteri descritti nel bando.

Art. 5 – Giuria nazionale

La composizione della giuria sarà pubblicata sul sito ufficiale del concorso entro la metà del mese di settembre.

La giuria, a suo insindacabile giudizio, sceglierà, tra le opere selezionate dalla pregiuria, quelle vincitrici, assegnando i premi ai loro autori/partecipanti.

Art. 6 – Giurie regionali e locali

La composizione delle giurie regionali e locali sarà resa pubblica entro la metà del mese di settembre.

Le giurie regionali e locali, a loro insindacabile giudizio, sceglieranno le opere vincitrici, assegnando i premi ai loro autori/partecipanti.

Gli organizzatori dei concorsi regionali e locali possono nominare pregiurie regionali e locali che effettueranno, a proprio insindacabile giudizio, una preselezione delle opere che partecipano al concorso regionale o locale secondo i criteri descritti nel bando.

Art. 7 – Criteri per la selezione delle opere finaliste

I criteri che saranno utilizzati da parte delle giurie per la valutazione e la scelta delle opere finaliste, laddove applicabili, sono:

qualità tecnica, includendo in questo anche la definizione e risoluzione dell’immagine, a cui verrà assegnato un peso nella valutazione pari al 30% del punteggio totale assegnato;

interpretazione personale ed equilibrio tra capacità narrativa ed estetizzazione, a cui verrà assegnato un peso pari al 20% del punteggio totale assegnato;

utilità per Wikipedia: qualità dell’immagine bilanciata con le esigenze di rappresentazione documentaria a cui verrà assegnato un peso pari al 50% del punteggio totale assegnato.

A parità di valutazione, saranno privilegiate le immagini di monumenti scarsamente rappresentati nelle precedenti edizioni.

Le 10 fotografie finaliste parteciperanno alla fase internazionale di Wiki Loves Monuments 2026, insieme alle finaliste degli altri Paesi coinvolti dal concorso.

Ogni partecipante può ricevere un solo premio per ogni fase del concorso (regionale/locale e nazionale).

Art. 8 – Scadenza e data di premiazione

Le fotografie possono essere caricate a partire dalle 00:00:00 (ora italiana) del 1º settembre 2026. La data ultima di scadenza per caricare in Wikimedia Commons le proprie fotografie è fissata alle ore 23:59:59 (ora italiana) del 30 settembre 2026.

La premiazione del concorso nazionale avverrà entro 4 mesi dal termine del concorso, in data e luogo che verranno successivamente definiti.

Le premiazioni dei concorsi regionali e locali avverranno entro 5 mesi dal termine del concorso, in date e luoghi che verranno successivamente definiti.

Art. 9 – Natura dei premi, montepremi e consegna

I premi sono offerti da Wikimedia Italia e da suoi donatori, sponsor e partner tecnici. Il valore del montepremi verrà reso noto sul sito ufficiale del concorso e verrà calcolato sul totale del valore commerciale degli oggetti IVA inclusa.

Wikimedia Italia avrà la facoltà di consegnare di volta in volta i premi alla cerimonia di premiazione.

Per il concorso nazionale saranno premiati i primi 10 autori delle migliori fotografie in classifica caricate su Wikimedia Commons secondo le indicazioni del presente Regolamento. Di queste 10 fotografie, 5 saranno selezionate tra quelle raffiguranti un monumento appartenente alla categoria “ville e palazzi storici“[9.1] presente nell’apposito elenco “Ville e palazzi storici”) e altre 5 tra quelle raffiguranti un’altra tipologia di bene culturale presente nell’apposito elenco. Gli elenchi di questi monumenti, filtrabili per categoria, sono disponibili sul sito del concorso.

Per i concorsi regionali e locali il numero e l’entità dei premi saranno pubblicati sul sito del concorso entro il 15 settembre 2026. In ogni caso potranno essere premiati esclusivamente gli autori di opere caricate su Wikimedia Commons secondo le indicazioni del presente Regolamento, indipendentemente dal soggetto raffigurato, purché facente parte di uno degli elenchi sopra indicati.

Gli organizzatori dei concorsi regionali e locali possono assegnare eventuali premi speciali sulla base di uno specifico tema o di un’area geografica.

9.1. Rientrano in questa categoria i seguenti monumenti edificati prima del 1950: ville, palazzi residenziali, palazzi di rappresentanza, casali, masserie e cascine, limitatamente a quelli presenti negli elenchi disponibili su app.wikilovesmonuments.it.

Art. 10 – Variazioni

Qualsiasi variazione riguardante le modalità di partecipazione potrà essere adottata solo da Wikimedia Italia e, qualora ricorra la necessità, comunicata ai partecipanti.

Art. 11 – Accettazione del Regolamento

La partecipazione al concorso implica la conoscenza e accettazione integrale del presente regolamento.

Art. 12 – Pubblicazione del Regolamento e miscellanea

Il Regolamento e bando di concorso vengono pubblicati sul sito ufficiale di Wikimedia Italia.

Gli organizzatori non potranno essere ritenuti in alcun modo responsabili dell’uso che terzi potranno fare delle foto scaricate dai siti riferibili agli organizzatori medesimi.

Per ulteriori informazioni, scrivere al seguente indirizzo e-mail: contatti@wikilovesmonuments.it


## T3 — Le avventure di Pinocchio (1892), Capitolo IX

```json

{
  "slot": "T3",
  "used_in": [
    "L3"
  ],
  "url": "https://it.wikisource.org/wiki/Le_avventure_di_Pinocchio_(1892)/Capitolo_9",
  "title": "Le avventure di Pinocchio (1892), Capitolo IX",
  "publisher": "Wikisource",
  "authors": [
    "Carlo Collodi",
    "Wikisource contributors"
  ],
  "published": "1892",
  "genre": "literature_public_domain",
  "cefr": "B2",
  "usable_levels": [
    "B1",
    "B2"
  ],
  "band": [
    250,
    300
  ],
  "target_words": 255,
  "license": "CC BY-SA 3.0 (transcription); underlying 1892 Collodi text public domain",
  "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
  "hard_lexis": "5–7% untrimmed chapter; selected action/dialogue 4–5%",
  "accessed": "2026-09-30",
  "adapted": true,
  "words_used": null,
  "license_verified": true,
  "status": "accepted_with_adaptation",
  "license_evidence_url": "https://it.wikisource.org/wiki/Le_avventure_di_Pinocchio_(1892)/Capitolo_9",
  "text_file": "papers/2026-09-30/B1/source-texts/T3.txt",
  "original_words": 652,
  "average_words_per_sentence": 13.6,
  "attribution_requirements": "Credit Carlo Collodi, novel/chapter/edition, Wikisource contributors, source URL and CC BY-SA 3.0 link; identify cuts and modernization, retain share-alike for adapted transcription, and do not imply endorsement.",
  "pool_source_file": "factory/corpus/pool/58ecdd35aca4.md"
}

```

### License evidence

Page metadata explicitly says CC BY-SA 3.0 and GFDL for the transcription; page names Carlo Collodi and the 1892 edition. Current footer links CC BY-SA. For conservative reuse, comply with transcription CC BY-SA 3.0 even though the original nineteenth-century novel is public domain. Text fetched directly from original HTML and compared to the displayed page.

https://creativecommons.org/licenses/by-sa/3.0/

Credit Carlo Collodi, novel/chapter/edition, Wikisource contributors, source URL and CC BY-SA 3.0 link; identify cuts and modernization, retain share-alike for adapted transcription, and do not imply endorsement.

### CEFR verdict

ACCEPT WITH ADAPTATION (B2 → B1). Concrete sequential action and dialogue: school journey, heard music, arrival, sign-reading, ticket price, unsuccessful offers and sale Narration has passato remoto and a few archaic lexical forms; speech has ordinary present/future/conditional, simple clauses Repeated demonstratives and responses supply authentic coherence: «Quei suoni», «quel baraccone», «Allora», «Quattro soldi», «ultima offerta», «E il libro fu venduto»

An authentic concrete action narrative, replacing the weak school diary; dialogue and financial problem are self-contained like the B1 travel-story anchor, though the source tense/orthography requires one-level modernization.

652 whitespace words; 13.6 words/sentence; estimated hard lexis 5–7% untrimmed chapter; selected action/dialogue 4–5%.

### Bounded adaptation plan

Retain the first school-route sentence then select the music-to-theatre and ticket-price-to-book-sale chain; omit the fantasy paragraph, sound imitations, clothing-offer repetitions and final moralizing aside to approach 255–280 words. Modernize at most ten narrator passato-remoto forms and at most six archaic/common lexical forms (e.g. menava→portava, anderò→andrò, risoluzione→decisione), and split long sentences. Keep direct dialogue, price of four soldi, book identity and cause/effect unchanged. Preserve at least 11 genuine connected units with explicit source anaphora and question/answer dependencies; no invented transport, chronology or actions. If 11 unique units cannot be kept under the allowed changes, flag rather than force a reconstruction.

### Full cleaned original Italian text

Smesso che fu di nevicare, Pinocchio, col suo bravo Abbecedario nuovo sotto il braccio, prese la strada che menava alla scuola: e strada facendo, fantasticava nel suo cervellino mille ragionamenti e mille castelli in aria uno più bello dell’altro.

E discorrendo da sè solo, diceva:

— Oggi, alla scuola, voglio subito imparare a leggere: domani poi imparerò a scrivere, e domani l’altro imparerò a fare i numeri. Poi, colla mia abilità, guadagnerò molti quattrini e coi primi quattrini che mi verranno in tasca, voglio subito fare al mio babbo una bella casacca di panno. Ma che dico di panno? Gliela voglio fare tutta d’argento e d’oro, e coi bottoni di brillanti. E quel pover’uomo se la merita davvero: perchè, insomma, per comprarmi i libri e per farmi istruire, è rimasto in maniche di camicia.... a questi freddi! Non ci sono che i babbi che sieno capaci di certi sacrifizi!...

Mentre tutto commosso diceva così, gli parve di sentire in lontananza una musica di pifferi e di colpi di grancassa: pì-pì-pì, pì-pì-pì, zum, zum, zum, zum.

Si fermò e stette in ascolto. Quei suoni venivano di fondo a una lunghissima strada traversa, che conduceva a un piccolo paesetto fabbricato sulla spiaggia del mare.

— Che cosa sia questa musica? Peccato che io debba andare a scuola, se no.... —

E rimase lì perplesso. A ogni modo, bisognava prendere una risoluzione; o a scuola, o a sentire i pifferi.

— Oggi anderò a sentire i pifferi, e domani a scuola. Per andare a scuola c’è sempre tempo — disse finalmente quel monello, facendo una spallucciata.

Detto fatto, infilò giù per la strada traversa e cominciò a correre a gambe. Più correva e più sentiva distinto il suono dei pifferi e dei tonfi della grancassa: pì-pì-pì, pì-pì-pì, pì-pì-pì, zum, zum, zum, zum.

Quand’ecco che si trovò in mezzo a una piazza tutta piena di gente, la quale si affollava intorno a un gran baraccone di legno e di tela dipinta di mille colori.

— Che cos’è quel baraccone? — domandò Pinocchio, voltandosi a un ragazzetto che era lì del paese.

— Leggi il cartello, che c’è scritto, e lo saprai.

— Lo leggerei volentieri, ma per l’appunto oggi non so leggere.

— Bravo bue! Allora te lo leggerò io. Sappi dunque che in quel cartello a lettere rosse come il fuoco, c’è scritto: Gran Teatro dei Burattini....

— È molto che è incominciata la commedia?

— Comincia ora.

— E quanto si spende per entrare?

— Quattro soldi. —

Pinocchio, che aveva addosso la febbre della curiosità, perse ogni ritegno e disse, senza vergognarsi, al ragazzetto, col quale parlava:

— Mi daresti quattro soldi fino a domani?

— Te li darei volentieri, — gli rispose l’altro canzonandolo — ma oggi per l’appunto non te li posso dare.

— Per quattro soldi, ti vendo la mia giacchetta — gli disse allora il burattino.

— Che vuoi che mi faccia di una giacchetta di carta fiorita? Se ci piove su, non c’è più verso di cavarsela da dosso.

— Vuoi comprare le mie scarpe?

— Sono buone per accendere il fuoco.

— Quanto mi dài del berretto?

— Bell’acquisto davvero! Un berretto di midolla di pane! C’è il caso che i topi me lo vengano a mangiare in capo!—

Pinocchio era sulle spine. Stava lì lì per fare un’ultima offerta: ma non aveva coraggio: esitava, tentennava, pativa. Alla fine disse:

— Vuoi darmi quattro soldi di quest’Abbecedario nuovo?

— Io sono un ragazzo e non compro nulla dai ragazzi — gli rispose il suo piccolo interlocutore, che aveva molto più giudizio di lui.

— Per quattro soldi l’Abbecedario lo prendo io — gridò un rivenditore di panni usati, che s’era trovato presente alla conversazione.

E il libro fu venduto lì sui due piedi. E pensare che quel pover’uomo di Geppetto era rimasto a casa, a tremare dal freddo in maniche di camicia, per comprare l’Abbecedario al figliuolo!


## T4 — Le fontanelle nelle città italiane: il progetto di OpenStreetMap Italia si rivela un servizio per la comunità

```json

{
  "slot": "T4",
  "used_in": [
    "S1"
  ],
  "url": "https://www.wikimedia.it/news/le-fontanelle-nelle-citta-italiane-i-dati-aperti-di-openstreetmap-si-rivelano-un-servizio-per-la-comunita/",
  "title": "Le fontanelle nelle città italiane: il progetto di OpenStreetMap Italia si rivela un servizio per la comunità",
  "publisher": "Wikimedia Italia",
  "authors": [
    "Adriana Marino"
  ],
  "published": "2026-07-24",
  "genre": "news_general",
  "cefr": "B2",
  "usable_levels": [
    "B1",
    "B2"
  ],
  "band": [
    230,
    260
  ],
  "target_words": 240,
  "license": "CC BY-SA 3.0",
  "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
  "hard_lexis": "4–6%",
  "accessed": "2026-09-30",
  "adapted": true,
  "words_used": null,
  "license_verified": true,
  "status": "accepted_with_adaptation",
  "license_evidence_url": "https://www.wikimedia.it/news/le-fontanelle-nelle-citta-italiane-i-dati-aperti-di-openstreetmap-si-rivelano-un-servizio-per-la-comunita/",
  "text_file": "papers/2026-09-30/B1/source-texts/T4.txt",
  "original_words": 259,
  "average_words_per_sentence": 32.4,
  "attribution_requirements": "Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement. Keep adapted text under CC BY-SA 3.0 (or an explicitly permitted compatible successor); no additional restrictions.",
  "pool_source_file": "factory/corpus/pool/b7fa7302c41f.md"
}

```

### License evidence

Original article HTML footer explicitly applies CC BY-SA 3.0 to all site content unless otherwise stated. No textual exception; image excluded.

License terms: https://creativecommons.org/licenses/by-sa/3.0/ ; Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement. Keep adapted text under CC BY-SA 3.0 (or an explicitly permitted compatible successor); no additional restrictions.

### CEFR verdict

ACCEPT WITH ADAPTATION (B2 → B1), at most one level. Concrete light-news curiosity on locating public water fountains Present and passato prossimo plus simple relative clauses; nouns support article/preposition gaps Full-source sentence length is above B1 rhythm but can be split without changing facts; «approvvigionamento» is the one main technical noun

Anchor comparison: Light civic/technology news close to Due strani camerieri in topic accessibility and structure-gap opportunities.

Quantitative sanity: 259 whitespace-delimited words; 32.4 words/sentence; estimated non-everyday vocabulary 4–6%. Estimates are editorial judgments, not vocabulary-frequency measurements.

### Bounded adaptation plan

Retain almost the whole 259-word original; omit the Il Post cross-reference and shorten the seven-city list to about 240 words. Split four long sentences and substitute at most four terms such as approvvigionamento. Do not alter project date, relationship between volunteer data and the fountain map, or add claims of completeness.

### Full cleaned original Italian text

Con l’arrivo delle alte temperature, una mappa delle fontanelle pubbliche nelle principali città italiane ha attirato l’attenzione del pubblico, mostrando dove trovare punti di approvvigionamento d’acqua in luoghi come Roma, Milano, Torino, Venezia, Bologna, Palermo e Bari. La mappa, rilanciata recentemente da Il Post, nasce da un lavoro di raccolta e aggiornamento dei dati geografici portato avanti dalla comunità italiana di OpenStreetMap.

Alla base di questo risultato c’è infatti il progetto “Comuni senza POI”, l’iniziativa della comunità italiana di OpenStreetMap sviluppata nel luglio 2025. Il progetto aveva l’obiettivo di individuare e completare la presenza di alcuni punti di interesse POI, dall’inglese “Point of Interest”, ancora mancanti in molti comuni italiani, migliorando la qualità e la completezza della mappa libera.

Tra le categorie prese in considerazione c’erano anche le fontanelle pubbliche, insieme ad altri elementi di interesse quotidiano come scuole, parchi giochi, uffici postali, municipi e luoghi di culto. Grazie al contributo dei volontari della comunità, numerosi dati sono stati aggiunti o aggiornati su OpenStreetMap, rendendo queste informazioni disponibili per mappe, applicazioni e servizi realizzati da chiunque.

La diffusione della mappa delle fontanelle dimostra concretamente il valore dei dati aperti: informazioni raccolte in modo collaborativo dalla comunità possono trasformarsi in strumenti utili per affrontare esigenze quotidiane, dalla ricerca di una fonte d’acqua durante le giornate più calde fino alla conoscenza più approfondita del territorio.

È questo uno degli obiettivi di OpenStreetMap: costruire una rappresentazione aggiornata e condivisa del mondo che ci circonda, grazie al contributo di migliaia di persone che ogni giorno s’impegnano a verificare e migliorare le informazioni geografiche.


## T5 — Intervista a Vincent Russo

```json

{
  "slot": "T5",
  "used_in": [
    "S2"
  ],
  "url": "https://it.wikinews.org/wiki/Intervista_a_Vincent_Russo",
  "title": "Intervista a Vincent Russo",
  "publisher": "Wikinotizie",
  "authors": [
    "Bramfab",
    "Wikinotizie contributors"
  ],
  "published": "2023-06-12",
  "genre": "interview",
  "cefr": "B2",
  "usable_levels": [
    "B1",
    "B2"
  ],
  "band": [
    200,
    240
  ],
  "target_words": 225,
  "license": "CC BY 4.0",
  "license_url": "https://creativecommons.org/licenses/by/4.0/",
  "hard_lexis": "4–6% selected interview",
  "accessed": "2026-09-30",
  "adapted": true,
  "words_used": null,
  "license_verified": true,
  "status": "accepted_with_adaptation",
  "license_evidence_url": "https://it.wikinews.org/wiki/Intervista_a_Vincent_Russo",
  "text_file": "papers/2026-09-30/B1/source-texts/T5.txt",
  "original_words": 772,
  "average_words_per_sentence": 18.4,
  "attribution_requirements": "Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement.",
  "pool_source_file": "factory/corpus/pool/28cc2c248340.md"
}

```

### License evidence

Original article footer explicitly licenses post-25-09-2005 text CC BY 4.0. No exception indicated. Interview is dated 12 June 2023.

License terms: https://creativecommons.org/licenses/by/4.0/ ; Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement.

### CEFR verdict

ACCEPT WITH ADAPTATION (B2 → B1), at most one level. Authentic questions and first-person responses with «ho frequentato», «erano», «l’ho letta», «sono comparse» Future «resterà», present «posso immaginare» and completed study/work experiences Some abstract or colloquial terms; omit the biographical/profanity passage and philosophical long question

Anchor comparison: Question-answer personal learning/work experience matches INTERVISTA A VITTORIA; future print/digital topic offers temporal contrasts.

Quantitative sanity: 772 whitespace-delimited words; 18.4 words/sentence; estimated non-everyday vocabulary 4–6% selected interview. Estimates are editorial judgments, not vocabulary-frequency measurements.

### Bounded adaptation plan

Select first encounter and changing habits blocks plus the question-answer block about the future of paper reading; trim to 225 words. Keep questions bold at authoring and preserve authentic past/present/future distinctions. No invented interviewer prompts, speaker’s future plans or tense changes. Additional selected clauses may be taken from the work/study block to provide sufficient distinct verbs, but do not force all tense categories if unsupported. Exclude profanity and speculative biographical/mortality passages.

### Full cleaned original Italian text

Wikinotizie vi presenta un'intervista a Vincent Russo. Vincent Russo, social media manager del giornale Fatto Quotidiano ha accolto il nostro invito a rispondere ad alcune domande, elaborate da Bramfab, sulla sua esperienza con Wikipedia, e il suo giudizio su di essa.

Quando Lei si è imbattuto/a per la prima volta in Wikipedia? Per quale motivo? Che impressione ne ha ricavato?

Primi anni 2000 è possibile? Insieme ad Amazon.com è stato uno dei primi siti internazionali che ho frequentato. Le pagine erano ancora in inglese, per tanti anni l'ho letta in inglese, poi mano a mano sono comparse le voci anche in italiano.

Dopo di che, col passare degli anni, come è cambiata la sua confidenza con l'enciclopedia? È rimasta invariata o ne è diventato un utilizzatore abitudinario?

Non riesco a immaginare l'internet senza wikipedia. E' quasi sempre la mia prima fonte di informazione su qualsiasi cosa, sia che si tratti di un gruppo musicale, o di qualche storia sportiva, albi, statistiche, l'età dei personaggi famosi.

Ha mai modificato delle pagine di Wikipedia o avuto la tentazione di farlo? Come è andata?

La tentazione macabra mi viene quando muore un personaggio famoso, tale da meritare una voce su wikipedia, di inserire la data di morte. Ma credo di non averlo mai fatto. Mi è capitato invece di aggiornare il profilo dell'azienda per cui ho lavorato, aggiungere qualche dato o cercare di far cancellare qualche "cattiveria" di troppo.

Come valuta l'impatto che Wikipedia ha avuto nel suo ambiente di lavoro/studio?

Ha un grosso rimpianto, mi sono laureato prima dell'avvento massiccio di internet in Italia e di base per lo studio no direi di no. Per il lavoro invece è un discorso a parte, sia per reperire informazioni, o anche solamente per corredare di citazioni una presentazione, questo tipo di cose. Penso però di usarla più per le mie passioni e i miei interessi che per mere questioni di lavoro.

Wikipedia è nata e cresciuta senza una redazione e senza direttori, in opposizione alle maggiori enciclopedie cartacee e anche all'Encyclopédie, di d'Alembert e Diderot, eppure il suo successo sembra dimostrare che questa modalità di scrivere un'enciclopedia sia quello che consenta maggiormente di raggiungere l'obiettivo di aggregare il sapere dell'umanità. Cosa ne pensa a riguardo?

Wikipedia è l'internet, è l'internet compiuta, senza scopo di lucro, vive di donazioni e si alimenta di link, c'è una grande community dietro di appassionati. Per me è la "democrazia di internet". E come la democrazia, anche con tutti i suoi difetti, è la migliore forma di governo conosciuta, così è Wikipedia, non abbiamo la controprova, ma è secondo è uno dei modi migliori di impiegare l'internet al servizio delle persone.

Se presente, ha letto la sua biografia scritta in Wikipedia? Cosa ne pensa? La biografia, come tutte le voci dell'enciclopedia, è distribuita secondo una licenza libera che consente di riutilizzarla gratuitamente anche a scopi commerciali, cosa ne pensa? Appoggia la scelta di scrivere l'enciclopedia secondo una licenza libera o secondo lei dovrebbe essere più restrittiva?

Purtroppo no, non c'è ancora una mia biografia su Wikipedia, e mi spaventa un po' il fatto che un giorno possa apparire, perché sicuramente ci sarà qualche f.d.p che tirerà fuori il mio voto di maturità, o qualcosa che io non avrei mai messo nella mia biografia. Io penso che le voci di bio dovrebbero comparire, se meritevoli di una voce, solo dopo la scomparsa dell'autore, eviterei le voci di persone in vita o le trasformerei in scheda in un forum, in qualche altra cosa ben distinta da una voce vera e propria.

Cosa ne pensa di un possibile futuro senza testi cartacei, in cui la conoscenza sia trasmessa gratuitamente, soltanto digitalmente su testi liberamente modificabile?

Non credo di vedere questo futuro, senza carta, almeno non in questa mia vita. In generale la lettura sulla carta è ancora la preferita non solo di noi persone di mezza età, ma anche dei giovani. Quindi un giorno posso immaginare l'invenzione di un supporto che gli somigli, ma no la carta resterà, anche solo per una piccola élite di persone ma resterà.

Ha mai sentito parlare dei progetti fratelli di Wikipedia, come Wikinotizie? O anche Wikisource, la libreria che si pone lo scopo di raccogliere e preservare i testi entrati nel pubblico dominio? Oppure Wikimedia Commons la grande raccolta, in continua crescita, di immagini in pubblico dominio? Che cosa ne pensa a riguardo?

Wikimedia commons la conosco e ne ho fatto anche uso, conosco anche Wikisource ma non ne avevo mai sentito parlare di Wikinotizie, eppure sono dentro questo settore, che pecca. Felice di avervi conosciuto così e grazie spero di aver dato un buon contributo ai lettori.



Authoring caution (T5): The suggested early-experience + future-paper selection has no conditional. The original also contains «dovrebbero», «eviterei», «trasformerei» in a biography-policy answer, but that passage is more abstract. Do not invent conditional content merely to satisfy a desired tense mix; choose genuine original clauses or flag the slot.

## T6 — Wikipedia per i beni culturali: il laboratorio Wikimedia all’Università degli Studi di Milano

```json

{
  "slot": "T6",
  "used_in": [
    "S3"
  ],
  "url": "https://www.wikimedia.it/news/wikipedia-per-i-beni-culturali-il-laboratorio-wikimedia-alluniversita-degli-studi-di-milano/",
  "title": "Wikipedia per i beni culturali: il laboratorio Wikimedia all’Università degli Studi di Milano",
  "publisher": "Wikimedia Italia",
  "authors": [
    "Adriana Marino"
  ],
  "published": "2026-09-10",
  "genre": "news_general",
  "cefr": "B2",
  "usable_levels": [
    "B1",
    "B2"
  ],
  "band": [
    170,
    200
  ],
  "target_words": 185,
  "license": "CC BY-SA 3.0",
  "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
  "hard_lexis": "6–8% original; selected practical section about 4–5%",
  "accessed": "2026-09-30",
  "adapted": true,
  "words_used": null,
  "license_verified": true,
  "status": "accepted_with_adaptation",
  "license_evidence_url": "https://www.wikimedia.it/news/wikipedia-per-i-beni-culturali-il-laboratorio-wikimedia-alluniversita-degli-studi-di-milano/",
  "text_file": "papers/2026-09-30/B1/source-texts/T6.txt",
  "original_words": 842,
  "average_words_per_sentence": 29.0,
  "attribution_requirements": "Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement. Keep adapted text under CC BY-SA 3.0 (or an explicitly permitted compatible successor); no additional restrictions.",
  "pool_source_file": "factory/corpus/pool/54a71910e744.md"
}

```

### License evidence

Original HTML footer explicitly applies CC BY-SA 3.0 to all site content unless otherwise stated. No textual exception; separately credited image omitted.

License terms: https://creativecommons.org/licenses/by-sa/3.0/ ; Credit title, named author(s), publisher, original URL and license link; indicate excerpting/simplification and do not imply endorsement. Keep adapted text under CC BY-SA 3.0 (or an explicitly permitted compatible successor); no additional restrictions.

### CEFR verdict

ACCEPT WITH ADAPTATION (B2 → B1), at most one level. Authentic report of a local university cultural initiative, with dates and 27 participants Past tense, passives and purpose clauses describe course activities and results Abstract nominal vocabulary can be reduced by selecting practical descriptions rather than data-structure passages

Anchor comparison: Local initiative report with concrete activities and participants comparable to Parchi in movimento, though more academic.

Quantitative sanity: 842 whitespace-delimited words; 29.0 words/sentence; estimated non-everyday vocabulary 6–8% original; selected practical section about 4–5%. Estimates are editorial judgments, not vocabulary-frequency measurements.

### Bounded adaptation plan

Use the opening two paragraphs plus a shortened course-objective paragraph and concrete final results to about 185 words. Remove staff names/titles, English jargon, sandbox/disorfanizzazione, and advanced programme detail. Split at most three sentences and replace at most five abstract words; do not turn the completed June–August event into a future invitation, or invent costs, enrolment routes or requirements.

### Full cleaned original Italian text

Dal 13 giugno al 1° agosto 2026 si è svolta la settima edizione del laboratorio “I progetti Wikimedia per i beni culturali”, inserito nel Master di secondo livello in Digital Humanities dell’Università degli Studi di Milano. L’attività ha coinvolto 27 studenti e ha proposto un percorso pratico dedicato alla conoscenza e all’utilizzo di Wikipedia e degli altri progetti Wikimedia per la valorizzazione e la diffusione del patrimonio culturale.

Il laboratorio, svolto interamente online in modalità live, ha accompagnato gli studenti dalla conoscenza delle principali regole di Wikipedia fino alla realizzazione e pubblicazione di contenuti enciclopedici, con particolare attenzione ai beni culturali.

I docenti e gli obiettivi del laboratorio

Il laboratorio è stato curato da Marco Chemello, formatore e responsabile scuola/università dello staff di Wikimedia Italia, e Luigi Catalani, direttore della Biblioteca nazionale di Potenza, che hanno seguito gli studenti nelle diverse fasi del percorso.

L’obiettivo è stato quello di fornire agli studenti gli strumenti necessari per contribuire in modo consapevole ai progetti Wikimedia, imparando a utilizzare Wikipedia come spazio di produzione e condivisione della conoscenza sul patrimonio culturale.

Nel corso degli incontri sono stati affrontati i principi fondamentali di Wikipedia, le modalità di scrittura e revisione delle voci, la ricerca e l’utilizzo delle fonti, il diritto d’autore e le licenze libere, oltre alle possibilità offerte da Wikimedia Commons e Wikidata. La panoramica è stata accompagnata da un’attività laboratoriale continua: ogni partecipante ha infatti scelto un argomento su cui lavorare, sviluppando progressivamente una voce nella propria sandbox fino alla revisione finale e alla pubblicazione.

L’attività ha permesso così di collegare le competenze proprie delle Digital Humanities con le pratiche dell’open knowledge, trasformando il lavoro degli studenti in nuovi contenuti accessibili e riutilizzabili online.

Il programma del laboratorio

Primo incontro: conoscere Wikipedia e iniziare a contribuire

Il laboratorio si è aperto con un’introduzione ai progetti Wikimedia e alle attività previste. La prima parte è stata dedicata a Wikipedia, ai suoi cinque pilastri e ai principi fondamentali che regolano la partecipazione all’enciclopedia libera.

Tra il primo e il secondo incontro gli studenti hanno iniziato a individuare il tema della propria voce, privilegiando argomenti legati ai beni culturali e verificando la disponibilità di una bibliografia adeguata.

Secondo incontro: fonti, progetti Wikimedia e scrittura

Il secondo appuntamento ha ampliato la conoscenza dell’ecosistema Wikimedia, introducendo anche le basi di Wikisource e Wikivoyage e presentando il concorso fotografico Wiki Loves Monuments.

La parte centrale dell’incontro è stata dedicata al laboratorio di scrittura: gli studenti hanno continuato a sviluppare le proprie voci, lavorando in particolare sull’utilizzo delle fonti e sulla corretta organizzazione di note e bibliografia.

Terzo incontro: immagini, diritto d’autore e Wikimedia Commons

Il terzo incontro ha portato l’attenzione sui contenuti multimediali e sulle modalità di utilizzo delle immagini nei progetti Wikimedia.

Una parte importante della lezione è stata dedicata al diritto d’autore, alle immagini in pubblico dominio e alle licenze libere. Gli studenti hanno approfondito il funzionamento di Wikimedia Commons e le modalità corrette per caricare e descrivere i file.

Quarto incontro: Wikidata e la dimensione dei dati

Il laboratorio ha quindi affrontato Wikidata, il progetto Wikimedia dedicato alla gestione strutturata dei dati.

Dopo una prima introduzione al funzionamento della piattaforma, gli studenti hanno lavorato sull’arricchimento degli elementi relativi ai beni culturali oggetto delle proprie voci e sulla creazione di nuovi elementi quando necessario.

Parallelamente è proseguito il lavoro editoriale sulle voci di Wikipedia, ormai giunte alla fase conclusiva.

Quinto incontro: revisione e pubblicazione

L’ultimo appuntamento è stato dedicato alla revisione finale delle voci e alla loro pubblicazione.

Prima della pubblicazione, gli studenti hanno avuto la possibilità di sottoporre più volte le proprie bozze alla revisione dei docenti, intervenendo sui contenuti, sulle fonti, sulla struttura e sugli aspetti formali.

La fase conclusiva ha riguardato anche le attività successive alla pubblicazione, come l’inserimento delle categorie, il collegamento con Wikidata e la disorfanizzazione delle nuove voci, per favorire una loro migliore integrazione all’interno dell’enciclopedia.

I risultati

Il laboratorio ha coinvolto 27 studenti, ciascuno impegnato nella creazione, traduzione o ampliamento di contenuti su Wikipedia.

Il lavoro documentato sulla pagina del progetto comprende 16 voci ampliate, 9 nuove voci create e 2 voci tradotte, per un totale di 27 soggetti. Tra gli argomenti affrontati figurano opere letterarie, artisti, edifici e complessi monumentali, istituzioni culturali, opere d’arte e altri temi legati al patrimonio culturale.

Tra le voci ampliate o create dagli studenti si trovano, ad esempio, Patera di Parabiago, Villa Strohl Fern, Padiglione d’arte contemporanea di Milano, Abbazia di San Benedetto in Polirone, Fabbrica del Duomo di Como e Archivio storico del Comune di Catania. Il progetto comprende inoltre attività di traduzione di voci provenienti da altre edizioni linguistiche di Wikipedia.

Il percorso ha quindi prodotto non soltanto un’esperienza formativa per gli studenti del Master, ma anche un insieme di nuovi contenuti e miglioramenti destinati a rimanere disponibili nell’enciclopedia libera.

Il laboratorio rappresenta così un esempio concreto di come la formazione universitaria possa incontrare l’open knowledge: gli studenti non si limitano ad apprendere il funzionamento degli strumenti digitali, ma li utilizzano per produrre nuova conoscenza, mettendola a disposizione di un pubblico potenzialmente globale.


## Rejected T3 first-live candidate

https://www.istitutocomprensivoniscemi.edu.it/2026/04/25/racconti-di-un-viaggio/ — page is explicitly CC BY 4.0, but the place descriptions are parallel and could permute. Rejected for the reconstruction slot, not for authenticity/licensing. Full cleaned original retained separately in source-texts/T3-school-rejected.txt and pool factory/corpus/pool/7a8290b5be9a.md. No named minors or photographs retained.
