package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.CascadeType
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import java.time.LocalDateTime


@Entity
@Table(
    name = "RESERVATION",
    indexes = [Index(name = "IX_RESERVATION_1", columnList = "festivalier_id")],
)
data class ReservationEntity(
    @Id
    @Column(nullable = false, length = 20)
    val numeroReservation: String,

    @Column(nullable = false)
    var dateReservation: LocalDateTime,

    @ManyToOne(optional = false)
    @JoinColumn(name = "festivalier_id", nullable = false)
    var festivalier: FestivalierEntity,

    /** Composition : les sélections naissent et meurent avec la réservation. */
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "reservation_id", nullable = false)
    var selections: MutableCollection<SelectionEntity> = mutableListOf(),
) {
    override fun equals(other: Any?) = this === other || (other is ReservationEntity && numeroReservation == other.numeroReservation)
    override fun hashCode() = numeroReservation.hashCode()
    override fun toString() = "ReservationEntity(numeroReservation=$numeroReservation, dateReservation=$dateReservation)"
}
