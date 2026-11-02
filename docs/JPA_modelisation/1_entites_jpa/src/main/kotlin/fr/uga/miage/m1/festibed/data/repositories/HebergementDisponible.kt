package fr.uga.miage.m1.festibed.data.repositories

import java.math.BigDecimal

/** Ligne de résultat de la recherche d'hébergements (projection : pas de chargement des 6 sous-types). */
data class HebergementDisponible(
    val idEtablissement: Long,
    val numeroHebergement: String,
    val nomCommercial: String,
    val nomCommune: String,
    val typeHebergement: String,
    val capacite: Int,
    val prixNuit: BigDecimal,
    val noteMoyenne: BigDecimal?,
    val latitude: BigDecimal?,
    val longitude: BigDecimal?,
)
