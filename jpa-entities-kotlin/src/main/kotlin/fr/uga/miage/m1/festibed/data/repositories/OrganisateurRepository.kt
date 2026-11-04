package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.OrganisateurEntity
import org.springframework.data.jpa.repository.JpaRepository
import java.util.UUID

interface OrganisateurRepository : JpaRepository<OrganisateurEntity, UUID> {
    fun findByEmail(email: String): OrganisateurEntity?
}
