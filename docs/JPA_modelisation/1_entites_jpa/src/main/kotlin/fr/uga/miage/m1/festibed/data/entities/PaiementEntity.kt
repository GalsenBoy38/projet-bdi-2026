package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.StatutPaiement
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.OneToOne
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.UUID

/**
 * Prévu dans le modèle, non développé dans le prototype (statut NON_GERE).
 * Clé technique : numTransaction est fourni par le prestataire de paiement et peut être absent.
 */
@Entity
@Table(
    name = "PAIEMENT",
    uniqueConstraints = [
        UniqueConstraint(name = "UK_PAIEMENT_1", columnNames = ["numTransaction"]),
        UniqueConstraint(name = "UK_PAIEMENT_2", columnNames = ["reservation_id"]),
    ],
)
data class PaiementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @OneToOne(optional = false)
    @JoinColumn(name = "reservation_id", nullable = false)
    var reservation: ReservationEntity,

    @Column(length = 30)
    var numTransaction: String? = null,

    @Column(nullable = false, precision = 10, scale = 2)
    var montantPaiement: BigDecimal,

    @Column
    var datePaiement: LocalDateTime? = null,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(nullable = false, length = 20)
    var statutPaiement: StatutPaiement = StatutPaiement.NON_GERE,
) {
    override fun equals(other: Any?) = this === other || (other is PaiementEntity && id != null && id == other.id)
    override fun hashCode() = PaiementEntity::class.hashCode()
    override fun toString() = "PaiementEntity(id=$id, statutPaiement=$statutPaiement)"
}
