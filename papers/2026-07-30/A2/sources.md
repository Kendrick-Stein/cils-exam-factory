# Sources — A2 2026-07-30

## Slot T1 — breve articolo di giornale (descrizione di persone/cose/avvenimenti), target 180–240 words, feeds Test di comprensione della lettura, Prova n. 1

### Candidate 1 — ACCEPT WITH ADAPTATION

- url: https://www.rainews.it/tgr/bolzano/articoli/2026/03/streets-for-kids-i-bambini-si-riappropriano-delle-strade-f60efb48-2042-4b64-abf7-c21d2d0a8bb8.html
- title: Streets for Kids, i bambini si riappropriano delle strade
- publisher: RaiNews, TGR Bolzano
- published: 2026-03-18
- accessed: 2026-07-30
- fetch-evidence: curl/Jina returned the live Italian body beginning «Per un pomeriggio via Martin Knoller, nel quartiere Gries di Bolzano, è rimasta chiusa al traffico»; URL shown above. WebSearch independently exposed the same title, date and body sentences.
- CEFR: **ACCEPT WITH ADAPTATION (from B1 to A2)** — primary B1; usable_levels: A2,B1
  - Evidence: cronaca concreta su strada, giochi e famiglie; passato prossimo, presente e passive trasparenti («è rimasta chiusa», «viene chiusa»), con una sola relativa semplice.
  - Evidence: i nomi di associazioni e sintagmi come «mezzi motorizzati» e «socializzazione» alzano il carico a B1, ma la selezione elimina il paragrafo più istituzionale e conserva fatti visibili e ordinati.
  - Anchor comparison: funzione e inferenza bassa sono compatibili con il breve profilo informativo dell’anchor A2; il ritmo giornalistico è leggermente più denso.
  - Numbers: 216 words; 27.0 words/sentence; hard lexis ~4% (the high mean comes from transparent coordination and proper names, not multi-level subordination).
- Adaptation plan: selezione per sola sottrazione del corpo autentico; omessi il lungo elenco di enti e il paragrafo finale sulle interviste, senza riscrivere le frasi conservate.

Streets for Kids, i bambini si riappropriano delle strade

Per un pomeriggio via Martin Knoller, nel quartiere Gries di Bolzano, è rimasta chiusa al traffico e si è trasformata in una strada per il gioco e la socializzazione.

L'iniziativa Streets for Kids arriva da Vienna e da altre città del Nord Europa: per qualche ora una strada viene chiusa ai mezzi motorizzati e diventa uno spazio di libertà e movimento per bambine e bambini e per le loro famiglie. Ecco allora che tornano vecchi giochi come il salto con la corda o l'hula hop ma ci sono anche proposte musicali, laboratori, truccabimbi, cibo e tanto altro.

A Bolzano la cooperativa Blufink ha organizzato - con il coordinamento di Katherina Longariva - Streets for Kids davanti alla scuola primaria di lingua tedesca di via Martin Knoller.

Streets for Kids ha avuto il patrocinio del comune di Bolzano e del consiglio di quartiere Gries San Quirino. Diverse le associazioni che hanno contribuito alla riuscita della festa, dal VKE allo Jugenddienst di Bolzano, da Kinder in Bewegung - bambini in movimento - a Bozen Fiorisce fino alla LaAV, Lettura ad alta voce.

Ai bambini presenti è stato chiesto anche di disegnare la città che vorrebbero. C'è da scommettere che la vorrebbero proprio come è stata per un pomeriggio grazie all'iniziativa Streets for Kids.

## Slot T2 — testo regolativo (avviso pubblico, istruzioni, dépliant), target 150–200 words, feeds Test di comprensione della lettura, Prova n. 2

### Candidate 1 — ACCEPT WITH ADAPTATION (pool 30e7086e2579)

- url: https://blog.giallozafferano.it/naturaecucina/gamberetti-in-padella/
- title: Gamberetti in padella
- publisher: Natura e Cucina (GialloZafferano Blog)
- published: not dated on page
- accessed: 2026-07-30 (pooled fetch: 2026-07-29)
- pool-evidence: selected first with `python3 scripts/pool_select.py --level A2 --genre practical_realia --words 150-200`; source file `factory/corpus/pool/30e7086e2579.md`; no refetch performed, as required by the pool-first rule.
- CEFR: **ACCEPT WITH ADAPTATION (from B1 to A2)** — pool primary B1; usable_levels: A2,B1,B2
  - Evidence: sequenza regolativa lineare con imperativi A2 («metti», «aggiungi», «lascia», «trasferisci») e dati concreti su minuti, ingredienti e azioni.
  - Evidence: «sfrigolare», «lascia sfumare l’alcol» e «lascia insaporire» sono lessico culinario B1, ma il contesto operativo rende il significato recuperabile.
  - Anchor comparison: come la «Ricetta» dei micro-testi ufficiali A2, presenta scopo, ordine e risultato espliciti, qui con maggiore profondità adatta alla prova vero/falso.
  - Numbers: 185 words; 15.4 words/sentence; hard lexis ~4%.
