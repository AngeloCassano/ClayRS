from clayrs.recsys import NXFullGraph
import random

item_spiegati = 0
used_verboIniziale = {}
used_avverbio = {}
used_avverbioFinale = {}
used_verboIniziale2 = {}
used_incipitRacc = {}


# Funzione che prende in input il grafo creato, le proprieta rankate da considerare, i due dizionari dei film piaciuti
# e raccomandati e inizializza la struttura dati che sara data in input alla funzione che genera la spiegazione
# partendo da questi dati
def build_triple_structure(G: NXFullGraph, score_properties, profile, recommendation):
    triple_structure = [] #list of triple of URI (URI film name -URI property- URI film name)
    profile_prop = get_property_movies(profile)                       # temporary list of the profile films' properties
    recommendations_prop = get_property_movies(recommendation)        # temporary list of the reccomenated films' properties
    # dall'elenco delle proprietà vado a ricavare i film del profilo e quelli raccomandati, operazioni inutili
    profile = []
    recommendations = []
    for line in profile_prop:
        if not (line[0] in profile):
            profile.append(line[0])

    for line in recommendations_prop:
        if not (line[0] in recommendations):
            recommendations.append(line[0])

    for proprieta, score in score_properties.items():

        prop = proprieta
        # estraggo i nodi opposti alla proprieta (film)
        opposite_nodes = estraiNodiOpposti_item_prop(G, prop)
        profile_nodes = []
        recomm_nodes = []
        for current in opposite_nodes:
            if current in profile and current not in profile_nodes:       # se il film piaciuto non e stato gia inserito
                profile_nodes.append(current)                                 # lo inserisco
            elif current in recommendations and current not in recomm_nodes:
                recomm_nodes.append(current)                                  # faccio lo stesso per i film raccomandati

        if len(profile_nodes) != 0 and len(recomm_nodes) != 0:     # aggiungo alla struttura dati creata gli item
            triple_structure.append(str(recomm_nodes) + "\t" + prop + "\t" + str(profile_nodes))

    return triple_structure

# Funzione che prende in input un dizionario di film e attraverso il confronto degli uri con le proprieta di ogni film
# all'interno del file di mapping seleziona e ritorna solo le proprieta dei film di interesse nel dizionario
def get_property_movies(item_raccom):
    property_movies = []
    property = []
    with open('movies_stored_prop.mapping', 'r') as f:
        for line in f:
            line = line.rstrip().split('\t')
            property_movies.append(line)

    for name, uri in item_raccom.items():
        for line in property_movies:
            if uri == line[0]:
                property.append(line)

    return property

# Funzione che prende in input il grafo creato e una proprieta ed estrae i nodi opposti alla proprieta
def estraiNodiOpposti_item_prop(G: NXFullGraph, item):

    map_prop = {}
    prop_in_edges = G.get_predecessors(item)                    # calcola archi entranti nella proprieta
    for in_edge in prop_in_edges:
        in_opposite_node = in_edge                  # prende il nodo opposto
        map_prop[in_opposite_node] = "in"

    prop_out_edges = G.get_successors(item)                      # calcola archi uscenti dalla proprieta
    for out_edge in prop_out_edges:
        out_opposite_node = out_edge               # prende il nodo opposto
        map_prop[out_opposite_node] = "out"

    opposite_nodes = map_prop.keys()
    return opposite_nodes

# Funzione principale del Generator che in base al tipo di configurazione per l'explanation data in input
# richiama le rispettive sottofunzioni per la generazione della spiegazione (baseline, schema, primolivello)
# L'explanation è ritornata come output sotto forma di stringa
def generate_explanation(triple_structure, item_raccom, profile, G: NXFullGraph, scelta_configurazione, template, html):
    explanation = ""

    if scelta_configurazione == "baseline":               # codice per la generazione della spiegazione baseline
        if len(item_raccom) == 1:
            simple_explanation = "I suggest this movie because many people like it and it's very popular."
        else:
            simple_explanation = "I suggest these movies because many people like them and they are very popular."
        explanation = simple_explanation

    elif scelta_configurazione == "schema":               # codice per la generazione della spiegazione schema
        schema_explanation = ""
        if len(item_raccom) == 1:
            value1 = item_raccom.values()
            value = list(value1)
            schema_explanation = get_descrizione_film(value[0], item_raccom)
        else:
            for key, value in item_raccom.items():
                schema_explanation += get_descrizione_film(value, item_raccom)
                schema_explanation += "\n\n"
        explanation = schema_explanation

    elif scelta_configurazione == "primolivello":         # codice per la generazione della spiegazione di primolivello
        if len(item_raccom) == 1:   #se ce un solo film raccomandato
            if len(triple_structure) > 0:
                triple_structure = optimize_triple_structure_single_reccomandation(triple_structure, item_raccom, 15)
        elif len(triple_structure) > 0:
            triple_structure = optimize_triple_structure_multiple_recomendation(triple_structure, item_raccom)

        explanation = get_explanation_primo_livello(template, item_raccom, triple_structure, profile, G, html)

    return explanation


