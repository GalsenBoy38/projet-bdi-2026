package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.TypeHebergement
import jakarta.persistence.CascadeType
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.JoinTable
import jakarta.persistence.ManyToMany
import jakarta.persistence.ManyToOne
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import java.math.BigDecimal
import java.util.UUID

/**
 * Offre réservable d'un établissement, proposée indépendamment de tout festival.
 * Pas de liste « nuitees » (des centaines par hébergement) : passer par NuiteeRepository.
 */
@Entity
@Table(
    name = "hebergement",
    uniqueConstraints = [
        UniqueConstraint(name = "uk_hebergement_etablissement_numero", columnNames = ["etablissement_id", "numero"]),
    ],
)
data class HebergementEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(nullable = false)
    val id: UUID? = null,

    @ManyToOne(optional = false)
    @JoinColumn(name = "etablissement_id", nullable = false)
    var etablissement: EtablissementEntity,

    /** Numéro propre à l'établissement : H001, H002... */
    @Column(nullable = false, length = 10)
    var numero: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "type_hebergement", nullable = false, length = 30)
    var typeHebergement: TypeHebergement,

    /** Nombre de personnes : la somme des capacités d'une sélection doit couvrir ses Pass. */
    @Column(nullable = false)
    var capacite: Int,

    @Column(name = "prix_nuit", nullable = false, precision = 8, scale = 2)
    var prixNuit: BigDecimal,

    @Column(length = 500)
    var description: String? = null,

    @Column(nullable = false)
    var actif: Boolean = true,

    /** Composition : les photos naissent et meurent avec l'hébergement. */
    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumn(name = "hebergement_id", nullable = false)
    var photos: MutableCollection<PhotoHebergementEntity> = mutableListOf(),

    /** Table d'association « equipement » (n,n sans attribut). */
    @ManyToMany
    @JoinTable(
        name = "equipement",
        joinColumns = [JoinColumn(name = "hebergement_id")],
        inverseJoinColumns = [JoinColumn(name = "option_hebergement_id")],
    )
    var options: MutableSet<OptionHebergementEntity> = mutableSetOf(),
)
