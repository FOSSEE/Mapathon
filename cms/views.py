# Create your views here.
from django.forms import model_to_dict
from django.http import Http404
from django.shortcuts import render
from mapathon.config import *

from cms.models import Page, Nav, SubNav, Footer, Banner


def home(request, permalink=''):
    if permalink == '':
        permalink = 'home'
    page = Page.objects.filter(permalink=permalink, active=True)
    footer = Footer.objects.filter(active=True)
    banner = Banner.objects.filter(active=True)
    analytics_code = GOOGLE_ANALYTICS_CODE
    if page.exists():
        page = page.first()
    else:
        raise Http404("The requested page does not exists")
    nav_objs = Nav.objects.filter(active=True).order_by('position')

    navs = []

    for nav in nav_objs:
        nav_obj = model_to_dict(nav)
        nav_obj['subnavs'] = nav.subnav_set.filter(
            active=True).order_by('position')
        navs.append(nav_obj)

    return render(
        request, 'cms_base.html', {'page': page, 'navs': navs, 'footer': footer.first(), 'banner' : banner.first(), 'analytics_code' : analytics_code}
    )
