package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Entity
import jakarta.persistence.Table
import java.util.UUID

@Entity
@Table(name = "hebergeur")
class HebergeurEntity(
    id: UUID? = null,
    nom: String,
    email: String,
    motDePasseHache: String,
) : UtilisateurBackofficeEntity(id, nom, email, motDePasseHache)
