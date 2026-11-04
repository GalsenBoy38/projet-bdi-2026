package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import java.io.Serializable
import java.util.UUID

@Embeddable
data class NotationFestivalId(
    @Column(name = "idFestival", nullable = false)
    val idFestival: UUID? = null,

    @Column(name = "idUtilisateur", nullable = false)
    val idUtilisateur: UUID? = null,
) : Serializable