# Funzione usata per la generazione della explanation di tipo schema
# Prende in input l'item da raccomandare e la lista delle raccomandazioni e ritorna una stringa con la spiegazione di
# tipo schema (descrizione del film sotto forma di elenco di caratteristiche e proprieta)
def get_descrizione_film(item_raccomandato, recommendation):
    explanation = ""
    property_movies = get_property_movies(recommendation)    # richiamo la funzione che seleziona le proprieta delle raccomandazioni
    property_item = []
    subject_prop = []
    subject_prop_provv = {}
    for line in property_movies:
        if item_raccomandato == line[0]:              # confrontando l'item da raccomandare con tutte le raccomandazioni
            property_item.append(line)                # prendo solo le proprieta che si riferiscono all'item da raccomandare

    if len(property_item) > 0:                        # inizia qui la costruzione della spiegazione
        explanation += "Info: " + pulisci_uri_item(item_raccomandato) + "\n\n"    # pulisco l'URI dell'item raccomandato
        for prop_corrente in property_item:                                       # per ogni proprieta dell'item raccomandato
            subject = prop_corrente[1]
            subject = pulisci_subject(subject)                                    # pulisco l'URI del tipo di proprieta
            if subject != "rdf-schema#seeAlso" and subject != "openingFilm" and subject != "soundRecording" and subject != "subject" and subject != "film" and subject != "closingFilm" and subject != "owl#differentFrom" and subject != "releaseLocation":
                prop_corrente_pulita = pulisci_uri_prop(prop_corrente[2])         # pulisco l'uri della proprieta
                list = [subject, prop_corrente_pulita]
                subject_prop.append(list)
                subject_prop_provv[subject] = prop_corrente_pulita

        for key, value in subject_prop_provv.items():       # per ogni propieta mi costruisco le righe della descrizione
            prop_subject = []
            for items in subject_prop:
                if key == items[0]:
                    prop_subject.append(items[1])
            prop_with_subject = ""
            for propCorrente in prop_subject:
                prop_with_subject += propCorrente + ", "
            prop_with_subject += "."
            prop_with_subject = prop_with_subject.replace(", .", ";\n")

            explanation += "- " + key + ": " + prop_with_subject     # aggiungo le righe della descrizione alla stringa della spiegazione

    explanation = pulisci_explanation(explanation)

    return explanation

# Funzione che ottimizza la struttura dati creata precedentemente per poter generare la spiegazione
# Vengono effettuate le fasi centrali del Generator di accorpamento e filtraggio delle proprieta per evitare ripetizioni
# Questa funzione e specifica per quando c'e solo un item raccomandato
def optimize_triple_structure_single_reccomandation(triple_structure, item_raccom, numero_prop):
    triple_structure_cleaned_all = []
    for current in triple_structure:
        current = current.replace("['", "")
        current = current.replace("']", "")
        triple_structure_cleaned_all.append(current)
    triple_structure_cleaned = [] #list of URI triple
    for s in triple_structure_cleaned_all:
        splitted = s.split('\t')
        items_racc = splitted[0].split(', ')
        for i in items_racc:
            for name, uri in item_raccom.items():
                if i == uri:
                    triple_structure_cleaned.append(i + "\t" + splitted[1] + "\t" + splitted[2])

    triple_structure_cleaned_2 = []
    if len(triple_structure_cleaned) > 0:
        considered_items = []
        limit = numero_prop
        list_prop_cons = []
        list_prop_cons.append(triple_structure_cleaned[0])
        if limit >= len(triple_structure_cleaned):
            limit = len(triple_structure_cleaned)
        if len(triple_structure_cleaned) > 1:
            for i in range(1, limit):                                     # fase di filtraggio
                add = True
                splitline = triple_structure_cleaned[i].split('\t')
                current_property = splitline[1]
                current_property = pulisci_property(current_property)      # viene pulito l'URI della proprietà
                for j in range(i):
                    splitlineJ = triple_structure_cleaned[j].split('\t')
                    old_property = splitlineJ[1]
                    old_property = pulisci_property(old_property)         # viene pulito l'URI della seconda proprieta
                    if current_property == old_property:                  # se le due proprieta sono uguali
                        add = False                                       # la seconda non verra presa in considerazione
                if add:
                    list_prop_cons.append(triple_structure_cleaned[i])
                elif limit < len(triple_structure_cleaned):
                    limit = limit + 1
        for k in range(len(list_prop_cons)):                              # fase di accorpamento
            splitlineI = list_prop_cons[k].split('\t')
            recI = splitlineI[0]
            properties = splitlineI[1]
            profI = splitlineI[2]
            for j in range(k + 1, len(list_prop_cons)):
                splitlineK = list_prop_cons[j].split('\t')
                recK = splitlineK[0]
                properties1 = splitlineK[1]
                profK = splitlineK[2]
                if recI == recK and profI == profK and profI not in considered_items:
                    properties += "-and-" + properties1         # proprieta in comune tra gli item vengono messe insieme
            if profI not in considered_items:
                considered_items.append(profI)
                profI_pulito = ""
                prof_splitted = profI.split(', ')
                for z in range(len(prof_splitted)):
                    profI_pulito += pulisci_uri_item(prof_splitted[z]) + ", "
                profI_pulito = profI_pulito[0:-2]
                triple_structure_cleaned_2.append(pulisci_uri_item(recI) + "\t" + properties + "\t" + profI_pulito)

    triple_structure = triple_structure_cleaned_2

    return triple_structure


