from .models import Category

def categorias(request):
    categorias = Category.objects.all()
    categorias_ordenadas = sorted(categorias, key=lambda x: x.categoryName)
    return {'categorias': categorias_ordenadas}