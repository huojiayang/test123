import hashlib
import re
import time
import os
import pandas as pd
import ast
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import render, redirect,HttpResponse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import email.mime.text
import smtplib
import requests as rqs
import html
import time
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
#  加密 md5进行加密 -->> 不可逆的  123 --> md5 -->abc
#  使用md5进行加密 ： 固定的密码生成固定的加密内容 123 --->> abc
# from BookManagementSystem.librarian.models import Author
from librarian import models


# 定义一个 加密函数pwd_encrypt，对用户的密码进行md5加密
def pwd_encrypt(password):
    md5 = hashlib.md5()  # 获取md5对象
    md5.update(password.encode())  # 进行更新注意需要使用 字符串的二进制格式
    result = md5.hexdigest()  # 获取加密后的内容
    return result


# 注册视图
def register(request):
    # （1）如果是POST请求，我们要完成以下功能：
    if request.method == 'POST':
        # 1. 获取表单提交过来的内容
        username = request.POST.get('username')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        # 2.对密码进行加密
        password = pwd_encrypt(password)
        # 3. 保存到数据库
        models.Librarian.objects.create(name=username, nickname=nickname, password=password, achievement='-', status='-')
        book = models.Books.objects.all()
        us_bo = models.Librarian.objects.filter(name=username)
        for i in us_bo:
            for j in book:
                models.UserBook.objects.create(user_id=i.id, book_id=j.id, achievement='-', status='-')
        # 4. 重定向到登录界面
        return redirect('/librarian/login/')

    # （2）如果是GET请求，只需要返回注册页面即可。
    return render(request, 'register.html')


# 登录
def login(request):
    error_msg = ''
    #5（1）如果是POST请求，我们需要完成以下功能：
    if request.method == 'POST':
        # 1.获取表单提交过来的内容
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        print("username---------------->", username)
        # 2. 对输入的密码进行加密
        pwd = pwd_encrypt(pwd)
        # 3.数据库查询
        # select * from librarian where name=username and password =pwd
        ret = models.Librarian.objects.filter(name=username, password=pwd)
        # print(ret) # 如果用户不存在 返回空 QuerySet对象,转换成False
        if ret:
            # 有此用户 -->> 跳转到首页
            # 登录成功后，将用户名和昵称保存到session 中，
            request.session['username'] = username
            librarian_obj = ret.last()  # 获取librarian对象
            nickname = librarian_obj.nickname
            request.session['nickname'] = nickname
            # 将用户的id 保存到session中
            request.session['id'] = librarian_obj.id
            return redirect('/')
        else:
            # 没有此用户-->> 用户名或者密码错误
            error_msg = 'Username或Password错误请重新输入'
    return render(request, 'login.html', {'error_msg': error_msg})


# 退出(登出)
def logout(request):
    # 1. 将session中的用户名、昵称删除
    request.session.flush()
    # 2. 重定向到 登录界面
    return redirect('/librarian/login/')


# 装饰器
def librarian_decorator(func):
    def inner(request, *args, **kwargs):
        username = request.session.get('username')
        nickname = request.session.get('nickname')
        if username and nickname:
            """用户登录过"""
            return func(request, *args, **kwargs)
        else:
            """用户没有登录，重定向到登录页面"""
            return redirect('/librarian/login/')

    return inner


# publisher操作
@librarian_decorator
def add_publisher(request):
    if request.method == 'POST':
        # 1.获取内容
        publisher_name = request.POST.get('publisher_name')
        publisher_address = request.POST.get('publisher_address')
        Maintainer = request.POST.get('Maintainer')
        update_date = request.POST.get('update_date')
        file = request.POST.get('file')
        video = request.POST.get('video')
        site = request.POST.get('site')
        # 2.保存数据库
        models.Publisher.objects.create(name=publisher_name, address=publisher_address,Maintainer=Maintainer,update_date=update_date,file=file,video=video,site=site)
        # 3.重定向到类型列表
        return redirect('/librarian/publisher_list/')
    return render(request, 'publisher_add.html')


# publish list
@librarian_decorator
def publisher_list(request, page=1):
    if request.method == "GET":
        publisher_obj_list = models.Publisher.objects.all()  # 获取出版社所有数据
        paginator = Paginator(publisher_obj_list, 10)  # 实例化分页对象，每页显示10条数据
        total_page_num = paginator.num_pages  # 总页码
        current_page_num = page if page else request.GET.get("page", 1)  # 当前页，默认显示第一页
        publisher_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
        page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
        # 当前页
        if total_page_num > 10:  # 当总页码大于10时
            if current_page_num < 9:  # 当前页小于10时
                page_range = range(1, 11)
            elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
                page_range = range(current_page_num - 2, total_page_num + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 8)
        else:
            page_range = page_range
        return render(request, "publisher_list.html", locals())


