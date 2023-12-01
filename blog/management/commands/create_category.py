"""
create super_user
"""
from ... import models 
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
        Django command to create super_user
    """


    def handle(self, *args, **options):

        if models.Categories.objects.count() != 0:
            self.stdout.write(f'Categories Created')


        else:
            'we createe each categoryu'
            cats = [
                   'Leave Management','Payroll_Management',' Human Resource Management','KPI Analytics',
                   'Performance Management','Email Marketing'
                ]
            for cat in cats:
                models.Categories.objects.create(
                    names= cat,
                    slug=cat
                )
            self.stdout.write(f'Created Categories Successfull')

            


    # def  add_arguments(self, parser) -> None:
    #     parser.add_argument('email',type=str,help='enter the admin email')