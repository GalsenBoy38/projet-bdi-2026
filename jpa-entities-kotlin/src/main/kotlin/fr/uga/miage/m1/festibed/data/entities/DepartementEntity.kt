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
import java.util.UUID

@Entity
@Table(
    name = "departement",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_departement_code", columnNames = ["code"]),
    ],
)
data class DepartementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    /** "01", "2A", "974"... */
    @Column(nullable = false, length = 3)
    var code: String,

    @Column(nullable = false, length = 50)
    var nom: String,

    @ManyToOne(optional = false)
    @JoinColumn(name = "region_id", nullable = false)
    var region: RegionEntity,
)