# Funzione che ottimizza la struttura dati creata precedentemente per poter generare la spiegazione
# Vengono effettuate le fasi centrali del Generator di accorpamento e filtraggio delle proprieta per evitare ripetizioni
# Questa funzione e specifica per quando ci sono piu item raccomandati e ha lo stesso funzionamento della precedente
def optimize_triple_structure_multiple_recomendation(triple_structure, item_raccom):
    triple_structure_cleaned = []
    for current in triple_structure:
        current = current.replace("['", "")
        current = current.replace("']", "")
        triple_structure_cleaned.append(current)

    triple_structure_cleaned_2 = []
    considered_items = []
    limit = len(item_raccom)
    list_prop_cons = []
    covered_items = []
    if limit >= len(triple_structure):
        limit = len(triple_structure)
    i = 0
    while i < limit:
        splitline = triple_structure_cleaned[i].split('\t')
        movies = splitline[0].split(', ')
        add = False
        found = []
        for j in range(len(movies)):
            if movies[j] in covered_items:
                found.insert(j, False)
            else:
                found.insert(j, True)
                covered_items.append(movies[j])

        items = ""
        for s in range(len(found)):
            if found[s] == True:
                add = True
                items += movies[s] + ", "

        if len(items) != 0:
            items = items[0:-2]
        if add:
            list_prop_cons.append(items + "\t" + splitline[1] + "\t" + splitline[2])
        elif limit < len(triple_structure):
            limit = limit + 1
        i = i + 1

    for i in range(len(list_prop_cons)):
        splitlineI = list_prop_cons[i].split('\t')
        recI = splitlineI[0]
        properties = splitlineI[1]
        profI = splitlineI[2]
        for m in range(i + 1, len(list_prop_cons)):
            splitlineJ = list_prop_cons[m].split('\t')
            recJ = splitlineJ[0]
            properties1 = splitlineJ[1]
            profJ = splitlineJ[2]
            if profI == profJ and profI not in considered_items and recI == recJ:
                properties += "-and-" + properties1
        if profI not in considered_items:
            considered_items.append(profI)
        profI_pulito = ""
        prof_splitted = profI.split(', ')
        for n in range(len(prof_splitted)):
            profI_pulito += pulisci_uri_item(prof_splitted[n]) + ", "
        profI_pulito = profI_pulito[0:-2]
        recI_pulito = ""
        rec_splitted = recI.split(', ')
        for p in range(len(rec_splitted)):
            recI_pulito += pulisci_uri_item(rec_splitted[p]) + ", "
        recI_pulito = recI_pulito[0:-2]
        triple_structure_cleaned_2.append(recI_pulito + "\t" + properties + "\t" + profI_pulito)

    triple_structure = triple_structure_cleaned_2

    return triple_structure


