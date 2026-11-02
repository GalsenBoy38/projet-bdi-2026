package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table

@Entity
@Table(
    name = "DEPARTEMENT",
    indexes = [Index(name = "IX_DEPARTEMENT_1", columnList = "idRegion")],
)
data class DepartementEntity(
    /** Clé naturelle : "01", "2A", "974"... */
    @Id
    @Column(name = "codeDepartement", nullable = false, length = 3)
    val codeDepartement: String,

    @Column(name = "nomDepartement", nullable = false, length = 50)
    var nomDepartement: String,

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "idRegion", nullable = false)
    var region: RegionEntity,
) {
    override fun equals(other: Any?) = this === other || (other is DepartementEntity && codeDepartement == other.codeDepartement)
    override fun hashCode() = codeDepartement.hashCode()
    override fun toString() = "DepartementEntity(codeDepartement=$codeDepartement, nomDepartement=$nomDepartement)"
}
