from rest_framework import serializers
from jobs import models  as job_models


class FilterQuetionFormatterSerializer(serializers.ModelSerializer):
    'this clean a quetion and sends the front end a much cleaner data structure'
    title = serializers.CharField()
    fill_in_the_gap = serializers.SerializerMethodField()
    filter_quetion_option = serializers.SerializerMethodField()
    filter_quetion_multi_choice_quetion = serializers.SerializerMethodField()


    def get_filter_quetion_multi_choice_quetion(self,obj):
        return obj.filterquetionmultichoicequetion_set.all().values(
            'id','quetion','option_to_choose_from'
        )

    def get_filter_quetion_option(self,obj):
        return obj.filterquetionoption_set.all().values(
            'id','quetion','option_to_choose_from',
        )

    def get_fill_in_the_gap(self,obj):
        return obj.filterquetionfillingap_set.all().values(
            'id',
            'quetion'
        )


    def create(self, validated_data):return dict() 
    def update(self, instance, validated_data):return dict()
    
     
    class Meta:
        model = job_models.JobFilterQuetion
        fields = ['title','fill_in_the_gap','filter_quetion_option','filter_quetion_multi_choice_quetion'] 





























class TestQuetionFormatterSerializer(serializers.ModelSerializer):
    'this clean a quetion and sends the front end a much cleaner data structure'
    title = serializers.CharField()
    fill_in_the_gap = serializers.SerializerMethodField()
    filter_quetion_option = serializers.SerializerMethodField()
    filter_quetion_multi_choice_quetion = serializers.SerializerMethodField()


    def get_filter_quetion_multi_choice_quetion(self,obj):
        return obj.testquetionmultichoicequetion_set.all().values(
            'id','quetion','option_to_choose_from'
        )

    def get_filter_quetion_option(self,obj):
        return obj.testquetionoption_set.all().values(
            'id','quetion','option_to_choose_from',
        )

    def get_fill_in_the_gap(self,obj):
        return obj.testquetionfillingap_set.all().values(
            'id',
            'quetion'
        )


    def create(self, validated_data):return dict() 
    def update(self, instance, validated_data):return dict()
    
     
    class Meta:
        model = job_models.JobTestQuetion
        fields = ['title','fill_in_the_gap','filter_quetion_option','filter_quetion_multi_choice_quetion'] 





