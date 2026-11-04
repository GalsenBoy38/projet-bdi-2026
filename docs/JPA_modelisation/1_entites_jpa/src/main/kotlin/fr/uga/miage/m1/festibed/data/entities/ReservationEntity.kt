package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.CascadeType
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
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
    indexes = [Index(name = "IX_RESERVATION_1", columnList = "idUtilisateur")],
)
data class ReservationEntity(
    @Id
    @Column(name = "numeroReservation", nullable = false, length = 20)
    val numeroReservation: String,

    @Column(name = "dateReservation", nullable = false)
    var dateReservation: LocalDateTime,

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "idUtilisateur", nullable = false)
    var festivalier: FestivalierEntity,

    /** Composition : les sélections naissent et meurent avec la réservation. */
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "numeroReservation", nullable = false)
    var selections: MutableCollection<SelectionEntity> = mutableListOf(),
) {
    override fun equals(other: Any?) = this === other || (other is ReservationEntity && numeroReservation == other.numeroReservation)
    override fun hashCode() = numeroReservation.hashCode()
    override fun toString() = "ReservationEntity(numeroReservation=$numeroReservation, dateReservation=$dateReservation)"
}
