from flask import current_app, abort, render_template, g
from info import db
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.models import News


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

    user = g.user.to_dict() if g.user else None

    # 将数据传入模板渲染
    return render_template("detail.html", news=news.to_dict(), rank_list=rank_list, user=user)
