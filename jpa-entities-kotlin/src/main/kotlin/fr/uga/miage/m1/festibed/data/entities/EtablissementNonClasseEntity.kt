package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.TypeNonClasse
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Table
import java.math.BigDecimal
import java.util.UUID

/** Établissement non classé importé d'OpenStreetMap : classement toujours null. */
@Entity
@Table(name = "etablissement_non_classe")
class EtablissementNonClasseEntity(
    id: UUID? = null,
    nomCommercial: String,
    adresse: String? = null,
    codePostal: String,
    nomCommune: String,
    commune: CommuneEntity? = null,
    telephone: String? = null,
    email: String? = null,
    siteWeb: String? = null,
    capaciteAccueil: Int,
    latitude: BigDecimal? = null,
    longitude: BigDecimal? = null,
    osmRef: String? = null,
    hebergeur: HebergeurEntity? = null,

    @Enumerated(EnumType.STRING)
    @Column(name = "type_non_classe", nullable = false, length = 30)
    var typeNonClasse: TypeNonClasse,

    /** Étoiles déclarées dans OSM : information, pas un classement officiel. */
    @Column(name = "nb_etoiles_declarees")
    var nbEtoilesDeclarees: Int? = null,

    @Column(name = "nb_chambres")
    var nbChambres: Int? = null,

    @Column(name = "nb_lits")
    var nbLits: Int? = null,
) : EtablissementEntity(
    id, nomCommercial, adresse, codePostal, nomCommune, commune, telephone, email, siteWeb, capaciteAccueil,
    null, null, null, latitude, longitude, osmRef, hebergeur,
)
