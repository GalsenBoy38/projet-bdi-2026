package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.StatutSelection
import jakarta.persistence.CascadeType
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
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.util.UUID

/**
 * Une sélection = un festival + ses Pass + ses nuitées (indissociables, « réservation groupée »).
 * Un même festival n'apparaît qu'une fois par réservation (UK reservation_id + festival_id).
 * La colonne reservation_id est gérée par ReservationEntity.selections ; les nuitées occupées
 * se lisent par NuiteeRepository.findAllBySelectionId (pas de collection ici : relations unidirectionnelles).
 */
@Entity
@Table(
    name = "SELECTION",
    uniqueConstraints = [UniqueConstraint(name = "UK_SELECTION_1", columnNames = ["reservation_id", "festival_id"])],
    indexes = [Index(name = "IX_SELECTION_1", columnList = "festival_id")],
)
data class SelectionEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @ManyToOne(optional = false)
    @JoinColumn(name = "festival_id", nullable = false)
    var festival: FestivalEntity,

    /** Prix du Pass au moment de la réservation (le prix du festival peut changer ensuite). */
    @Column(nullable = false, precision = 8, scale = 2)
    var prixPassSelection: BigDecimal,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(nullable = false, length = 20)
    var statutSelection: StatutSelection = StatutSelection.CONFIRMEE,

    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "selection_id", nullable = false)
    var passes: MutableCollection<PassEntity> = mutableListOf(),
) {
    override fun equals(other: Any?) = this === other || (other is SelectionEntity && id != null && id == other.id)
    override fun hashCode() = SelectionEntity::class.hashCode()
    override fun toString() = "SelectionEntity(id=$id, statutSelection=$statutSelection)"
}
