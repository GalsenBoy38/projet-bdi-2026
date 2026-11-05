package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Classement
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.Inheritance
import jakarta.persistence.InheritanceType
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/**
 * Établissement d'hébergement. Héritage JOINED : une table par typologie officielle (établissements
 * classés) + ETABLISSEMENT_NON_CLASSE (lieux recensés par OpenStreetMap).
 * Classe abstraite (pas data class) : Kotlin interdit d'hériter d'une data class.
 *
 * classement, dateClassement et classementProroge sont tous trois renseignés (classé) ou tous trois NULL
 * (non classé) : contrainte CHECK du schéma. Les sous-classes classées les exigent dans leur constructeur.
 *
 * Performance : une requête polymorphe joint les 7 sous-tables ; pour la recherche d'hébergements,
 * HebergementRepository.rechercherDisponibles utilise une projection DTO.
 */
@Entity
@Table(
    name = "ETABLISSEMENT",
    uniqueConstraints = [UniqueConstraint(name = "UK_ETABLISSEMENT_1", columnNames = ["osmRef"])],
    indexes = [
        Index(name = "IX_ETABLISSEMENT_1", columnList = "latitudeEtablissement, longitudeEtablissement"),
        Index(name = "IX_ETABLISSEMENT_2", columnList = "codePostalEtablissement"),
        Index(name = "IX_ETABLISSEMENT_3", columnList = "hebergeur_id"),
        Index(name = "IX_ETABLISSEMENT_4", columnList = "commune_id"),
    ],
)
@Inheritance(strategy = InheritanceType.JOINED)
abstract class EtablissementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(nullable = false, length = 100)
    var nomCommercial: String,

    /** NULL pour un lieu OSM sans adresse à moins de 200 m (refuge, camping isolé…). */
    @Column(length = 80)
    var adresse: String? = null,

    @Column(nullable = false, length = 5)
    var codePostalEtablissement: String,

    @Column(nullable = false, length = 50)
    var nomCommuneEtablissement: String,

    /** Commune INSEE (OSM ou géocodage BAN) ; nomCommuneEtablissement reste le libellé postal. */
    @ManyToOne
    @JoinColumn(name = "commune_id")
    var commune: CommuneEntity? = null,

    /** Premier numéro OSM ; NULL si l'établissement n'est pas dans OSM ou n'y a pas de numéro. */
    @Column(length = 30)
    var telephoneEtablissement: String? = null,

    @Column(length = 150)
    var emailEtablissement: String? = null,

    @Column(length = 350)
    var siteWebEtablissement: String? = null,

    @Column(nullable = false)
    var capaciteAccueil: Int,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(length = 50)
    var classement: Classement? = null,

    @Column
    var dateClassement: LocalDate? = null,

    @Column
    var classementProroge: Boolean? = null,

    /** Point OSM si l'établissement y est recensé, sinon géocodage BAN de l'adresse. */
    @Column(precision = 12, scale = 9)
    var latitudeEtablissement: BigDecimal? = null,

    @Column(precision = 12, scale = 9)
    var longitudeEtablissement: BigDecimal? = null,

    /** Objet OpenStreetMap correspondant (« node/123 », « relation/456 »), pour les mises à jour. */
    @Column(length = 25)
    var osmRef: String? = null,

    @ManyToOne
    @JoinColumn(name = "hebergeur_id")
    var hebergeur: HebergeurEntity? = null,
) {
    val estClasse: Boolean get() = classement != null

    /**
     * Moyenne des notations, dénormalisée pour le filtre « note de l'établissement ».
     * LECTURE SEULE pour JPA : mise à jour par EtablissementRepository.ajouterNote (UPDATE atomique).
     */
    @Column(precision = 3, scale = 2, insertable = false, updatable = false)
    val noteMoyenne: BigDecimal? = null

    @Column(nullable = false, insertable = false, updatable = false)
    val nbNotes: Int = 0

    override fun equals(other: Any?) = this === other || (other is EtablissementEntity && id != null && id == other.id)
    override fun hashCode() = EtablissementEntity::class.hashCode()
    override fun toString() = "${this::class.simpleName}(id=$id, nomCommercial=$nomCommercial)"
}