# Funzione che genera la spiegazione di primolivello in linguaggio naturale
# Si possono scegliere due tipi di template per generare la spiegazione e la possibilita di inserire tag html
# per la visualizzazione degli items e delle proprieta in una pagina web
def get_explanation_primo_livello(template, item_raccom, triple_structure, profile, G: NXFullGraph, html):
    natural_language_explanation = ""
    global item_spiegati

    if template == 1:                      # costruzione della spiegazione con il primo template
        if len(item_raccom) == 1:                      # costruzione della spiegazione se c'e un solo item raccomandato
            if len(triple_structure) > 0:
                natural_language_explanation = verboIniziale_getRandom() + " " \
                                               + get_item_raccomandato(triple_structure, 0, html) \
                                               + " because " + get_frasi(triple_structure, profile, G, html)
                natural_language_explanation = natural_language_explanation.replace("_", " ")
                while "  " in natural_language_explanation:
                    natural_language_explanation = natural_language_explanation.replace("  ", " ")
            else:
                natural_language_explanation = "Your preferences are really particular! " \
                                               "Sorry, but I can't still explain why you received such a recommendation."

        else:                                          # costruzione della spiegazione se ci sono più items raccomandati
            if len(triple_structure) > 0:
                for i in range(len(triple_structure)):
                    natural_language_explanation += verboIniziale_getRandom() + " " \
                                                    + get_item_raccomandato(triple_structure, i, html) \
                                                    + " because " + get_group_frasi(triple_structure, i, profile, G, html)
                natural_language_explanation = natural_language_explanation.replace("_", " ")
                while "  " in natural_language_explanation:
                    natural_language_explanation = natural_language_explanation.replace("  ", " ")

                #if item_spiegati != 0 and item_spiegati < 5: modificato a.c.
                if item_spiegati < (len(item_raccom)): # modificato a.c.
                    natural_language_explanation += "\nThe other recommendations are really particular, I can't still " \
                                                    "explain why you received them."
            else:
                natural_language_explanation = "Your preferences are really particular! Sorry, but I can't still explain" \
                                               " why you received such a recommendation."

    elif template == 2:                    # costruzione della spiegazione con il secondo template
        if len(item_raccom) == 1:                      # costruzione della spiegazione se c'è un solo item raccomandato
            if len(triple_structure) > 0:
                natural_language_explanation = verboIniziale2_getRandom() + " " \
                                               + get_frasi(triple_structure, profile, G, html) + " "
                frasi_raccomandazione = incipitRacc_getRandom()
                if "So_why_don$t_you" not in frasi_raccomandazione:
                    natural_language_explanation += frasi_raccomandazione + " watch "\
                                                    + get_item_raccomandato(triple_structure, 0, html)
                else:
                    natural_language_explanation += frasi_raccomandazione + " watch " \
                                                    + get_item_raccomandato(triple_structure, 0, html) + " ?"

                natural_language_explanation = natural_language_explanation.replace("_", " ")
                natural_language_explanation = natural_language_explanation.replace("  ", " ")
                natural_language_explanation = natural_language_explanation.replace("$", "\'")
                while "  " in natural_language_explanation:
                    natural_language_explanation = natural_language_explanation.replace("  ", " ")
                if not natural_language_explanation.endswith(".") and not natural_language_explanation.endswith("?"):
                    natural_language_explanation += "."
            else:
                natural_language_explanation = "Your preferences are really particular!" \
                                               " Sorry, but I can't still explain why you received such a recommendation."

        else:                                          # costruzione della spiegazione se ci sono più items raccomandati
            if len(triple_structure) > 0:
                for n in range(len(triple_structure)):
                    if n + 1 < len(triple_structure) and n != 0:
                        natural_language_explanation += get_avverbio(triple_structure) + " " \
                                                        + verboIniziale2_getRandom() + " " + get_group_frasi_2(triple_structure, n, profile, G, html) + ". "
                    elif n < len(triple_structure) and n != 0:
                        natural_language_explanation += get_avverbio_finale(triple_structure) \
                                                        + " " + verboIniziale2_getRandom() + " " + get_group_frasi_2(triple_structure, n, profile, G, html) + ". "
                    else:
                        natural_language_explanation += verboIniziale2_getRandom() + " " \
                                                        + get_group_frasi_2(triple_structure, n, profile, G, html) + ". "

                    frasi_raccomandazione = incipitRacc_getRandom()
                    if "So_why_don$t_you" not in frasi_raccomandazione:
                        natural_language_explanation += "\n" + frasi_raccomandazione + " watch " \
                                                        + get_item_raccomandato(triple_structure, n, html) + ".\n"
                    else:
                        natural_language_explanation += "\n" + frasi_raccomandazione + " watch " \
                                                        + get_item_raccomandato(triple_structure, n, html) + "?\n"

                natural_language_explanation = natural_language_explanation.replace("_", " ")
                natural_language_explanation = natural_language_explanation.replace("$", "\'")
                while "  " in natural_language_explanation:
                    natural_language_explanation = natural_language_explanation.replace("  ", " ")
                if item_spiegati < (len(item_raccom)):
                    natural_language_explanation += "\nThe other recommendations are really particular, I can't still explain why you received them."
            else:
                natural_language_explanation = "Your preferences are really particular! Sorry, but I can't still explain why you received such a recommendation."

    return natural_language_explanation


