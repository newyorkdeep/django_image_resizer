from django.shortcuts import render
from .forms import UploadedForm, NumberInputForm, nameForm
from .models import UploadedImage
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image as PILImage
from django.shortcuts import redirect
import os
import io
import zipfile
from django.http import HttpResponse
from django.http import FileResponse
from django.conf import settings

# Global storage for numbers
GLOBAL_NUMBERS = {'number1': None, 'number2': None}
GLOBAL_NAME = None

def resize_all_images(request, size=None):
    from .models import UploadedImage
    if size is None:
        size = (GLOBAL_NUMBERS['number1'], GLOBAL_NUMBERS['number2'])
    items = UploadedImage.objects.all()
    for item in items:
        if item.image and hasattr(item.image, 'path'):
            try:
                #ogwidth, ogheight = item.resolution
                if (size[0]==None and size[1]!=None):
                    oldwidth, oldheight = item.resolution
                    newwidth=int(size[1]*(oldwidth/oldheight))
                    resize_image(item.image.path, (newwidth, size[1]))
                elif (size[0]!=None and size[1]==None):
                    oldwidth, oldheight = item.resolution
                    newheight=int(size[0]*(oldheight/oldwidth))
                    resize_image(item.image.path, (size[0], newheight))
                else:
                    resize_image(item.image.path, size)
            except Exception as e:
                # Optionally log the error
                pass
    return redirect('index')

def download_all_images(request):
    from .models import UploadedImage
    images = UploadedImage.objects.all()
    zip_buffer = io.BytesIO()
    # Use compression and stream the response to avoid partial/corrupt archives
    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for img in images:
            try:
                if img.image and hasattr(img.image, 'path') and os.path.isfile(img.image.path):
                    arcname = os.path.basename(img.image.path)
                    zip_file.write(img.image.path, arcname=arcname)
            except Exception:
                # Skip files that cannot be read to avoid breaking the whole archive
                continue
    zip_buffer.seek(0)
    return FileResponse(zip_buffer, as_attachment=True, filename="manipulated_images.zip")

def download_image(request, image_id):
    from .models import UploadedImage
    img = UploadedImage.objects.get(id=image_id)
    if img.image and hasattr(img.image, 'path') and os.path.isfile(img.image.path):
        response = FileResponse(open(img.image.path, 'rb'), as_attachment=True, filename=os.path.basename(img.image.path))
        return response
    else:
        # Handle file not found
        return HttpResponse('File not found', status=404)

def resize_image(image_path, size):
    img = PILImage.open(image_path)
    img = img.resize(size, PILImage.LANCZOS)  # Use LANCZOS filter for better quality
    img.save(image_path)

# Create your views here.
def index(request):
    global GLOBAL_NUMBERS
    global GLOBAL_NAME
    def get_file_size(path):
        try:
            size = os.path.getsize(path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except Exception:
            return "Unknown size"

    if request.method == 'POST' and request.FILES:
        images = request.FILES.getlist('image')
        for img in images:
            fs = FileSystemStorage()
            filename = fs.save(img.name, img)
            uploaded_file_url = fs.url(filename)
            #resize_image(os.path.join(fs.location, filename), (800, 600))
            # Save to model
            UploadedImage.objects.create(image=filename)
        # Use Post/Redirect/Get to prevent duplicate uploads when the page is refreshed
        return redirect('index')
    items = UploadedImage.objects.all()
    for item in items:
        if item.image and hasattr(item.image, 'path') and os.path.isfile(item.image.path):
            item.file_size = get_file_size(item.image.path)
        else:
            item.file_size = "Unknown size"
    return render(request, 'index.html', {'items': items, 'numbers': GLOBAL_NUMBERS, 'group_name': GLOBAL_NAME})

def number_input(request):
    global GLOBAL_NUMBERS
    if request.method == 'POST':
        form = NumberInputForm(request.POST)
        if form.is_valid():
            GLOBAL_NUMBERS['number1'] = form.cleaned_data['number1']
            GLOBAL_NUMBERS['number2'] = form.cleaned_data['number2']
            #return render(request, 'index.html', {'numbers': GLOBAL_NUMBERS})
            return resize_all_images(request, (GLOBAL_NUMBERS['number1'], GLOBAL_NUMBERS['number2']))
    else:
        form = NumberInputForm()
    return render(request, 'number_input.html', {'form': form, 'numbers': GLOBAL_NUMBERS})

def group_name(request):
    global GLOBAL_NAME
    if request.method == 'POST':
        form = nameForm(request.POST)
        if form.is_valid():
            GLOBAL_NAME = form.cleaned_data['nameGiven']
            # Rename all images to include the group name
            from .models import UploadedImage
            items = UploadedImage.objects.all()
            for idx, item in enumerate(items, start=1):
                if item.image and hasattr(item.image, 'path') and os.path.isfile(item.image.path):
                    old_path = item.image.path
                    dir_name = os.path.dirname(old_path)
                    ext = os.path.splitext(old_path)[1]
                    new_filename = f"{GLOBAL_NAME}_{idx}{ext}"
                    new_path = os.path.join(dir_name, new_filename)
                    # Avoid overwriting files
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        # Update model
                        from django.conf import settings
                        rel_path = os.path.relpath(new_path, settings.MEDIA_ROOT)
                        item.image.name = rel_path.replace('\\', '/')
                        item.save()
            return redirect(index)
    else:
        form = nameForm()
    return render(request, 'group_name.html', {'form': form, 'name': GLOBAL_NAME})

def convert_all_images_to_jpg(request):
    from .models import UploadedImage
    items = UploadedImage.objects.all()
    for item in items:
        if item.image and hasattr(item.image, 'path'):
            img = PILImage.open(item.image.path)
            rgb_img = img.convert('RGB')  # Ensure no alpha channel for JPEG
            new_path = os.path.splitext(item.image.path)[0] + '.jpg'
            rgb_img.save(new_path, 'JPEG')
            # Optionally, update the model to point to the new file
            item.image.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
            item.save()
            # Optionally, remove the old file if different
            if new_path != item.image.path and os.path.exists(item.image.path):
                os.remove(item.image.path)
    return redirect('index')

def convert_all_images_to_png(request):
    from .models import UploadedImage
    items = UploadedImage.objects.all()
    for item in items:
        if item.image and hasattr(item.image, 'path'):
            img = PILImage.open(item.image.path)
            rgb_img = img.convert('RGB')  # Ensure no alpha channel for JPEG
            new_path = os.path.splitext(item.image.path)[0] + '.png'
            rgb_img.save(new_path, 'PNG')
            # Optionally, update the model to point to the new file
            item.image.name = os.path.relpath(new_path, settings.MEDIA_ROOT)
            item.save()
            # Optionally, remove the old file if different
            if new_path != item.image.path and os.path.exists(item.image.path):
                os.remove(item.image.path)
    return redirect('index')

def nuke(request):
    items=UploadedImage.objects.all()
    for item in items:
        # Delete the file from storage
        if item.image and hasattr(item.image, 'path'):
            try:
                if os.path.isfile(item.image.path):
                    os.remove(item.image.path)
            except Exception as e:
                # Optionally log the error
                pass
        # Delete the database record
        item.delete()
    return redirect('index')