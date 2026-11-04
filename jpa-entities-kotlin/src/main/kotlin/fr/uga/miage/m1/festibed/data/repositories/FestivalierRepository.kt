package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.FestivalierEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface FestivalierRepository : JpaRepository<FestivalierEntity, UUID> {
    fun findByEmail(email: String): FestivalierEntity?
    fun findByFournisseurAuthAndIdentifiantExterne(fournisseurAuth: String, identifiantExterne: String): FestivalierEntity?
}
