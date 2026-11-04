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
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.UUID

/** Prévu dans le modèle, non développé dans le prototype (statut NON_GERE). */
@Entity
@Table(
    name = "paiement",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_paiement_num_transaction", columnNames = ["num_transaction"]),
    ],
)
data class PaiementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @OneToOne(optional = false)
    @JoinColumn(name = "reservation_id", nullable = false, unique = true)
    var reservation: ReservationEntity,

    /** Fourni par le prestataire de paiement : null tant que le paiement n'est pas développé. */
    @Column(name = "num_transaction", length = 30)
    var numTransaction: String? = null,

    @Column(nullable = false, precision = 10, scale = 2)
    var montant: BigDecimal,

    @Column(name = "date_paiement")
    var datePaiement: LocalDateTime? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    var statut: StatutPaiement = StatutPaiement.NON_GERE,
)