- Adaptation plan: per la versione d’esame eliminare soltanto il primo paragrafo promozionale, lasciando le istruzioni autentiche nella banda 150–200; nessuna riscrittura.

Gamberetti in padella

A prima vista può sembrare un piatto elaborato, ma in realtà è sorprendentemente semplice da preparare. Questi gamberetti in padella si cucinano in pochi minuti, con pochissimi ingredienti che ne esaltano tutto il sapore. Una ricetta veloce, leggera e davvero irresistibile!

Preparazione dei gamberetti

Metti una padella sul fuoco e fai rosolare uno spicchio d’aglio con un filo d’olio extravergine d’oliva, finché non inizia a dorarsi. A questo punto rimuovilo dalla padella.

Aggiungi i gamberetti interi, precedentemente lavati e lasciati scolare per qualche minuto. Non appena iniziano a sfrigolare, versa il vino bianco e lascia sfumare l’alcol. Una volta evaporato l’alcol, abbassa la fiamma, copri con un coperchio e lascia cuocere per circa 10 minuti, mescolando di tanto in tanto.

Trascorso questo tempo, aggiungi il prezzemolo tritato e, se necessario, un altro filo d’olio. Regola di sale e pepe a piacere.

Lascia insaporire ancora per un paio di minuti, poi spegni il fuoco. Trasferisci i gamberetti in un piatto da portata, condiscili con qualche goccia di succo di limone (se ti piace) e servili ben caldi.

## Slot T3 — 6 micro-testi funzionali con titolo (offerte, avvisi, servizi), target 120–180 words, feeds Test di comprensione della lettura, Prova n. 3

### Candidate 1 — ACCEPT

- url: https://www.visittrentino.info/it/guida/cosa-fare/eventi/feste-sagre-estate/la-magnalonga-dell-alta-vallagarina_e_1875674
- title: La Magnalonga dell’Alta Vallagarina — sei voci del programma 2026
- publisher: Visit Trentino
- published: not dated on page; event date 2026-09-06
- accessed: 2026-07-30
- fetch-evidence: live curl/Jina output returned «La Magnalonga dell’Alta Vallagarina è la prima e più longeva passeggiata enogastronomica del Trentino» and the titled entries «TAPPA 2» and «TAPPA 3»; WebFetch independently exposed the same page, date, locations and menu.
- CEFR: **ACCEPT (target A2)** — primary A2; usable_levels: A1,A2,B1
  - Evidence: sei unità autonome con titoli, luoghi e piatti espliciti; sintassi nominale o frasi brevi, senza inferenze culturali necessarie.
  - Evidence: lessico quotidiano di cibo e passeggiata domina; nomi locali come «rostì», «marzemino» e «fortaie» funzionano come etichette concrete, non come conoscenze richieste.
  - Anchor comparison: riproduce direttamente la forma dei sei micro-testi titolati dell’anchor A2 («Sconti», «Ricetta», «Sport», «Nuovo servizio»), qui come programma gastronomico.
  - Numbers: 179 words total; 29.8 words per micro-text; hard lexis ~4%.
- Adaptation plan: selezione di sei voci dal programma autentico; rimossi link e tappe non usate, nessuna riscrittura.

**La prima passeggiata enogastronomica del Trentino**

La Magnalonga dell’Alta Vallagarina è la prima e più longeva passeggiata enogastronomica del Trentino con 10 km di camminata non competitiva fra i vigneti e i borghi dell’Alta Vallagarina.

**TAPPA 2 | TRACCE NEL SOTTOBOSCO | loc. Praolini (Volano)**

Speck cotto con rostì e cappuccio. VEG: Medaglione di pomodoro con salsa, rostì e cappuccio.

**TAPPA 3 | INCANTESIMI NEL PIATTO | loc. Prà dei Fanti (Volano)**

