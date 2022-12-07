from django.db import models

# Create your models here.
# administrator

class Librarian(models.Model):
    name = models.CharField(max_length=32, verbose_name="用户名",null=True, blank=True)  # 用户名
    nickname = models.CharField(max_length=32, verbose_name="昵称",null=True, blank=True)  # 昵称
    password = models.CharField(max_length=32, verbose_name="密码",null=True, blank=True)  # 密码
    achievement = models.CharField(max_length=32, verbose_name="成绩", null=True, blank=True)  # 成绩
    status = models.CharField(max_length=32, verbose_name="状态", null=True, blank=True)  # 状态
    # books_id = models.CharField(max_length=32, verbose_name="bookid", null=True, blank=True)



# publisher数据模型
class Publisher(models.Model):
    na = (('DT', u'DT'), ('TV', u'TV'), ('PD', u'PD'))
    name = models.CharField(max_length=128, verbose_name="OP",choices=na,null=True, blank=True)  # name
    address = models.CharField(max_length=128, verbose_name="Description",null=True, blank=True)  #description
    Maintainer = models.CharField(max_length=128, verbose_name="Maintainer",null=True, blank=True)  # 发布者
    update_date = models.CharField(max_length=128, verbose_name="Update_date",null=True, blank=True)
    file = models.CharField(max_length=128, verbose_name="File",null=True, blank=True)
    video = models.CharField(max_length=128, verbose_name="video",null=True, blank=True)
    site = models.CharField(max_length=128, verbose_name="Site", null=True, blank=True)


    # BOOKS数据模型
class Books(models.Model):
    book_num = models.CharField(max_length=32, verbose_name="图书编号",null=True, blank=True)  # 图书编号
    book_name = models.CharField(max_length=128, verbose_name="图书名称",null=True, blank=True)  # 图书名称
    author = models.CharField(max_length=255, verbose_name="作者",null=True, blank=True)  # 作者
    book_type = models.CharField(max_length=32,  verbose_name="图书类型",null=True, blank=True)  # 图书类型
    book_price = models.CharField( max_length=32,verbose_name="图书价格",null=True, blank=True)  # 图书价格
    book_inventory = models.IntegerField(verbose_name="图书库存",null=True, blank=True)  # 图书库存
    book_score = models.CharField(max_length=255, verbose_name="图书评分",null=True, blank=True)  # 评分
    book_description = models.TextField(verbose_name="图书简介",null=True, blank=True)  # 图书简介
    book_sales = models.IntegerField(verbose_name="图书销量",null=True, blank=True)  # 图书销量
    comment_nums = models.IntegerField(default=0, verbose_name="评论量",null=True, blank=True)  # 评论量
    achievement = models.CharField(max_length=32, verbose_name="成绩", null=True, blank=True)  # 成绩
    status = models.CharField(max_length=32, verbose_name="状态", null=True, blank=True)  # 状态
    publisher = models.ForeignKey(to='Publisher', on_delete=models.CASCADE, verbose_name="出版社名称",null=True, blank=True)  # 出版社和图书一对多关系
    # librarian = models.ForeignKey(to='Librarian', on_delete=models.CASCADE, verbose_name="图书", null=True, blank=True)

# 图片数据
class Image(models.Model):
    img_address = models.ImageField(upload_to='images',verbose_name="图片路径",null=True, blank=True)  # 图片路径 -->> 会将路径封装成一个对象，需要使用模块Pillow,python 3.6 后 使用 PIL 模块
    img_label = models.CharField(max_length=128, verbose_name="图片名称",null=True, blank=True)  # 图片名称
    books = models.ForeignKey(to='Books', on_delete=models.CASCADE, verbose_name="图书",null=True, blank=True)  # 图书的图片

# 视频位置
class Video(models.Model):
    video_address = models.CharField(max_length=128, verbose_name="视频路径",null=True, blank=True)  # 视频路径
    video_label = models.CharField(max_length=128, verbose_name="视频名称",null=True, blank=True)  # 视频名称
    books = models.ForeignKey(to='Books', on_delete=models.CASCADE, verbose_name="图书",null=True, blank=True)  # 图书的id

# 考试位置
class Test(models.Model):
    test_address = models.CharField(max_length=128, verbose_name="考试路径",null=True, blank=True)
    test_label = models.CharField(max_length=128, verbose_name="考试名称",null=True, blank=True)
    books = models.ForeignKey(to='Books', on_delete=models.CASCADE, verbose_name="图书",null=True, blank=True)

class File(models.Model):
    file_address = models.CharField(max_length=128, verbose_name="文件路径",null=True, blank=True)
    file_label = models.CharField(max_length=128, verbose_name="文件名称",null=True, blank=True)
    books = models.ForeignKey(to='Books', on_delete=models.CASCADE, verbose_name="图书",null=True, blank=True)



# author
class Author(models.Model):
    name = models.CharField(max_length=128, verbose_name="作者名称",null=True, blank=True)
    books = models.ManyToManyField(to='Books', related_name="author_book", verbose_name="图书",null=True, blank=True)


# 用户
class User(models.Model):
    name = models.CharField(max_length=32, verbose_name="用户名",null=True, blank=True)
    nickname = models.CharField(max_length=32, verbose_name="用户昵称",null=True, blank=True)
    password = models.CharField(max_length=32, verbose_name="密码",null=True, blank=True)
    phone = models.CharField(max_length=11, verbose_name="电话号码",null=True, blank=True)  # 电话
    last_time = models.DateTimeField(auto_now=True, verbose_name="登录时间",null=True, blank=True)
    books = models.ManyToManyField(to="Books", verbose_name="图书",null=True, blank=True)


# 单点

class UserBook(models.Model):
    user_id = models.CharField(max_length=32, verbose_name="userId",null=True, blank=True)
    book_id = models.CharField(max_length=32, verbose_name="bookId",null=True, blank=True)
    achievement = models.CharField(max_length=32, verbose_name="成绩", null=True, blank=True)  # 成绩
    status = models.CharField(max_length=32, verbose_name="状态", null=True, blank=True)  # 状态
    user_answer = models.CharField(max_length=128, verbose_name="学生答案", null=True, blank=True)  # 答案
    answer = models.CharField(max_length=128, verbose_name="标准答案", null=True, blank=True)  # 答案
    

