package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.util.UUID

/** Droit d'accès individuel à un festival (le festival se retrouve par la sélection). */
@Entity
@Table(
    name = "pass",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_pass_code", columnNames = ["code"]),
    ],
)
data class PassEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @Column(nullable = false, length = 40)
    var code: String,
)
