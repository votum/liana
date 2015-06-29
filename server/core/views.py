# -*- coding: utf-8 -*-
import json
from articles.models import Article

from django.shortcuts import render


def home(request):
    return render(request, 'index.html', {})
