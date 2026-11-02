package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.ReservationEntity
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface ReservationRepository : JpaRepository<ReservationEntity, String> {
    fun findAllByFestivalierId(festivalierId: Long): Collection<ReservationEntity>

    /** Validation anonyme : accès par email + numéro de réservation. */
    @Query(
        """select r from ReservationEntity r join fetch r.festivalier f
           where r.numeroReservation = :numero and f.email = :email""",
    )
    fun trouverAnonyme(@Param("numero") numero: String, @Param("email") email: String): ReservationEntity?
}
