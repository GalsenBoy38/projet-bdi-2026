package fr.uga.miage.m1.festibed.data.repositories

import fr.uga.miage.m1.festibed.data.entities.OrganisateurEntity
import org.springframework.data.jpa.repository.JpaRepository

interface OrganisateurRepository : JpaRepository<OrganisateurEntity, Long> {
    fun findByEmail(email: String): OrganisateurEntity?
}
