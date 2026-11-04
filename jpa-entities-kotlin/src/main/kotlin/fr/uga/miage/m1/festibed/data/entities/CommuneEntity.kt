package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.math.BigDecimal
import java.util.UUID

@Entity
@Table(
    name = "commune",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_commune_code_insee", columnNames = ["code_insee"]),
    ],
)
data class CommuneEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    /** Code INSEE sur 5 caractères ("01024", "2A004"). */
    @Column(name = "code_insee", nullable = false, length = 5)
    var codeInsee: String,

    @Column(nullable = false, length = 60)
    var nom: String,

    @Column(precision = 12, scale = 9)
    var latitude: BigDecimal? = null,

    @Column(precision = 12, scale = 9)
    var longitude: BigDecimal? = null,

    @ManyToOne(optional = false)
    @JoinColumn(name = "departement_id", nullable = false)
    var departement: DepartementEntity,
)
