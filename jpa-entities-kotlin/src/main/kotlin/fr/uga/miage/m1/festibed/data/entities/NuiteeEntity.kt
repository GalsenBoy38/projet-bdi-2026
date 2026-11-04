package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.math.BigDecimal
import java.time.LocalDate
import java.util.UUID

/**
 * Nuit pendant laquelle un hébergement est proposé à FestiBed. Une seule ligne par (hébergement, date) :
 * impossible de vendre deux fois la même nuit. L'occupation se fait UNIQUEMENT par l'UPDATE conditionnel
 * NuiteeRepository.occuper (… where selection is null), jamais par un save() après lecture.
 */
@Entity
@Table(
    name = "nuitee",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_nuitee_hebergement_date", columnNames = ["hebergement_id", "date_nuitee"]),
    ],
    indexes = [
        Index(name = "idx_nuitee_date_selection", columnList = "date_nuitee, selection_id"),
    ],
)
data class NuiteeEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @ManyToOne(optional = false)
    @JoinColumn(name = "hebergement_id", nullable = false)
    var hebergement: HebergementEntity,

    @Column(name = "date_nuitee", nullable = false)
    var dateNuitee: LocalDate,

    @Column(nullable = false, precision = 8, scale = 2)
    var prix: BigDecimal,

    /** null : nuit libre ; sinon nuit réservée par cette sélection. */
    @ManyToOne
    @JoinColumn(name = "selection_id")
    var selection: SelectionEntity? = null,
) {

    val libre: Boolean get() = selection == null
}