@librarian_decorator
def update_publisher(request):
    """update publisher"""
    if request.method == "GET":
        id = request.GET.get("id")
        publisher = models.Publisher.objects.get(id=id)
        return render(request, "publisher_update.html", locals())
    else:
        id = request.POST.get("id")
        names = request.POST.get("name")
        address = request.POST.get("address")
        Maintainer = request.POST.get('Maintainer')
        update_date = request.POST.get('update_date')
        file = request.POST.get('file')
        video = request.POST.get('video')
        site = request.POST.get('site')
        models.Publisher.objects.filter(id=id).update(name=names, address=address,Maintainer=Maintainer,update_date=update_date,file=file,video=video,site=site)
        return redirect("/librarian/publisher_list/")


def delete_publisher(request):
    """删除publisher"""
    # 获取publisher_list.html页面传过来的id
    id = request.GET.get("id")
    #根据id，从数据库中获取出版社对象
    publisher = models.Publisher.objects.get(id=id)
    # 从数据库中删除该出版社对象
    publisher.delete()
    return redirect("/librarian/publisher_list/")




@librarian_decorator
def add_book(request):
    """添加品控天条"""
    if request.method == "GET":
        # 从数据库中查询所有出版社对象
        publisher_list = models.Publisher.objects.all()
        # 将页面转调到添加图书的页面
        return render(request, "book_add.html", locals())
    elif request.method == "POST":
        from faker import Faker
        f = Faker(locale="zh_CN")  # 初始化Faker对象
        book_num = f.msisdn()  # 图书编码
        # 获取book_add.html表单提交过来的数据
        book_name = request.POST.get("book_name")
        author = request.POST.get("author")
        book_type = request.POST.get("book_type")
        book_price = request.POST.get("book_price")
        book_inventory = request.POST.get("book_inventory")
        book_score = request.POST.get("book_score")
        book_description = request.POST.get("book_description")
        book_sales = request.POST.get("book_sales")
        comment_nums = request.POST.get("comment_nums")

        # 将表单获取到的数据保存到数据库中
        book_obj = models.Books.objects.create(
            book_num=book_num,
            book_name=book_name,
            author=author,
            book_type=book_type,
            book_price=book_price,
            book_inventory=book_inventory,
            book_score=book_score,
            book_description=book_description,
            book_sales=book_sales,
            comment_nums=comment_nums,
            achievement='-',
            status='-'
        )
        userdata = models.Librarian.objects.all()
        for i in userdata:
            models.UserBook.objects.create(
                user_id=i.id,
                book_id=book_obj.id,
                achievement='-',
                status='-'
            )
        # 保存图片
        # 注意上传字段使用 FILES.getlist() 来获取 多张图片
        userfiles = request.FILES.getlist('book_image')  # 图书缩略图
        # 循环遍历读取每一张图片保存到images下  -->>枚举 （0,'<InMemoryUploadedFile: 3.jpg (image/jpeg)>'）
        for index, image_obj in enumerate(userfiles):
            name = image_obj.name.rsplit('.', 1)[1]  # 图书格式
            path = 'librarian/static/images/books/{}_{}.{}'.format(book_obj.id, index, name)
            # 保存图片
            with open(path, mode='wb') as f:
                for content in image_obj.chunks():
                    f.write(content)

            # 2.保存图片路径到数据库
            obj_image = models.Image()
            path1 = 'images/books/{}_{}.{}'.format(book_obj.id, index, name)
            email_path_img = 'images/books/{}_{}.{}'.format(book_obj.id, index, name)
            obj_image.img_address = path1
            obj_image.img_label = image_obj.name  # 图片原名称
            obj_image.books = book_obj  # 设置图片和商品的关系
            obj_image.save()

        book_video = request.FILES.getlist('book_video')
        for index, video_obj in enumerate(book_video):
            name = video_obj.name.rsplit('.', 1)[1]
            if not os.path.exists('librarian/static/images/video'):
                os.makedirs('librarian/static/images/video')
            path = 'librarian/static/images/video/{}_{}.{}'.format(book_obj.id, index, name)
            with open(path, mode='wb') as f:
                for content in video_obj.chunks():
                    f.write(content)

            obj_video = models.Video()
            path1 = 'images/video/{}_{}.{}'.format(book_obj.id, index, name)
            obj_video.video_address = path1
            obj_video.video_label = video_obj.name
            obj_video.books = book_obj
            obj_video.save()

        # 添加考试题
        book_test = request.FILES.getlist('book_test')
        for index, test_obj in enumerate(book_test):
            name = test_obj.name.rsplit('.', 1)[1]
            if not os.path.exists('librarian/static/images/test'):
                os.makedirs('librarian/static/images/test')
            path = 'librarian/static/images/test/{}_{}.{}'.format(book_obj.id, index, name)
            with open(path, mode='wb') as f:
                for content in test_obj.chunks():
                    f.write(content)
            obj_video = models.Test()
            path1 = 'images/test/{}_{}.{}'.format(book_obj.id, index, name)
            obj_video.test_address = path1
            obj_video.test_label = test_obj.name
            obj_video.books = book_obj
            obj_video.save()

        book_file = request.FILES.getlist('book_file')
        for index, file_obj in enumerate(book_file):
            name = file_obj.name.rsplit('.', 1)[1]
            if not os.path.exists('librarian/static/images/file'):
                os.makedirs('librarian/static/images/file')
            path = 'librarian/static/images/file/{}_{}.{}'.format(book_obj.id, index, name)
            with open(path, mode='wb') as f:
                for content in file_obj.chunks():
                    f.write(content)
            obj_file = models.File()
            path1 = 'images/file/{}_{}.{}'.format(book_obj.id, index, name)
            obj_file.file_address = path1
            obj_file.file_label = file_obj.name
            obj_file.books = book_obj
            obj_file.save()

        update_name = models.Librarian.objects.get(id=request.session['id'])
        print(update_name.name,'FFFFFFFFFFFFFFFFFFFF')
        sends = ['836767534@qq.com', '244606552@qq.com', 'superyangbb@163.com']
        html = '<html><body><h1>{0}上传了关于{1}课程，去学习吧</h1><table frame="box", boder="2", rules="all"><tr><th>NAME</th><th>DESCRIBE</th><th>img</th></tr><td>{1}</td><td>{2}</td><td><img src="cid:bugimg"></td></table></body></html>'.format(
            update_name.name, book_name, book_type)
        msg=MIMEMultipart('related')

        msgTxt = email.mime.text.MIMEText(html, 'html', 'utf-8')
        msg.attach(msgTxt)
        msg['Subject'] = '图书管理系统自动提示消息 勿回复 谢谢'
        msg['From'] ='411270810@qq.com'
        msg['To'] =",".join(sends)
        print(os.path.join('./static',email_path_img),'========')
        # file = open(os.path.join('BookSystem/librarian/static',email_path_img),'rb')
        with open(os.path.join('./static',email_path_img),'rb')as f:
            imgdata = f.read()
        bugimg = MIMEImage(imgdata)
        bugimg.add_header('Content-ID', 'bugimg')  # 替换html中标识为bugimg的标签
        msg.attach(bugimg)
        # ssl 协议
        s = smtplib.SMTP_SSL('smtp.qq.com', str(465), timeout=2)
        # 明文
        # s = smtplib.SMTP('smtp.qq.com', str(465), timeout=2)
        # tls 协议
        # s = smtplib.SMTP('smtp.qq.com', str(465), timeout=2)
        # s.starttls()
        s.login('411270810@qq.com', 'dgbkjgyzljgnbhee')
        s.sendmail('411270810@qq.com', sends, msg.as_string())
        s.quit()

        # 3.重定向到商品列表
        return redirect("/librarian/book_list")




