from django.db import models
from django.contrib.auth.models import User



class Recipe(models.Model):
    recipe_name = models.CharField(max_length=30)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    description = models.CharField(max_length=100)
    ingredients = models.TextField()
    servings = models.PositiveIntegerField(default=2)

    preparation_instructions = models.TextField()
    cooking_instructions = models.TextField()

    cooking_time = models.PositiveIntegerField()  # tempo di preparazione in minuti
    
    creation_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='recipe_images', blank=True, null=True) #TODO: aggiungere un'immagine di default
    
    DIFFICULTIES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES)
    
    liked_by = models.ManyToManyField(User, related_name='liked_recipes', blank=True, null=True)
    
    CATEGORIES = [
        ('A', 'Antipasto'),
        ('P', 'Primo Piatto'),
        ('S', 'Secondo Piatto'),
        ('C', 'Contorno'),
        ('D', 'Dessert'),
    ]
    categories = models.CharField(max_length=1, null=True, blank=True, choices=CATEGORIES)
    
    calories = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.recipe_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    bio = models.CharField(max_length=50,null=True, blank=True) 
    profile_image = models.ImageField(upload_to='media/profile_images', default='media/profile_images/default_profile.png') #TODO: aggiungere un'immagine di default

    
    def __str__(self):
        return self.user.username

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.recipe.recipe_name}'
