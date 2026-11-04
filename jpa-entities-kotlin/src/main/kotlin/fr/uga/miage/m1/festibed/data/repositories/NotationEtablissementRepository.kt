package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.NotationEtablissementEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface NotationEtablissementRepository : JpaRepository<NotationEtablissementEntity, UUID> {
    fun findAllByEtablissementId(etablissementId: UUID): Collection<NotationEtablissementEntity>
    fun existsByEtablissementIdAndFestivalierId(etablissementId: UUID, festivalierId: UUID): Boolean
}
