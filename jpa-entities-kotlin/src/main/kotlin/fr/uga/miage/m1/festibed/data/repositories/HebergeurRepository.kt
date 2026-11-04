package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.HebergeurEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface HebergeurRepository : JpaRepository<HebergeurEntity, UUID> {
    fun findByEmail(email: String): HebergeurEntity?
}
