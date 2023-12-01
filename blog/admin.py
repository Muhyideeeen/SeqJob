from django.contrib import admin
from . import models
# Register your models here.




class  BlogPost_Paragraphinline(admin.TabularInline):
    model= models.BlogParagraph
    extra=1
    # fieldsets

# class  Blog_Imagesinline(admin.TabularInline):
#     model= models.BlogImages
#     extra=1
#     max_num =2


class BlogpostAdmin(admin.ModelAdmin):
    fieldsets=[(None,{'fields':['title','main_image','author','categories']})]
    inlines=[BlogPost_Paragraphinline]



admin.site.register(models.BlogPost,BlogpostAdmin)
admin.site.register(models.Categories)
admin.site.register(models.Comment)
admin.site.register(models.EmailSubscribers)


"the settings below has to do with the Admin Designs"
admin.site.site_header= "e-metric Admin"
admin.site.site_title = "e-metric Portal"
admin.site.index_title  = "Welcome to  e-metric Portal"