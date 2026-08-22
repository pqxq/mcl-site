from django.core.management.base import BaseCommand
from home.models import (
    AboutPage, AboutPageHighlight, AboutPageStat, AboutPageValuePillar,
    AboutPageProfile, AboutPageFacility, AboutPageFAQ
)


class Command(BaseCommand):
    help = "Seeds editable records for AboutPage in Wagtail CMS"

    def handle(self, *args, **options):
        page = AboutPage.objects.filter(id=4).first()
        if not page:
            page = AboutPage.objects.first()
        if not page:
            self.stdout.write(self.style.ERROR("No AboutPage found in database."))
            return

        # 1. Update basic page fields
        page.subtitle = 'Сучасний освітній заклад для обдарованої молоді — поєднуємо академічні традиції, інноваційні методики та європейські стандарти освіти.'
        page.hero_badge = 'Миколаївський ліцей №9'
        page.intro = '<p>Миколаївський ліцей №9 — це сучасний, відкритий та інноваційний освітній простір, спрямований на всебічний розвиток інтелектуальних, творчих та лідерських здібностей кожної дитини.</p><p>Ми створюємо умови, за яких навчання стає захоплюючим процесом відкриття знань. Наш заклад поєднує фундаментальну академічну підготовку з формуванням практичних компетенцій XXI століття: критичного мислення, цифрової грамотності, командної взаємодії та креативності.</p>'
        page.mission_title = 'Наша місія'
        page.mission = '<p>Формування високоосвіченої, національно свідомої, творчої та всебічно розвиненої особистості, здатної до самореалізації в сучасному динамічному світі.</p><p>Ми прагнемо забезпечити рівний доступ до якісної профільної освіти, розвивати лідерські якості, наукову допитливість та готовність до викликів майбутнього.</p>'
        page.values_title = 'Цінності ліцею'
        page.values = '<p>Освітня філософія нашого ліцею базується на партнерстві, академічній доброчесності та створенні безпечного середовища для всебічного розвитку учнівської молоді.</p>'
        page.profiles_title = 'Освітні напрями та пріоритети'
        page.profiles_subtitle = 'Обирайте напрям, який відповідає талантам і прагненням майбутнього ліцеїста'
        page.subpages_title = 'Розділи про наш ліцей'
        page.subpages_subtitle = 'Ознайомтеся з історією, адміністрацією, педагогічним колективом та службами ліцею'
        page.facilities_title = 'Сучасний освітній простір'
        page.facilities_subtitle = 'Створюємо комфортні, безпечні та високотехнологічні умови для кожного ліцеїста'
        page.faq_title = 'Часті запитання батьків та учнів'
        page.faq_subtitle = 'Основна інформація про організацію освітнього процесу та вступ до ліцею'
        page.save()

        # 2. Highlights (Pills)
        page.highlights.all().delete()
        AboutPageHighlight.objects.create(page=page, title='Поглиблене вивчення предметів', icon='bi-check-circle-fill', sort_order=0)
        AboutPageHighlight.objects.create(page=page, title='Безпечне освітнє середовище', icon='bi-shield-lock-fill', sort_order=1)
        AboutPageHighlight.objects.create(page=page, title='Сучасні цифрові інструменти', icon='bi-laptop', sort_order=2)

        # 3. Stats
        page.stats.all().delete()
        AboutPageStat.objects.create(page=page, number='1991', title='Рік заснування', description='Понад 30 років успішного розвитку', icon='bi-calendar-check', sort_order=0)
        AboutPageStat.objects.create(page=page, number='650+', title='Учнів ліцею', description='Дружня ліцейна родина однодумців', icon='bi-people-fill', sort_order=1)
        AboutPageStat.objects.create(page=page, number='52', title='Педагогів', description='Вчителі вищої категорії та методисти', icon='bi-person-badge-fill', sort_order=2)
        AboutPageStat.objects.create(page=page, number='100%', title='Вступ до ЗВО', description='Успішне складання НМТ та ДПА', icon='bi-trophy-fill', sort_order=3)

        # 4. Value Pillars
        page.value_pillars.all().delete()
        AboutPageValuePillar.objects.create(page=page, title='Академічна якість та доброчесність', description='Глибокі знання, чесність у навчанні та прагнення до самовдосконалення.', icon='bi-mortarboard-fill', sort_order=0)
        AboutPageValuePillar.objects.create(page=page, title='Партнерство та взаємоповага', description='Довіра і відкритий діалог між учнями, педагогами та батьками.', icon='bi-people-fill', sort_order=1)
        AboutPageValuePillar.objects.create(page=page, title='Інновації та творчість', description='Впровадження сучасних методик, STEM-освіти та підтримка креативних ідей.', icon='bi-lightbulb-fill', sort_order=2)
        AboutPageValuePillar.objects.create(page=page, title='Безпека та психологічний комфорт', description="Турбота про фізичне і ментальне здоров'я кожної дитини.", icon='bi-shield-fill-check', sort_order=3)

        # 5. Academic Profiles
        page.academic_profiles.all().delete()
        AboutPageProfile.objects.create(page=page, badge='Точні науки', title='Математика & IT', description="Поглиблене вивчення алгебри, геометрії, інформатики, алгоритмізації та комп'ютерного моделювання.", tags='Математика, Інформатика, Алгоритми', icon='bi-cpu-fill', sort_order=0)
        AboutPageProfile.objects.create(page=page, badge='Мови та світ', title='Філологічний напрям', description='Академічна українська та англійська мови, розвиток мовлення, дебатні практики та зарубіжна література.', tags='Англійська мова, Українська мова, Література', icon='bi-translate', sort_order=1)
        AboutPageProfile.objects.create(page=page, badge='Дослідження', title='STEM & Природничі', description='Практичні лабораторні роботи з фізики, хімії та біології, участь у наукових дослідженнях Малої академії наук.', tags='Фізика, Хімія, Біологія', icon='bi-flask-fill', sort_order=2)
        AboutPageProfile.objects.create(page=page, badge='Суспільство', title='Суспільно-гуманітарний', description='Історія України, правознавство, основи економіки, громадянська освіта та лідерські проєкти.', tags='Історія, Право, Лідерство', icon='bi-bank', sort_order=3)

        # 6. Campus Facilities
        page.facilities.all().delete()
        AboutPageFacility.objects.create(page=page, title='Сертифіковане укриття', description='Обладнане захисне приміщення з вентиляцією, автономним освітленням, Wi-Fi та запасами води.', icon='bi-shield-check', sort_order=0)
        AboutPageFacility.objects.create(page=page, title='Мультимедійні класи', description="Інтерактивні дошки, комп'ютерні лабораторії та швидкісний інтернет для сучасного навчання.", icon='bi-display', sort_order=1)
        AboutPageFacility.objects.create(page=page, title='Спортивний комплекс', description='Облаштований спортивний зал, тренажерна зона та спортивний майданчик для активного відпочинку.', icon='bi-trophy', sort_order=2)
        AboutPageFacility.objects.create(page=page, title='Бібліотека & Медіатека', description='Багатий книжковий фонд, художня література та комфортний простір для самопідготовки.', icon='bi-journal-bookmark', sort_order=3)

        # 7. FAQs
        page.faqs.all().delete()
        AboutPageFAQ.objects.create(page=page, question='Як вступити до Миколаївського ліцею №9?', answer='<p>Прийом заяв на вступ здійснюється через наш онлайн-сервіс у розділі <a href="/publichna-informatsiia/vstup-do-litseiu/">«Вступ до ліцею»</a> або безпосередньо в закладі. Для зарахування необхідно надати заяву батьків, копію свідоцтва про народження / паспорта та особову справу з попереднього закладу освіти.</p>', sort_order=0)
        AboutPageFAQ.objects.create(page=page, question='Як організовано безпеку учнів під час тривог?', answer="<p>Ліцей має власне сертифіковане укриття, перевірене всіма державними службами. Під час повітряної тривоги всі учасники освітнього процесу оперативно переходять до захисного простору, де облаштовано навчальні місця, Wi-Fi зв'язок, вентиляцію та санітарні зони.</p>", sort_order=1)
        AboutPageFAQ.objects.create(page=page, question='Які форми навчання підтримуються в ліцеї?', answer='<p>Освітній процес організовано в очному, змішаному та дистанційному форматах відповідно до безпекової ситуації в регіоні. Ліцей використовує сучасну електронну платформу, інтерактивні журнали та хмарні сервіси для зручної взаємодії.</p>', sort_order=2)
        AboutPageFAQ.objects.create(page=page, question='Чи є можливість відвідувати позакласні гуртки та секції?', answer='<p>Так, для учнів діють спортивні секції, дебатний клуб, наукове товариство МАН, мовні клуби та студії творчості. Усі заняття спрямовані на розкриття індивідуальних талантів ліцеїстів.</p>', sort_order=3)

        self.stdout.write(self.style.SUCCESS("Successfully populated editable AboutPage records in Wagtail database!"))
