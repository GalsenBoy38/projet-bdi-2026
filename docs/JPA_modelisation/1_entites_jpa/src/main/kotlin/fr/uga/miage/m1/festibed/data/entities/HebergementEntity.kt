package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.TypeHebergement
import jakarta.persistence.CascadeType
import jakarta.persistence.Column
import jakarta.persistence.EmbeddedId
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Index
import jakarta.persistence.JoinColumn
import jakarta.persistence.JoinColumns
import jakarta.persistence.JoinTable
import jakarta.persistence.ManyToMany
import jakarta.persistence.ManyToOne
import jakarta.persistence.MapsId
import jakarta.persistence.OneToMany
import jakarta.persistence.Table
import org.hibernate.annotations.JdbcTypeCode
import org.hibernate.type.SqlTypes
import java.math.BigDecimal

/**
 * Offre réservable d'un établissement, proposée indépendamment de tout festival.
 * Pas de liste « nuitees » : des centaines de lignes par hébergement ; passer par NuiteeRepository.
 */
@Entity
@Table(name = "HEBERGEMENT")
data class HebergementEntity(
    @EmbeddedId
    val id: HebergementId,

    @MapsId("idEtablissement")
    @ManyToOne(optional = false)
    @JoinColumn(name = "etablissement_id", nullable = false)
    var etablissement: EtablissementEntity,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(nullable = false, length = 30)
    var typeHebergement: TypeHebergement,

    /** Nombre de personnes : la somme des capacités d'une sélection doit couvrir ses Pass. */
    @Column(nullable = false)
    var capaciteHebergement: Int,

    @Column(length = 500)
    var descriptionHebergement: String? = null,

    @Column(nullable = false, precision = 8, scale = 2)
    var prixNuitHebergement: BigDecimal,

    @Column(nullable = false)
    var actifHebergement: Boolean = true,

    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumns(
        JoinColumn(name = "etablissement_id", referencedColumnName = "etablissement_id", nullable = false),
        JoinColumn(name = "numeroHebergement", referencedColumnName = "numeroHebergement", nullable = false),
    )
    var photos: MutableCollection<PhotoHebergementEntity> = mutableListOf(),

    /** Table d'association EQUIPEMENT (n,n sans attribut). */
    @ManyToMany
    @JoinTable(
        name = "EQUIPEMENT",
        joinColumns = [
            JoinColumn(name = "etablissement_id", referencedColumnName = "etablissement_id"),
            JoinColumn(name = "numeroHebergement", referencedColumnName = "numeroHebergement"),
        ],
        inverseJoinColumns = [JoinColumn(name = "option_id")],
        indexes = [Index(name = "IX_EQUIPEMENT_1", columnList = "option_id")],
    )
    var options: MutableSet<OptionHebergementEntity> = mutableSetOf(),
) {
    override fun equals(other: Any?) = this === other || (other is HebergementEntity && id == other.id)
    override fun hashCode() = id.hashCode()
    override fun toString() = "HebergementEntity(id=$id, typeHebergement=$typeHebergement, capaciteHebergement=$capaciteHebergement)"
}
