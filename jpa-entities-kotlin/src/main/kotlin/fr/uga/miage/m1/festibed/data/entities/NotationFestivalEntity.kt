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

/** Une seule note par couple festival / festivalier. */
@Entity
@Table(
    name = "notation_festival",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_notation_festival_festival_festivalier", columnNames = ["festival_id", "festivalier_id"]),
    ],
)
data class NotationFestivalEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @ManyToOne(optional = false)
    @JoinColumn(name = "festival_id", nullable = false)
    var festival: FestivalEntity,

    @ManyToOne(optional = false)
    @JoinColumn(name = "festivalier_id", nullable = false)
    var festivalier: FestivalierEntity,

    /** 1 à 5. */
    @Column(nullable = false)
    var note: Int,

    @Column(name = "date_note", nullable = false)
    var dateNote: LocalDate,
)
