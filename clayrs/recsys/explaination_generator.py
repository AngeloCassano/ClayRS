# Funzione che prende in input il grafo creato, le proprieta rankate da considerare, i due dizionari dei film piaciuti
# e raccomandati e inizializza la struttura dati che sara data in input alla funzione che genera la spiegazione
# partendo da questi dati
def build_triple_structure(G, score_properties, profile, recommendation):
    NewPreGenArchitecture = [] #list of triple of URI (URI film name -URI property- URI film name)
    profile_prov = get_property_movies(profile)                       # temporary list of the profile films' properties
    recommendations_prov = get_property_movies(recommendation)        # temporary list of the reccomenated films' properties
    # dall'elenco delle proprietà vado a ricavare i film del profilo e quelli raccomandati, operazioni inutili
    profile = []
    recommendations = []
    for line in profile_prov:
        if not (line[0] in profile):
            profile.append(line[0])

    for line in recommendations_prov:
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
            NewPreGenArchitecture.append(str(recomm_nodes) + "\t" + prop + "\t" + str(profile_nodes))

    return NewPreGenArchitecture

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
def estraiNodiOpposti_item_prop(G, item):

    map_prop = {}
    prop_in_edges = G.in_edges(item)                    # calcola archi entranti nella proprieta
    for in_edge in prop_in_edges:
        in_opposite_node = in_edge[0]                  # prende il nodo opposto
        map_prop[in_opposite_node] = ""

    prop_out_edges = G.out_edges(item)                      # calcola archi uscenti dalla proprieta
    for out_edge in prop_out_edges:
        out_opposite_node = out_edge[1]                # prende il nodo opposto
        map_prop[out_opposite_node] = ""

    opposite_nodes = map_prop.keys()
    return opposite_nodes