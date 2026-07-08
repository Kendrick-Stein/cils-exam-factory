# Sources — A1 2026-07-08

Session: CILS A1 (adulti) · Exam: cils · Hunter run: 2026-07-08.
Fetch failures this run (candidates dropped, cause noted): subito.it (HTTP 403, also static-www mirror — no classified-ad micro-texts available), focusjunior.it (HTTP 403), ricette.giallozafferano.it (HTTP 402), cultura.gov.it/domenicalmuseo (TLS socket closed, 3 attempts), museozoologia.museiincomuneroma.it (SSL handshake failure), uffizi.it Italian info pages (404 / only EN indexed).
All texts below were fetched live on 08/07/2026. No text is reproduced from memory.

---

## Slot T1 — testo informativo semplice (presentazione di un luogo/servizio), target 100–140 parole, feeds Lettura P1 (4 MC A–C)

### Candidate 1 — ACCEPT WITH ADAPTATION (from A2)
- url: https://www.bibliotecasalaborsa.it/
- title: Biblioteca Salaborsa (presentazione della biblioteca, homepage)
- publisher: Biblioteca Salaborsa — Comune di Bologna (whitelist: comune.bologna.it / altri comuni; il sito usa contatti @comune.bologna.it)
- published: n.d. (pagina istituzionale) · accessed: 08/07/2026
- attribution: Testo adattato da: Biblioteca Salaborsa, bibliotecasalaborsa.it, https://www.bibliotecasalaborsa.it/, consultato il 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)**
  - Evidence: solo presente indicativo («si trova», «offre», «dispone», «è adatta»); lessico concreto quotidiano quasi tutto VdB (biblioteca, libri, musica, famiglie, bambini, bar, telefono); un'unica relativa («che combina») e liste nominali — niente passati, niente congiuntivi.
  - Anchor: registro e ritmo da dépliant di servizio, in linea con i «testi informativi / opuscoli informativi» previsti dalle linee guida A1 (analysis/A1.md §4.1).
  - Numbers: ~95 parole; frasi medie ~13 parole (liste lunghe); hard-lexis ~5% grezzo (risorse digitali, postazioni informatiche, fasciatoio, accessibili, appassionati) — tutto eliminabile con tagli.
- Adaptation plan: spezzare le liste in frasi semplici S-V-O («In biblioteca ci sono libri, giornali, film e musica. C'è il wi-fi gratis.»); tagliare «struttura moderna che combina…», EmiLib, «postazioni informatiche», «fasciatoio», «risorse digitali»; mantenere ≥5 fatti distinti: (1) indirizzo Piazza del Nettuno 3, Bologna; (2) materiali: libri, audiolibri, giornali, video, musica; (3) wi-fi gratis e sale studio; (4) sezione ragazzi; (5) Sala Ascolto Vinili / LEILA (oggetti in prestito); (6) Bar Altroverso; (7) telefono 051 2194400. Lunghezza finale 100–140 parole (lo split delle liste porta a ~110 senza aggiungere contenuto).

Cleaned text:

> **Biblioteca Salaborsa**
>
> Biblioteca Salaborsa si trova in Piazza del Nettuno, 3 a Bologna ed è una struttura moderna che combina spazi per la ricerca, lo studio e il tempo libero.
>
> La biblioteca offre libri, audiolibri, quotidiani e periodici, video, musica e accesso a risorse digitali. Dispone di free wi-fi, sale studio, postazioni informatiche, fasciatoio e ambienti completamente accessibili. È adatta alle famiglie con bambini e dotata di aria condizionata.
>
> Sezione dedicata ai ragazzi: Biblioteca Salaborsa Ragazzi. Sala Ascolto Vinili per appassionati di musica. LEILA: biblioteca degli oggetti in prestito. Bar Altroverso nello spazio della biblioteca.
>
> Telefono: 051 2194400.

### Candidate 2 — ACCEPT WITH ADAPTATION (from A2, backup)
- url: https://anagrafe.iccu.sbn.it/it/ricerca/dettaglio.html?codice_isil=it-BO0563
- title: Biblioteca Salaborsa — scheda Anagrafe delle biblioteche italiane
- publisher: ICCU — Anagrafe delle biblioteche italiane. **Off-whitelist justification:** registro pubblico istituzionale (Ministero della Cultura), accesso libero, dati descrittivi forniti dalla biblioteca stessa.
- published: scheda anagrafica aggiornata periodicamente (n.d.) · accessed: 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)** — stile nominale da scheda (presente, elenchi); però lessico parzialmente amministrativo («emeroteca», «document delivery», «prestito interbibliotecario» ≈ 8% hard) da tagliare integralmente; ~90 parole utili; frasi ~12 parole. Usable only as backup: richiede più tagli del candidate 1.
- Adaptation plan: tenere sede, fondazione 2001, raccolta (libri, periodici, DVD, mappe, musica), sezione ragazzi, wi-fi, contatti; eliminare metri quadri, cifre di catalogo e servizi tecnici. NB: gli orari della scheda ICCU sono obsoleti — non usarli (fa fede bibliotecasalaborsa.it/orari, slot T2 c2).

