package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.PassEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface PassRepository : JpaRepository<PassEntity, UUID> {
    fun findByCode(code: String): PassEntity?
}
