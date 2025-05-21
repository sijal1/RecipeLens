# Import necessary modules
import base64
import string
import os
from .forms import ImageUploadForm  # Correct import
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.shortcuts import redirect, get_object_or_404
from .models import UserInteraction  # we'll define this model soon
from django.utils import timezone
from django.shortcuts import render
from django.conf import settings
from .forms import ImageUploadForm
from PIL import Image
from .encoder import get_recipes
import json
from django.core.files.base import ContentFile
from django.contrib import messages

# Get the directory of the current script (views.py)
current_dir = os.path.dirname(__file__)

def get_user_uploads(request):
    """Helper function to get user uploads for the sidebar"""
    if request.user.is_authenticated:
        return UserInteraction.objects.filter(user=request.user).order_by('-timestamp')
    return None

def home_page(request):
    raw_image = None
    uploaded_image = None
    recipe_list_to_return = []

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            raw_image = form.cleaned_data['image']
            uploaded_image = base64.b64encode(raw_image.file.read()).decode('ascii')
            
            # Reset file pointer after reading
            raw_image.seek(0)
            
            # Open image for prediction
            img_for_prediction = Image.open(raw_image)
            recipe_list = get_recipes(img_for_prediction)

            # Load JSON data
            json_file_path = os.path.join(current_dir, 'static', 'main', 'indian_recipes.json')
            recipes_data = json.load(open(json_file_path))

            for i in range(len(recipe_list)):
                name = recipe_list[i]
                matching_recipes = list(filter(lambda x: x["name"] == name, recipes_data))
                if matching_recipes:
                    matching_recipe = matching_recipes[0]
                    calories = matching_recipe['calories']
                    cooking_time = matching_recipe['cooking_time']
                    ingredients = matching_recipe['ingredients']
                    directions = matching_recipe['directions']
                    list_to_append = [string.capwords(name), calories, cooking_time, ingredients, directions]
                    recipe_list_to_return.append(list_to_append)

            # Save to UserInteraction if user is authenticated
            if request.user.is_authenticated and recipe_list:
                try:
                    # Reset file pointer again
                    raw_image.seek(0)
                    
                    # Create UserInteraction instance
                    interaction = UserInteraction(
                        user=request.user,
                        predicted_recipe=recipe_list[0],  # Save the top prediction
                        timestamp=timezone.now(),
                        ingredients=matching_recipes[0]['ingredients'] if matching_recipes else ''  # Save ingredients
                    )
                    
                    # Save the image file
                    interaction.uploaded_image.save(
                        raw_image.name,
                        ContentFile(raw_image.read()),
                        save=False
                    )
                    
                    # Save the interaction
                    interaction.save()
                    messages.success(request, 'Image uploaded and saved to your profile!')
                except Exception as e:
                    messages.error(request, 'Failed to save image to profile. Please try again.')
            elif not request.user.is_authenticated and recipe_list:
                messages.info(request, 'Log in to save your uploads to your profile!')

    else:
        form = ImageUploadForm()

    context = {
        'form': form, 
        'uploaded_image': uploaded_image,
        'recipe_list_to_return': recipe_list_to_return[:4],
        'similar_recipe_list': recipe_list_to_return[4:10],
        'user_uploads': get_user_uploads(request)
    }

    return render(request, 'main/home.html', context)

@login_required
def recipe_detail(request, upload_id):
    """View for displaying a specific recipe from user's upload history"""
    upload = get_object_or_404(UserInteraction, id=upload_id, user=request.user)
    
    # Load recipe details from JSON
    json_file_path = os.path.join(current_dir, 'static', 'main', 'indian_recipes.json')
    recipes_data = json.load(open(json_file_path))
    
    recipe_details = None
    for recipe in recipes_data:
        if recipe['name'].lower() == upload.predicted_recipe.lower():
            recipe_details = recipe
            break
    
    context = {
        'upload': upload,
        'recipe': recipe_details,
        'user_uploads': get_user_uploads(request),
        'current_upload': upload
    }
    
    return render(request, 'main/recipe_detail.html', context)

@login_required
def upload_view(request):
    recipe_list_to_return = []
    uploaded_image = None

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded file
            image_file = request.FILES['image']
            
            # Create a PIL Image object for prediction
            raw_image_pil = Image.open(image_file)
            
            # Get predictions
            predicted_recipes = get_recipes(raw_image_pil)
            
            if predicted_recipes:
                top_recipe = predicted_recipes[0]
                
                # Load recipe details for ingredients
                json_file_path = os.path.join(current_dir, 'static', 'main', 'indian_recipes.json')
                recipes_data = json.load(open(json_file_path))
                ingredients = ''
                for recipe in recipes_data:
                    if recipe['name'].lower() == top_recipe.lower():
                        ingredients = recipe['ingredients']
                        break
                
                # Create UserInteraction instance
                interaction = UserInteraction(
                    user=request.user,
                    predicted_recipe=top_recipe,
                    timestamp=timezone.now(),
                    ingredients=ingredients
                )
                
                # Save the image file
                interaction.uploaded_image.save(
                    image_file.name,
                    ContentFile(image_file.read()),
                    save=False
                )
                
                # Save the interaction
                interaction.save()
                
                return redirect('recipe_detail', upload_id=interaction.id)
    else:
        form = ImageUploadForm()

    context = {
        'form': form,
        'uploaded_image': uploaded_image,
        'user_uploads': get_user_uploads(request)
    }
    
    return render(request, 'main/upload.html', context)

@login_required
def history_view(request):
    history = UserInteraction.objects.filter(user=request.user).order_by('-timestamp')
    context = {
        'history': history,
        'user_uploads': get_user_uploads(request)
    }
    return render(request, 'main/history.html', context)

@login_required
def profile_view(request):
    total_uploads = UserInteraction.objects.filter(user=request.user).count()
    last_upload = UserInteraction.objects.filter(user=request.user).order_by('-timestamp').first()
    all_uploads = UserInteraction.objects.filter(user=request.user).order_by('-timestamp')

    context = {
        'user': request.user,
        'total_uploads': total_uploads,
        'last_upload': last_upload,
        'all_uploads': all_uploads,
        'user_uploads': get_user_uploads(request)
    }
    
    return render(request, 'main/profile.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful signup
    else:
        form = SignupForm()
    
    return render(request, 'main/signup.html', {'form': form})