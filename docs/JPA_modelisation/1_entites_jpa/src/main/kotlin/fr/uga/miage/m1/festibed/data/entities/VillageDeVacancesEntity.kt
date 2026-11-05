package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import fr.uga.miage.m1.festibed.enums.MentionVillage
import fr.uga.miage.m1.festibed.enums.TypeSejour
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

@Entity
@Table(name = "VILLAGE_DE_VACANCES")
class VillageDeVacancesEntity(
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
    var nbLogements: Int,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(length = 30)
    var mention: MentionVillage? = null,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(length = 30)
    var typeSejour: TypeSejour? = null,
) : EtablissementEntity(
    id, nomCommercial, adresse, codePostalEtablissement, nomCommuneEtablissement, commune, telephoneEtablissement,
    emailEtablissement, siteWebEtablissement, capaciteAccueil, classement, dateClassement, classementProroge,
    latitudeEtablissement, longitudeEtablissement, osmRef, hebergeur,
)
