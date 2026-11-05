package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.TypeNonClasse
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Index
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.util.UUID

/**
 * Hébergement touristique recensé par OpenStreetMap mais absent de la liste officielle des établissements
 * classés (chambres d'hôtes, gîtes, appartements, auberges de jeunesse, hôtels non classés…).
 * Pas de classement : classement, dateClassement et classementProroge restent NULL.
 */
@Entity
@Table(
    name = "ETABLISSEMENT_NON_CLASSE",
    indexes = [Index(name = "IX_ETABLISSEMENT_NON_CLASSE_1", columnList = "typeNonClasse")],
)
class EtablissementNonClasseEntity(
    id: UUID? = null,
    nomCommercial: String,
    adresse: String? = null,
    codePostalEtablissement: String,
    nomCommuneEtablissement: String,
    commune: CommuneEntity? = null,
    telephoneEtablissement: String? = null,
    emailEtablissement: String? = null,
    siteWebEtablissement: String? = null,
    capaciteAccueil: Int,
    latitudeEtablissement: BigDecimal? = null,
    longitudeEtablissement: BigDecimal? = null,
    osmRef: String? = null,
    hebergeur: HebergeurEntity? = null,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(nullable = false, length = 30)
    var typeNonClasse: TypeNonClasse,

    /** Étoiles déclarées dans OSM (1 à 5) : information, pas un classement officiel. */
    @Column
    var nbEtoilesDeclarees: Int? = null,

    @Column
    var nbChambres: Int? = null,

    @Column
    var nbLits: Int? = null,
) : EtablissementEntity(
    id, nomCommercial, adresse, codePostalEtablissement, nomCommuneEtablissement, commune, telephoneEtablissement,
    emailEtablissement, siteWebEtablissement, capaciteAccueil, null, null, null,
    latitudeEtablissement, longitudeEtablissement, osmRef, hebergeur,
)
