package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Embeddable
import java.io.Serializable
import java.time.LocalDate

/** Clé de NUITEE : (hébergement, date). Une seule ligne par nuit : impossible de vendre deux fois la même nuit. */
@Embeddable
data class NuiteeId(
    val hebergementId: HebergementId? = null,

    @Column(name = "dateNuitee", nullable = false)
    val dateNuitee: LocalDate? = null,
) : Serializable
