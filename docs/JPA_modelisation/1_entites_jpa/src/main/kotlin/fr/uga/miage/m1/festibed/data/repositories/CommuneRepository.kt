package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.CommuneEntity
import org.springframework.data.jpa.repository.JpaRepository

interface CommuneRepository : JpaRepository<CommuneEntity, String> {
    fun findAllByDepartementCodeDepartement(codeDepartement: String): Collection<CommuneEntity>
}
