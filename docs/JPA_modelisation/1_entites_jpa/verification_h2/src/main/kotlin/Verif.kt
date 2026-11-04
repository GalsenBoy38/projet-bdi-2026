/*
 * FestiBed - Groupe 3 - Vérification des entités JPA sur H2 (sans Spring Boot).
 *   mode « essai »   : schéma + jeu d'essai Excel (2_insertion_excel/insert_jeu_essai_scenarios_h2.sql)
 *   mode « complet » : schéma + peuplement complet (3_peuplement_donnees/csv, 1,6 million de lignes)
 * Vérifie : contrôles SQL, hbm2ddl.auto=validate, lectures (héritage, clés composées, projections),
 * écritures (cascade, UUID générés), UPDATE conditionnels, concurrence, repositories Spring Data.
 *
 *   cd docs/JPA_modelisation/1_entites_jpa/verification_h2
 *   mvn -q compile dependency:build-classpath -Dmdep.outputFile=cp.txt
 *   java -cp "target/classes;$(cat cp.txt)" VerifKt essai        (ou : complet ; « : » au lieu de « ; » sous Linux/macOS)
 */
import fr.uga.miage.m1.festibed.data.entities.*
import fr.uga.miage.m1.festibed.data.repositories.*
import fr.uga.miage.m1.festibed.enums.Domaine
import org.hibernate.SessionFactory
import org.springframework.data.jpa.repository.support.JpaRepositoryFactory
import org.springframework.data.domain.PageRequest
import java.math.BigDecimal
import org.hibernate.cfg.Configuration
import java.sql.DriverManager
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger

/** Dossier docs/JPA_modelisation (le programme se lance depuis 1_entites_jpa/verification_h2). */
val P: String = java.io.File("../..").canonicalPath.replace('\\', '/')
val CLASSES = listOf(
    UtilisateurEntity::class, FestivalierEntity::class, UtilisateurBackofficeEntity::class, OrganisateurEntity::class,
    HebergeurEntity::class, RegionEntity::class, DepartementEntity::class, CommuneEntity::class, FestivalEntity::class,
    NotationFestivalEntity::class, EtablissementEntity::class, HotelDeTourismeEntity::class, AubergeCollectiveEntity::class,
    CampingEntity::class, ParcResidentielDeLoisirsEntity::class, VillageDeVacancesEntity::class,
    ResidenceDeTourismeEntity::class, EtablissementNonClasseEntity::class, NotationEtablissementEntity::class,
    HebergementEntity::class,
    OptionHebergementEntity::class, PhotoHebergementEntity::class, NuiteeEntity::class,
    ReservationEntity::class, SelectionEntity::class, PassEntity::class, PaiementEntity::class,
)
var ko = 0
fun check(cond: Boolean, msg: String) { println("  [${if (cond) "OK" else "KO"}] $msg"); if (!cond) ko++ }

fun sessionFactory(url: String): SessionFactory {
    val cfg = Configuration()
        .setProperty("hibernate.connection.url", url)
        .setProperty("hibernate.connection.username", "sa")
        .setProperty("hibernate.connection.password", "")
        .setProperty("hibernate.hbm2ddl.auto", "validate")
        .setProperty("hibernate.jdbc.batch_size", "50")
        .setProperty("hibernate.show_sql", "false")
    CLASSES.forEach { cfg.addAnnotatedClass(it.java) }
    return cfg.buildSessionFactory()
}

fun sql(url: String, vararg scripts: String) {
    DriverManager.getConnection(url, "sa", "").use { c ->
        scripts.forEach { s -> c.createStatement().use { it.execute("RUNSCRIPT FROM '$s' CHARSET 'UTF-8'") } }
    }
}