Orzotto con lucanica e marzemino alla trentina. VEG: Orzotto con radicchio e marzemino alla trentina.

**TAPPA 6 | I SEGRETI DELLO GNOMO | loc. Fornaci (Volano)**

Selezione di formaggi trentini con miele. In abbinamento a Rosato Vigneti delle Dolomiti IGT della Cantina Vivallis.

**TAPPA 7 | IL RISVEGLIO DEL BOSCO | loc. Castel Pietra (Calliano)**

Carne salada con riccioli di patate fritte e misticanza. VEG: Polpette di verdure con riccioli di patate fritte e misticanza. In abbinamento a Marzemino Trentino dell’Az. Agr. Salizzoni.

**TAPPA 8 | MAGIA FINALE | Parco Europa (Calliano)**

Fortaie a scelta con zucchero, limone o composta di frutta. In abbinamento a Moscato Giallo Castel Beseno Superiore della Cantina di Aldeno.

## Slot T4 — breve testo informativo quotidiano, target 90–130 words, feeds Test di analisi delle strutture di comunicazione, Prova n. 1

### Candidate 1 — ACCEPT

- url: https://www.focusjunior.it/news/10-consigli-per-tornare-a-scuola-senza-stress-dopo-le-vacanze-di-natale/
- title: 10 consigli per tornare a scuola senza stress dopo le vacanze di Natale
- publisher: Focus Junior
- published: 2026-01-05
- accessed: 2026-07-30
- fetch-evidence: WebFetch returned the live Italian body with «Si torna a scuola dopo le lunghe vacanze di Natale» and the headings «Recupera il ritmo del sonno» / «Pianifica le urgenze»; URL shown above.
- CEFR: **ACCEPT (target A2)** — primary A2; usable_levels: A1,A2,B1
  - Evidence: presente, passato prossimo e imperativi frequenti («inizia», «prendi», «dividi», «metti»), con lessico familiare di scuola, sonno, compiti e voti.
  - Evidence: domande dirette e subordinate semplici con «dopo», «in cui» e «quando»; ogni consiglio esplicita subito l’azione.
  - Anchor comparison: ritmo istruttivo e inferenza bassa equivalgono agli avvisi/consigli quotidiani dell’anchor A2, con una struttura più adatta al cloze.
  - Numbers: 129 words; 14.3 words/sentence; hard lexis ~3%.
- Adaptation plan: none; estratto per sola selezione dell’introduzione e dei primi due consigli, senza riscrittura.

10 consigli per tornare a scuola senza stress dopo le vacanze di Natale

Si torna a scuola dopo le lunghe vacanze di Natale. È tempo, quindi, di rimettersi in pari con i compiti e prepararsi per le ultime verifiche prima della pagella. Ecco i consigli di Focus Junior.

Recupera il ritmo del sonno

Durante le vacanze sei andato a letto e, soprattutto, ti sei alzato tardi? Non puoi pretendere che al suono della campanella il tuo corpo sia attivo e la tua mente vigile. Inizia ad anticipare la sveglia di 15 minuti ogni giorno.

Pianifica le urgenze

Gennaio è il mese dei recuperi. Non studiare tutto insieme. Prendi un foglio e dividi le materie: metti in cima quelle in cui hai il voto più basso o la verifica imminente.

## Slot T5 — racconto personale/intervista breve, target 90–130 words, feeds Test di analisi delle strutture di comunicazione, Prova n. 2

### Candidate 1 — ACCEPT WITH ADAPTATION

- url: https://www.ansa.it/basilicata/notizie/2026/05/14/dalla-cucina-lucana-di-nonna-rosa-a-food-network-la-ricetta-di-vittoria-de-nittis_8b683fe1-8241-4fed-9079-cabbf4eebd0c.html
- title: Dalla cucina lucana di nonna Rosa a Food Network, la “ricetta” di Vittoria De Nittis
- publisher: ANSA Basilicata
- published: 2026-05-14
- accessed: 2026-07-30
- fetch-evidence: WebFetch exposed the full live Italian article and the direct speech «La mia avventura con “Chef in Camicia” nasce nel 2020» / «Lavoravo per una famosa multinazionale»; URL and date shown above.
- CEFR: **ACCEPT WITH ADAPTATION (from B1 to A2)** — primary B1; usable_levels: A2,B1
  - Evidence: prima persona con contrasto produttivo fra presente, imperfetto e passato prossimo («nasce», «lavoravo», «mi sono ritrovata», «ho visto», «ho mandato»), ideale per il cloze verbi A2.
  - Evidence: cibo, casa e lavoro sono concreti; «multinazionale», «cassa integrazione» e l’inciso giornalistico richiedono una selezione B1→A2 ma non conoscenze esterne.
  - Anchor comparison: tono autobiografico e sequenza cronologica si affiancano naturalmente al profilo personale dell’anchor A2, con registro giornalistico un poco più denso.
  - Numbers: 117 words; 19.5 words/sentence; hard lexis ~4%.