# funzione che pulisce l'URI di un item lasciando solo il nome dell'item
def pulisci_uri_item(item_corrente):
    item_corrente = item_corrente.replace("http://dbpedia.org/resource/", "")
    item_corrente = item_corrente.replace("/", " ")

    item_pulito = ""
    splitted = item_corrente.split("_")
    for x in range(len(splitted)):
        if not splitted[x].startswith("(") and not splitted[x].endswith(")"):
            item_pulito += splitted[x] + " "

    item_pulito += "."
    item_pulito = item_pulito.replace(" .", "")

    return item_pulito


# Funzione che pulisce l'URI del tipo di proprieta lasciando solo il tipo
def pulisci_subject(subject):
    subject = subject.replace("http://dbpedia.org/ontology/", "")
    subject = subject.replace("http://purl.org/dc/terms/", "")
    subject = subject.replace("http://www.w3.org/2002/07/", "")
    subject = subject.replace("http://www.w3.org/2000/01/", "")

    return subject


# Funzione che pulisce l'URI di una proprieta lasciando solo il nome della proprietà
def pulisci_uri_prop(prop_corrente):
    prop_corrente = prop_corrente.replace("http://dbpedia.org/resource/Category:", "")
    prop_corrente = prop_corrente.replace("http://dbpedia.org/resource/", "")

    prop_pulita = ""
    splitted = prop_corrente.split("_")
    for x in range(len(splitted)):
        if not splitted[x].startswith("(") and not splitted[x].endswith(")"):
            prop_pulita += splitted[x] + " "

    prop_pulita += "."
    prop_pulita = prop_pulita.replace(" .", "")

    return prop_pulita


# Funzione che pulisce la spiegazione generata ed elimina eventuali segni di punteggiatura errati o in eccesso
def pulisci_explanation(explanation):
    explanation = explanation.replace(", ;", ";")
    explanation = explanation.replace(", .", ".")
    explanation = explanation.replace("; .", ".")
    explanation = explanation.replace(" and .", ".")
    explanation = explanation.replace(" as   _", " ")
    explanation = explanation.replace("_", " ")
    explanation = explanation.replace("@", " ")
    explanation = explanation.replace("  ", "")
    explanation = explanation.replace("and you like also movies .", ".")
    explanation = explanation.replace(" as and", " and")
    explanation = explanation.replace(", .", ".")
    explanation = explanation.replace(" as .", ".")
    explanation = explanation.replace("movies Films", " Films")
    explanation = explanation.replace("movies Film", " Films")
    explanation = explanation.replace("alsoFilms", "also Films")

    return explanation


# Funzione che pulisce l'URI di una proprieta per essere inserita nella struttura dati prima di generare la spiegazione
def pulisci_property(property):
    property = property.replace("http://dbpedia.org/resource/Category:Films_based_on_works_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:Films_directed_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:Screenplays_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:Film_scores_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:Films_produced_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:Compositions_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:Works_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:Plays_by_", "")
    property = property.replace("http://dbpedia.org/resource/Category:", "")
    property = property.replace("http://dbpedia.org/resource/Template:", "")
    property = property.replace("http://dbpedia.org/resource/", "")

    return property


# Funzione che sceglie random da una lista il verbo iniziale per la generazione della spiegazione
def verboIniziale_getRandom():
    verbo_iniziale = ["I_suggest_you", "I_propose_you", "I_recommend_you"]
    global used_verboIniziale
    if len(used_verboIniziale) == len(verbo_iniziale):
        used_verboIniziale.clear()

    verbo = random.choice(verbo_iniziale)
    while verbo in used_verboIniziale.keys():
        verbo = random.choice(verbo_iniziale)

    used_verboIniziale[verbo] = ""
    return verbo


# Funzione che sceglie random da una lista l'avverbio per la generazione della spiegazione
def avverbio_getRandom():
    avverbio = ["Furthermore", "In_addition", "Besides", "Next", "Moreover"]
    global used_avverbio
    if len(used_avverbio) == len(avverbio):
        used_avverbio.clear()

    avv = random.choice(avverbio)
    while avv in used_avverbio.keys():
        avv = random.choice(avverbio)

    used_avverbio[avv] = ""
    return avv


