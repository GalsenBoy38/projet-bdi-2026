package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.SelectionEntity
import org.springframework.data.jpa.repository.JpaRepository

interface SelectionRepository : JpaRepository<SelectionEntity, Long> {
    fun findAllByFestivalId(festivalId: Long): Collection<SelectionEntity>
}
