package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.PaiementEntity
import org.springframework.data.jpa.repository.JpaRepository

interface PaiementRepository : JpaRepository<PaiementEntity, Long> {
    fun findByReservationNumeroReservation(numeroReservation: String): PaiementEntity?
}
