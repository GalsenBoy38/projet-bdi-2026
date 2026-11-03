package fr.uga.miage.m1.festibed.enums

/** Type d'un établissement non classé, d'après la balise OSM tourism=* (wilderness_hut, non réservable, est écarté). */
enum class TypeNonClasse {
    HOTEL,
    MOTEL,
    CHAMBRE_D_HOTES,
    GITE_CHALET,
    APPARTEMENT,
    AUBERGE_DE_JEUNESSE,
    CAMPING,
    AIRE_DE_CAMPING_CAR,
    REFUGE_GARDE,
}
