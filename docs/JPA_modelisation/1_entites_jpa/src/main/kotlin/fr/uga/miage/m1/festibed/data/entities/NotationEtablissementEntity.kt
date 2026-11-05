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

/** Note d'un festivalier (une seule par couple etablissement / festivalier). */
@Entity
@Table(
    name = "NOTATION_ETABLISSEMENT",
    indexes = [Index(name = "IX_NOTATION_ETABLISSEMENT_1", columnList = "festivalier_id")],
)
data class NotationEtablissementEntity(
    @EmbeddedId
    val id: NotationEtablissementId = NotationEtablissementId(),

    @MapsId("idEtablissement")
    @ManyToOne(optional = false)
    @JoinColumn(name = "etablissement_id", nullable = false)
    var etablissement: EtablissementEntity,

    @MapsId("idUtilisateur")
    @ManyToOne(optional = false)
    @JoinColumn(name = "festivalier_id", nullable = false)
    var festivalier: FestivalierEntity,

    /** 1 à 5. */
    @Column(nullable = false)
    var noteEtablissement: Int,

    @Column(nullable = false)
    var dateNoteEtablissement: LocalDate,
) {
    override fun equals(other: Any?) = this === other || (other is NotationEtablissementEntity && id == other.id)
    override fun hashCode() = id.hashCode()
    override fun toString() = "NotationEtablissementEntity(id=$id, noteEtablissement=$noteEtablissement)"
}