def book_list(request, page=1):
    """品控天条列表"""
    if request.method == "GET":
        print(request.session['id'],'#######aAAA',request.session['username'])
        book_list = []

        book_obj_list = models.Books.objects.all()
        for i in book_obj_list:
            data = {'achievement':'-', 'status': '-'}
            data['id'] = i.id
            data['book_name'] = i.book_name
            data['author'] = i.author
            data['book_type'] = i.book_name
            data['book_price'] = i.book_name
            data['book_score'] = i.book_name
            user_obj = models.UserBook.objects.filter(user_id=request.session['id'], book_id=i.id)
            for j in user_obj:
                data['achievement'] = j.achievement
                data['status'] = j.status
            img = models.Image.objects.filter(books_id=i.id)
            for q in img:
                data['img_path'] = q.img_address.name
            video = models.Video.objects.filter(books_id=i.id)
            for v in video:
                data['video_path'] = v.video_address
            file = models.File.objects.filter(books_id=i.id)
            for f in file:
                data['file_path'] = f.file_address
                data['file_name'] = f.file_label
            book_list.append(data)
        print(book_list,'北京!!!!')

        paginator = Paginator(book_obj_list, 10)  # 实例化分页对象，每页显示10条数据
        total_page_num = paginator.num_pages  # 总页码
        current_page_num = page  # 当前页，默认显示第一页
        book_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
        page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
        # 确定页码范围
        if total_page_num > 10:  # 当总页码大于10时
            if current_page_num < 9:  # 当前页小于10时
                page_range = range(1, 11)
            elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
                page_range = range(current_page_num - 2, total_page_num + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 8)
        return render(request, "book_list.html", locals())



