import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import MenuItem, Category

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # format: "data:image/png;base64,....."
            try:
                header, imgstr = data.split(';base64,')
                ext = header.split('/')[-1] 
                id = str(uuid.uuid4())
                data = ContentFile(base64.b64decode(imgstr), name=id + '.' + ext)
            except Exception:
                pass # let super handle validation error if format is bad

        return super().to_internal_value(data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'
