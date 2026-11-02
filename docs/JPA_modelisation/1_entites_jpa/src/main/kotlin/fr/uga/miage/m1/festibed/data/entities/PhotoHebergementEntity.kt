package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.SequenceGenerator
import jakarta.persistence.Table

/** Photo d'un hébergement. La clé étrangère est gérée par HebergementEntity.photos (relation unidirectionnelle). */
@Entity
@Table(
    name = "PHOTO_HEBERGEMENT",
    indexes = [Index(name = "IX_PHOTO_HEBERGEMENT_1", columnList = "idEtablissement, numeroHebergement")],
)
data class PhotoHebergementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seqPhotoHebergement")
    @SequenceGenerator(name = "seqPhotoHebergement", sequenceName = "SEQ_PHOTO_HEBERGEMENT", allocationSize = 50)
    @Column(name = "idPhotoHebergement", nullable = false)
    val id: Long? = null,

    @Column(name = "urlPhotoHebergement", nullable = false, length = 300)
    var urlPhotoHebergement: String,
)
