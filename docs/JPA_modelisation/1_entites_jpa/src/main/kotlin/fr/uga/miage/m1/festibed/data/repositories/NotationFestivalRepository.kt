package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.NotationFestivalEntity
import fr.uga.miage.m1.festibed.data.entities.NotationFestivalId
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface NotationFestivalRepository : JpaRepository<NotationFestivalEntity, NotationFestivalId> {
    fun existsByFestivalIdAndFestivalierId(festivalId: UUID, festivalierId: UUID): Boolean
}
