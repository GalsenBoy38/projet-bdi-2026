package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.SelectionEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface SelectionRepository : JpaRepository<SelectionEntity, UUID> {
    fun findAllByFestivalId(festivalId: UUID): Collection<SelectionEntity>
}
