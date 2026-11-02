package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.FetchType
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.Inheritance
import jakarta.persistence.InheritanceType
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.SequenceGenerator
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.time.LocalDate

/**
 * Établissement d'hébergement classé (jeu public). Héritage JOINED : une table par typologie.
 * Classe abstraite (pas data class) : Kotlin interdit d'hériter d'une data class.
 *
 * Performance : une requête polymorphe joint les 6 sous-tables ; pour la recherche d'hébergements,
 * HebergementRepository.rechercherDisponibles utilise une projection DTO.
 */
@Entity
@Table(
    name = "ETABLISSEMENT",
    indexes = [
        Index(name = "IX_ETABLISSEMENT_1", columnList = "latitudeEtablissement, longitudeEtablissement"),
        Index(name = "IX_ETABLISSEMENT_2", columnList = "codePostalEtablissement"),
        Index(name = "IX_ETABLISSEMENT_3", columnList = "idUtilisateur"),
    ],
)
@Inheritance(strategy = InheritanceType.JOINED)
abstract class EtablissementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seqEtablissement")
    @SequenceGenerator(name = "seqEtablissement", sequenceName = "SEQ_ETABLISSEMENT", allocationSize = 50)
    @Column(name = "idEtablissement", nullable = false)
    val id: Long? = null,

    @Column(name = "nomCommercial", nullable = false, length = 80)
    var nomCommercial: String,

    @Column(name = "adresse", nullable = false, length = 80)
    var adresse: String,

    @Column(name = "codePostalEtablissement", nullable = false, length = 5)
    var codePostalEtablissement: String,

    @Column(name = "nomCommuneEtablissement", nullable = false, length = 50)
    var nomCommuneEtablissement: String,

    /** Absent du jeu public : NULL tant que l'hébergeur ne l'a pas renseigné. */
    @Column(name = "telephoneEtablissement", length = 30)
    var telephoneEtablissement: String? = null,

    @Column(name = "siteWebEtablissement", length = 350)
    var siteWebEtablissement: String? = null,

    @Column(name = "capaciteAccueil", nullable = false)
    var capaciteAccueil: Int,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "classement", nullable = false, length = 50)
    var classement: Classement,

    @Column(name = "dateClassement", nullable = false)
    var dateClassement: LocalDate,

    @Column(name = "classementProroge", nullable = false)
    var classementProroge: Boolean = false,

    /** Coordonnées obtenues par géocodage BAN (absentes du CSV public). */
    @Column(name = "latitudeEtablissement", precision = 12, scale = 9)
    var latitudeEtablissement: BigDecimal? = null,

    @Column(name = "longitudeEtablissement", precision = 12, scale = 9)
    var longitudeEtablissement: BigDecimal? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "idUtilisateur")
    var hebergeur: HebergeurEntity? = null,
) {
    /**
     * Moyenne des notations, dénormalisée pour le filtre « note de l'établissement ».
     * LECTURE SEULE pour JPA : mise à jour par EtablissementRepository.ajouterNote (UPDATE atomique).
     */
    @Column(name = "noteMoyenne", precision = 3, scale = 2, insertable = false, updatable = false)
    val noteMoyenne: BigDecimal? = null

    @Column(name = "nbNotes", nullable = false, insertable = false, updatable = false)
    val nbNotes: Int = 0

    override fun equals(other: Any?) = this === other || (other is EtablissementEntity && id != null && id == other.id)
    override fun hashCode() = EtablissementEntity::class.hashCode()
    override fun toString() = "${this::class.simpleName}(id=$id, nomCommercial=$nomCommercial)"
}
