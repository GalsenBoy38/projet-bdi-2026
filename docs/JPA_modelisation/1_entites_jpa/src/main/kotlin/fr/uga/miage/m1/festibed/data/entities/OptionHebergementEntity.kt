package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.util.UUID

/** Équipement proposé (wifi, parking...). Associé aux hébergements par la table EQUIPEMENT. */
@Entity
@Table(
    name = "OPTION_HEBERGEMENT",
    uniqueConstraints = [UniqueConstraint(name = "UK_OPTION_HEBERGEMENT_1", columnNames = ["libelleOptionHebergement"])],
)
data class OptionHebergementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "idOptionHebergement", nullable = false)
    val id: UUID? = null,

    @Column(name = "libelleOptionHebergement", nullable = false, length = 50)
    var libelleOptionHebergement: String,
)