# Funzione che sceglie random da una lista l'avverbio finale per la generazione della spiegazione
def avverbioFinale_getRandom():
    avverbio_finale = ["Finally", "At_last", "Lastly"]
    global used_avverbioFinale
    if len(used_avverbioFinale) == len(avverbio_finale):
        used_avverbioFinale.clear()

    avv = random.choice(avverbio_finale)
    while avv in used_avverbioFinale.keys():
        avv = random.choice(avverbio_finale)

    used_avverbioFinale[avv] = ""
    return avv


# Funzione che prende dalla struttura dati precedentemente creata gli items raccomandati e gli organizza
# in modo da inserirli all'interno della spiegazione, varia in base al numero di items raccomandati
# Due configurazioni per aggiungere o meno i tag html per lo stile
def get_item_raccomandato(triple_structure, i, html):
    items = triple_structure[i].split('\t')[0].split(', ')
    item = ""
    global item_spiegati
    if html:                                            # configurazione con tag html
        if len(items) == 1:
            item = "<b>" + items[0] + "</b>"
            item_spiegati = item_spiegati + 1
        elif len(items) == 2:
            item += "<b>" + items[0] + "</b> and <b>" + items[1] + "</b>"
            item_spiegati = item_spiegati + 2
        else:
            for z in range(len(items) - 2):
                item += "<b>" + items[z] + "</b>, "
                item_spiegati = item_spiegati + 1
            item += "<b>" + items[len(items) - 2] + "</b> and <b>" + items[len(items) - 1] + "</b>"
            item_spiegati = item_spiegati + 2
    else:                                               # configurazione senza tag html
        if len(items) == 1:
            item = items[0]
            item_spiegati = item_spiegati + 1
        elif len(items) == 2:
            item += items[0] + "and" + items[1]
            item_spiegati = item_spiegati + 2
        else:
            for z in range(len(items) - 2):
                item += items[z] + ", "
                item_spiegati = item_spiegati + 1
            item += items[len(items) - 2] + "and" + items[len(items) - 1]
            item_spiegati = item_spiegati + 2

    return item


# Funzione che sceglie random da una lista un altro tipo di verbo iniziale per la generazione della spiegazione
def verboIniziale2_getRandom():
    verbo_iniziale_2 = ["I_note", "It_seems", "I_see"]
    global used_verboIniziale2
    if len(used_verboIniziale2) == len(verbo_iniziale_2):
        used_verboIniziale2.clear()

    verbo = random.choice(verbo_iniziale_2)
    while verbo in used_verboIniziale2.keys():
        verbo = random.choice(verbo_iniziale_2)

    used_verboIniziale2[verbo] = ""
    return verbo


# Funzione che sceglie random da una lista l'incipit della frase per la generazione della spiegazione
def incipitRacc_getRandom():
    incipit_racc = ["So_I_suggest_you_to", "Thus_I_suggest_you_to", "This_is_why_I_suggest_you_to",
                    "So_I_recommend_you_to", "So_I_think_you_should", "This_is_why_you_should",
                    "Thus_you_should", "This_is_why_I_recommend_you_to", "This_is_why_I_think_you_should",
                    "So_why_don$t_you", "Thus_it_could_be_that_you_like_to"]
    global used_incipitRacc
    if len(used_incipitRacc) == len(incipit_racc):
        used_incipitRacc.clear()

    incipit = random.choice(incipit_racc)
    while incipit in used_incipitRacc.keys():
        incipit = random.choice(incipit_racc)

    used_incipitRacc[incipit] = ""
    return incipit


# Funzione che per ogni riga della struttura dati creata richiama la funzione che costruisce le frasi
def get_frasi(triple_structure, profile, G: NXFullGraph, html):
    frasi = ""
    for i in range(len(triple_structure)):
        frasi += costruisci_frase(triple_structure, i, profile, G, html)

    return frasi


# Funzione che richiama la funzione che costruisce la frase
def get_group_frasi(triple_structure, i, profile, G: NXFullGraph, html):
    return costruisci_frase(triple_structure, i, profile, G, html)


# Funzione che costruisce la frase che spiega la raccomandazione e inserisce gli avverbi in base al numero di raccomandazioni
def costruisci_frase(triple_structure, i, profile, G: NXFullGraph, html):
    frase = ""
    if i + 2 < len(triple_structure):
        frase += "you " + get_avverbio_gradimento(triple_structure, i, profile, G) + "like " + get_lista_proprieta(triple_structure, i, html) + ".\n " + get_avverbio(triple_structure)
    elif i + 1 < len(triple_structure):
        frase += "you " + get_avverbio_gradimento(triple_structure, i, profile, G) + "like " + get_lista_proprieta(triple_structure, i, html) + ".\n " + get_avverbio_finale(triple_structure)
    else:
        frase += "you " + get_avverbio_gradimento(triple_structure, i, profile, G) + "like " + get_lista_proprieta(triple_structure, i, html) + ".\n "

    return frase


