package fr.uga.miage.m1.festibed.repositories

import fr.uga.miage.m1.festibed.data.entities.EtablissementNonClasseEntity
import fr.uga.miage.m1.festibed.data.entities.HebergementEntity
import fr.uga.miage.m1.festibed.data.entities.OptionHebergementEntity
import fr.uga.miage.m1.festibed.data.entities.PhotoHebergementEntity
import fr.uga.miage.m1.festibed.data.repositories.EtablissementRepository
import fr.uga.miage.m1.festibed.data.repositories.HebergementRepository
import fr.uga.miage.m1.festibed.data.repositories.OptionHebergementRepository
import fr.uga.miage.m1.festibed.data.entities.CampingEntity
import fr.uga.miage.m1.festibed.enums.TypeHebergement
import fr.uga.miage.m1.festibed.enums.TypeNonClasse
import jakarta.persistence.EntityManager
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest
import org.springframework.dao.DataIntegrityViolationException
import org.springframework.data.domain.PageRequest
import org.springframework.test.context.ActiveProfiles
import java.math.BigDecimal
import java.time.LocalDate
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue

@DataJpaTest
@ActiveProfiles("test")
class HebergementRepositoryTest {

    @Autowired
    lateinit var hebergementRepository: HebergementRepository

    @Autowired
    lateinit var optionRepository: OptionHebergementRepository

    @Autowired
    lateinit var etablissementRepository: EtablissementRepository

    @Autowired
    lateinit var em: EntityManager

    @Test
    fun `les options sont partagées entre hébergements (ManyToMany via equipement)`() {
        val jeu = Jeu(em)
        val wifi = optionRepository.save(OptionHebergementEntity(libelle = "Wi-Fi"))
        val piscine = optionRepository.save(OptionHebergementEntity(libelle = "Piscine"))
        val h1 = jeu.hebergement("H001").also { it.options += setOf(wifi, piscine) }
        val h2 = jeu.hebergement("H002").also { it.options += wifi }
        hebergementRepository.saveAllAndFlush(listOf(h1, h2))
        em.clear()

        assertEquals(setOf("Wi-Fi", "Piscine"), hebergementRepository.findById(h1.id!!).get().options.map { it.libelle }.toSet())
        assertEquals(setOf(h1.id, h2.id), hebergementRepository.findAllByOptionsLibelle("Wi-Fi").map { it.id }.toSet())
        assertEquals(listOf(h1.id), hebergementRepository.findAllByOptionsLibelle("Piscine").map { it.id })
        assertEquals(2, optionRepository.count())
    }

    @Test
    fun `les photos suivent leur hébergement (cascade et orphanRemoval)`() {
        val h = Jeu(em).hebergement()
        h.photos += listOf(PhotoHebergementEntity(url = "https://p/1.jpg"), PhotoHebergementEntity(url = "https://p/2.jpg"))
        hebergementRepository.saveAndFlush(h)
        em.clear()

        val relu = hebergementRepository.findById(h.id!!).get()
        assertEquals(2, relu.photos.size)
        relu.photos.removeIf { it.url.endsWith("1.jpg") }
        hebergementRepository.saveAndFlush(relu)
        em.clear()

        assertEquals(listOf("https://p/2.jpg"), hebergementRepository.findById(h.id!!).get().photos.map { it.url })
    }

    @Test
    fun `deux hébergements d'un même établissement ne peuvent pas avoir le même numéro`() {
        val h = Jeu(em).hebergement("H001")

        assertFailsWith<DataIntegrityViolationException> {
            hebergementRepository.saveAndFlush(
                HebergementEntity(
                    etablissement = h.etablissement, numero = "H001", typeHebergement = TypeHebergement.BUNGALOW,
                    capacite = 4, prixNuit = BigDecimal("80.00"),
                ),
            )
        }
    }

    @Test
    fun `l'héritage JOINED renvoie la bonne sous-classe`() {
        val jeu = Jeu(em)
        val camping = jeu.camping()
        val auberge = jeu.persister(
            EtablissementNonClasseEntity(
                nomCommercial = "Auberge de Jeunesse", codePostal = "73100", nomCommune = "Aix-les-Bains",
                capaciteAccueil = 40, typeNonClasse = TypeNonClasse.AUBERGE_DE_JEUNESSE,
            ),
        )
        em.clear()

        assertIs<CampingEntity>(etablissementRepository.findById(camping.id!!).get())
        val relue = etablissementRepository.findById(auberge.id!!).get()
        assertIs<EtablissementNonClasseEntity>(relue)
        assertNull(relue.classement)
        assertTrue(!relue.estClasse)
        assertEquals(1, etablissementRepository.findAllByCommuneCodeInsee("73008").size)
    }

    @Test
    fun `ajouterNote met à jour la moyenne et le compteur`() {
        val camping = Jeu(em).camping()

        etablissementRepository.ajouterNote(camping.id!!, BigDecimal(4))
        etablissementRepository.ajouterNote(camping.id!!, BigDecimal(5))

        val relu = etablissementRepository.findById(camping.id!!).get()
        assertEquals(2, relu.nbNotes)
        assertEquals(0, BigDecimal("4.50").compareTo(relu.noteMoyenne))
    }

    @Test
    fun `rechercherDisponibles trouve les hébergements ayant une nuit libre près du festival`() {
        val jeu = Jeu(em)
        val libre = jeu.hebergement("H001")
        val pris = jeu.hebergement("H002")
        jeu.nuits(libre, LocalDate.of(2027, 7, 12), 3)
        jeu.nuits(pris, LocalDate.of(2027, 8, 1), 3)

        val trouves = hebergementRepository.rechercherDisponibles(
            LocalDate.of(2027, 7, 12), LocalDate.of(2027, 7, 15), 2,
            BigDecimal("45.4"), BigDecimal("46.0"), BigDecimal("5.5"), BigDecimal("6.3"), PageRequest.of(0, 10),
        )

        assertEquals(listOf(libre.id), trouves.map { it.id })
    }
}
