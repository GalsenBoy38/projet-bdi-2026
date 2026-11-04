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
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.math.BigDecimal
import java.util.UUID

/**
 * Une sélection = un festival + ses Pass + ses nuitées (indissociables, « réservation groupée »).
 * Un même festival n'apparaît qu'une fois par réservation. Les nuitées occupées se lisent par
 * NuiteeRepository.findAllBySelectionId.
 */
@Entity
@Table(
    name = "selection",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_selection_reservation_festival", columnNames = ["reservation_id", "festival_id"]),
    ],
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
    @Column(name = "prix_pass", nullable = false, precision = 8, scale = 2)
    var prixPass: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    var statut: StatutSelection = StatutSelection.CONFIRMEE,

    /** Composition : les Pass naissent et meurent avec la sélection. */
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "selection_id", nullable = false)
    var passes: MutableCollection<PassEntity> = mutableListOf(),
)
