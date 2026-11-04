package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.util.UUID

/** Photo d'un hébergement ; la clé étrangère hebergement_id est gérée par HebergementEntity.photos. */
@Entity
@Table(name = "photo_hebergement")
data class PhotoHebergementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(nullable = false, length = 300)
    var url: String,
)
