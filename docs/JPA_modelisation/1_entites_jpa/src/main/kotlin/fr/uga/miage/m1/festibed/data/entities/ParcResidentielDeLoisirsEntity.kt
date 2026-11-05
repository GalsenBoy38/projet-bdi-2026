package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Table
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

@Entity
@Table(name = "PARC_RESIDENTIEL_DE_LOISIRS")
class ParcResidentielDeLoisirsEntity(
    id: UUID? = null,
    nomCommercial: String,
    adresse: String,
    codePostalEtablissement: String,
    nomCommuneEtablissement: String,
    commune: CommuneEntity? = null,
    telephoneEtablissement: String? = null,
    emailEtablissement: String? = null,
    siteWebEtablissement: String? = null,
    capaciteAccueil: Int,
    classement: Classement,
    dateClassement: LocalDate,
    classementProroge: Boolean = false,
    latitudeEtablissement: BigDecimal? = null,
    longitudeEtablissement: BigDecimal? = null,
    osmRef: String? = null,
    hebergeur: HebergeurEntity? = null,

    @Column(nullable = false)
    var nbEmplacementsParc: Int,
) : EtablissementEntity(
    id, nomCommercial, adresse, codePostalEtablissement, nomCommuneEtablissement, commune, telephoneEtablissement,
    emailEtablissement, siteWebEtablissement, capaciteAccueil, classement, dateClassement, classementProroge,
    latitudeEtablissement, longitudeEtablissement, osmRef, hebergeur,
)
