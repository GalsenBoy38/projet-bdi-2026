package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.EmbeddedId
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.JoinColumns
import jakarta.persistence.ManyToOne
import jakarta.persistence.MapsId
import jakarta.persistence.Table
import java.math.BigDecimal

/**
 * Nuit pendant laquelle un hébergement est proposé à FestiBed.
 * selection == null : nuit libre ; sinon nuit réservée par cette sélection.
 * L'occupation se fait UNIQUEMENT par l'UPDATE conditionnel NuiteeRepository.occuper
 * (… WHERE idSelection IS NULL), jamais par un save() après lecture.
 */
@Entity
@Table(
    name = "NUITEE",
    indexes = [
        Index(name = "IX_NUITEE_1", columnList = "dateNuitee, idSelection"),
        Index(name = "IX_NUITEE_2", columnList = "idSelection"),
    ],
)
data class NuiteeEntity(
    @EmbeddedId
    val id: NuiteeId,

    @MapsId("hebergementId")
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumns(
        JoinColumn(name = "idEtablissement", referencedColumnName = "idEtablissement"),
        JoinColumn(name = "numeroHebergement", referencedColumnName = "numeroHebergement"),
    )
    var hebergement: HebergementEntity,

    @Column(name = "prixNuitee", nullable = false, precision = 8, scale = 2)
    var prixNuitee: BigDecimal,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "idSelection")
    var selection: SelectionEntity? = null,
) {
    val libre: Boolean get() = selection == null

    override fun equals(other: Any?) = this === other || (other is NuiteeEntity && id == other.id)
    override fun hashCode() = id.hashCode()
    override fun toString() = "NuiteeEntity(id=$id, prixNuitee=$prixNuitee)"
}
