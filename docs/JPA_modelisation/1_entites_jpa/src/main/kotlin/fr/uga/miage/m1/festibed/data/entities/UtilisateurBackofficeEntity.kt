package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.PrimaryKeyJoinColumn
import jakarta.persistence.Table
import java.util.UUID

@Entity
@Table(name = "UTILISATEUR_BACKOFFICE")
@PrimaryKeyJoinColumn(name = "idUtilisateur")
abstract class UtilisateurBackofficeEntity(
    id: UUID? = null,
    nom: String,
    email: String,

    /** Hash BCrypt (Spring Security), jamais le mot de passe en clair. */
    @Column(name = "motDePasseHache", nullable = false, length = 100)
    var motDePasseHache: String,
) : UtilisateurEntity(id, nom, email)