@librarian_decorator
def update_book(request):
    """修改品控天条"""
    if request.method == "GET":
        # 1.获取book_list.html页面传过来的id
        id = request.GET.get("id")
        # 2.从数据库中获取要修改的图书对象
        book_obj = models.Books.objects.get(id=id)
        # 3. 获取所有的出版社数据

        return render(request, "book_update.html", locals())

    else:
        # 获取book_update.html表单提交过来的数据
        id = request.POST.get("id")
        book_name = request.POST.get("book_name")
        book_type = request.POST.get("book_type")
        author = request.POST.get("author")
        book_price = request.POST.get("book_price")
        book_inventory = request.POST.get("book_inventory")
        book_score = request.POST.get("book_score")
        book_description = request.POST.get("book_description")
        book_sales = request.POST.get("book_sales")
        comment_nums = request.POST.get("comment_nums")

        # 将表单提交过来的数据保存到数据库
        book_obj = models.Books.objects.filter(id=id).update(
            book_name=book_name,
            book_type=book_type,
            author=author,
            book_price=book_price,
            book_inventory=book_inventory,
            book_score=book_score,
            book_description=book_description,
            book_sales=book_sales,
            comment_nums=comment_nums,
            achievement='-',
            status='-'
        )
        print(request.FILES)
        # 保存图片
        # 注意上传字段使用 FILES.getlist() 来获取 多张图片
        userfiles = request.FILES.getlist('book_image')  # 图书缩略图
        for index, image_obj in enumerate(userfiles):
            name = image_obj.name.rsplit('.', 1)[1]  # 图书格式
            path = 'librarian/static/images/books/{}_{}.{}'.format(id, index, name)
            # 保存图片
            with open(path, mode='wb') as f:
                for content in image_obj.chunks():
                    f.write(content)
            path1 = 'images/books/{}_{}.{}'.format(id, index, name)

            models.Image.objects.filter(books_id=id).update(
                img_label=userfiles[0].name,
                img_address=path1
            )

        # 保存视频
        book_video = request.FILES.getlist('book_video')
        for index, video_obj in enumerate(book_video):
            name = video_obj.name.rsplit('.', 1)[1]
            if not os.path.exists('librarian/static/images/video'):
                os.makedirs('librarian/static/images/video')
            path = 'librarian/static/images/video/{}_{}.{}'.format(id, index, name)
            with open(path, mode='wb') as f:
                for content in video_obj.chunks():
                    f.write(content)
        # 保存视频路径到数据库
            path1 = 'images/video/{}_{}.{}'.format(id, index, name)
            models.Video.objects.filter(books_id=id).update(
                video_label=book_video[0].name,
                video_address=path1
            )

        # 添加考试题
        book_test = request.FILES.getlist('book_test')
        for index, test_obj in enumerate(book_test):
            name = test_obj.name.rsplit('.', 1)[1]
            if not os.path.exists('librarian/static/images/test'):
                os.makedirs('librarian/static/images/test')
            path = 'librarian/static/images/test/{}_{}.{}'.format(id, index, name)
            with open(path, mode='wb') as f:
                for content in test_obj.chunks():
                    f.write(content)
            path1 = 'images/test/{}_{}.{}'.format(id, index, name)
            models.Test.objects.filter(books_id=id).update(
                test_label=book_test[0].name,
                test_address=path1
            )
        book_file = request.FILES.getlist('book_file')
        for index, file_obj in enumerate(book_file):
            name = file_obj.name.rsplit('.', 1)[1]
            if not os.path.exists('librarian/static/images/file'):
                os.makedirs('librarian/static/images/file')
            path = 'librarian/static/images/file/{}_{}.{}'.format(id, index, name)
            with open(path, mode='wb') as f:
                for content in file_obj.chunks():
                    f.write(content)
            path1 = 'images/file/{}_{}.{}'.format(id, index, name)
            models.File.objects.filter(books_id=id).update(
                file_label=book_file[0].name,
                file_address=path1
            )
        # 重定向到图书列表页面
        return redirect("/librarian/book_list")


def delete_book(request):
    """删除品控天条"""
    #  1. 获取book_list.html传来的id
    id = request.GET.get("id")
    # 2. 根据id，从数据库中获取出版社对象并且删除
    models.Books.objects.get(id=id).delete()
    models.UserBook.objects.filter(book_id=id,user_id=request.session['id']).delete()
    # 3.  删除数据后返回到出版社列表页面。
    return redirect("librarian:book_list")


def test_data(request):
    if request.method == 'GET':
        id = request.GET.get("id")
        print(id,2222222222)
        test_row = models.Test.objects.filter(books_id=id)
        list_dic = []
        for i in test_row:
            df = pd.read_excel(os.path.join('librarian/static',i.test_address), engine='openpyxl')
            head_list = list(df.columns)  # 获取数据的列名称
            for i in df.values:
                a_line = dict(zip(head_list, i))  # 将每行数据和列名称转换成字典
                a_line['id'] = len(list_dic)
                a_line['num'] = len(list_dic) + 1
                a_line['book_id'] = id
                list_dic.append(a_line)  # 将字典追加到列表上
            #
        return render(request, "test.html", locals())

