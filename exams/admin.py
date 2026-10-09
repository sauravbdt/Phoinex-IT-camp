from django.contrib import admin

from .models import (
    MockTest,
    Section,
    Question,
    AnswerOption,
    AudioMaterial,
)


admin.site.register(MockTest)
admin.site.register(Section)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(AudioMaterial)