package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.PrimaryKeyJoinColumn
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.util.UUID

@Entity
@Table(
    name = "FESTIVALIER",
    uniqueConstraints = [
        UniqueConstraint(name = "UK_FESTIVALIER_1", columnNames = ["fournisseurAuth", "identifiantExterneFestivalier"]),
    ],
)
@PrimaryKeyJoinColumn(name = "idUtilisateur")
class FestivalierEntity(
    id: UUID? = null,
    nom: String,
    email: String,

    /** GOOGLE, FACEBOOK... ; NULL pour une validation anonyme ou un compte de test du peuplement. */
    @Column(name = "fournisseurAuth", length = 30)
    var fournisseurAuth: String? = null,

    @Column(name = "identifiantExterneFestivalier", length = 100)
    var identifiantExterneFestivalier: String? = null,
) : UtilisateurEntity(id, nom, email)
