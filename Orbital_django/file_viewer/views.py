from django.contrib.auth import get_user
from django.http import HttpResponse
from django.shortcuts import render
import os
import zipfile
# from unrar import rarfile
# from wand.image import Image
from models import Document, Annotation, Comment, AnnotationReply


def serve_file(request):
    document = Document.objects.get(id=int(request.GET["document_id"]))
    file = document.unique_file
    file_position = file.file_field.storage.path(file.file_field)
    content = open(file_position, 'rb')
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = "attachment; filename=%s.pdf" % document.title
    return response


def edit_doc_title(request):
    document = Document.objects.get(id=int(request.POST["document_id"]))
    new_doc_title = request.POST["new_doc_title"]
    document.title = new_doc_title
    document.save()
    return HttpResponse()


def display_file_viewer_page(request):
    if request.method == "POST":
        if request.POST["operation"] == "delete_annotation":
            annotation = Annotation.objects.get(id=int(request.POST["annotation_id"]))
            annotation.delete()
            return HttpResponse()

        elif request.POST["operation"] == "delete_annotation_reply":
            document = Document.objects.get(id=int(request.POST["document_id"]))
            reply_annotation = AnnotationReply.objects.get(id=int(request.POST["reply_id"]))
            reply_annotation.delete()
            context = {
                "document": document,
                "annotations": document.annotation_set.order_by("page_index"),
            }
            return render(request, "file_viewer/annotation_viewer_subpage.html", context)

        elif request.POST["operation"] == "delete_comment":
            document = Document.objects.get(id=int(request.POST["document_id"]))
            comment = Comment.objects.get(id=int(request.POST["comment_id"]))
            comment.delete()
            context = {
                "document": document,
                "comments": document.comment_set.order_by("-post_time"),
            }
            return render(request, "file_viewer/comment_viewer_subpage.html", context)

        elif request.POST["operation"] == "like_annotation":
            annotation = Annotation.objects.get(id=int(request.POST["annotation_id"]))
            annotation.num_like += 1
            annotation.save()
            return HttpResponse()

        elif request.POST["operation"] == "like_annotation_reply":
            annotation_reply = AnnotationReply.objects.get(id=int(request.POST["annotation_reply_id"]))
            annotation_reply.num_like += 1
            annotation_reply.save()
            return HttpResponse()

        elif request.POST["operation"] == "like_comment":
            comment = Comment.objects.get(id=int(request.POST["comment_id"]))
            comment.num_like += 1
            comment.save()
            return HttpResponse()

        elif request.POST["operation"] == "collect":
            user = get_user(request)
            document = Document.objects.get(id=int(request.POST["document_id"]))
            document.collectors.add(user)
            document.save()
            return HttpResponse()

        elif request.POST["operation"] == "uncollect":
            user = get_user(request)
            document = Document.objects.get(id=int(request.POST["document_id"]))
            document.collectors.remove(user)
            document.save()
            return HttpResponse()

        elif request.POST["operation"] == "refresh":
            document = Document.objects.get(id=int(request.POST["document_id"]))
            context = {
                "document": document,
                "comments": document.comment_set.order_by("-post_time"),
            }
            return render(request, "file_viewer/comment_viewer_subpage.html", context)

        elif request.POST["operation"] == "comment":
            document = Document.objects.get(id=int(request.POST["document_id"]))
            if request.POST["comment_content"] != "":    
                comment = Comment()
                comment.content = request.POST["comment_content"]
                comment.commenter = get_user(request)
                comment.document_this_comment_belongs = document
                if "reply_to_comment_id" in request.POST:
                    comment.reply_to_comment = Comment.objects.get(id=int(request.POST["reply_to_comment_id"]))
                comment.save()
            context = {
                "document": document,
                "comments": document.comment_set.order_by("-post_time"),
            }
            return render(request, "file_viewer/comment_viewer_subpage.html", context)

        elif request.POST["operation"] == "annotate":
            document = Document.objects.get(id=int(request.POST["document_id"]))
            annotation = Annotation()
            annotation.content = request.POST["annotation_content"]
            annotation.annotator = get_user(request)
            annotation.document_this_annotation_belongs = document
            annotation.page_index = request.POST["page_id"].split("_")[2]
            annotation.height_percent = request.POST["height_percent"]
            annotation.width_percent = request.POST["width_percent"]
            annotation.top_percent = request.POST["top_percent"]
            annotation.left_percent = request.POST["left_percent"]
            annotation.frame_color = request.POST["frame_color"]
            annotation.save()
            context = {
                "document": document,
                "annotations": document.annotation_set.order_by("page_index"),
                "new_annotation_id": annotation.id,
            }
            return render(request, "file_viewer/annotation_viewer_subpage.html", context)

        elif request.POST["operation"] == "reply_annotation":
            document = Document.objects.get(id=int(request.POST["document_id"]))
            if request.POST["annotation_reply_content"] != "":
                annotation_reply = AnnotationReply()
                annotation = Annotation.objects.get(id=int(request.POST["reply_to_annotation_id"]))    
                annotation_reply.content = request.POST["annotation_reply_content"]
                annotation_reply.replier = get_user(request)
                annotation_reply.reply_to_annotation = annotation
                if request.POST.has_key("reply_to_annotation_reply_id"):
                    annotation_reply.reply_to_annotation_reply = AnnotationReply.objects.get(id=int(request.POST["reply_to_annotation_reply_id"]))
                annotation_reply.save()
            context = {
                "document": document,
                "annotations": document.annotation_set.order_by("page_index"),
            }
            return render(request, "file_viewer/annotation_viewer_subpage.html", context)

    else:
        document = Document.objects.get(id=int(request.GET["document_id"]))
        file = document.unique_file

        file_position = file.file_field.storage.path(file.file_field)
        file_url = file.file_field.url

        file_directory_name, file_name_and_extension = os.path.split(file_position)
        file_name, extension = file_name_and_extension.split(".")
        img_folder_path = os.path.join(file_directory_name, file_name)

        pages = []

        user = get_user(request)
        collected = False
        if user.is_authenticated() and document in user.collected_document_set.all():
            collected = True

        document.num_visit += 1
        document.save()
        
        if extension == "zip":
            zip_file = zipfile.ZipFile(file_position, "r")
            zip_alphabetical_list = sorted(zip_file.namelist())

            if not os.path.isdir(img_folder_path):
                os.mkdir(img_folder_path)
                i = 0
                for page_name in zip_alphabetical_list:
                    zip_file.extract(page_name, img_folder_path)
                    os.rename(os.path.join(img_folder_path, page_name),
                              os.path.join(img_folder_path, str(i) + "." + page_name.split(".")[-1]))
                    pages.extend([os.path.dirname(file_url)[1:] + "/" + file_name + "/" + str(i) + "." + page_name.split(".")[-1]])
                    i += 1
            else:
                i = 0
                for page_name in zip_alphabetical_list:
                    pages.extend([os.path.dirname(file_url)[1:] + "/" + file_name + "/" + str(i) + "." + page_name.split(".")[-1]])
                    i += 1

        elif extension == "rar":
            rar_file = rarfile.RarFile(file_position, "r")
            rar_alphabetical_list = sorted(rar_file.namelist())

            if not os.path.isdir(img_folder_path):
                os.mkdir(img_folder_path)
                i = 0
                for page_name in rar_alphabetical_list:
                    rar_file.extract(page_name, img_folder_path)
                    os.rename(os.path.join(img_folder_path, page_name),
                              os.path.join(img_folder_path, str(i) + "." + page_name.split(".")[-1]))
                    pages.extend([os.path.dirname(file_url)[1:] + "/" + file_name + "/" + str(i) + "." + page_name.split(".")[-1]])
                    i += 1
            else:
                i = 0
                for page_name in rar_alphabetical_list:
                    pages.extend([os.path.dirname(file_url)[1:] + "/" + file_name + "/" + str(i) + "." + page_name.split(".")[-1]])
                    i += 1

        elif extension == "pdf":
            '''
            if not os.path.isdir(img_folder_path):
                os.mkdir(img_folder_path)
                document_images = Image(filename=file_position, resolution=240)
                for i, page in enumerate(document_images.sequence):
                    with Image(page) as page_image:
                        page_image.alpha_channel = False
                        page_image.save(filename = os.path.join(img_folder_path, str(i) + ".png"))
                        pages.extend([os.path.dirname(file_url)[1:] + "/" + file_name + "/" + str(i) + ".png"])
            else:
                document_images = Image(filename=file_position, resolution=180)
                for i, page in enumerate(document_images.sequence):
                    pages.extend([os.path.dirname(file_url)[1:] + "/" + file_name + "/" + str(i) + ".png"])
            '''
            context = {
                "document": document,
                "file_url": file_url[1:],
                "comments": document.comment_set.order_by("-post_time"),
                "annotations": document.annotation_set.order_by("page_index"),
                "collected": collected
            }
            return render(request, "file_viewer/pdf_file_viewer_page.html", context)

        context = {
            "numPages": len(pages),
            "document": document,
            "pages": pages,
            "comments": document.comment_set.order_by("-post_time"),
            "annotations": document.annotation_set.order_by("page_index"),
            "collected": collected,
        }
        return render(request, "file_viewer/file_viewer_page.html", context)
