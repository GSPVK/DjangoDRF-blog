from rest_framework import serializers


class TruncateTextSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if hasattr(instance, 'text'):
            representation['text'] = instance.text[:100]
        return representation