Cleaned text:

> **Biblioteca Salaborsa**
>
> Biblioteca pubblica comunale centrale di Bologna, fondata nel 2001. La raccolta include volumi e opuscoli, periodici, documenti audiovisivi, CD-ROM, DVD, mappe e documenti musicali a stampa.
>
> Offre emeroteca, sezione ragazzi, storia locale e laboratorio multimediale. Disponibili fotocopie, accesso internet con Wi-Fi, prestito locale e prestito digitale.
>
> Indirizzo: Piazza del Nettuno 3 - 40124 Bologna. Telefono: 051 2194400. Email: bibliotecasalaborsa@comune.bologna.it. Sito: www.bibliotecasalaborsa.it.

---

## Slot T2 — testo regolativo/avviso semplice (orari, prezzi, regole), target 100–140 parole, feeds Lettura P2 (8 V/F)

### Candidate 1 — ACCEPT WITH ADAPTATION (from A2)
- url: https://www.museiincomuneroma.it/it/infopage/museo-civico-di-zoologia
- title: Museo Civico di Zoologia — informazioni pratiche (orari, biglietti)
- publisher: Musei in Comune — Roma Capitale (whitelisted: museiincomuneroma.it)
- published: pagina informativa corrente (n.d.) · accessed: 08/07/2026
- attribution: Testo adattato da: Museo Civico di Zoologia, museiincomuneroma.it, https://www.museiincomuneroma.it/it/infopage/museo-civico-di-zoologia, consultato il 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)**
  - Evidence: realia regolativa in stile nominale + presente indicativo («non sono rimborsabili»); informazione portata da numeri, giorni e prezzi — nessuna morfologia oltre il presente; hard-lexis burocratico circoscritto («diritto di prevendita», «preacquistati», «rimborsabili o modificabili», «area metropolitana») ≈ 5%, eliminabile.
  - Anchor: coincide col genere A1 «avvisi pubblici / opuscoli informativi» (analysis/A1.md §4.1); la densità di dati discreti è ideale per 8 V/F.
  - Numbers: ~100 parole (testo pulito); frasi/blocchi medi ~9 parole; ≥14 dettagli discreti (indirizzo; mar–dom; 9–19; 24 e 31/12 9–14; ultimo ingresso 1h prima; chiuso lunedì; chiuso 1/5; chiuso 25/12; intero 7,00; ridotto 5,50; residenti 6,00/4,50; online +1 €; call center 060608 9–19; biglietti non rimborsabili).
  - Nota: il fetch mostra il refuso «Aldrovanni»; la via corretta sul portale è «Via Ulisse Aldrovandi, 18» (normalizzazione ortografica, non contenutistica).
- Adaptation plan: trasformare le voci in frasi semplici complete («Il museo è aperto da martedì a domenica, dalle 9.00 alle 19.00. Il lunedì il museo è chiuso. Il biglietto intero costa 7 euro…»); tagliare «diritto di prevendita»/«non rimborsabili o modificabili» oppure ridurre a «Il biglietto online costa 1 euro in più»; selezionare 8–10 dettagli per i V/F; restare nel presente indicativo.

Cleaned text:

