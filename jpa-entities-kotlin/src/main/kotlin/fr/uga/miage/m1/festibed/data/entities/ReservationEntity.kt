package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.CascadeType
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.time.LocalDateTime
import java.util.UUID

/**
 * Réservation validée (le panier reste côté client 15 min, cf. stratégie de concurrence).
 * Le paiement n'est pas référencé ici : PaiementEntity porte la relation (PaiementRepository).
 */
@Entity
@Table(
    name = "reservation",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_reservation_numero", columnNames = ["numero"]),
    ],
)
data class ReservationEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    /** Code opaque "FB" + 10 caractères : sert aussi à la consultation anonyme (email + numéro). */
    @Column(nullable = false, length = 20)
    var numero: String,

    @Column(name = "date_reservation", nullable = false)
    var dateReservation: LocalDateTime,

    @ManyToOne(optional = false)
    @JoinColumn(name = "festivalier_id", nullable = false)
    var festivalier: FestivalierEntity,

    /** Composition : les sélections naissent et meurent avec la réservation. */
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "reservation_id", nullable = false)
    var selections: MutableCollection<SelectionEntity> = mutableListOf(),
)
