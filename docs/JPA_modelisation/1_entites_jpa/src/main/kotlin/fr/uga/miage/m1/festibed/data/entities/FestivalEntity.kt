package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.Domaine
import fr.uga.miage.m1.festibed.enums.Periodicite
import fr.uga.miage.m1.festibed.enums.SousDomaine
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.FetchType
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
        Index(name = "IX_FESTIVAL_2", columnList = "codeInsee"),
        Index(name = "IX_FESTIVAL_3", columnList = "domaine"),
        Index(name = "IX_FESTIVAL_4", columnList = "idOrganisateur"),
    ],
)
data class FestivalEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "idFestival", nullable = false)
    val id: UUID? = null,

    @Column(name = "nomFestival", nullable = false, length = 100)
    var nomFestival: String,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "domaine", nullable = false, length = 40)
    var domaine: Domaine,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "sousDomaine", length = 70)
    var sousDomaine: SousDomaine? = null,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "periodicite", length = 30)
    var periodicite: Periodicite? = null,

    @Column(name = "moisDebut", nullable = false)
    var moisDebut: Int,

    @Column(name = "siteWebFestival", length = 150)
    var siteWebFestival: String? = null,

    /** Identifiant du jeu public : NON unique (codes génériques XX999 et valeurs vides). */
    @Column(name = "numIdentification", length = 50)
    var numIdentification: String? = null,

    @Column(name = "dateCreation")
    var dateCreation: LocalDate? = null,

    @Column(name = "codePostalFestival", nullable = false, length = 5)
    var codePostalFestival: String,

    @Column(name = "dateDebutFestival", nullable = false)
    var dateDebutFestival: LocalDate,

    @Column(name = "dateFinFestival", nullable = false)
    var dateFinFestival: LocalDate,

    /** Dates de la source publique (éditions 2017-2020), conservées pour la traçabilité. */
    @Column(name = "dateDebutAncien")
    var dateDebutAncien: LocalDate? = null,

    @Column(name = "dateFinAncien")
    var dateFinAncien: LocalDate? = null,

    /** Nombre maximal de Pass que l'organisateur confie à FestiBed (>= 30). */
    @Column(name = "quotaPass", nullable = false)
    var quotaPass: Int,

    @Column(name = "prixPass", nullable = false, precision = 8, scale = 2)
    var prixPass: BigDecimal,

    /**
     * Pass déjà vendus. LECTURE SEULE pour JPA (insertable/updatable = false) : modifiée uniquement
     * par l'UPDATE conditionnel FestivalRepository.reserverPass ; sinon la sauvegarde d'un festival
     * modifié par l'organisateur écraserait les ventes faites entre-temps (lost update).
     */
    @Column(name = "nbPassVendus", nullable = false, insertable = false, updatable = false)
    val nbPassVendus: Int = 0,

    @Column(name = "actifFestival", nullable = false)
    var actifFestival: Boolean = true,

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "codeInsee", nullable = false)
    var commune: CommuneEntity,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "idOrganisateur")
    var organisateur: OrganisateurEntity? = null,
) {
    val passDisponibles: Int get() = quotaPass - nbPassVendus

    override fun equals(other: Any?) = this === other || (other is FestivalEntity && id != null && id == other.id)
    override fun hashCode() = FestivalEntity::class.hashCode()
    override fun toString() = "FestivalEntity(id=$id, nomFestival=$nomFestival)"
}
