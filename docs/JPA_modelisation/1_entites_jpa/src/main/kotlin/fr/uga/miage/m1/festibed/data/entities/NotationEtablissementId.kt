package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import java.io.Serializable
import java.util.UUID

@Embeddable
data class NotationEtablissementId(
    @Column(name = "idEtablissement", nullable = false)
    val idEtablissement: UUID? = null,

    @Column(name = "idUtilisateur", nullable = false)
    val idUtilisateur: UUID? = null,
) : Serializable
