from django.db import models

# Create your models here.
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='img/')
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def resolution(self):
        from PIL import Image as PILImage
        if self.image and hasattr(self.image, 'path'):
            try:
                with PILImage.open(self.image.path) as img:
                    width, height = img.size
                    return [width, height]
            except Exception:
                return "Unknown"
        return "Unknown"
    
    @property
    def resolutiontxt(self):
        from PIL import Image as PILImage
        if self.image and hasattr(self.image, 'path'):
            try:
                with PILImage.open(self.image.path) as img:
                    width, height = img.size
                    return f'{width} x {height}'
            except Exception:
                return "Unknown"
        return "Unknown"
    
    def __str__(self):
        return self.image.name