def test_data_update(request):
    if request.method == 'POST':
        print('#'*100)
        book_id = request.POST.get('book_id')
        result = request.POST.get('resolt')
        results = 0
        status = '通过'
        test_row = models.Test.objects.filter(books_id=book_id)
        for i in test_row:
            df = pd.read_excel(os.path.join('librarian/static',i.test_address), engine='openpyxl')
            result_data = df['result'].to_list()
            for index, value in enumerate(result_data):
                if str(value) == str(ast.literal_eval(result)[index]):
                    results += 10
                else:
                    continue
        print(results)
        if results < 70:
            status = '未通过请重新学习'
        models.UserBook.objects.filter(user_id=request.session['id'], book_id=book_id).update(
            achievement=results,
            status=status,
            answer=result_data,
            user_answer=result
        )

    response = HttpResponse()
    response.content = ''
    response.content_type = 'application / json;/text/html;charset=UTF-8'
    response.status_code = 200
    return HttpResponse(response)


def test_validation(request):
    if request.method == 'GET':
        book_id = request.GET.get("book_id")
        answer = None
        row = models.UserBook.objects.filter(user_id=request.session['id'], book_id=book_id)
        for i in row:
            user_answer = i.user_answer
            achievement = i.achievement
        test_row = models.Test.objects.filter(books_id=book_id)
        for j in test_row:
            list_dic = []
            df = pd.read_excel(os.path.join('librarian/static', j.test_address), engine='openpyxl')
        head_list = list(df.columns)
        for i in df.values:
            a_line = dict(zip(head_list, i))  
            a_line['id'] = len(list_dic)
            a_line['num'] = len(list_dic) + 1
            a_line['book_id'] = id
            list_dic.append(a_line)
        for i in range(len(list_dic)):
            if str(ast.literal_eval(user_answer)[i]) == str(list_dic[i]['result']):
                list_dic[i]['status'] = True
            else:
                list_dic[i]['status'] = False
            if str(list_dic[i]['A']) == str(ast.literal_eval(user_answer)[i]):
                list_dic[i]['user_letter'] = 'A'
            elif str(list_dic[i]['B']) == str(ast.literal_eval(user_answer)[i]):
                list_dic[i]['user_letter'] = 'B'
            elif str(list_dic[i]['C']) == str(ast.literal_eval(user_answer)[i]):
                list_dic[i]['user_letter'] = 'C'
            elif str(list_dic[i]['D']) == str(ast.literal_eval(user_answer)[i]):
                list_dic[i]['user_letter'] = 'D'
        for i in list_dic:
            if i['A'] == i['result']:
                i['letter'] = 'A'
            elif i['B'] == i['result']:
                i['letter'] = 'B'
            elif i['C'] == i['result']:
                i['letter'] = 'C'
            elif i['D'] == i['result']:
                i['letter'] = 'D'
        list_dic_ = list_dic
        return render(request, "test_result_show.html", locals())
        









@librarian_decorator
def add_author(request):
    """加入user作者"""
    if request.method == "GET":
        # 1. 获取所有图书
        book_obj_list = models.Books.objects.all()
        # 2. 返回作者添加页面
        return render(request, "author_add.html", locals())

    elif request.method == "POST":
        name = request.POST.get("name")
        books_id = request.POST.get("books")
        # 将作者添加到数据库
        author_obj = models.Author.objects.create(name=name)
        author_obj.books.set(books_id)  # 设置关系
        return redirect("/librarian/author_list")


# 作者列表
@librarian_decorator
def author_list(request, page=1):
    """user作者表"""
    # 第一种方法：
    # author_obj_list = models.Author.objects.all()
    # bk = Paginator(author_obj_list, 5)
    # num = bk.num_pages
    # page = bk.page(page)

    # 第二种方法
    author_obj_list = models.Author.objects.all()
    res_lst = []  # 用来存放图书和作者信息,传值的前端
    for author_obj in author_obj_list:
        book_obj_list = author_obj.books.all()  # 获取每个作者的所有图书
        print(book_obj_list)
        res_dic = {
            "author_obj": author_obj,  # 作者对象
            "book_obj_list": book_obj_list,  # 每个作者的图书列表
        }
        res_lst.append(res_dic)
    paginator = Paginator(res_lst, 10)  # 实例化分页对象，每页显示10条数据
    total_page_num = paginator.num_pages  # 总页码
    current_page_num = page  # 当前页，默认显示第一页
    author_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
    page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
    # 页码范围
    if total_page_num > 10:  # 当总页码大于10时
        if current_page_num < 9:  # 当前页小于10时
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)

    return render(request, "author_list.html", locals())


