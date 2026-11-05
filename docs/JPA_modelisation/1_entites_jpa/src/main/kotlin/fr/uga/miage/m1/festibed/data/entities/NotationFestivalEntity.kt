package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.EmbeddedId
import jakarta.persistence.Entity
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.MapsId
import jakarta.persistence.Table
import java.time.LocalDate

/** Note d'un festivalier (une seule par couple festival / festivalier). */
@Entity
@Table(
    name = "NOTATION_FESTIVAL",
    indexes = [Index(name = "IX_NOTATION_FESTIVAL_1", columnList = "festivalier_id")],
)
data class NotationFestivalEntity(
    @EmbeddedId
    val id: NotationFestivalId = NotationFestivalId(),

    @MapsId("idFestival")
    @ManyToOne(optional = false)
    @JoinColumn(name = "festival_id", nullable = false)
    var festival: FestivalEntity,

    @MapsId("idUtilisateur")
    @ManyToOne(optional = false)
    @JoinColumn(name = "festivalier_id", nullable = false)
    var festivalier: FestivalierEntity,

    /** 1 à 5. */
    @Column(nullable = false)
    var noteFestival: Int,

    @Column(nullable = false)
    var dateNoteFestival: LocalDate,
) {
    override fun equals(other: Any?) = this === other || (other is NotationFestivalEntity && id == other.id)
    override fun hashCode() = id.hashCode()
    override fun toString() = "NotationFestivalEntity(id=$id, noteFestival=$noteFestival)"
}
