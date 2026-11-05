package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.Table
import java.util.UUID

/** Photo d'un hébergement. La clé étrangère est gérée par HebergementEntity.photos (relation unidirectionnelle). */
@Entity
@Table(
    name = "PHOTO_HEBERGEMENT",
    indexes = [Index(name = "IX_PHOTO_HEBERGEMENT_1", columnList = "etablissement_id, numeroHebergement")],
)
data class PhotoHebergementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(nullable = false, length = 300)
    var urlPhotoHebergement: String,
)
