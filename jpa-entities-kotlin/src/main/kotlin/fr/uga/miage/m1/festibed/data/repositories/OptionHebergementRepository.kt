package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.OptionHebergementEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface OptionHebergementRepository : JpaRepository<OptionHebergementEntity, UUID> {
    fun findByLibelle(libelle: String): OptionHebergementEntity?
}