fun main(args: Array<String>) {
    val mode = args.firstOrNull() ?: "essai"
    val base = java.io.File("target/h2_$mode").absolutePath.replace('\\', '/')
    java.io.File("$base.mv.db").delete()
    val url = "jdbc:h2:file:$base;LOCK_TIMEOUT=10000"
    val t0 = System.currentTimeMillis()
    if (mode == "essai") {
        sql(url, "$P/3_peuplement_donnees/01_schema_h2.sql", "$P/2_insertion_excel/insert_jeu_essai_scenarios_h2.sql")
    } else {
        // 02_charger_h2.sql utilise des chemins relatifs (csv/...) : on les rend absolus
        val charger = java.io.File("target/charger_h2.sql")
        charger.writeText(java.io.File("$P/3_peuplement_donnees/02_charger_h2.sql").readText()
            .replace("CSVREAD('csv/", "CSVREAD('$P/3_peuplement_donnees/csv/"))
        sql(url, "$P/3_peuplement_donnees/01_schema_h2.sql", charger.absolutePath.replace('\\', '/'))
    }
    println("== Chargement $mode : ${(System.currentTimeMillis() - t0) / 1000} s")

    println("== Contrôles SQL (04_controles.sql)")
    DriverManager.getConnection(url, "sa", "").use { c ->
        val texte = java.io.File("$P/3_peuplement_donnees/04_controles.sql").readText()
        texte.split(";").map { it.lines().filterNot { l -> l.trim().startsWith("--") }.joinToString("\n").trim() }
            .filter { it.isNotEmpty() }.forEach { q ->
                c.createStatement().executeQuery(q).use { rs ->
                    rs.next()
                    val nom = rs.getString(1); val v = rs.getLong(2)
                    val anomalie = nom.startsWith("anomalies")
                    if (anomalie && !(mode == "essai" && nom.contains("moitie"))) check(v == 0L, "$nom = $v")
                    else println("  [--] $nom = $v")
                }
            }
    }

    println("== Hibernate validate + requêtes JPA")
    val sf = sessionFactory(url)
    check(true, "schéma validé par Hibernate (hbm2ddl.auto=validate)")
    val idMusilac: UUID
    sf.openSession().use { s ->
        val f = s.createQuery("from FestivalEntity f join fetch f.commune c join fetch c.departement d join fetch d.region where f.nomFestival = 'Musilac'", FestivalEntity::class.java).singleResult
        idMusilac = f.id!!
        check(f.commune.departement.region.nomRegion == "Auvergne-Rhône-Alpes", "Musilac -> ${f.commune.nomCommune} -> ${f.commune.departement.nomDepartement} -> ${f.commune.departement.region.nomRegion}, ${f.passDisponibles} Pass disponibles")
        val sierroz = s.createQuery("from EtablissementEntity e where e.nomCommercial = 'CAMPING INTERNATIONAL DU SIERROZ'", EtablissementEntity::class.java).singleResult
        check(sierroz is CampingEntity && sierroz.categorie != null, "polymorphisme JOINED : ${sierroz::class.simpleName}, catégorie ${(sierroz as CampingEntity).categorie}, ${sierroz.latitudeEtablissement}/${sierroz.longitudeEtablissement}")
        check(sierroz.estClasse && sierroz.commune != null, "établissement classé -> commune ${sierroz.commune?.nomCommune} (${sierroz.commune?.codeInsee}), OSM ${sierroz.osmRef}, tél. ${sierroz.telephoneEtablissement}")
        val nonClasse = s.createQuery("from EtablissementNonClasseEntity e join fetch e.commune", EtablissementNonClasseEntity::class.java).setMaxResults(1).singleResult
        check(!nonClasse.estClasse && nonClasse.osmRef != null, "établissement non classé (OSM) : ${nonClasse.nomCommercial}, ${nonClasse.typeNonClasse}, ${nonClasse.commune?.nomCommune}, ${nonClasse.osmRef}")
        val h = s.find(HebergementEntity::class.java, HebergementId(sierroz.id, "H001"))
        check(h != null && h.capaciteHebergement == 2, "Hebergement par clé composée : $h, options=${h?.options?.size}, photos=${h?.photos?.size}")
        val nuits = s.createQuery("from NuiteeEntity n where n.hebergement = :h and n.selection is null order by n.id.dateNuitee", NuiteeEntity::class.java)
            .setParameter("h", h).resultList
        check(nuits.isNotEmpty(), "nuitées libres de l'emplacement Sierroz : ${nuits.map { it.id.dateNuitee }}")
        val resa = s.createQuery("select distinct r from ReservationEntity r join fetch r.selections sel where sel.festival.id = :f", ReservationEntity::class.java)
            .setParameter("f", idMusilac).setMaxResults(1).resultList.firstOrNull()
        val sel = resa?.selections?.first { it.festival.id == idMusilac }
        val nuiteesSel = if (sel == null) emptyList() else s.createQuery("from NuiteeEntity n where n.selection.id = :s", NuiteeEntity::class.java).setParameter("s", sel.id).resultList
        check(sel != null && sel.passes.isNotEmpty() && nuiteesSel.isNotEmpty(), "réservation ${resa?.numeroReservation} -> sélection Musilac : ${sel?.passes?.size} Pass, ${nuiteesSel.size} nuitées")
        val nf = s.createQuery("select count(n) from NotationFestivalEntity n", java.lang.Long::class.java).singleResult
        check(nf.toLong() > 0, "notations festival lisibles ($nf)")
        val dto = s.createQuery("""select e.nomCommercial, h.id.numeroHebergement, h.capaciteHebergement from HebergementEntity h join h.etablissement e
             where h.capaciteHebergement >= 2 and exists (select 1 from NuiteeEntity n where n.hebergement = h and n.selection is null and n.id.dateNuitee = :d)""", Array<Any>::class.java)
            .setParameter("d", LocalDate.of(2027, 7, 12)).setMaxResults(5).resultList
        check(dto.isNotEmpty(), "projection de recherche d'hébergements libres le 12/07/2027 : ${dto.size} résultats")
    }

    println("== Écritures : validation d'un panier (transaction tout ou rien)")
    val nuitLibre: NuiteeEntity
    sf.openSession().use { s ->
        nuitLibre = s.createQuery("from NuiteeEntity n where n.selection is null and n.hebergement.capaciteHebergement >= 2 and n.id.dateNuitee >= :d order by n.id.dateNuitee", NuiteeEntity::class.java)
            .setParameter("d", LocalDate.of(2027, 7, 12)).setMaxResults(1).singleResult
    }
    val numero = "FBTEST00001"
    sf.openSession().use { s ->
        val tx = s.beginTransaction()
        val festivalier = s.createQuery("from FestivalierEntity", FestivalierEntity::class.java).setMaxResults(1).singleResult
        val festival = s.find(FestivalEntity::class.java, idMusilac)
        val sel = SelectionEntity(
            festival = festival,
            prixPassSelection = festival.prixPass,
            passes = mutableListOf(PassEntity(codePass = "PASS-TEST-1"), PassEntity(codePass = "PASS-TEST-2")),
        )
        val resa = ReservationEntity(
            numeroReservation = numero,
            dateReservation = LocalDateTime.now(),
            festivalier = festivalier,
            selections = mutableListOf(sel),
        )
        s.persist(resa)
        s.flush()
        val nuits = s.createMutationQuery("update NuiteeEntity n set n.selection = :sel where n.id = :id and n.selection is null")
            .setParameter("sel", sel).setParameter("id", nuitLibre.id).executeUpdate()
        val pass = s.createMutationQuery("update FestivalEntity f set f.nbPassVendus = f.nbPassVendus + :n where f.id = :f and f.nbPassVendus + :n <= f.quotaPass")
            .setParameter("n", 2).setParameter("f", idMusilac).executeUpdate()
        s.persist(PaiementEntity(reservation = resa, montantPaiement = festival.prixPass.multiply(2.toBigDecimal())))
        tx.commit()
        check(nuits == 1 && pass == 1, "UPDATE conditionnels : $nuits nuitée occupée, $pass festival mis à jour")
        check(sel.id != null && sel.passes.all { it.id != null }, "cascade + UUID générés : idSelection=${sel.id}, idPass=${sel.passes.map { it.id }}")
    }
    sf.openSession().use { s ->
        val f = s.find(FestivalEntity::class.java, idMusilac)
        val vendusSql = s.createNativeQuery("select count(*) from PASS p join SELECTION s on s.idSelection = p.idSelection where s.idFestival = '$idMusilac'", java.lang.Long::class.java).singleResult
        check(f.nbPassVendus.toLong() == vendusSql.toLong(), "nbPassVendus (${f.nbPassVendus}) = Pass en base ($vendusSql)")
        val tx = s.beginTransaction()
        f.nomFestival = "Musilac"            // l'organisateur modifie son festival : nbPassVendus ne doit pas être écrasé
        f.quotaPass = f.quotaPass + 1
        val avant = f.nbPassVendus
        s.createMutationQuery("update FestivalEntity f set f.nbPassVendus = f.nbPassVendus + 1 where f.id = :f")
            .setParameter("f", idMusilac).executeUpdate()   // une vente concurrente pendant la modification
        tx.commit()
        s.clear()
        val apres = s.find(FestivalEntity::class.java, idMusilac).nbPassVendus
        check(apres == avant + 1, "la sauvegarde du festival par l'organisateur n'écrase pas nbPassVendus ($avant -> $apres)")
    }
    println("== Concurrence : 8 validations simultanées sur la même nuitée")
    val selIds = sf.openSession().use { s ->
        s.createQuery("select s.id from SelectionEntity s where s.festival.id = :f", UUID::class.java)
            .setParameter("f", idMusilac).setMaxResults(8).resultList
    }
    val cible = sf.openSession().use { s ->
        s.createQuery("from NuiteeEntity n where n.selection is null", NuiteeEntity::class.java).setMaxResults(1).singleResult.id
    }
    val gagnants = AtomicInteger()
    val depart = CountDownLatch(1)
    val pool = Executors.newFixedThreadPool(8)
    selIds.forEach { sid ->
        pool.submit {
            sf.openSession().use { s ->
                val tx = s.beginTransaction()
                depart.await()
                val n = s.createMutationQuery("update NuiteeEntity n set n.selection.id = :sel where n.id = :id and n.selection is null")
                    .setParameter("sel", sid).setParameter("id", cible).executeUpdate()
                Thread.sleep(100)          // garde le verrou un moment
                if (n == 1) gagnants.incrementAndGet()
                tx.commit()
            }
        }
    }
    depart.countDown(); pool.shutdown(); pool.awaitTermination(60, java.util.concurrent.TimeUnit.SECONDS)
    check(gagnants.get() == 1, "une seule validation obtient la nuitée (${gagnants.get()} gagnant sur ${selIds.size})")
    println("== Repositories Spring Data (requêtes JPQL des UPDATE conditionnels)")
    val em = sf.createEntityManager()
    val fac = JpaRepositoryFactory(em)
    val festivals = fac.getRepository(FestivalRepository::class.java)
    val nuitees = fac.getRepository(NuiteeRepository::class.java)
    val hebergements = fac.getRepository(HebergementRepository::class.java)
    val etabs = fac.getRepository(EtablissementRepository::class.java)
    val resas = fac.getRepository(ReservationRepository::class.java)
    val trouves = festivals.rechercher(LocalDate.of(2027, 7, 1), LocalDate.of(2027, 7, 31), Domaine.MUSIQUES_ACTUELLES, BigDecimal(200), PageRequest.of(0, 20))
    check(trouves.isNotEmpty() && trouves.all { it.passDisponibles > 0 }, "FestivalRepository.rechercher : ${trouves.size} festivals de musiques actuelles en juillet avec Pass disponibles")
    val musilac = festivals.findById(idMusilac).get()
    val dispo = hebergements.rechercherDisponibles(musilac.dateDebutFestival, musilac.dateFinFestival, 2,
        musilac.commune.latitude!! - BigDecimal("0.3"), musilac.commune.latitude!! + BigDecimal("0.3"),
        musilac.commune.longitude!! - BigDecimal("0.4"), musilac.commune.longitude!! + BigDecimal("0.4"), PageRequest.of(0, 10))
    check(dispo.any { it.nomCommercial.contains("SIERROZ") }, "HebergementRepository.rechercherDisponibles autour de Musilac : ${dispo.size} résultats, dont ${dispo.firstOrNull { it.nomCommercial.contains("SIERROZ") }}")
    em.transaction.begin()
    val restant = musilac.passDisponibles
    val ok1 = festivals.reserverPass(idMusilac, restant)
    val ok2 = festivals.reserverPass(idMusilac, 1)
    check(ok1 == 1 && ok2 == 0, "reserverPass : les $restant derniers Pass -> $ok1, un de plus -> $ok2 (refus)")
    check(festivals.modifierQuota(idMusilac, 10) == 0, "modifierQuota sous les Pass vendus -> refusé")
    val sel = em.find(SelectionEntity::class.java, selIds.first())
    val hSierroz = HebergementId(etabs.findAll().first { it.nomCommercial == "CAMPING INTERNATIONAL DU SIERROZ" }.id, "H001")
    val libresS = nuitees.nuitsLibres(hSierroz, musilac.dateDebutFestival, musilac.dateFinFestival).map { it.id.dateNuitee!! }
    val pris = nuitees.occuper(sel, hSierroz, libresS)
    val repris = nuitees.occuper(sel, hSierroz, libresS)
    check(pris == libresS.size && repris == 0, "NuiteeRepository.occuper : ${libresS.size} nuits -> $pris occupées, 2e tentative -> $repris")
    check(nuitees.retirerSiLibre(NuiteeId(hSierroz, libresS.first())) == 0, "retirerSiLibre sur une nuit réservée -> refusé")
    val noteAvant = etabs.findById(hSierroz.idEtablissement!!).get().nbNotes
    etabs.ajouterNote(hSierroz.idEtablissement!!, BigDecimal(5))
    check(etabs.findById(hSierroz.idEtablissement!!).get().nbNotes == noteAvant + 1, "EtablissementRepository.ajouterNote : nbNotes $noteAvant -> ${noteAvant + 1}")
    val r = resas.findAll(PageRequest.of(0, 1)).first()
    check(resas.findAllByFestivalierId(r.festivalier.id!!).isNotEmpty(), "ReservationRepository.findAllByFestivalierId (requête dérivée)")
    check(fac.getRepository(NuiteeRepository::class.java).findAllBySelectionId(sel.id!!).size >= libresS.size, "NuiteeRepository.findAllBySelectionId (requête dérivée sur selection.id)")
    check(fac.getRepository(FestivalierRepository::class.java).findByEmail(r.festivalier.email) != null, "FestivalierRepository.findByEmail")
    check(fac.getRepository(OrganisateurRepository::class.java).findByEmail("ronald.organisateur@festibed.test") != null, "OrganisateurRepository.findByEmail (compte de Ronald)")
    check(fac.getRepository(NotationFestivalRepository::class.java).count() > 0, "NotationFestivalRepository (clé composée)")
    check(resas.trouverAnonyme(r.numeroReservation, r.festivalier.email) != null && resas.trouverAnonyme(r.numeroReservation, "x@y.z") == null, "ReservationRepository.trouverAnonyme (email + numéro)")
    em.transaction.rollback()
    em.close()
    sf.close()
    println(if (ko == 0) "TOUT EST OK" else "$ko contrôle(s) en échec")
    kotlin.system.exitProcess(if (ko == 0) 0 else 1)
}
