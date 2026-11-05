package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Domaine
import fr.uga.miage.m1.festibed.enums.Periodicite
import fr.uga.miage.m1.festibed.enums.SousDomaine
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

@Entity
@Table(
    name = "FESTIVAL",
    indexes = [
        Index(name = "IX_FESTIVAL_1", columnList = "dateDebutFestival, dateFinFestival"),
        Index(name = "IX_FESTIVAL_2", columnList = "commune_id"),
        Index(name = "IX_FESTIVAL_3", columnList = "domaine"),
        Index(name = "IX_FESTIVAL_4", columnList = "organisateur_id"),
    ],
)
data class FestivalEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(nullable = false, length = 100)
    var nomFestival: String,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(nullable = false, length = 40)
    var domaine: Domaine,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(length = 70)
    var sousDomaine: SousDomaine? = null,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(length = 30)
    var periodicite: Periodicite? = null,

    @Column(nullable = false)
    var moisDebut: Int,

    @Column(length = 150)
    var siteWebFestival: String? = null,

    /** Identifiant du jeu public : NON unique (codes génériques XX999 et valeurs vides). */
    @Column(length = 50)
    var numIdentification: String? = null,

    @Column
    var dateCreation: LocalDate? = null,

    @Column(nullable = false, length = 5)
    var codePostalFestival: String,

    @Column(nullable = false)
    var dateDebutFestival: LocalDate,

    @Column(nullable = false)
    var dateFinFestival: LocalDate,

    /** Dates de la source publique (éditions 2017-2020), conservées pour la traçabilité. */
    @Column
    var dateDebutAncien: LocalDate? = null,

    @Column
    var dateFinAncien: LocalDate? = null,

    /** Nombre maximal de Pass que l'organisateur confie à FestiBed (>= 30). */
    @Column(nullable = false)
    var quotaPass: Int,

    @Column(nullable = false, precision = 8, scale = 2)
    var prixPass: BigDecimal,

    /**
     * Pass déjà vendus. LECTURE SEULE pour JPA (insertable/updatable = false) : modifiée uniquement
     * par l'UPDATE conditionnel FestivalRepository.reserverPass ; sinon la sauvegarde d'un festival
     * modifié par l'organisateur écraserait les ventes faites entre-temps (lost update).
     */
    @Column(nullable = false, insertable = false, updatable = false)
    val nbPassVendus: Int = 0,

    @Column(nullable = false)
    var actifFestival: Boolean = true,

    @ManyToOne(optional = false)
    @JoinColumn(name = "commune_id", nullable = false)
    var commune: CommuneEntity,

    @ManyToOne
    @JoinColumn(name = "organisateur_id")
    var organisateur: OrganisateurEntity? = null,
) {
    val passDisponibles: Int get() = quotaPass - nbPassVendus

    override fun equals(other: Any?) = this === other || (other is FestivalEntity && id != null && id == other.id)
    override fun hashCode() = FestivalEntity::class.hashCode()
    override fun toString() = "FestivalEntity(id=$id, nomFestival=$nomFestival)"
}
