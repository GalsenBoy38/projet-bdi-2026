package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.ReservationEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface ReservationRepository : JpaRepository<ReservationEntity, UUID> {
    fun findByNumero(numero: String): ReservationEntity?
    fun findAllByFestivalierId(festivalierId: UUID): Collection<ReservationEntity>

    /** Validation anonyme : accès par email + numéro de réservation. */
    fun findByNumeroAndFestivalierEmail(numero: String, email: String): ReservationEntity?
}
