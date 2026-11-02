package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.HebergeurEntity
import org.springframework.data.jpa.repository.JpaRepository

interface HebergeurRepository : JpaRepository<HebergeurEntity, Long> {
    fun findByEmail(email: String): HebergeurEntity?
}
