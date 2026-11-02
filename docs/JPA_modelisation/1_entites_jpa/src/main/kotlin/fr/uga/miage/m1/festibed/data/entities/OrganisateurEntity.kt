package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Entity
import jakarta.persistence.PrimaryKeyJoinColumn
import jakarta.persistence.Table

@Entity
@Table(name = "ORGANISATEUR")
@PrimaryKeyJoinColumn(name = "idUtilisateur")
class OrganisateurEntity(
    id: Long? = null,
    nom: String,
    email: String,
    motDePasseHache: String,
) : UtilisateurBackofficeEntity(id, nom, email, motDePasseHache)
