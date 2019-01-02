from flask import current_app, abort,render_template

from info.modules.news import news_blu
from info.utils.models import News

# 新闻详情
@news_blu.route("/<news_id>")
def news_detail(news_id):
    # 根据id 查询新闻数据
    try:
        news=News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    # 将数据传入模版渲染
    return render_template("detail.html",news=news.to_dict())