package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Entity
import jakarta.persistence.Table
import java.util.UUID

@Entity
@Table(name = "organisateur")
class OrganisateurEntity(
    id: UUID? = null,
    nom: String,
    email: String,
    motDePasseHache: String,
) : UtilisateurBackofficeEntity(id, nom, email, motDePasseHache)