@librarian_decorator
def update_author(request):
    if request.method == "GET":
        id = request.GET.get("id")
        author_obj = models.Author.objects.get(id=id)
        # 查询所有图书
        book_obj_list = models.Books.objects.all()
        return render(request, "author_update.html", locals())

    else:
        # 保存修改的数据
        id = request.POST.get("id")
        names = request.POST.get("name")
        books_id = request.POST.get("books")
        # 根据id，查找对象并修改
        author_obj = models.Author.objects.filter(id=id).first()
        # print(author_obj)
        author_obj.name = names
        author_obj.books.set(books_id)
        author_obj.save()
        # 重定向到作者列表
        return redirect("/librarian/author_list")


def delete_author(request):
    id = request.GET.get("id")
    author = models.Author.objects.get(id=id)
    author.delete()
    return redirect("librarian:author_list")


# User 用户注册
@librarian_decorator
def add_user(request):
    if request.method == "GET":
        # 查询所有的书
        book_obj_list = models.Books.objects.all()
        return render(request, "user_add.html", locals())

    else:
        name = request.POST.get("name")
        nickname = request.POST.get("nickname")

        phone = request.POST.get("phone")
        books = request.POST.get("books")
        password = request.POST.get("password")
        # 对密码进行加密
        password = pwd_encrypt(password)
        user_obj = models.User.objects.create(
            name=name,
            nickname=nickname,
            password=password,
            phone=phone,
        )
        user_obj.books.set(books)
        return redirect("/librarian/user_list")

@librarian_decorator
def user_list(request, page=1):
    user_obj_list = models.User.objects.all()
    paginator = Paginator(user_obj_list, 10)  # 实例化分页对象，每页显示10条数据
    total_page_num = paginator.num_pages  # 总页码
    current_page_num = page  # 当前页，默认显示第一页
    user_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
    page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
    # 当前页
    if total_page_num > 10:  # 当总页码大于10时
        if current_page_num < 9:  # 当前页小于10时
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)

    return render(request, "user_list.html", locals())

@librarian_decorator
def update_user(request):
    if request.method == "GET":
        id = request.GET.get("id")
        user_obj = models.User.objects.get(id=id)
        book_obj_list = models.Books.objects.all()
        return render(request, "user_update.html", locals())
    else:
        id = request.POST.get("id")
        phone = request.POST.get("phone")
        nick_name = request.POST.get("nickname")
        password = request.POST.get("password")
        books = request.POST.get("books")
        # .对密码进行加密
        password = pwd_encrypt(password)
        # 根据id，查找对象并修改
        user_obj = models.User.objects.filter(id=id).first()
        user_obj.password = password
        user_obj.nick_name = nick_name
        user_obj.phone = phone
        user_obj.save()
        user_obj.books.set(books)  # 设置用户与时间的关系
        author_obj = models.User.objects.filter(id=id).update(password=password, nickname=nick_name, phone=phone)

        return redirect("/librarian/user_list")

def delete_user(request):
    id = request.GET.get("id")
    models.User.objects.get(id=id).delete()
    return redirect("librarian:user_list")

@librarian_decorator
def search(request):
    # 要前端中获取用户输入的关键字
    search_keywords = request.POST.get("search_keywords", "")
    # print(search_keywords)
    if search_keywords:
        book_list = []
        books_obj_list = models.Books.objects.filter(
            Q(book_name__icontains=search_keywords) | Q(
                author__icontains=search_keywords))  # 根据关键词搜索数据库记录，icontains是不区分大小写
        for i in books_obj_list:
            data = {'achievement': '-', 'status': '-'}
            data['id'] = i.id
            data['book_price'] = i.book_price
            data['book_type'] = i.book_type
            data['author'] = i.author
            data['book_num'] = i.book_num
            data['book_name'] = i.book_name
            data['book_score'] = i.book_name
            data['book_sales'] = 'None'
            data['comment_nums'] = 'None'
            data['comment_nums'] = 'None'
            data['publisher_name'] = 'None'
            data['book_inventory'] = 'None'
            data['book_description'] = 'None'

            print(request.session['id'],'>>>>>>>>>>>>>>',i.id)
            user_obj = models.UserBook.objects.filter(user_id=request.session['id'], book_id=i.id)
            for j in user_obj:
                print(j.achievement,'111111',j.status)
                data['achievement'] = j.achievement
                data['status'] = j.status
            img = models.Image.objects.filter(books_id=i.id)
            for q in img:
                data['img_path'] = q.img_address.name

            book_list.append(data)
        print(book_list, '北京!!!!')
        # publishers_obj_list = models.Publisher.objects.filter(
        #     Q(name__icontains=search_keywords) | Q(address=search_keywords))
        #
        # users_obj_list = models.User.objects.filter(
        #     Q(name__icontains=search_keywords) | Q(nickname__icontains=search_keywords))
        # 判断查询结果，用来控制前端页面绘制
        # if len(books_obj_list) != 0:  # 如果能查询到，前端显示图书查询结果
        #     books_search_result = True
        # elif len(publishers_obj_list) != 0:  # 如果能查到，前端显示出版社查询结果
        #     publishers_search_result = True
        # elif len(users_obj_list) != 0:
        #     user_search_result = True  # 如果能查到，前端显示用户信息
        # else:
        #     error_msg = "没有查询到结果，请重新输入"
    else:
        error_msg = "你输入的信息错误,请重新出入"
    return render(request, "search_result.html", locals())

