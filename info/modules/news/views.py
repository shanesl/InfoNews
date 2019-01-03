from flask import current_app, abort, render_template, g, jsonify, request
from info import db
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.models import News, Comment
from info.utils.response_code import RET, error_map


# 新闻详情
@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # 根据id查询新闻数据
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    # 查询点击量前10的新闻
    rank_list = []
    try:
        rank_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except BaseException as e:
        current_app.logger.error(e)

    rank_list = [news.to_basic_dict() for news in rank_list]

    # user_login_data()
    # 点击量+1
    news.clicks += 1
    user = g.user
    is_collected = False
    if user:  # 用户已登录
        # 查询 当前用户是否已收藏了该新闻
        if news in user.collection_news:
            is_collected = True

    # 查询该新闻的所有评论 生成时间排序
    comments = []
    try:
        comments = news.comments.order_by(Comment.create_time.desc()).all()
    except BaseException as e:
        current_app.logger.error(e)

    comment_list =[]
    for comment in comments:
        comment_dict = comment.to_dict()

        # 查询评论是否被当前用户点过赞
        is_like = False
        if user:
            if comment in user.like_comments:
                is_like = True

        comment_dict["is_like"]=is_like
        comment_list.append(comment_dict)

    user = user.to_dict() if user else None
    # 将数据传入模板渲染
    return render_template("detail.html", news=news.to_dict(), rank_list=rank_list, user=user,
                           is_collected=is_collected, comments=[comment.to_dict() for comment in comments] )


# 新闻收藏
@news_blu.route("/news_collect", methods=["POST"])
@user_login_data
def news_collect():
    user = g.user
    if not user:  # 未登录
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SERVERERR])

    # 获取参数
    action = request.json.get("action")
    news_id = request.json.get("news_id")
    # 校验参数
    if not all([action, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action 建立/解除 收藏关系
    if action == "collect":
        user.collection_news.append(news)
    else:  # 取消收藏
        user.collection_news.remove(news)

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 新闻评论
@news_blu.route("/news_comment", methods=["POST"])
@user_login_data
def news_comment():
    user = g.user
    if not user:  # 未登录
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_content = request.json.get("comment")
    parent_id = request.json.get("parent_id")
    news_id = request.json.get("news_id")

    # 校验参数
    if not all([comment_content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 生成一个评论对象
    comment = Comment()
    comment.content = comment_content
    comment.news_id = news_id
    comment.user_id = user.id

    if parent_id:  # 子评论
        try:
            parent_id = int(parent_id)
            comment.parent_id = parent_id
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    db.session.add(comment)
    # 为了生成主键，必须手动提交
    try:
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # json 返回结果（必须返回该评论的id）
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())


# 新闻点赞
@news_blu.route("/comment_like", methods=["POST"])
@user_login_data
def comment_like():
    # 判断用户是否登录
    user = g.user
    if not user:  # 未登录
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    action = request.json.get("action")
    comment_id = request.json.get("comment_id")

    # 校验参数
    if not all([action, comment_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 获取评论数据
    try:
        comment_id = int(comment_id)
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action 建立、解除关系
    if action == "add":
        user.like_comments.append(comment)
        comment.like_count += 1
    else:
        user.like_comments.remove(comment)
        comment.like_count -= 1

    # json 返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
