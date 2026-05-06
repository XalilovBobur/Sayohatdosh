from django.core.management.base import BaseCommand
from apps.survey.models import Interest

class Command(BaseCommand):
    help = 'Update interest names and populate display names'

    def handle(self, *args, **options):
        # 'O'yingohlar' ni 'kinotearlar' ga o'zgartirish va display_name ni 'Kinoteatr' qilish
        try:
            interest = Interest.objects.filter(name__icontains='yingohlar').first()
            if interest:
                interest.name = 'kinotearlar'
                interest.display_name = 'Kinoteatr'
                interest.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ "{interest.name}" muvaffaqiyatli "kinotearlar" ga o\'zgartirildi va display_name "Kinoteatr" qilib belgilandi')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('❌ "O\'yingohlar" topilmadi')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Xatolik: {e}')
            )

        # Set display_name for all interests (if not set, use name)
        for interest in Interest.objects.all():
            if not interest.display_name:
                interest.display_name = interest.name
                interest.save()
                self.stdout.write(f'✅ {interest.name} uchun display_name o\'rnatildi')

        # Barcha interest'larni ko'rsatish
        self.stdout.write('\n📋 Barcha kategoriyalar:')
        for interest in Interest.objects.all():
            self.stdout.write(f'  - {interest.name} (display: {interest.display_name})')