@librarian_decorator
def search2(request):
    # 要前端中获取用户输入的关键字
    search_keywords2 = request.POST.get("search_keywords2", "")
    print(search_keywords2,44444444444)
    print(request.session['id'])
    if search_keywords2:
        book_list = []
        books_obj_list = models.UserBook.objects.filter(Q(status__startswith=search_keywords2))  # 根据关键词搜索数据库记录，icontains是不区分大小写
        for j in books_obj_list:
            if int(j.user_id) == int(request.session['id']):
                data = {'achievement': '-', 'status': '-'}
                data['achievement'] = j.achievement
                data['status'] = j.status
                user_obj = models.Books.objects.filter(id=j.book_id)
                for i in user_obj:
                    data['id'] = i.id
                    data['book_price'] = i.book_price
                    data['book_type'] = i.book_type
                    data['author'] = i.author
                    data['book_num'] = i.book_num
                    data['book_name'] = i.book_name
                    data['book_score'] = i.book_name
                    data['book_sales'] = 'None'
                    data['comment_nums'] = 'None'
                    data['comment_nums'] = 'None'
                    data['publisher_name'] = 'None'
                    data['book_inventory'] = 'None'
                    data['book_description'] = 'None'
                    img = models.Image.objects.filter(books_id=j.book_id)
                    for q in img:
                        data['img_path'] = q.img_address.name

                book_list.append(data)
        print(book_list, '北京!!!!')
    elif search_keywords2 == '':
        book_list = []
        books_obj_list = models.UserBook.objects.filter(user_id=request.session['id'])
        for j in books_obj_list:
            if int(j.user_id) == int(request.session['id']):
                data = {'achievement': '-', 'status': '-'}
                data['achievement'] = j.achievement
                data['status'] = j.status
                user_obj = models.Books.objects.filter(id=j.book_id)
                for i in user_obj:
                    data['id'] = i.id
                    data['book_price'] = i.book_price
                    data['book_type'] = i.book_type
                    data['author'] = i.author
                    data['book_num'] = i.book_num
                    data['book_name'] = i.book_name
                    data['book_score'] = i.book_name
                    data['book_sales'] = 'None'
                    data['comment_nums'] = 'None'
                    data['comment_nums'] = 'None'
                    data['publisher_name'] = 'None'
                    data['book_inventory'] = 'None'
                    data['book_description'] = 'None'
                img = models.Image.objects.filter(books_id=j.book_id)
                for q in img:
                    data['img_path'] = q.img_address.name

                book_list.append(data)
        print(book_list,22222)
    else:
        error_msg = "你输入的信息错误,请重新出入"
    return render(request, "search_result.html", locals())

@librarian_decorator
def study(request):
    books_obj_list = models.UserBook.objects.filter(user_id=request.session['id'])
    datas = []
    yes_ = {'name':'通过','value':0}
    no_ = {'name':'未通过','value':0}
    none_ = {'name':'待学习','value':0}
    course = []
    achievement = []
    for i in books_obj_list:
        if i.status == '通过':
            yes_['value'] += 1
            book = models.Books.objects.filter(id=i.book_id)
            for j in book:
                course.append(j.book_name)
                achievement.append(i.achievement)
        elif i.status == '未通过请重新学习':
            no_['value'] += 1
            book = models.Books.objects.filter(id=i.book_id)
            for j in book:
                course.append(j.book_name)
                achievement.append(i.achievement)
        else:
            none_['value'] += 1

    datas.append(yes_)
    datas.append(no_)
    datas.append(none_)
    return JsonResponse({'datas':datas, 'course': course, 'achievement': achievement})
    # return JsonResponse({'datas':'{}'.format(datas), 'course': '{}'.format(course), 'achievement': '{}'.format(achievement)})



@librarian_decorator
def rank(request):
    book_id = request.GET.get("book_id")
    books_obj_list = models.UserBook.objects.filter(book_id=book_id)
    datas = []
    usernames=[]
    status = True
    myself = {'index': None, 'achievement': None}
    for i in books_obj_list:
        if i.status == '-':
            continue
        data = {'username': None, 'book_name': None, 'achievement': i.achievement}
        book = models.Books.objects.filter(id=i.book_id)
        for j in book:
            data['book_name'] = j.book_name
        user = models.Librarian.objects.filter(id=i.user_id)
        for j in user:
            data['username'] = j.name
        datas.append(data)
    result = sorted(datas, key=lambda  X:X['achievement'], reverse=True)
    if len(result) == 0 or result is None:
        status = False
    else:
        for row in result:
            usernames.append(row['username'])
        user_ = models.Librarian.objects.filter(id=request.session['id'])
        for j in user_:
            user_index = usernames.index(j.name) + 1
            myself['index'] = user_index
        achievement_ = models.UserBook.objects.filter(user_id=request.session['id'],book_id=book_id)
        for j in achievement_:
            myself['achievement'] = j.achievement
    return render(request, "ranking.html", locals())