> **Museo Civico di Zoologia — Informazioni**
>
> Indirizzo: Via Ulisse Aldrovandi, 18 — Roma.
>
> Orari: da martedì a domenica 9.00–19.00. 24 e 31 dicembre: 9.00–14.00. Ultimo ingresso un'ora prima della chiusura.
>
> Giorni di chiusura: lunedì, 1 maggio, 25 dicembre.
>
> Biglietti: intero € 7,00; ridotto € 5,50. Residenti Roma Capitale e area metropolitana: intero € 6,00; ridotto € 4,50.
>
> Acquisto biglietti: online con diritto di prevendita di € 1; al call center 060608, tutti i giorni 9.00–19.00 (diritto di prevendita € 1); in biglietteria il giorno stesso senza diritto di prevendita. I biglietti preacquistati online o tramite il call center 060608 non sono rimborsabili o modificabili.
>
> Informazioni e prenotazioni: 060608 (tutti i giorni 9.00–19.00).

### Candidate 2 — ACCEPT WITH ADAPTATION (from A2, backup — short)
- url: https://www.bibliotecasalaborsa.it/orari
- title: Orari — Biblioteca Salaborsa
- publisher: Biblioteca Salaborsa — Comune di Bologna
- published: pagina orari corrente (n.d.) · accessed: 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)** — presente indicativo e giorni/ore; una frase regolativa autentica («L'ultima entrata consentita nell'edificio è sempre un quarto d'ora prima della chiusura»); ~60 parole: sotto banda 100–140, quindi backup (servirebbe integrare con la pagina Ragazzi dello stesso sito). 8 dettagli discreti presenti (dom chiuso; lun 14–20; mar–ven 9–20; sab 9–19; ultima entrata −15′; festività nazionali; 4 ottobre San Petronio; vigilie 9–14).
- Adaptation plan: frasi semplici per ogni dettaglio; sostituire «consentita» con costruzione al presente; se usato, allungare solo con dettagli fetchati dallo stesso dominio.

Cleaned text:

> **Orari — Biblioteca Salaborsa**
>
> Domenica: chiuso. Lunedì: 14.00–20.00. Da martedì a venerdì: 9.00–20.00. Sabato: 9.00–19.00.
>
> L'ultima entrata consentita nell'edificio è sempre un quarto d'ora prima della chiusura.
>
> La biblioteca rimane chiusa per le festività nazionali e il 4 ottobre (San Petronio). Orario ridotto (9.00–14.00) durante la vigilia di Pasqua, la vigilia di Natale e il 31 dicembre.

---

## Slot T3 — 4 micro-testi funzionali (annunci, cartelli, avvisi), 20–30 parole l'uno, feeds Lettura P3 (abbinamento 4 ↔ 6)

Nota slot: subito.it (annunci privati) irraggiungibile (403) — set composto da 4 realia istituzionali/commerciali autentiche di 4 pubblicatori diversi (treno, mercato, museo, biblioteca). Nessun contatto personale presente; numeri rimasti (060608) sono servizi pubblici istituzionali.

### Micro A — avviso di servizio (treno/biciclette) — ACCEPT
- url: https://www.trenitalia.com/it/informazioni.html
- title: Informazioni e assistenza — trasporto biciclette
- publisher: Trenitalia (whitelisted)
- published: pagina di servizio corrente (n.d.) · accessed: 08/07/2026
- CEFR: **ACCEPT (A1/A2 realia)** — presente + modale «puoi» (sillabo A1); 21 parole; lessico concreto (bicicletta, sacca, gratuitamente); unico aggiustamento: eliminare l'avverbio «opportunamente».
- Adaptation plan: togliere «opportunamente»; facoltativo chiudere con il dato fetchato del supplemento («supplemento € 3,50 con prenotazione obbligatoria» sui treni con servizio bici) come aggancio per la continuazione.
- Continuazione naturale possibile: «Per la bicicletta montata paghi un supplemento di 3,50 euro.»

Cleaned text:

> **In treno con la bici**
>
> Puoi trasportare gratuitamente a bordo la bicicletta se smontata e contenuta in una sacca (80x110x45 cm) o pieghevole opportunamente chiusa.

### Micro B — cartello di negozio (chiusura estiva) — ACCEPT
- url: https://www.mercatodelleerbe.eu/
- title: Mercato delle Erbe di Bologna — chiusure estive
- publisher: Mercato delle Erbe (sito ufficiale). **Off-whitelist justification:** realia commerciale autentica ad accesso libero del mercato comunale coperto di Bologna.
- published: avviso estivo corrente (luglio/agosto) · accessed: 08/07/2026
- CEFR: **ACCEPT (A1 realia)** — cartello con date e orari, zero morfologia difficile; ~23 parole (assemblate da righe contigue della stessa pagina: intestazione «Chiusure estive», righe delle attività, riga orari).
- Adaptation plan: nessuna oltre l'assemblaggio dichiarato; scegliere 1–2 righe di attività.
- Continuazione naturale possibile: «La pescheria riapre il 28 agosto.»

Cleaned text:

> **Chiusure estive**
>
> Pescheria Tinarelli: dal 30 luglio al 27 agosto. Mozzabella: dal 6 al 21 agosto. Il mercato è aperto lunedì–sabato 7.00–19.30.

### Micro C — annuncio di evento al museo — ACCEPT
- url: https://www.museiincomuneroma.it/it/didattica/notturno-con-la-scienza-0
- title: Notturno con la scienza — Museo Civico di Zoologia
- publisher: Musei in Comune — Roma Capitale (whitelisted)
- published: evento del 19/05/2012 (realia: any age per rules.recency) · accessed: 08/07/2026
- CEFR: **ACCEPT (A1/A2 realia)** — annuncio con ora, prezzo (gratuito) e regola di prenotazione; ~21 parole dopo trim; lessico VdB (museo, sera, ingresso, visite).
- Adaptation plan: comporre l'annuncio con i soli dati fetchati (ingresso gratuito dalle 20.00, visite guidate ogni 30 minuti, prenotazione obbligatoria, info 060608); omettere i numeri telefonici storici 2012; togliere il riferimento all'anno.
- Continuazione naturale possibile: «Il museo resta aperto fino alle 2 di notte.» (dato fetchato: accesso libero 20.00–02.00)

Cleaned text:

> **Notturno con la scienza — Museo Civico di Zoologia**
>
> Ingresso gratuito dalle 20.00. Visite guidate ogni 30 minuti. Prenotazione obbligatoria. Informazioni: 060608.

### Micro D — avviso in biblioteca — ACCEPT
- url: https://www.bibliotecasalaborsa.it/events/salaborsa_dal_1_luglio
- title: Cosa puoi fare adesso in Salaborsa
- publisher: Biblioteca Salaborsa — Comune di Bologna
- published: 25/06/2020 (agg. 31/08/2020; realia: any age) · accessed: 08/07/2026
- CEFR: **ACCEPT (A1/A2 realia)** — presente + modali «puoi/devi» (sillabo A1); 23 parole; frase autentica citata verbatim dalla pagina.
- Adaptation plan: nessuna (eventualmente togliere «invece»).
- Continuazione naturale possibile: «Puoi prenotare il posto per telefono.»

Cleaned text:

> **Avviso — Biblioteca Salaborsa**
>
> In biblioteca puoi cercare di persona quel che vuoi e registrare il prestito. Se vuoi studiare in biblioteca, invece, devi sempre prenotare.

---

## Slot T4 — breve testo descrittivo quotidiano (un mercato), target 70–100 parole, feeds Strutture P1 (cloze articoli determinativi, ≥10)

### Candidate 1 — ACCEPT WITH ADAPTATION (from A2)
- url: https://www.mercatodelleerbe.eu/
- title: Mercato delle Erbe di Bologna — presentazione, prodotti, orari
- publisher: Mercato delle Erbe (sito ufficiale). **Off-whitelist justification:** realia autentica ad accesso libero del mercato comunale coperto di Bologna (stessa giustificazione del Micro B).
- published: pagina corrente (n.d.) · accessed: 08/07/2026
- attribution: Testo adattato da: Mercato delle Erbe di Bologna, mercatodelleerbe.eu, https://www.mercatodelleerbe.eu/, consultato il 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)**
  - Evidence: descrizione al presente di luogo quotidiano (mercato, negozi, frutta, verdura, pane); nessun tempo passato; sintassi nominale/coordinata; hard-lexis limitato a formule commerciali («affianca», «enoteche», «punti ristorativi», «effettuare acquisti») ≈ 6% grezzo, tutte sostituibili con equivalenti VdB nella semplificazione della stessa frase.
  - Anchor: tema «fare la spesa» dei domini personale/pubblico A1; parallelo ai testi descrittivi brevi delle prove strutture.
  - Numbers: ~66 parole pulite (banda 70–100 raggiunta con lo split in frasi semplici); frasi medie ~11; articoli determinativi generabili naturalmente ≥10 (il mercato, i negozi, le bancarelle, i ristoranti, la frutta, la verdura, il pane, i salumi, i formaggi, la carne, la sera, la domenica).
- Adaptation plan: riscrivere in frasi semplici fondate sulle frasi fetchate: «Il Mercato delle Erbe è in via Ugo Bassi 23, a Bologna. Al mercato ci sono le bancarelle, i negozi e i ristoranti. Compri la frutta, la verdura, il pane, i salumi, i formaggi e la carne. I ristoranti offrono piatti e bevande. Il mercato è aperto dal lunedì al sabato…»; «effettuare acquisti» → «comprare»; tagliare «enoteche» e «sia vegetariani che carnivori».

Cleaned text:

> **Il Mercato delle Erbe di Bologna**
>
> Il Mercato affianca alle tradizionali bancarelle e negozi, ristoranti, enoteche, punti di incontro.
>
> Presso la struttura è possibile effettuare acquisti di frutta, verdura, pane, salumi, formaggi e carni. I punti ristorativi offrono bevande e piatti, sia vegetariani che carnivori.
>
> Indirizzo: Via Ugo Bassi 23 — Bologna.
>
> Orari: lunedì–sabato 7.00–19.30. Ristorazione: pranzo 12.00–15.30; sera 18.00–24.00. Domenica: pranzo 12.00–15.30; sera 18.00–23.00.

### Candidate 2 — ACCEPT WITH ADAPTATION (from A2, backup)
- url: https://turismo.bologna.it/il-mercato-delle-erbe-tra-bancarelle-e-ristoranti-tipici/
- title: Il mercato delle erbe: tra bancarelle e ristoranti tipici
- publisher: Turismo Bologna (portale turistico del Comune di Bologna — famiglia whitelist «comune.bologna.it / altri comuni»)
- published: n.d. · accessed: 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1) sull'estratto finale** — l'estratto tenuto è al presente con superlativo relativo («il più grande mercato coperto») e seconda persona («Puoi fare la spesa, mangiare e bere»); i paragrafi storici del pezzo (passato remoto «fu edificato», «fu riaperto» → B1/B2) sono stati eliminati in pulizia e NON fanno parte del testo utilizzabile; una frase passiva residua («sono state trasformate») e gli anglicismi (food court, street food) da tagliare. ~70 parole; frasi ~19 (da spezzare); hard-lexis ~4% dopo i tagli.
- Adaptation plan: tenere solo le frasi «Oggi, il Mercato delle Erbe è…» e «Puoi fare la spesa…»; tagliare la frase sul 2014 (passivo) o ridurla a presente; spezzare la relativa «dove è possibile acquistare…» in frase autonoma.

