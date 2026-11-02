package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import java.io.Serializable

/** Clé de HEBERGEMENT : composition avec l'établissement (H001, H002... propres à chaque établissement). */
@Embeddable
data class HebergementId(
    @Column(name = "idEtablissement", nullable = false)
    val idEtablissement: Long? = null,

    @Column(name = "numeroHebergement", nullable = false, length = 10)
    val numeroHebergement: String? = null,
) : Serializable
