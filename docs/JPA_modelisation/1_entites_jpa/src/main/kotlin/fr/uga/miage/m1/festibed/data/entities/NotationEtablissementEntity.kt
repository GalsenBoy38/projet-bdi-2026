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

/** Note d'un festivalier (une seule par couple etablissement / festivalier). */
@Entity
@Table(
    name = "NOTATION_ETABLISSEMENT",
    indexes = [Index(name = "IX_NOTATION_ETABLISSEMENT_1", columnList = "idUtilisateur")],
)
data class NotationEtablissementEntity(
    @EmbeddedId
    val id: NotationEtablissementId = NotationEtablissementId(),

    @MapsId("idEtablissement")
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "idEtablissement", nullable = false)
    var etablissement: EtablissementEntity,

    @MapsId("idUtilisateur")
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "idUtilisateur", nullable = false)
    var festivalier: FestivalierEntity,

    /** 1 à 5. */
    @Column(name = "noteEtablissement", nullable = false)
    var noteEtablissement: Int,

    @Column(name = "dateNoteEtablissement", nullable = false)
    var dateNoteEtablissement: LocalDate,
) {
    override fun equals(other: Any?) = this === other || (other is NotationEtablissementEntity && id == other.id)
    override fun hashCode() = id.hashCode()
    override fun toString() = "NotationEtablissementEntity(id=$id, noteEtablissement=$noteEtablissement)"
}
