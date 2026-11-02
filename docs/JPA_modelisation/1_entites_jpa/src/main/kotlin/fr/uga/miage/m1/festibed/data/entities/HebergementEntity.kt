package fr.uga.miage.m1.festibed.data.entities

import fr.uga.miage.m1.festibed.enums.TypeHebergement
import jakarta.persistence.CascadeType
import jakarta.persistence.Column
import jakarta.persistence.EmbeddedId
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.FetchType
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
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "idEtablissement", nullable = false)
    var etablissement: EtablissementEntity,

    @Enumerated(EnumType.STRING)
    @JdbcTypeCode(SqlTypes.VARCHAR)
    @Column(name = "typeHebergement", nullable = false, length = 30)
    var typeHebergement: TypeHebergement,

    /** Nombre de personnes : la somme des capacités d'une sélection doit couvrir ses Pass. */
    @Column(name = "capaciteHebergement", nullable = false)
    var capaciteHebergement: Int,

    @Column(name = "descriptionHebergement", length = 500)
    var descriptionHebergement: String? = null,

    @Column(name = "prixNuitHebergement", nullable = false, precision = 8, scale = 2)
    var prixNuitHebergement: BigDecimal,

    @Column(name = "actifHebergement", nullable = false)
    var actifHebergement: Boolean = true,

    @OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)
    @JoinColumns(
        JoinColumn(name = "idEtablissement", referencedColumnName = "idEtablissement", nullable = false),
        JoinColumn(name = "numeroHebergement", referencedColumnName = "numeroHebergement", nullable = false),
    )
    var photos: MutableCollection<PhotoHebergementEntity> = mutableListOf(),

    /** Table d'association EQUIPEMENT (n,n sans attribut). */
    @ManyToMany
    @JoinTable(
        name = "EQUIPEMENT",
        joinColumns = [
            JoinColumn(name = "idEtablissement", referencedColumnName = "idEtablissement"),
            JoinColumn(name = "numeroHebergement", referencedColumnName = "numeroHebergement"),
        ],
        inverseJoinColumns = [JoinColumn(name = "idOptionHebergement")],
        indexes = [Index(name = "IX_EQUIPEMENT_1", columnList = "idOptionHebergement")],
    )
    var options: MutableSet<OptionHebergementEntity> = mutableSetOf(),
) {
    override fun equals(other: Any?) = this === other || (other is HebergementEntity && id == other.id)
    override fun hashCode() = id.hashCode()
    override fun toString() = "HebergementEntity(id=$id, typeHebergement=$typeHebergement, capaciteHebergement=$capaciteHebergement)"
}
