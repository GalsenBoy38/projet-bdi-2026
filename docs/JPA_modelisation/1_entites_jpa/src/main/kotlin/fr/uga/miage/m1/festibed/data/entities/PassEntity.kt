package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Index
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.util.UUID

/**
 * Droit d'accès individuel à un festival. La colonne idSelection est gérée par SelectionEntity.passes ;
 * le festival se retrouve par la sélection (dépendance transitive supprimée, 3e forme normale).
 */
@Entity
@Table(
    name = "PASS",
    uniqueConstraints = [UniqueConstraint(name = "UK_PASS_1", columnNames = ["codePass"])],
    indexes = [Index(name = "IX_PASS_1", columnList = "idSelection")],
)
data class PassEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "idPass", nullable = false)
    val id: UUID? = null,

    @Column(name = "codePass", nullable = false, length = 40)
    var codePass: String,
)
