package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import fr.uga.miage.m1.festibed.enums.MentionVillage
import fr.uga.miage.m1.festibed.enums.TypeSejour
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.PrimaryKeyJoinColumn
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.time.LocalDate

@Entity
@Table(name = "VILLAGE_DE_VACANCES")
@PrimaryKeyJoinColumn(name = "idEtablissement")
class VillageDeVacancesEntity(
    id: Long? = null,
    nomCommercial: String,
    adresse: String,
    codePostalEtablissement: String,
    nomCommuneEtablissement: String,
    telephoneEtablissement: String? = null,
    siteWebEtablissement: String? = null,
    capaciteAccueil: Int,
    classement: Classement,
    dateClassement: LocalDate,
    classementProroge: Boolean = false,
    latitudeEtablissement: BigDecimal? = null,
    longitudeEtablissement: BigDecimal? = null,
    hebergeur: HebergeurEntity? = null,

    @Column(name = "nbLogements", nullable = false)
    var nbLogements: Int,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "mention", length = 30)
    var mention: MentionVillage? = null,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "typeSejour", length = 30)
    var typeSejour: TypeSejour? = null,
) : EtablissementEntity(
    id, nomCommercial, adresse, codePostalEtablissement, nomCommuneEtablissement, telephoneEtablissement,
    siteWebEtablissement, capaciteAccueil, classement, dateClassement, classementProroge,
    latitudeEtablissement, longitudeEtablissement, hebergeur,
)
