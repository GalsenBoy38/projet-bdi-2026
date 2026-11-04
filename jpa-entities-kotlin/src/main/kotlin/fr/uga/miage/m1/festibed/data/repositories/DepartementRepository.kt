package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.DepartementEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface DepartementRepository : JpaRepository<DepartementEntity, UUID> {
    fun findByCode(code: String): DepartementEntity?
}
