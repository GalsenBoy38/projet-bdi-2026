package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.util.UUID

/** Équipement (Wi-Fi, parking...), associé aux hébergements par la table « equipement » (@ManyToMany). */
@Entity
@Table(
    name = "option_hebergement",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_option_hebergement_libelle", columnNames = ["libelle"]),
    ],
)
data class OptionHebergementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(nullable = false, length = 50)
    var libelle: String,
)
