package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import fr.uga.miage.m1.festibed.enums.MentionVillage
import fr.uga.miage.m1.festibed.enums.TypeSejour
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

@Entity
@Table(name = "village_de_vacances")
class VillageDeVacancesEntity(
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

    @Column(name = "nb_logements", nullable = false)
    var nbLogements: Int,

    @Enumerated(EnumType.STRING)
    @Column(length = 30)
    var mention: MentionVillage? = null,

    @Enumerated(EnumType.STRING)
    @Column(name = "type_sejour", length = 30)
    var typeSejour: TypeSejour? = null,
) : EtablissementEntity(
    id, nomCommercial, adresse, codePostal, nomCommune, commune, telephone, email, siteWeb, capaciteAccueil,
    classement, dateClassement, classementProroge, latitude, longitude, osmRef, hebergeur,
)
