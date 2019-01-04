from flask import render_template, g, request, jsonify, current_app, abort

from info import db
from info.modules.user import user_blu
from info.utils.common import file_upload
from info.utils.constants import USER_COLLECTION_MAX_NEWS, QINIU_DOMIN_PREFIX, USER_RELEASE_MAX_NEWS
from info.utils.models import UserCollection, Category, News
from info.utils.response_code import error_map, RET


@user_blu.route("/user_info")
def user_info():
    return render_template("news/user.html", user=g.user.to_dict())


@user_blu.route("/base_info", methods=['GET', 'POST'])
def base_info():
    user = g.user
    if request.method == 'GET':
        return render_template("news/user_base_info.html", user=user.to_dict())

    # POST 提交资料
    # 获取参数
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")
    # 校验参数
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 修改用户数据
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender

    # json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@user_blu.route('/pic_info', methods=["GET", "POST"])
def pic_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pic_info.html", user=user.to_dict())

    # POST
    # 获取参数
    avatar_file = request.files.get("avatar")
    # 获取文件数据
    try:
        file_bytes = avatar_file.read()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 上传文件到七牛云服务器  一般会将文件单独管理起来  业务服务器 文件服务器
    try:
        file_name = file_upload(file_bytes)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # 修改头像链接
    user.avatar_url = file_name
    # json 返回， 必须返回头像链接
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_dict())


@user_blu.route('/pass_info', methods=["GET", "POST"])
def pass_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    # POST
    # 获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    # 校验参数
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 校验就密码
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg=error_map[RET.PWDERR])

    # 修改新密码
    user.password = new_password

    # json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@user_blu.route('/collection')
def collection():
    user = g.user
    # 获取参数
    p = request.args.get("p", 1)
    # 校验参数
    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    # 查询当前用户收藏的新闻 分页查询 收藏时间倒序
    try:
        pn = user.collection_news.order_by(UserCollection.create_time.desc()).paginate(p, USER_COLLECTION_MAX_NEWS)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    data = {
        "news_list": [news.to_dict() for news in pn.items],
        "cur_page": pn.page,
        "total_page": pn.pages
    }

    return render_template("news/user_collection.html", data=data)


@user_blu.route('/news_release', methods=["GET", "POST"])
def news_release():
    user = g.user

    if request.method == "GET":
        # 获取分类信息
        try:
            categories = Category.query.filter(Category.id != 1).all()
        except BaseException as e:
            current_app.logger.error(e)
            return abort(500)

        # 将分类数据传入模版渲染
        return render_template("news/user_news_release.html", categories=categories)

    # POST
    # 获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    content = request.form.get("content")
    img_file = request.files.get("index_image")
    # 校验参数
    if not all([title, category_id, digest, img_file, content]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 创建新闻
    news = News()
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.content = content

    # 将图片上传七牛云空间
    try:
        img_bytes = img_file.read()
        file_name = file_upload(img_bytes)  # 上传图片生成随机图片名
        news.index_image_url = QINIU_DOMIN_PREFIX + file_name  # 图片路径注意有无域名前缀
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])
    # 设置其他数据
    news.source = "个人发布"
    news.user_id = user.id  # 作者id
    news.status = 1  # 待审核状态

    # 添加到数据库
    db.session.add(news)
    # json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@user_blu.route('/news_list')
def news_list():
    user = g.user
    # 获取参数
    p = request.args.get("p", 1)
    # 校验参数
    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询当前用户发布的新闻发布时间倒序，分页查询
    try:
        pn = user.news_list.order_by(News.create_time.desc()).paginate(p, USER_RELEASE_MAX_NEWS)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    data = {
        "news_list": [news.to_review_dict() for news in pn.items],
        "total_page": pn.pages,
        "cur_page": pn.page

    }  # 注意要传递的数据是否正确

    return render_template("news/user_news_list.html", data=data)


@user_blu.route('/user_follow')
def user_follow():



    return render_template("news/user_follow.html")