# Funzione che richiama una seconda funzione che costruisce la frase in un modo differente
def get_group_frasi_2(triple_structure, i, profile, G: NXFullGraph, html):
    return costruisci_frase_2(triple_structure, i, profile, G, html)


# Funzione che costruisce la frase che spiega la raccomandazione in un modo differente
def costruisci_frase_2(triple_structure, i, profile, G: NXFullGraph, html):
    frase = ""
    frase += "you " + get_avverbio_gradimento(triple_structure, i, profile, G) + "like " + get_lista_proprieta(triple_structure, i, html)

    return frase

# Funzione che recupera la lista delle proprieta dalla struttura dati creata e che verranno usate nella spiegazione
# e le inserisce nella frase della spiegazione in modo opportuno
# Due configurazioni nel caso in cui si voglia inserire o meno i tag html per lo stile
def get_lista_proprieta(triple_structure, i, html):
    splitted = triple_structure[i].split('\t')
    properties = splitted[1].split('-and-')
    lista_proprieta = ""
    domain = "movies"

    for j in range(len(properties)):
        natural_language_property = get_subject_prop(properties[j]).replace("_", "") + " "
        if "ovie" in natural_language_property or "film" in natural_language_property or "Film" in natural_language_property or "films" in natural_language_property or "creenplay" in natural_language_property or "franchise" in natural_language_property or "serie" in natural_language_property:
            domain = ""
        natural_language_property = domain + " " + natural_language_property

        if html:
            if len(natural_language_property) > 0:
                lista_proprieta += "<i>" + natural_language_property[0:-1] + "</i>"
            if j + 2 < len(properties):
                lista_proprieta += ", "
            elif j + 1 < len(properties):
                lista_proprieta += " and "
        else:
            if len(natural_language_property) > 0:
                lista_proprieta += natural_language_property[0:-1]
            if j + 2 < len(properties):
                lista_proprieta += ", "
            elif j + 1 < len(properties):
                lista_proprieta += " and "

    lista_film = splitted[2].split(',')
    films = ""
    if html:
        if len(lista_film) == 1:
            films += "<b>" + lista_film[0] + "</b>"
        elif len(lista_film) == 2:
            films += "<b>" + lista_film[0] + "</b> and <b>" + lista_film[1] + "</b>"
        else:
            for z in range(len(lista_film) - 2):
                films += "<b>" + lista_film[z] + "</b>, "
            films += "<b>" + lista_film[len(lista_film) - 2] + "</b> and <b>" + lista_film[len(lista_film) - 1] + "</b>"
    else:
        if len(lista_film) == 1:
            films += lista_film[0]
        elif len(lista_film) == 2:
            films += lista_film[0] + " and " + lista_film[1]
        else:
            for x in range(len(lista_film) - 2):
                films += lista_film[x] + ", "
            films += lista_film[len(lista_film) - 2] + " and " + lista_film[len(lista_film) - 1]
    lista_proprieta += ", "

    return lista_proprieta + "such as " + films


# Funzione che sceglie l'avverbio di gradimento in modo dinamico in base al numero di volte che la proprieta
# appare nel profilo dell'utente. La scelta viene effettuata attraverso il calcolo di un punteggio di frequenza
def get_quantificatore(property, movies_user_rated, G: NXFullGraph):
    movies_with_prop_only_one = {}
    property_movies = []
    film_with_property = 0
    prop_in_edges = G.get_predecessors(property)
    """with open('movies_stored_prop.mapping', 'r') as f:
        for line in f:
            line = line.rstrip().split('\t')
            property_movies.append(line)
    for line in property_movies:
        if property == line[2]:
            movies_with_prop_only_one[line[0]] = ""

    for movie_curr in movies_with_prop_only_one.keys():
        for key, value in movies_user_rated.items():
            if movie_curr == value:
                film_with_property = film_with_property + 1
    """
    score = len(prop_in_edges) / len(movies_user_rated)
    if score == 1.0:
        quantificatore = "always "
    elif score < 1.0 and score >= 0.6:
        quantificatore = "often "
    elif score < 0.6 and score >= 0.3:
        quantificatore = "sometimes "
    else:
        quantificatore = " "

    return quantificatore


