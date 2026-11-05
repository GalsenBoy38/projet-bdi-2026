package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import java.math.BigDecimal

@Entity
@Table(
    name = "COMMUNE",
    indexes = [Index(name = "IX_COMMUNE_1", columnList = "departement_id")],
)
data class CommuneEntity(
    /** Code INSEE sur 5 caractères (zéros initiaux conservés : "01024"). */
    @Id
    @Column(nullable = false, length = 5)
    val codeInsee: String,

    @Column(nullable = false, length = 40)
    var nomCommune: String,

    @Column(precision = 12, scale = 9)
    var latitude: BigDecimal? = null,

    @Column(precision = 12, scale = 9)
    var longitude: BigDecimal? = null,

    @ManyToOne(optional = false)
    @JoinColumn(name = "departement_id", nullable = false)
    var departement: DepartementEntity,
) {
    override fun equals(other: Any?) = this === other || (other is CommuneEntity && codeInsee == other.codeInsee)
    override fun hashCode() = codeInsee.hashCode()
    override fun toString() = "CommuneEntity(codeInsee=$codeInsee, nomCommune=$nomCommune)"
}
