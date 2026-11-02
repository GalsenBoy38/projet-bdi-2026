package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.EmbeddedId
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
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
    indexes = [Index(name = "IX_NOTATION_FESTIVAL_1", columnList = "idUtilisateur")],
)
data class NotationFestivalEntity(
    @EmbeddedId
    val id: NotationFestivalId = NotationFestivalId(),

    @MapsId("idFestival")
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "idFestival", nullable = false)
    var festival: FestivalEntity,

    @MapsId("idUtilisateur")
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "idUtilisateur", nullable = false)
    var festivalier: FestivalierEntity,

    /** 1 à 5. */
    @Column(name = "noteFestival", nullable = false)
    var noteFestival: Int,

    @Column(name = "dateNoteFestival", nullable = false)
    var dateNoteFestival: LocalDate,
) {
    override fun equals(other: Any?) = this === other || (other is NotationFestivalEntity && id == other.id)
    override fun hashCode() = id.hashCode()
    override fun toString() = "NotationFestivalEntity(id=$id, noteFestival=$noteFestival)"
}