# Funzione che richiama la funzione che sceglie l'avverbio di gradimento in modo dinamico in base al numero di volte
# che la proprieta appare nel profilo dell'utente
def get_avverbio_gradimento(triple_structure, i, profile, G: NXFullGraph):
    property = triple_structure[i].split('\t')[1].split('-and-')[0]
    return get_quantificatore(property, profile, G)


# Funzione che in base al numero di raccomandazioni decide se inserire o meno l'avverbio nella frase
def get_avverbio(triple_structure):
    if len(triple_structure) == 1:
        return ""
    else:
        return "\n" + avverbio_getRandom() + ", "


# Funzione che in base al numero di raccomandazioni decide se inserire o meno l'avverbio nella frase e inoltre
# sceglie quale avverbio inserire (normale o finale) controllando se si tratta dell'ultimo item da raccomandare
def get_avverbio_finale(triple_structure):
    if len(triple_structure) == 1:
        return ""
    elif len(triple_structure) == 2:
        return "\n" + avverbio_getRandom() + ", "
    else:
        return "\n" + avverbioFinale_getRandom() + ", "


# Funzione che carica dal file di mapping le proprieta con i rispettivi tipi
def carica_properties_item():
    properties_items = []
    with open('properties_subject_movies.mapping', 'r') as f:
        for line in f:
            line = line.split('\t')
            if len(line) == 2:
                splitline = [line[0], line[1]]
                properties_items.append(splitline)
            else:
                splitline = [line[0], "N.D."]
                properties_items.append(splitline)

    return properties_items


# Funzione che carica dal file di mapping i predicati con i rispettivi tipi
def carica_properties_text():
    predicate_text = []
    with open('subject_movies.mapping', 'r') as f:
        for line in f:
            line = line.split('\t')
            if len(line) == 2:
                splitline = [line[0], line[1]]
                predicate_text.append(splitline)
            else:
                splitline = [line[0], "N.D."]
                predicate_text.append(splitline)

    return predicate_text


# Funzione che prende e inserisce nella frase il tipo della proprieta che si sta considerando e che recupera dai file
# di mapping, insieme al predicato corrispondente al tipo di proprieta
# Viene fatta anche la pulizia degli URI
def get_subject_prop(prop_corrente):
    properties_items = carica_properties_item()            # carico le proprieta con il rispettivo tipo
    predicate_text = carica_properties_text()              # carico i predicati con i rispettivi tipi
    predicate = ""
    text = ""
    for items in properties_items:
        if prop_corrente == items[0]:
            predicate += items[1].rstrip()
            break
    for elem in predicate_text:
        if predicate == elem[0]:
            text += elem[1].rstrip()
            break
    prop_corrente = prop_corrente.replace("http://dbpedia.org/resource/Category:", "")
    prop_corrente = prop_corrente.replace("http://dbpedia.org/resource/Template:", "")
    prop_corrente = prop_corrente.replace("http://dbpedia.org/resource/", "")

    prop_pulita = ""
    splitted = prop_corrente.split('_')
    for i in range(len(splitted)):
        prop_pulita += splitted[i] + " "

    prop_pulita += "."
    prop_pulita = prop_pulita.replace(" .", "")
    prop_pulita = prop_pulita.replace("(director)", "")
    prop_pulita = prop_pulita.replace("(composer)", "")
    prop_pulita = prop_pulita.replace("(", "")
    prop_pulita = prop_pulita.replace(")", "")
    if text is None:
        text = ""
    prop_corrente1 = text + " " + prop_pulita

    return prop_corrente1

# Funzione che prende in input il grafo creato e l'URI di una proprieta e stampa gli archi entranti (film piaciuti)
# e gli archi uscenti (film raccomandati) di quella spcifica proprieta
def stampa_vicini(G, item):
    archi_entranti = G.in_edges(item)
    print("Archi entranti per il nodo ", item, " (film piaciuti):")
    for archi_entranti_spec in archi_entranti:
        print(archi_entranti_spec[0])

    archi_uscenti = G.out_edges(item)
    print("Archi uscenti per il nodo ", item, " (film raccomandati):")
    for archi_uscenti_spec in archi_uscenti:
        print(archi_uscenti_spec[1])

# Funzione che disegna e visualizza il grafo creato
#DA INSERIRE NELLA CLASSE CHE CREA IL GRAFO NXFullGraph dei film e delle proprietà
#La stampa del grafo G: NXFullGraph non è implementata al suo posto stampa una stringa
#temporanea
def visualizza_grafo(G: NXFullGraph):
   print("*Stampa del grafo* \n")
