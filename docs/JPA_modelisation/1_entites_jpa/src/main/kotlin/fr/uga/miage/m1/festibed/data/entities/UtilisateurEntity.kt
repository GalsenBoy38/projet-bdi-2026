package fr.uga.miage.m1.festibed.data.entities

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Inheritance
import jakarta.persistence.InheritanceType
import jakarta.persistence.SequenceGenerator
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint

/**
 * Héritage JOINED : UTILISATEUR (commun) + une table par sous-type, même clé idUtilisateur.
 *   UtilisateurEntity
 *    ├── FestivalierEntity                 (FrontOffice, réseau social ou validation anonyme)
 *    └── UtilisateurBackofficeEntity       (compte interne, mot de passe haché)
 *         ├── OrganisateurEntity
 *         └── HebergeurEntity
 * Classe abstraite (pas data class) : Kotlin interdit d'hériter d'une data class.
 */
@Entity
@Table(
    name = "UTILISATEUR",
    uniqueConstraints = [UniqueConstraint(name = "UK_UTILISATEUR_1", columnNames = ["email"])],
)
@Inheritance(strategy = InheritanceType.JOINED)
abstract class UtilisateurEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seqUtilisateur")
    @SequenceGenerator(name = "seqUtilisateur", sequenceName = "SEQ_UTILISATEUR", allocationSize = 50)
    @Column(name = "idUtilisateur", nullable = false)
    val id: Long? = null,

    @Column(name = "nom", nullable = false, length = 100)
    var nom: String,

    @Column(name = "email", nullable = false, length = 150)
    var email: String,
) {
    override fun equals(other: Any?) = this === other || (other is UtilisateurEntity && id != null && id == other.id)
    override fun hashCode() = UtilisateurEntity::class.hashCode()
    override fun toString() = "${this::class.simpleName}(id=$id, email=$email)"
}
