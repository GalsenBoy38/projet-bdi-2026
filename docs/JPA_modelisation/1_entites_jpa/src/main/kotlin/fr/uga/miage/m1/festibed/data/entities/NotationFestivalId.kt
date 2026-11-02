package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import java.io.Serializable

@Embeddable
data class NotationFestivalId(
    @Column(name = "idFestival", nullable = false)
    val idFestival: Long? = null,

    @Column(name = "idUtilisateur", nullable = false)
    val idUtilisateur: Long? = null,
) : Serializable