Cleaned text (estratto tenuto):

> Oggi, il Mercato delle Erbe è il più grande mercato coperto nel centro storico della città, dove è possibile acquistare frutta e verdura, carne, formaggio, vino e molto altro. Nel 2014 alcune aree sono state trasformate in una food court per cibo tradizionale e street food. Puoi fare la spesa, mangiare e bere fino a tarda sera in un ambiente unico, accogliente, caldo in inverno e fresco in estate.

---

## Slot T5 — breve racconto/e-mail personale, target 70–100 parole, feeds Strutture P2 (cloze verbi: SOLO presente e passato prossimo come chiavi)

### Candidate 1 — ACCEPT WITH ADAPTATION (from A2)
- url: https://www.viaggiapiccoli.com/panchina-gigante-lago-di-garda-san-felice-del-benaco/
- title: La panchina gigante del Lago di Garda e altre 4 cose da fare a San Felice del Benaco
- publisher: Viaggiapiccoli (blog di viaggi in famiglia — whitelisted blogs_lifestyle)
- published: 18/04/2024, Giulia Gardini · accessed: 08/07/2026 — **recency note:** >12 mesi (le rules «preferiscono» blog <12 mesi); deroga motivata: racconti personali autentici a semplicità A2 sono rarissimi e il contenuto è quotidiano e atemporale (vacanza al lago in famiglia). Le alternative più recenti tentate (focusjunior, giallozafferano) sono bloccate.
- attribution: Testo adattato da: La panchina gigante del Lago di Garda e altre 4 cose da fare a San Felice del Benaco, viaggiapiccoli.com, https://www.viaggiapiccoli.com/panchina-gigante-lago-di-garda-san-felice-del-benaco/, consultato il 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)**
  - Evidence: catena narrativa interamente al passato prossimo con entrambi gli ausiliari — esattamente l'inventario chiavi A1 («siamo saliti», «siamo andati», «siamo partiti», «abbiamo visitato», «abbiamo portato», «abbiamo deciso», «è stata»); lessico quotidiano concreto (bagno, piscina, patatine, bambini, giorni); un riflessivo («ci siamo trovati», A2) e nessun imperfetto/congiuntivo nell'estratto tenuto.
  - Anchor: registro da diario/e-mail personale; corrisponde al genere «brevi racconti» delle linee guida A1.
  - Numbers: ~101 parole (estratto); frasi medie ~20 (da spezzare); hard-lexis ~3% («sponda bresciana», «ammirato», «Big Bench»).
