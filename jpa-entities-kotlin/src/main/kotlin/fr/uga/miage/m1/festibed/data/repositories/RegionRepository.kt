package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.RegionEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface RegionRepository : JpaRepository<RegionEntity, UUID> {
    fun findByNom(nom: String): RegionEntity?
}