@librarian_decorator
def index(request, page=1):
    # 从数据中获取出版社数据、作者数据、图书数据、用户数据
    publisher_num = models.Publisher.objects.count()
    author_num = models.Author.objects.count()
    book_num = models.Books.objects.count()
    user_num = models.User.objects.count()
    # 第1个图：图书销量和库存图
    # 获取每种图书类型的库存
    liter_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="文学")])
    pop_liter_book_inventory = sum(
        [book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="流行")])
    cultural_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="文化")])
    live_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="生活")])
    manage_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="经管")])
    science_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="科技")])
    # 图书类型存库列表
    book_type_inventory_list = [liter_book_inventory, pop_liter_book_inventory, cultural_book_inventory,
                                live_book_inventory, manage_book_inventory, science_book_inventory]
    # 获取图书类型销量数量
    liter_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="文学")])
    pop_liter_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="流行")])
    cultural_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="文化")])
    live_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="生活")])
    manage_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="经管")])
    science_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="科技")])
    # 图书类型销量列表
    book_type_sales_list = [liter_book_sales, pop_liter_book_sales, cultural_book_sales, live_book_sales,
                            manage_book_sales, science_book_sales]
    # 第2个图：图书类型占比图
    # 获取图书种类的数据
    liter_book_bum = models.Books.objects.filter(book_type="文学").count()
    pop_book_bum = models.Books.objects.filter(book_type="流行").count()
    cultural_book_bum = models.Books.objects.filter(book_type="文化").count()
    live_book_bum = models.Books.objects.filter(book_type="生活").count()
    manage_book_bum = models.Books.objects.filter(book_type="经管").count()
    science_book_bum = models.Books.objects.filter(book_type="科技").count()
    # 图书类型数量列表
    book_type_num_list = [liter_book_bum, pop_book_bum, cultural_book_bum, live_book_bum, manage_book_bum,
                          science_book_bum]
    # 第三个图：最近30天访问量
    # 来统计最近30天用户访问量
    # 当前年，月
    this_year = time.strftime("%Y", time.localtime(time.time()))
    # this_month = time.strftime("%m", time.localtime(time.time()))
    this_month = "9"
    res = models.User.objects.filter(last_time__month=this_month)
    print(res)
    # 按天分组
    # select = {'day': connection.ops.date_trunc_sql('day', 'last_time')}
    # 获取当月每天的用户访问数据
    count_data = models.User.objects.filter(last_time__year=this_year, last_time__month=this_month)
    # TODO：获取前30天的用户访问数量
    # 计算第前30天时间
    # time_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    # count_data = models.User.objects.filter(last_time__gte=time_30).extra(
    #     select=select).values('day').annotate(number=Count('id'))
    # 下面来处理数据，让当月的每天用户访问量和日期对应方便绘制折线图
    day_list = []  # 当月时间列表
    user_num_list = []  # 每天用户登录人数列表
    user_list = []
    for i, obj in enumerate(count_data):
        # day_list.append(obj[''].day)
        user_num_list.append(obj['number'])
    # 把当月时间列表和每天用户登录人数列表 转成成字典，方便后面进行数据处理
    user_login_dict = dict(zip(day_list, user_num_list))
    # 统计30天中每天用户登录人数，如果某一天没有人登录就置为0
    for day in range(1, 31):
        if day not in day_list:  # 如果某天不在数据库中的天数中时,说明这天网站没有用户浏览，用户数据为0
            user_login_dict[day] = 0
    # 按照日期顺序的方式，把这个月每天登录人数进行排序，把每天的登录人数放到列表里，方便给前端模板传值
    user_login_list = []
    for day in range(1, 31):
        for k, v in user_login_dict.items():
            if day == k:
                user_login_list.append(v)
    # 显示高销量的图书数据
    # 选择销量大于500的书籍并且倒序排列
    book_obj_list = models.Books.objects.filter(book_sales__gt=500).order_by("book_sales")
    paginator = Paginator(book_obj_list, 10)  # 实例化分页对象，每页显示10条数据
    total_page_num = paginator.num_pages  # 总页码
    current_page_num = page  # 当前页，默认显示第一页
    book_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
    page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
    # 当前页
    if total_page_num > 10:  # 当总页码大于10时
        if current_page_num < 9:  # 当前页小于10时
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)
    return render(request, 'index.html', locals())



def stream_video(request,arg_path):
    """将视频文件以流媒体的方式响应"""
    range_header = request.META.get('HTTP_RANGE').strip()
    range_re = re.compile('')
    range_re = re.compile('')



