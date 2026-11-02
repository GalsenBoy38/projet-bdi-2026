package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import java.io.Serializable

@Embeddable
data class NotationEtablissementId(
    @Column(name = "idEtablissement", nullable = false)
    val idEtablissement: Long? = null,

    @Column(name = "idUtilisateur", nullable = false)
    val idUtilisateur: Long? = null,
) : Serializable
