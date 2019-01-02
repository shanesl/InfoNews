from flask import current_app, abort, render_template, g, jsonify, request
from info import db
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.models import News
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
    news.clicks+=1
    user = g.user
    is_collected = False
    if user: # 用户已登录
        # 查询 当前用户是否已收藏了该新闻
        if news in user.collection_news:
            is_collected = True
    user = user.to_dict() if user else None

    # 将数据传入模板渲染
    return render_template("detail.html", news=news.to_dict(), rank_list=rank_list, user=user,is_collected=is_collected)


# 新闻收藏
@news_blu.route("/news_collect",methods=["POST"])
@user_login_data
def news_collect():
    user = g.user
    if not user:  # 未登录
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SERVERERR])

    # 获取参数
    action = request.json.get("action")
    news_id = request.json.get("news_id")
    # 校验参数
    if not all([action,news_id]):
        return jsonify(errno=RET.PARAMERR,errmsg=error_map[RET.PARAMERR])

    if action not in ["collect","cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
        news= News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    
    # 根据action 建立/解除 收藏关系
    if action == "collect":
        user.collection_news.append(news)
    else: # 取消收藏
        user.collection_news.remove(news)
        
    return jsonify(errno=RET.OK,errmsg=error_map[RET.OK])
