package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.CommuneEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface CommuneRepository : JpaRepository<CommuneEntity, UUID> {
    fun findByCodeInsee(codeInsee: String): CommuneEntity?
    fun findAllByDepartementCode(code: String): Collection<CommuneEntity>
}