- Adaptation plan: taglio a 70–100 parole; spezzare le coordinate in frasi brevi («Siamo saliti sulla Panchina Gigante. Abbiamo guardato il lago dall'alto.»); semplificazioni lessicali in-frase: «ammirato» → «guardato/visto», «sponda bresciana» → tagliare, «Big Bench numero 101» → «panchina gigante»; eliminare o non usare come chiave «ci siamo trovati»; chiavi cloze esclusivamente presente/passato prossimo (ausiliare da scegliere: avere per visitare/portare/fare, essere per andare/salire/partire), participio senza accordo richiesto.

Cleaned text:

> Abbiamo trascorso quattro giorni al Lago di Garda con i nostri bambini a fine giugno, ed è stata la nostra prima volta sulla sponda bresciana. Siamo saliti sulla Panchina Gigante, abbiamo ammirato il lago dall'alto, fatto il bagno alla Baia del Vento, siamo andati all'Isola dei Conigli e abbiamo visitato Isola del Garda. Abbiamo scelto il Camping Fornella e ci siamo trovati davvero bene. Un pomeriggio, dopo un bagno in piscina, abbiamo deciso di fare un aperitivo diverso dal solito. Abbiamo portato con noi qualcosa da bere e un pacco di patatine e siamo partiti verso la Big Bench numero 101.

### Candidate 2 — ACCEPT WITH ADAPTATION (from A2, backup — richiede più tagli)
- url: https://www.viaggiapiccoli.com/gita-in-camper-nellappenino-emiliano/
- title: Gita in camper nell'Appennino Emiliano
- publisher: Viaggiapiccoli (stesso publisher del candidate 1: subito.it/focusjunior/giallozafferano bloccati in questo run — nessun secondo publisher di racconti personali raggiungibile)
- published: 14/05/2024, Giulia Gardini · accessed: 08/07/2026 (stessa recency note del candidate 1)
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)** — nucleo al passato prossimo («siamo partiti», «siamo arrivati», «abbiamo mangiato benissimo», «abbiamo cercato»), subordinate semplici (perché, quando, dove); **tre tratti B1 isolati da eliminare con tagli**: «stava calando il sole» (stare+gerundio all'imperfetto), «avevamo prenotato» (trapassato), «ci aspettava» (imperfetto). ~200 parole di estratto; frasi ~20; hard-lexis ~3% (sosta, circuito, gestori, caseificio). Backup: più interventi del candidate 1.
- Adaptation plan: tenere solo le frasi a passato prossimo puro; tagliare intere le clausole con imperfetto/trapassato (mai riformularle in altri tempi); spezzare le coordinate; 70–100 parole.

Cleaned text (estratti narrativi):

> A fine estate abbiamo approfittato di un weekend lungo per andare alla scoperta dell'Appennino Emiliano in camper. Siamo partiti in camper dalla Romagna nel tardo pomeriggio, abbiamo cercato per la prima notte una sosta del circuito Agricamper. Siamo arrivati a Serramazzoni quando stava calando il sole e ci siamo goduti un bel tramonto sul prato dove abbiamo sostato. Il mattino successivo è partito ufficialmente il nostro tour dell'Appennino Emiliano in camper e ci siamo svegliati presto perché avevamo prenotato una visita al Caseificio Santa Rita Bio. Siamo saliti sul camper e in 10 minuti siamo arrivati alla struttura dove ci aspettava la nostra bravissima guida. All'Agriturismo I cacciatori non siamo rimasti delusi, anzi, abbiamo mangiato benissimo.

---

## Slot T6 — breve testo informativo, target 70–100 parole, feeds Strutture P3 (cloze lessicale MC, 8 gap, opzioni A–C)

### Candidate 1 — ACCEPT WITH ADAPTATION (from A2)
- url: https://www.trenitalia.com/it/servizi/trasporto-animali-domestici.html
- title: Viaggia in treno con il tuo animale domestico
- publisher: Trenitalia (whitelisted)
- published: pagina di servizio corrente (n.d.) · accessed: 08/07/2026
- attribution: Testo adattato da: Viaggia in treno con il tuo animale domestico, trenitalia.com, https://www.trenitalia.com/it/servizi/trasporto-animali-domestici.html, consultato il 08/07/2026
- CEFR: **ACCEPT WITH ADAPTATION (A2 → A1)**
  - Evidence: presente indicativo + modali «possono/può» (sillabo A1); tema quotidiano concreto (cane, gatto, treno, biglietto, sabato); imperativo negativo di cortesia «Non dimenticare» (imperativo 2ª sing. è nel sillabo produttivo A1); hard-lexis concentrato e asportabile: «museruola», «guinzaglio», «anagrafe canina», «libretto sanitario», «trasportino» (~6% grezzo).
  - Anchor: informativo di servizio, parallelo agli «opuscoli informativi» A1; ricco di lessico di base cloze-abile (treno, cane, gatto, biglietto, sabato, gratis, piccolo, portare) → ≥8 gap A–C naturali.
  - Numbers: ~105 parole pulite; frasi medie ~17 (da spezzare); hard-lexis ~6% grezzo → ~1% dopo i tagli.
- Adaptation plan: tagliare la frase sui documenti (anagrafe canina/libretto sanitario) e le sigle dimensioni (o ridurre a «in una piccola gabbia»→ semplificazione in-frase di «trasportino»: preferibile mantenere «trasportino» come parola trasparente non-chiave); spezzare il periodo tariffario in tre frasi semplici («Il biglietto per il cane costa 5 euro. Il sabato costa 1 euro. Sui treni regionali il cane paga metà biglietto.»); chiudere con «I cani da assistenza viaggiano gratis». 70–100 parole; gap solo su lessico VdB.

Cleaned text:

> **Viaggia in treno con il tuo animale domestico**
>
> Cani, gatti e altri animali domestici di piccola taglia possono viaggiare gratuitamente sui nostri treni in un trasportino di dimensioni massime 70x30x50 cm (massimo uno per ciascun passeggero).
>
> Ogni passeggero può portare un cane di qualsiasi taglia, tenuto al guinzaglio e munito di museruola, con biglietto: su Frecce e Intercity € 5,00 da domenica a venerdì e € 1,00 il sabato; sui treni regionali biglietto di seconda classe ridotto del 50%.
>
> Non dimenticare di portare con te il certificato di iscrizione all'anagrafe canina e il libretto sanitario del tuo cane, obbligatori per viaggiare.
>
> I cani da assistenza viaggiano gratuitamente.

(Second-candidate attempts for this slot failed at fetch: cultura.gov.it «Domenica al museo» — TLS errors ×3; ricette.giallozafferano.it — HTTP 402; focusjunior.it — HTTP 403.)

---

## Coverage

Slot T1: OK (candidate 1 — bibliotecasalaborsa.it presentazione; backup ICCU)
Slot T2: OK (candidate 1 — museiincomuneroma.it Museo Civico di Zoologia orari/biglietti; backup Salaborsa orari)
Slot T3: OK (micro A trenitalia bici + micro B mercatodelleerbe.eu chiusure estive + micro C museiincomuneroma.it notturno + micro D bibliotecasalaborsa.it avviso)
Slot T4: OK (candidate 1 — mercatodelleerbe.eu presentazione mercato; backup turismo.bologna.it)
Slot T5: OK (candidate 1 — viaggiapiccoli.com Panchina Gigante Lago di Garda, 04/2024, recency deroga motivata)
Slot T6: OK (candidate 1 — trenitalia.com animali domestici in treno)
