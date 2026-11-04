package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

@Entity
@Table(name = "auberge_collective")
class AubergeCollectiveEntity(
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
    classement: Classement,
    dateClassement: LocalDate,
    classementProroge: Boolean = false,
    latitude: BigDecimal? = null,
    longitude: BigDecimal? = null,
    osmRef: String? = null,
    hebergeur: HebergeurEntity? = null,

    @Column(name = "nb_chambres", nullable = false)
    var nbChambres: Int,
) : EtablissementEntity(
    id, nomCommercial, adresse, codePostal, nomCommune, commune, telephone, email, siteWeb, capaciteAccueil,
    classement, dateClassement, classementProroge, latitude, longitude, osmRef, hebergeur,
)
