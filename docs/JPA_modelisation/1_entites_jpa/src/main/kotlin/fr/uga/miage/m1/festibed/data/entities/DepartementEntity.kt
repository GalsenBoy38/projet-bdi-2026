package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table

@Entity
@Table(
    name = "DEPARTEMENT",
    indexes = [Index(name = "IX_DEPARTEMENT_1", columnList = "region_id")],
)
data class DepartementEntity(
    /** Clé naturelle : "01", "2A", "974"... */
    @Id
    @Column(nullable = false, length = 3)
    val codeDepartement: String,

    @Column(nullable = false, length = 50)
    var nomDepartement: String,

    @ManyToOne(optional = false)
    @JoinColumn(name = "region_id", nullable = false)
    var region: RegionEntity,
) {
    override fun equals(other: Any?) = this === other || (other is DepartementEntity && codeDepartement == other.codeDepartement)
    override fun hashCode() = codeDepartement.hashCode()
    override fun toString() = "DepartementEntity(codeDepartement=$codeDepartement, nomDepartement=$nomDepartement)"
}
