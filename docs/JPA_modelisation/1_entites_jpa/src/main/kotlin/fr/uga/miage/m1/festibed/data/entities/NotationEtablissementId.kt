package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import java.io.Serializable
import java.util.UUID

@Embeddable
data class NotationEtablissementId(
    @Column(name = "etablissement_id", nullable = false)
    val idEtablissement: UUID? = null,

    @Column(name = "festivalier_id", nullable = false)
    val idUtilisateur: UUID? = null,
) : Serializable
