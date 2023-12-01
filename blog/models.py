from django.db import models
from cloudinary_storage.storage import RawMediaCloudinaryStorage
# Create your models here.

class Categories(models.Model):

    class NameChoices(models.TextChoices):
        Email_Marketing ='Email Marketing'
        Performance_Management='Performance Management'
        KPI_Analytics='KPI Analytics'
        Human_Resource_Management=' Human Resource Management'
        Payroll_Management='Payroll_Management'
        Leave_Management='Leave Management'
    names = models.CharField(max_length=50,choices=NameChoices.choices)
    slug = models.SlugField(default="")
    
    def __str__(self):
        return self.names



class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    main_image= models.ImageField(upload_to='blogpost/main_image/%m/%d/')
    author = models.CharField(max_length=100)
    categories = models.ForeignKey(Categories,on_delete=models.CASCADE,blank=True,default='')
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def get_paragraph_intro(self):
        'this method get the post intro and extract 100 charachters'
        #input_text is where the text lives check BlogParagraph for more details
        try:
            return f'{self.blogparagraph_set.all()[0].input_text[0:100]}.....'
        except:
            return ''


class Comment(models.Model):
    name = models.CharField(max_length=200)
    comment_text = models.TextField()
    post = models.ForeignKey(BlogPost,on_delete=models.CASCADE,null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f'Comment By {self.name}'

class BlogParagraph(models.Model):
    "one BlogPost has many BlogParagraph"
    blogpost = models.ForeignKey(BlogPost,on_delete=models.CASCADE)
    input_text = models.TextField()
    image = models.ImageField(upload_to='blogParagraphImage/%m/%d/',blank=True)



class EmailSubscribers(models.Model):
    email = models.EmailField()

    def __str__(self): return f'{self.email} Subscribed'  