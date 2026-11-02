package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.FestivalierEntity
import org.springframework.data.jpa.repository.JpaRepository

interface FestivalierRepository : JpaRepository<FestivalierEntity, Long> {
    fun findByEmail(email: String): FestivalierEntity?
}
