package fr.uga.miage.m1.festibed.repositories

import fr.uga.miage.m1.festibed.data.repositories.FestivalRepository
import fr.uga.miage.m1.festibed.enums.Domaine
import jakarta.persistence.EntityManager
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest
import org.springframework.data.domain.PageRequest
import org.springframework.test.context.ActiveProfiles
import java.math.BigDecimal
import java.time.LocalDate
import kotlin.test.assertEquals

@DataJpaTest
@ActiveProfiles("test")
class FestivalRepositoryTest {

    @Autowired
    lateinit var festivalRepository: FestivalRepository

    @Autowired
    lateinit var em: EntityManager

    @Test
    fun `un nouveau festival n'a vendu aucun Pass`() {
        val festival = Jeu(em).festival()
        em.clear()

        assertEquals(0, festivalRepository.findById(festival.id!!).get().nbPassVendus)
    }

    @Test
    fun `reserverPass refuse de dépasser le quota`() {
        val festival = Jeu(em).festival(quota = 40)

        assertEquals(1, festivalRepository.reserverPass(festival.id!!, 39))
        assertEquals(0, festivalRepository.reserverPass(festival.id!!, 2))
        assertEquals(1, festivalRepository.reserverPass(festival.id!!, 1))
        assertEquals(0, festivalRepository.findById(festival.id!!).get().passDisponibles)
    }

    @Test
    fun `la sauvegarde du festival par l'organisateur n'écrase pas les Pass vendus`() {
        val festival = Jeu(em).festival()
        festivalRepository.reserverPass(festival.id!!, 5)

        val relu = festivalRepository.findById(festival.id!!).get()
        relu.prixPass = BigDecimal("120.00")
        festivalRepository.reserverPass(festival.id!!, 1)   // vente concurrente pendant la modification
        festivalRepository.saveAndFlush(relu)
        em.clear()

        assertEquals(6, festivalRepository.findById(festival.id!!).get().nbPassVendus)
    }

    @Test
    fun `modifierQuota refuse un quota inférieur aux Pass vendus`() {
        val festival = Jeu(em).festival(quota = 50)
        festivalRepository.reserverPass(festival.id!!, 45)

        assertEquals(0, festivalRepository.modifierQuota(festival.id!!, 40))
        assertEquals(1, festivalRepository.modifierQuota(festival.id!!, 60))
    }

    @Test
    fun `rechercher ne renvoie que les festivals actifs avec des Pass sur la période`() {
        val jeu = Jeu(em)
        val juillet = jeu.festival("Musilac")
        val complet = jeu.festival("Complet", quota = 30)
        val inactif = jeu.festival("Inactif").also { it.actif = false }
        jeu.festival("Septembre", debut = LocalDate.of(2027, 9, 1))
        festivalRepository.reserverPass(complet.id!!, 30)
        festivalRepository.saveAndFlush(inactif)

        val trouves = festivalRepository.rechercher(
            LocalDate.of(2027, 7, 1), LocalDate.of(2027, 7, 31), Domaine.MUSIQUES_ACTUELLES, null, PageRequest.of(0, 10),
        )

        assertEquals(listOf(juillet.id), trouves.map { it.id })
    }
}
