package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.NotationEtablissementEntity
import fr.uga.miage.m1.festibed.data.entities.NotationEtablissementId
import org.springframework.data.jpa.repository.JpaRepository

interface NotationEtablissementRepository : JpaRepository<NotationEtablissementEntity, NotationEtablissementId> {
    fun existsByEtablissementIdAndFestivalierId(etablissementId: Long, festivalierId: Long): Boolean
}
