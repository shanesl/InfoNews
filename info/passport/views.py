from flask import request, abort, current_app, make_response, Response

from info import rs
from info.constants import IMAGE_CODE_REDIS_EXPIRES
from info.libs.captcha.pic_captcha import captcha
from info.passport import passport_blu

# 获取验证码
@passport_blu.route("/get_img_code")
def get_img_code():
    # 获取参数
    img_code_id = request.args.get("img_code_id")
    # 参数校验
    if not img_code_id:
        return abort(403)   # 403 表示服务器拒绝访问

    # 生成图片验证码(图片+文字)
    img_name,img_text,img_bytes=captcha.generate_captcha()

    # 保存验证码文字和图片key redis 方便设置过期时间，性能也好，键值关系满足需求
    try:
        rs.set("img_code_id"+img_code_id,img_text,ex=IMAGE_CODE_REDIS_EXPIRES)
    except BaseException as e:
        current_app.logger.error(e)   # 记录错误信息
        return abort(500)  # (服务器内部错误)服务器遇到错误，无法完成请求
    # 返回图片 自定义响应对象

    response = make_response(img_bytes)  # type:Response
    # 设置响应头
    response.content_type="image/jpeg"
    return response


