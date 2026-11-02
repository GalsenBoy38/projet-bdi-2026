package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.SequenceGenerator
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint

@Entity
@Table(
    name = "REGION",
    uniqueConstraints = [UniqueConstraint(name = "UK_REGION_1", columnNames = ["nomRegion"])],
)
data class RegionEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seqRegion")
    @SequenceGenerator(name = "seqRegion", sequenceName = "SEQ_REGION", allocationSize = 50)
    @Column(name = "idRegion", nullable = false)
    val id: Long? = null,

    @Column(name = "nomRegion", nullable = false, length = 30)
    var nomRegion: String,
)
