from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.display_file_viewer_page, name="file_viewer"),

    url(r'^download', views.serve_file),

    url(r'^edit_doc_title', views.edit_doc_title),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
