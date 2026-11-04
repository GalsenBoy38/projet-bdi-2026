package fr.uga.miage.m1.festibed.repositories

import fr.uga.miage.m1.festibed.data.entities.FestivalierEntity
import fr.uga.miage.m1.festibed.data.entities.HebergeurEntity
import fr.uga.miage.m1.festibed.data.entities.OrganisateurEntity
import fr.uga.miage.m1.festibed.data.repositories.FestivalRepository
import fr.uga.miage.m1.festibed.data.repositories.FestivalierRepository
import fr.uga.miage.m1.festibed.data.repositories.HebergeurRepository
import fr.uga.miage.m1.festibed.data.repositories.OrganisateurRepository
import jakarta.persistence.EntityManager
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest
import org.springframework.dao.DataIntegrityViolationException
import org.springframework.test.context.ActiveProfiles
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotNull
import kotlin.test.assertNull

@DataJpaTest
@ActiveProfiles("test")
class UtilisateurRepositoryTest {

    @Autowired
    lateinit var festivalierRepository: FestivalierRepository

    @Autowired
    lateinit var organisateurRepository: OrganisateurRepository

    @Autowired
    lateinit var hebergeurRepository: HebergeurRepository

    @Autowired
    lateinit var festivalRepository: FestivalRepository

    @Autowired
    lateinit var em: EntityManager

    @Test
    fun `chaque sous-type est retrouvé par son email`() {
        organisateurRepository.save(OrganisateurEntity(nom = "Ronald", email = "ronald@festibed.test", motDePasseHache = "hash"))
        hebergeurRepository.save(HebergeurEntity(nom = "Hôte", email = "hote@festibed.test", motDePasseHache = "hash"))
        festivalierRepository.saveAndFlush(FestivalierEntity(nom = "Camille", email = "camille@festibed.test", fournisseurAuth = "GOOGLE", identifiantExterne = "g-1"))
        em.clear()

        assertNotNull(organisateurRepository.findByEmail("ronald@festibed.test"))
        assertNull(organisateurRepository.findByEmail("hote@festibed.test"))
        assertEquals("Camille", festivalierRepository.findByFournisseurAuthAndIdentifiantExterne("GOOGLE", "g-1")?.nom)
    }

    @Test
    fun `l'email est unique quel que soit le type d'utilisateur`() {
        organisateurRepository.saveAndFlush(OrganisateurEntity(nom = "Ronald", email = "meme@festibed.test", motDePasseHache = "hash"))

        assertFailsWith<DataIntegrityViolationException> {
            festivalierRepository.saveAndFlush(FestivalierEntity(nom = "Camille", email = "meme@festibed.test"))
        }
    }

    @Test
    fun `les festivals d'un organisateur (ManyToOne festival vers organisateur)`() {
        val ronald = organisateurRepository.save(OrganisateurEntity(nom = "Ronald", email = "ronald@festibed.test", motDePasseHache = "hash"))
        val jeu = Jeu(em)
        jeu.festival("Musilac").organisateur = ronald
        jeu.festival("Sans organisateur")
        em.flush()

        assertEquals(listOf("Musilac"), festivalRepository.findAllByOrganisateurId(ronald.id!!).map { it.nom })
        assertEquals(2, festivalRepository.findAllByCommuneDepartementCode("73").size)
    }
}
