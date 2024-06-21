
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib import messages
from .models import Recipe, Comment, UserProfile
from .forms import RecipeForm, CommentForm, UserRegistrationForm, LoginForm, UserChangeFormExtended, UserProfileForm
from django.contrib.auth.models import User


def home(request):
    recent_recipes = Recipe.objects.order_by('-creation_date')[:6]  # ultime 4 ricette inserite
    return render(request, 'recipes_sharing/home.html', {'recent_recipes': recent_recipes})

# TODO: funziona ma da migliorare, 
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user) # creo un profilo per il nuovo utente
            auth_login(request, user)
            messages.success(request, 'Registrazione avvenuta con successo.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'recipes_sharing/register.html', {'form': form}) 



def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Accesso al profilo {username} avvenuto con successo.')
                
                # Ottieni l'URL della pagina da cui l'utente proviene (se presente)
                prev_url = request.GET.get('next', 'home')
                return redirect(prev_url)
            else:
                messages.error(request, 'Username o password non validi.')
        else:
            messages.error(request, 'Username o password non validi.')
    else:
        form = AuthenticationForm()

    return render(request, 'recipes_sharing/login.html', {'form': form})

# TODO: decidere se usare redirect, o scegli tra    # crea pop up con javascript, # return render(request, 'recipes_sharing/logout.html')
@login_required
def logout(request):
    auth_logout(request)
    messages.info(request, 'Log out con successo.')
    return redirect('home')
    


def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile_user , newly_created = UserProfile.objects.get_or_create(user=user)
    
    return render(request, 'recipes_sharing/profile.html', {'profile_user': profile_user})




@login_required
def edit_profile(request, username):
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilo aggiornato con successo.')
            return redirect('view_profile', username=user.username)
    else:
        form = UserProfileForm(instance=user.userprofile)
    return render(request, 'recipes_sharing/edit_profile.html', {'form': form})



# TODO:  DA RICAMBIARE, voglio che venga mandato a template delete prima di eliminare il profilo
@login_required
def delete_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        if request.user == user:
            user.delete()
            auth_logout(request)
            messages.success(request, 'Profilo eliminato con successo.')
            return redirect('home')
        else:
            messages.error(request, 'Non sei autorizzato a eliminare questo profilo.')
            return redirect('view_profile', username=user.username)
    return render(request, 'recipes_sharing/delete_profile.html', {'profile_user': user})

def search(request):
    query = request.GET.get('q')
    difficulty = request.GET.get('difficulty')
    category = request.GET.get('category')

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(recipe_name__icontains=query)

    elif difficulty:
        recipes = recipes.filter(difficulty=difficulty)

    elif category:
        recipes = recipes.filter(categories=category)

    context = {
        'recipes': recipes
    }
    return render(request, 'recipes_sharing/search_results.html', context)



def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    comments = recipe.comments.all()
    is_favorite = recipe.liked_by.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    comment_form = CommentForm()
    return render(request, 'recipes_sharing/recipe_detail.html', {
        'recipe': recipe,
        'comments': comments,
        'is_favorite': is_favorite,
        'comment_form': comment_form
    })

@login_required(login_url='login')
def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            messages.success(request, 'Recipe created successfully.')
            return redirect('recipe_detail', recipe_id=recipe.id)
        else:
            messages.error(request, 'There was an error creating the recipe. Please check the form for errors.')
            print(form.errors)  # Log degli errori del form
    else:
        form = RecipeForm()
    return render(request, 'recipes_sharing/create_recipe.html', {'form': form})


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        messages.error(request, 'Non puoi modificare una ricetta che non hai creato!.')
        return redirect('recipe_detail', recipe_id=recipe.id)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ricetta modificata con successo.')
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
    
    return render(request, 'recipes_sharing/edit_recipe.html', {'form': form, 'recipe': recipe})

@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this recipe.')
    return redirect('home')


@login_required
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = CommentForm()
    return redirect('recipe_detail', recipe_id=recipe.id)


# TODO: DA IMPLEMENTARE 
"""
@login_required
def add_to_favourites(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if recipe.liked_by.filter(id=request.user.id).exists():
        recipe.liked_by.remove(request.user)
    else:
        recipe.liked_by.add(request.user)
    return redirect('recipe_detail', recipe_id=recipe.id)

# TODO: sce
@login_required
def liked_recipes(request):
    liked_recipes = request.user.liked_recipes.all()
    return render(request, 'recipes_sharing/liked_recipes.html', {'liked_recipes': liked_recipes})

"""

