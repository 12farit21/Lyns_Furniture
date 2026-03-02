from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate favicon and PWA icon files from static/images/logo.png using Pillow'

    SIZES = [
        ('favicon-16.png', (16, 16)),
        ('favicon-32.png', (32, 32)),
        ('apple-touch-icon.png', (180, 180)),
        ('icon-192.png', (192, 192)),
        ('icon-512.png', (512, 512)),
    ]

    def handle(self, *args, **options):
        try:
            from PIL import Image
        except ImportError:
            self.stderr.write(self.style.ERROR('Pillow is not installed. Run: pip install Pillow'))
            return

        source = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo.png'
        if not source.exists():
            self.stderr.write(self.style.ERROR(f'Source image not found: {source}'))
            return

        icons_dir = Path(settings.BASE_DIR) / 'static' / 'images' / 'icons'
        icons_dir.mkdir(parents=True, exist_ok=True)

        with Image.open(source) as img:
            # Convert to RGBA for transparency support
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            for filename, size in self.SIZES:
                resized = img.resize(size, Image.LANCZOS)
                output_path = icons_dir / filename
                resized.save(output_path, 'PNG', optimize=True)
                self.stdout.write(self.style.SUCCESS(f'Created {output_path.relative_to(settings.BASE_DIR)} ({size[0]}x{size[1]})'))

            # Generate multi-size favicon.ico (16, 32, 48)
            ico_images = []
            for size in [(16, 16), (32, 32), (48, 48)]:
                ico_images.append(img.resize(size, Image.LANCZOS).convert('RGBA'))

            ico_path = icons_dir / 'favicon.ico'
            ico_images[0].save(
                ico_path,
                format='ICO',
                sizes=[(16, 16), (32, 32), (48, 48)],
                append_images=ico_images[1:],
            )
            self.stdout.write(self.style.SUCCESS(f'Created {ico_path.relative_to(settings.BASE_DIR)} (16x16, 32x32, 48x48)'))

        self.stdout.write(self.style.SUCCESS('All icons generated successfully.'))
