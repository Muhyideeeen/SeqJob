import django_filters
from . import models



class BlogFilter(django_filters.FilterSet):


    class  Meta:
        model = models.BlogPost
        fields = ['categories__names','title']