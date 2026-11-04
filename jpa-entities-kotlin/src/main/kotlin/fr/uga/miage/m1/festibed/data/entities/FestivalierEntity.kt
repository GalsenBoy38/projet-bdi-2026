package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.util.UUID

@Entity
@Table(
    name = "festivalier",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_festivalier_compte_externe", columnNames = ["fournisseur_auth", "identifiant_externe"]),
    ],
)
class FestivalierEntity(
    id: UUID? = null,
    nom: String,
    email: String,

    /** GOOGLE, FACEBOOK... ; null pour une validation anonyme (email seul). */
    @Column(name = "fournisseur_auth", length = 30)
    var fournisseurAuth: String? = null,

    @Column(name = "identifiant_externe", length = 100)
    var identifiantExterne: String? = null,
) : UtilisateurEntity(id, nom, email)