- Adaptation plan: selezione per sola sottrazione delle battute più concrete; omessi commenti astratti su identità e mercato gastronomico, senza riscrittura.

Dalla cucina lucana di nonna Rosa a Food Network, la “ricetta” di Vittoria De Nittis

«La mia avventura con “Chef in Camicia” nasce nel 2020, durante il lockdown. Lavoravo per una famosa multinazionale - racconta all'ANSA - e mi sono ritrovata improvvisamente a casa, in cassa integrazione. Per gioco ho visto una storia Instagram in cui cercavano un “terrone fuori sede” a Milano e ho mandato un video in cui preparavo spaghetti, fagiolini e cacio ricotta. L'ho fatto senza alcuna aspettativa».

«Mi hanno detto di inventare un'idea - aggiunge - e così è nato “Giovani Nonne”, inizialmente pensato per YouTube e per i social di Chef in Camicia. Poi è arrivata la televisione e il programma è finito su Food Network».

## Slot T6 — breve testo informativo/annuncio, target 90–130 words, feeds Test di analisi delle strutture di comunicazione, Prova n. 3

### Candidate 1 — ACCEPT WITH ADAPTATION

- url: https://www.eventbrite.it/e/biglietti-concorto-kids-2026-1992414731095
- title: Concorto Kids 2026
- publisher: Concorto Film Festival / Eventbrite Italia
- published: not dated on page; event dates 2026-08-25–2026-08-27
- accessed: 2026-07-30
- fetch-evidence: direct curl through the Jina reader returned the live Eventbrite text beginning «È tornato Concorto Kids! All'interno di #Concorto2026 una tre-giorni dedicata a bimbe e bimbi» and the date/location line; URL shown above.
- CEFR: **ACCEPT WITH ADAPTATION (from B1 to A2)** — primary B1; usable_levels: A2,B1
  - Evidence: annuncio concreto con date, luogo, età, ingresso e attività; presente e invito diretto («vi aspettiamo», «vieni») sostengono il lessico quotidiano.
  - Evidence: il periodo centrale è lungo e include «narrazione» e «relazione con la natura», ma le informazioni verificabili restano esplicite e ordinate.
  - Anchor comparison: stessa funzione degli avvisi e dei nuovi servizi dell’anchor A2, con un programma familiare più ricco ma senza inferenza esterna.
  - Numbers: 123 words; 17.6 words/sentence; hard lexis ~4%.
- Adaptation plan: selezione per sola sottrazione dell’apertura, delle condizioni d’ingresso e della data; omessi sponsor, contatti e programma dettagliato, senza riscrittura.

Concorto Kids 2026

È tornato Concorto Kids! All'interno di #Concorto2026 una tre-giorni dedicata a bimbe e bimbi con laboratori e proiezioni.

È tornato Concorto Kids, e quest'anno è dedicato all'acqua!

All'interno di #Concorto2026, una tre giorni dedicata a bimbe e bimbi con proiezioni ma non solo! Quest'anno il tema è L'ACQUA e vi aspettiamo con laboratori pratici, proiezioni, merende e un pomeriggio dedicato a educatrici, educatori, insegnanti e genitori per approfondire il tema dell'arte come metodo di narrazione e relazione con la natura.

Per bimbe e bimbi dai 3 ai 12 anni (ma se ti incuriosisce vieni a dare un'occhiata comunque!), INGRESSO LIBERO con prenotazione obbligatoria.

Vi aspettiamo il 25, 26 e 27 agosto alla Galleria d'Arte Moderna Ricci Oddi di Piacenza.

## Coverage

Slot T1: OK (candidate 1)
Slot T2: OK (candidate 1; pool 30e7086e2579)
Slot T3: OK (candidate 1; six titled micro-texts)
Slot T4: OK (candidate 1)
Slot T5: OK (candidate 1)
Slot T6: OK (candidate 1)
