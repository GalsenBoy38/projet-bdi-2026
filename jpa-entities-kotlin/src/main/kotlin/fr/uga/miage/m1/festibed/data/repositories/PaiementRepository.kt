package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.PaiementEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface PaiementRepository : JpaRepository<PaiementEntity, UUID> {
    fun findByReservationId(reservationId: UUID): PaiementEntity?
}
