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
import java.time.LocalDate
import java.util.UUID

/** Une seule note par couple établissement / festivalier. */
@Entity
@Table(
    name = "notation_etablissement",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_notation_etablissement_etablissement_festivalier", columnNames = ["etablissement_id", "festivalier_id"]),
    ],
)
data class NotationEtablissementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @ManyToOne(optional = false)
    @JoinColumn(name = "etablissement_id", nullable = false)
    var etablissement: EtablissementEntity,

    @ManyToOne(optional = false)
    @JoinColumn(name = "festivalier_id", nullable = false)
    var festivalier: FestivalierEntity,

    /** 1 à 5. */
    @Column(nullable = false)
    var note: Int,

    @Column(name = "date_note", nullable = false)
    var dateNote: LocalDate,
)
